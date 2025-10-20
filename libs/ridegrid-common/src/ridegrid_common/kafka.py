"""Kafka producer and consumer utilities with idempotency and EOS support."""

import json
from typing import Any, Callable, Dict, List, Optional

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from aiokafka.errors import KafkaError

from .errors import KafkaError as RideGridKafkaError
from .logging import get_logger

logger = get_logger(__name__)


class KafkaProducer:
    """Async Kafka producer with idempotency and transactional support."""

    def __init__(
        self,
        bootstrap_servers: str,
        enable_idempotence: bool = True,
        transactional_id: Optional[str] = None,
    ):
        self.bootstrap_servers = bootstrap_servers
        self.enable_idempotence = enable_idempotence
        self.transactional_id = transactional_id
        self.producer: Optional[AIOKafkaProducer] = None

    async def start(self) -> None:
        """Start the Kafka producer."""
        try:
            self.producer = AIOKafkaProducer(
                bootstrap_servers=self.bootstrap_servers,
                enable_idempotence=self.enable_idempotence,
                transactional_id=self.transactional_id,
                acks="all",
                compression_type="snappy",
                linger_ms=10,
                batch_size=32768,
                value_serializer=lambda v: json.dumps(v).encode("utf-8"),
                key_serializer=lambda k: k.encode("utf-8") if k else None,
            )
            await self.producer.start()

            if self.transactional_id:
                async with self.producer.transaction():
                    pass  # Initialize transaction

            logger.info(
                "Kafka producer started",
                bootstrap_servers=self.bootstrap_servers,
                idempotent=self.enable_idempotence,
                transactional=bool(self.transactional_id),
            )
        except KafkaError as e:
            logger.error("Failed to start Kafka producer", error=str(e))
            raise RideGridKafkaError(f"Failed to start producer: {e}")

    async def stop(self) -> None:
        """Stop the Kafka producer."""
        if self.producer:
            await self.producer.stop()
            logger.info("Kafka producer stopped")

    async def send(
        self,
        topic: str,
        value: Dict[str, Any],
        key: Optional[str] = None,
        headers: Optional[List[tuple]] = None,
    ) -> None:
        """Send a message to Kafka."""
        try:
            await self.producer.send(
                topic,
                value=value,
                key=key,
                headers=headers,
            )
            logger.debug("Message sent", topic=topic, key=key)
        except KafkaError as e:
            logger.error("Failed to send message", topic=topic, key=key, error=str(e))
            raise RideGridKafkaError(f"Failed to send message: {e}")

    async def send_batch(
        self,
        topic: str,
        messages: List[Dict[str, Any]],
        key_field: str = "id",
    ) -> None:
        """Send a batch of messages."""
        try:
            batch = self.producer.create_batch()

            for msg in messages:
                key = msg.get(key_field)
                metadata = batch.append(
                    key=key.encode("utf-8") if key else None,
                    value=json.dumps(msg).encode("utf-8"),
                    timestamp=None,
                )

                if metadata is None:
                    # Batch full, send it
                    partitions = await self.producer.partitions_for(topic)
                    partition = hash(key) % len(partitions) if key else 0
                    await self.producer.send_batch(batch, topic, partition=partition)

                    batch = self.producer.create_batch()
                    batch.append(
                        key=key.encode("utf-8") if key else None,
                        value=json.dumps(msg).encode("utf-8"),
                        timestamp=None,
                    )

            # Send remaining messages
            if not batch.is_empty():
                partitions = await self.producer.partitions_for(topic)
                partition = 0
                await self.producer.send_batch(batch, topic, partition=partition)

            logger.info("Batch sent", topic=topic, count=len(messages))
        except KafkaError as e:
            logger.error("Failed to send batch", topic=topic, error=str(e))
            raise RideGridKafkaError(f"Failed to send batch: {e}")


class KafkaConsumer:
    """Async Kafka consumer with at-least-once or exactly-once semantics."""

    def __init__(
        self,
        bootstrap_servers: str,
        topics: List[str],
        group_id: str,
        enable_auto_commit: bool = True,
        isolation_level: str = "read_uncommitted",
    ):
        self.bootstrap_servers = bootstrap_servers
        self.topics = topics
        self.group_id = group_id
        self.enable_auto_commit = enable_auto_commit
        self.isolation_level = isolation_level
        self.consumer: Optional[AIOKafkaConsumer] = None

    async def start(self) -> None:
        """Start the Kafka consumer."""
        try:
            self.consumer = AIOKafkaConsumer(
                *self.topics,
                bootstrap_servers=self.bootstrap_servers,
                group_id=self.group_id,
                enable_auto_commit=self.enable_auto_commit,
                auto_offset_reset="earliest",
                isolation_level=self.isolation_level,
                value_deserializer=lambda v: json.loads(v.decode("utf-8")),
                key_deserializer=lambda k: k.decode("utf-8") if k else None,
            )
            await self.consumer.start()
            logger.info(
                "Kafka consumer started",
                topics=self.topics,
                group_id=self.group_id,
                auto_commit=self.enable_auto_commit,
            )
        except KafkaError as e:
            logger.error("Failed to start Kafka consumer", error=str(e))
            raise RideGridKafkaError(f"Failed to start consumer: {e}")

    async def stop(self) -> None:
        """Stop the Kafka consumer."""
        if self.consumer:
            await self.consumer.stop()
            logger.info("Kafka consumer stopped")

    async def consume(
        self,
        handler: Callable[[Dict[str, Any], str, Optional[str]], Any],
        batch_size: int = 100,
    ) -> None:
        """Consume messages and process with handler."""
        try:
            async for msg in self.consumer:
                try:
                    await handler(msg.value, msg.topic, msg.key)

                    if not self.enable_auto_commit:
                        await self.consumer.commit()

                except Exception as e:
                    logger.error(
                        "Error processing message",
                        topic=msg.topic,
                        partition=msg.partition,
                        offset=msg.offset,
                        error=str(e),
                    )
                    # Re-raise to trigger retry or DLQ
                    raise

        except KafkaError as e:
            logger.error("Kafka consumer error", error=str(e))
            raise RideGridKafkaError(f"Consumer error: {e}")

    async def consume_batch(
        self,
        handler: Callable[[List[Dict[str, Any]]], Any],
        max_batch_size: int = 100,
        timeout_ms: int = 1000,
    ) -> None:
        """Consume messages in batches."""
        try:
            batch = []

            async for msg in self.consumer:
                batch.append(
                    {
                        "value": msg.value,
                        "key": msg.key,
                        "topic": msg.topic,
                        "partition": msg.partition,
                        "offset": msg.offset,
                    }
                )

                if len(batch) >= max_batch_size:
                    try:
                        await handler(batch)

                        if not self.enable_auto_commit:
                            await self.consumer.commit()

                        batch = []

                    except Exception as e:
                        logger.error("Error processing batch", batch_size=len(batch), error=str(e))
                        raise

        except KafkaError as e:
            logger.error("Kafka consumer error", error=str(e))
            raise RideGridKafkaError(f"Consumer error: {e}")

    async def get_lag(self) -> Dict[str, Dict[int, int]]:
        """Get consumer lag per topic/partition."""
        if not self.consumer:
            return {}

        lag_info = {}

        for topic_partition in self.consumer.assignment():
            topic = topic_partition.topic
            partition = topic_partition.partition

            committed = await self.consumer.committed(topic_partition)
            highwater = await self.consumer.highwater(topic_partition)

            if committed is not None and highwater is not None:
                lag = highwater - committed

                if topic not in lag_info:
                    lag_info[topic] = {}

                lag_info[topic][partition] = lag

        return lag_info
