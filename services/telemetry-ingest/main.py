"""Telemetry Ingest Service - gRPC streaming for driver location data."""

import asyncio
import os
import sys
from datetime import datetime, timezone
from typing import AsyncIterator

import grpc
from concurrent import futures

# Add libs to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../libs/ridegrid-common/src"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../libs/ridegrid-proto"))

from ridegrid_common import (
    RedisManager,
    KafkaProducer,
    setup_logging,
    get_logger,
    init_metrics_collector,
    Settings,
)

try:
    from ridegrid_proto import ridegrid_pb2, ridegrid_pb2_grpc
except ImportError:
    # Proto files not generated yet
    ridegrid_pb2 = None
    ridegrid_pb2_grpc = None


class TelemetryIngestService:
    """gRPC service for streaming driver telemetry."""

    def __init__(
        self,
        redis_manager: RedisManager,
        kafka_producer: KafkaProducer,
        logger,
    ):
        self.redis = redis_manager
        self.kafka = kafka_producer
        self.logger = logger
        self.batch_buffer = []
        self.batch_size = 50
        self.batch_timeout = 1.0  # seconds

    async def StreamDriverTelemetry(
        self,
        request_iterator: AsyncIterator,
        context: grpc.aio.ServicerContext,
    ):
        """Stream driver telemetry data."""
        self.logger.info("Starting telemetry stream")

        try:
            async for telemetry in request_iterator:
                driver_id = telemetry.driver_id
                location = telemetry.location
                status = telemetry.status
                timestamp = datetime.now(timezone.utc)

                # Store latest location in Redis (geo-spatial index)
                await self.redis.geoadd(
                    "drivers:geo",
                    location.longitude,
                    location.latitude,
                    driver_id,
                )

                # Store driver state in Redis
                await self.redis.set_json(
                    f"driver:state:{driver_id}",
                    {
                        "driver_id": driver_id,
                        "lat": location.latitude,
                        "lon": location.longitude,
                        "heading": telemetry.heading,
                        "speed_kmh": telemetry.speed_kmh,
                        "status": status,
                        "last_seen": timestamp.isoformat(),
                    },
                    ex=300,  # 5 minute TTL
                )

                # Add to batch buffer for Kafka
                self.batch_buffer.append({
                    "driver_id": driver_id,
                    "location": {"lat": location.latitude, "lon": location.longitude},
                    "heading": telemetry.heading,
                    "speed_kmh": telemetry.speed_kmh,
                    "status": status,
                    "timestamp": timestamp.isoformat(),
                })

                # Flush batch if size threshold reached
                if len(self.batch_buffer) >= self.batch_size:
                    await self._flush_batch()

                self.logger.debug("Telemetry received", driver_id=driver_id)

            # Flush remaining messages
            if self.batch_buffer:
                await self._flush_batch()

            if ridegrid_pb2:
                return ridegrid_pb2.StreamTelemetryResponse(
                    success=True,
                    message="Telemetry stream processed successfully",
                )
            else:
                return {"success": True, "message": "Telemetry stream processed successfully"}

        except Exception as e:
            self.logger.error("Error processing telemetry stream", error=str(e))
            await context.abort(grpc.StatusCode.INTERNAL, str(e))

    async def _flush_batch(self):
        """Flush telemetry batch to Kafka."""
        if not self.batch_buffer:
            return

        try:
            await self.kafka.send_batch(
                "driver_telemetry.v1",
                self.batch_buffer,
                key_field="driver_id",
            )

            self.logger.info("Telemetry batch sent to Kafka", count=len(self.batch_buffer))
            self.batch_buffer = []

        except Exception as e:
            self.logger.error("Failed to send telemetry batch", error=str(e))

    async def GetDriverLocation(self, request, context: grpc.aio.ServicerContext):
        """Get current driver location."""
        driver_id = request.driver_id

        try:
            # Get from Redis
            driver_state = await self.redis.get_json(f"driver:state:{driver_id}")

            if not driver_state:
                await context.abort(grpc.StatusCode.NOT_FOUND, f"Driver {driver_id} not found")

            if ridegrid_pb2:
                return ridegrid_pb2.Driver(
                    driver_id=driver_id,
                    location=ridegrid_pb2.Location(
                        latitude=driver_state["lat"],
                        longitude=driver_state["lon"],
                    ),
                    heading=driver_state.get("heading", 0),
                    speed_kmh=driver_state.get("speed_kmh", 0),
                    status=driver_state.get("status", "OFFLINE"),
                )
            else:
                return {"driver_id": driver_id, **driver_state}

        except Exception as e:
            self.logger.error("Error getting driver location", driver_id=driver_id, error=str(e))
            await context.abort(grpc.StatusCode.INTERNAL, str(e))


async def serve():
    """Start the gRPC server."""
    # Load settings
    settings = Settings(service_name="ridegrid-telemetry-ingest")

    # Setup logging
    setup_logging(
        service_name=settings.service_name,
        log_level=settings.log_level,
        otel_endpoint=settings.otel_exporter_otlp_endpoint,
        enable_json=settings.is_production,
    )
    logger = get_logger(__name__)
    logger.info("Starting Telemetry Ingest service", environment=settings.environment)

    # Initialize metrics
    init_metrics_collector(settings.service_name, enable_otel=bool(settings.otel_exporter_otlp_endpoint))

    # Connect to Redis
    redis_manager = RedisManager(settings.redis_url)
    await redis_manager.connect()

    # Start Kafka producer
    kafka_producer = KafkaProducer(
        settings.kafka_bootstrap_servers,
        enable_idempotence=True,
    )
    await kafka_producer.start()

    # Create gRPC server
    server = grpc.aio.server(futures.ThreadPoolExecutor(max_workers=10))

    if ridegrid_pb2_grpc:
        ridegrid_pb2_grpc.add_TelemetryIngestServicer_to_server(
            TelemetryIngestService(redis_manager, kafka_producer, logger),
            server,
        )

    server.add_insecure_port("[::]:8000")
    await server.start()

    logger.info("Telemetry Ingest service listening on port 8000")

    try:
        await server.wait_for_termination()
    except KeyboardInterrupt:
        logger.info("Shutting down Telemetry Ingest service")
        await kafka_producer.stop()
        await redis_manager.disconnect()
        await server.stop(5)


if __name__ == "__main__":
    asyncio.run(serve())





