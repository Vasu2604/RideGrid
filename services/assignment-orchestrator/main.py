"""Assignment Orchestrator - Handle driver assignments with EOS guarantees."""

import asyncio
import json
import os
import sys
from datetime import datetime, timezone
from typing import Optional

# Add libs to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../libs/ridegrid-common/src"))

from ridegrid_common import (
    DatabaseManager,
    InboxManager,
    OutboxManager,
    KafkaProducer,
    KafkaConsumer,
    setup_logging,
    get_logger,
    init_metrics_collector,
    Settings,
)


class AssignmentOrchestrator:
    """Orchestrate driver assignments with exactly-once semantics."""

    def __init__(
        self,
        db_manager: DatabaseManager,
        inbox_manager: InboxManager,
        outbox_manager: OutboxManager,
        kafka_producer: KafkaProducer,
        logger,
    ):
        self.db = db_manager
        self.inbox = inbox_manager
        self.outbox = outbox_manager
        self.kafka = kafka_producer
        self.logger = logger

    async def process_candidate_match(self, message: dict, message_id: str):
        """Process a candidate match and create assignment."""
        ride_id = message["ride_id"]
        driver_id = message["driver_id"]

        self.logger.info(
            "Processing candidate match",
            ride_id=ride_id,
            driver_id=driver_id,
            message_id=message_id,
        )

        try:
            async with self.db.pool.acquire() as conn:
                async with conn.transaction():
                    # Check for duplicate processing (inbox pattern)
                    is_duplicate = await self.inbox.is_duplicate(
                        conn, message_id, "candidate_matches.v1"
                    )

                    if is_duplicate:
                        self.logger.info("Duplicate message, skipping", message_id=message_id)
                        return

                    # Check if ride is still available
                    ride = await conn.fetchrow(
                        "SELECT ride_id, status, driver_id FROM rides WHERE ride_id = $1",
                        ride_id,
                    )

                    if not ride:
                        self.logger.warning("Ride not found", ride_id=ride_id)
                        return

                    if ride["status"] != "REQUESTED":
                        self.logger.info(
                            "Ride already assigned or cancelled",
                            ride_id=ride_id,
                            status=ride["status"],
                        )
                        return

                    # Simulate driver acceptance (in real system, wait for driver response)
                    # For now, auto-accept the first match
                    rank = message.get("rank", 1)
                    accepted = rank == 1  # Auto-accept rank 1

                    # Insert assignment
                    await conn.execute(
                        """
                        INSERT INTO assignments (
                            ride_id, driver_id, eta_seconds, distance_km,
                            surge_multiplier, estimated_fare, rank, accepted
                        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                        ON CONFLICT (ride_id, driver_id) DO NOTHING
                        """,
                        ride_id,
                        driver_id,
                        message.get("eta_seconds"),
                        message.get("distance_km"),
                        message.get("surge_multiplier", 1.0),
                        message.get("estimated_fare"),
                        rank,
                        accepted,
                    )

                    if accepted:
                        # Update ride with assignment
                        now = datetime.now(timezone.utc)
                        await conn.execute(
                            """
                            UPDATE rides
                            SET driver_id = $1, status = 'DRIVER_ASSIGNED',
                                driver_assigned_at = $2, updated_at = $2,
                                eta_seconds = $3, estimated_fare = $4
                            WHERE ride_id = $5
                            """,
                            driver_id,
                            now,
                            message.get("eta_seconds"),
                            message.get("estimated_fare"),
                            ride_id,
                        )

                        # Update driver status
                        await conn.execute(
                            """
                            UPDATE drivers
                            SET status = 'ASSIGNED', updated_at = $1
                            WHERE driver_id = $2
                            """,
                            now,
                            driver_id,
                        )

                        # Add ride event to outbox
                        await self.outbox.insert_message(
                            conn,
                            topic="ride_events.v1",
                            key=ride_id,
                            payload={
                                "ride_id": ride_id,
                                "event_type": "DRIVER_ASSIGNED",
                                "driver_id": driver_id,
                                "eta_seconds": message.get("eta_seconds"),
                                "estimated_fare": message.get("estimated_fare"),
                                "timestamp": now.isoformat(),
                            },
                        )

                        # Add assignment confirmation to outbox
                        await self.outbox.insert_message(
                            conn,
                            topic="assignments.v1",
                            key=ride_id,
                            payload={
                                "ride_id": ride_id,
                                "driver_id": driver_id,
                                "accepted": True,
                                "assigned_at": now.isoformat(),
                            },
                        )

                        self.logger.info(
                            "Driver assigned to ride",
                            ride_id=ride_id,
                            driver_id=driver_id,
                        )

                    # Mark message as processed in inbox
                    await self.inbox.mark_processed(
                        conn, message_id, "candidate_matches.v1", message
                    )

        except Exception as e:
            self.logger.error(
                "Failed to process candidate match",
                ride_id=ride_id,
                driver_id=driver_id,
                error=str(e),
            )
            raise

    async def relay_outbox_messages(self):
        """Relay outbox messages to Kafka."""
        self.logger.info("Starting outbox relay")

        while True:
            try:
                messages = await self.outbox.get_pending_messages(limit=100)

                for msg in messages:
                    try:
                        payload = msg["payload"]
                        if isinstance(payload, str):
                            payload = json.loads(payload)

                        await self.kafka.send(
                            topic=msg["topic"],
                            value=payload,
                            key=msg["key"],
                        )

                        async with self.db.pool.acquire() as conn:
                            await self.outbox.mark_published(conn, msg["message_id"])

                        self.logger.debug(
                            "Outbox message published",
                            message_id=msg["message_id"],
                            topic=msg["topic"],
                        )

                    except Exception as e:
                        self.logger.error(
                            "Failed to publish outbox message",
                            message_id=msg["message_id"],
                            error=str(e),
                        )

                await asyncio.sleep(1)

            except asyncio.CancelledError:
                self.logger.info("Outbox relay cancelled")
                break
            except Exception as e:
                self.logger.error("Outbox relay error", error=str(e))
                await asyncio.sleep(5)


async def main():
    """Main entry point."""
    # Load settings
    settings = Settings(service_name="ridegrid-assignment-orchestrator")

    # Setup logging
    setup_logging(
        service_name=settings.service_name,
        log_level=settings.log_level,
        otel_endpoint=settings.otel_exporter_otlp_endpoint,
        enable_json=settings.is_production,
    )
    logger = get_logger(__name__)
    logger.info("Starting Assignment Orchestrator", environment=settings.environment)

    # Initialize metrics
    init_metrics_collector(settings.service_name, enable_otel=bool(settings.otel_exporter_otlp_endpoint))

    # Connect to database
    db_manager = DatabaseManager(settings.database_url)
    await db_manager.connect()

    inbox_manager = InboxManager(db_manager)
    outbox_manager = OutboxManager(db_manager)

    # Start Kafka producer
    kafka_producer = KafkaProducer(
        settings.kafka_bootstrap_servers,
        enable_idempotence=True,
    )
    await kafka_producer.start()

    # Create orchestrator
    orchestrator = AssignmentOrchestrator(
        db_manager, inbox_manager, outbox_manager, kafka_producer, logger
    )

    # Start outbox relay task
    outbox_task = asyncio.create_task(orchestrator.relay_outbox_messages())

    # Start Kafka consumer for candidate matches
    async def handle_candidate_match(value: dict, topic: str, key: str):
        # Use message offset as message_id for idempotency
        message_id = f"{topic}:{key}:{value.get('matched_at', datetime.now(timezone.utc).isoformat())}"
        await orchestrator.process_candidate_match(value, message_id)

    consumer = KafkaConsumer(
        settings.kafka_bootstrap_servers,
        ["candidate_matches.v1"],
        group_id="assignment-orchestrator-group",
        enable_auto_commit=False,  # Manual commit after processing
    )
    await consumer.start()

    logger.info("Assignment Orchestrator consuming from candidate_matches.v1")

    try:
        await consumer.consume(handle_candidate_match)
    except KeyboardInterrupt:
        logger.info("Shutting down Assignment Orchestrator")
    finally:
        outbox_task.cancel()
        await consumer.stop()
        await kafka_producer.stop()
        await db_manager.disconnect()


if __name__ == "__main__":
    asyncio.run(main())





