"""Matching Engine - Find nearby drivers for ride requests."""

import asyncio
import json
import os
import sys
from datetime import datetime, timezone
from typing import List, Tuple

# Add libs to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../libs/ridegrid-common/src"))

from ridegrid_common import (
    DatabaseManager,
    RedisManager,
    KafkaProducer,
    KafkaConsumer,
    setup_logging,
    get_logger,
    init_metrics_collector,
    Settings,
)


class MatchingEngine:
    """Core matching logic for driver-rider pairing."""

    def __init__(
        self,
        db_manager: DatabaseManager,
        redis_manager: RedisManager,
        kafka_producer: KafkaProducer,
        logger,
    ):
        self.db = db_manager
        self.redis = redis_manager
        self.kafka = kafka_producer
        self.logger = logger

    async def find_matches(self, ride_request: dict) -> List[dict]:
        """Find candidate drivers for a ride request."""
        ride_id = ride_request["ride_id"]
        origin_lat = ride_request["origin"]["lat"]
        origin_lon = ride_request["origin"]["lon"]
        ride_type = ride_request.get("ride_type", "ECONOMY")
        passenger_count = ride_request.get("passenger_count", 1)

        self.logger.info(
            "Finding matches",
            ride_id=ride_id,
            origin_lat=origin_lat,
            origin_lon=origin_lon,
        )

        # Try Redis geo-search first (hot path)
        nearby_drivers = await self._find_nearby_drivers_redis(
            origin_lon, origin_lat, radius_km=5, limit=10
        )

        if not nearby_drivers:
            # Fallback to PostGIS (cold path)
            nearby_drivers = await self._find_nearby_drivers_postgis(
                origin_lon, origin_lat, radius_km=5, limit=10
            )

        # Filter and rank candidates
        candidates = []
        for idx, (driver_id, distance_km) in enumerate(nearby_drivers):
            # Get driver details
            driver_state = await self.redis.get_json(f"driver:state:{driver_id}")
            
            if not driver_state:
                # Fetch from database
                driver_row = await self.db.fetchrow(
                    "SELECT driver_id, name, status, capacity FROM drivers WHERE driver_id = $1",
                    driver_id,
                )
                if not driver_row:
                    continue
                
                if driver_row["status"] != "IDLE":
                    continue
                
                if driver_row["capacity"] < passenger_count:
                    continue
            else:
                if driver_state.get("status") != "IDLE":
                    continue

            # Calculate ETA (simplified: 40 km/h average speed)
            eta_seconds = int((distance_km / 40) * 3600)

            # Calculate surge multiplier (simplified)
            surge_multiplier = await self._calculate_surge(origin_lat, origin_lon)

            # Calculate estimated fare
            base_fare = 5.0
            per_km_rate = 2.0
            estimated_fare = f"${(base_fare + distance_km * per_km_rate) * surge_multiplier:.2f}"

            candidate = {
                "ride_id": ride_id,
                "driver_id": driver_id,
                "eta_seconds": eta_seconds,
                "distance_km": distance_km,
                "surge_multiplier": surge_multiplier,
                "estimated_fare": estimated_fare,
                "rank": idx + 1,
                "matched_at": datetime.now(timezone.utc).isoformat(),
            }

            candidates.append(candidate)

        self.logger.info("Matches found", ride_id=ride_id, count=len(candidates))
        return candidates

    async def _find_nearby_drivers_redis(
        self, lon: float, lat: float, radius_km: float = 5, limit: int = 10
    ) -> List[Tuple[str, float]]:
        """Find nearby drivers using Redis GEORADIUS."""
        try:
            results = await self.redis.georadius(
                "drivers:geo",
                lon,
                lat,
                radius_km,
                unit="km",
                withdist=True,
                count=limit,
            )

            nearby = []
            for result in results:
                if isinstance(result, (list, tuple)) and len(result) >= 2:
                    driver_id = result[0]
                    distance = float(result[1])
                    nearby.append((driver_id, distance))

            return nearby

        except Exception as e:
            self.logger.error("Redis geo-search failed", error=str(e))
            return []

    async def _find_nearby_drivers_postgis(
        self, lon: float, lat: float, radius_km: float = 5, limit: int = 10
    ) -> List[Tuple[str, float]]:
        """Find nearby drivers using PostGIS."""
        try:
            rows = await self.db.fetch(
                """
                SELECT 
                    driver_id,
                    ST_Distance(
                        location::geography,
                        ST_SetSRID(ST_MakePoint($1, $2), 4326)::geography
                    ) / 1000 AS distance_km
                FROM drivers
                WHERE status = 'IDLE'
                AND ST_DWithin(
                    location::geography,
                    ST_SetSRID(ST_MakePoint($1, $2), 4326)::geography,
                    $3 * 1000
                )
                ORDER BY distance_km
                LIMIT $4
                """,
                lon,
                lat,
                radius_km,
                limit,
            )

            return [(row["driver_id"], row["distance_km"]) for row in rows]

        except Exception as e:
            self.logger.error("PostGIS search failed", error=str(e))
            return []

    async def _calculate_surge(self, lat: float, lon: float) -> float:
        """Calculate surge multiplier based on demand/supply."""
        # Simplified: check ride requests in area vs available drivers
        # In production, this would be more sophisticated
        return 1.0  # No surge for now

    async def process_ride_request(self, message: dict):
        """Process a ride request from Kafka."""
        ride_id = message["ride_id"]
        
        self.logger.info("Processing ride request", ride_id=ride_id)

        # Find candidate drivers
        candidates = await self.find_matches(message)

        if not candidates:
            self.logger.warning("No matches found", ride_id=ride_id)
            # Send to DLQ or retry topic
            await self.kafka.send(
                "dlq.no_drivers_available",
                value={"ride_id": ride_id, "reason": "No drivers available", "timestamp": datetime.now(timezone.utc).isoformat()},
                key=ride_id,
            )
            return

        # Publish candidates to assignment topic
        for candidate in candidates:
            await self.kafka.send(
                "candidate_matches.v1",
                value=candidate,
                key=ride_id,
            )

        self.logger.info("Candidates published", ride_id=ride_id, count=len(candidates))


async def main():
    """Main entry point."""
    # Load settings
    settings = Settings(service_name="ridegrid-matching-engine")

    # Setup logging
    setup_logging(
        service_name=settings.service_name,
        log_level=settings.log_level,
        otel_endpoint=settings.otel_exporter_otlp_endpoint,
        enable_json=settings.is_production,
    )
    logger = get_logger(__name__)
    logger.info("Starting Matching Engine", environment=settings.environment)

    # Initialize metrics
    init_metrics_collector(settings.service_name, enable_otel=bool(settings.otel_exporter_otlp_endpoint))

    # Connect to databases
    db_manager = DatabaseManager(settings.database_url)
    await db_manager.connect()

    redis_manager = RedisManager(settings.redis_url)
    await redis_manager.connect()

    # Start Kafka producer
    kafka_producer = KafkaProducer(
        settings.kafka_bootstrap_servers,
        enable_idempotence=True,
    )
    await kafka_producer.start()

    # Create matching engine
    matching_engine = MatchingEngine(db_manager, redis_manager, kafka_producer, logger)

    # Start Kafka consumer for ride requests
    async def handle_ride_request(value: dict, topic: str, key: str):
        await matching_engine.process_ride_request(value)

    consumer = KafkaConsumer(
        settings.kafka_bootstrap_servers,
        ["ride_requests.v1"],
        group_id="matching-engine-group",
        enable_auto_commit=True,
    )
    await consumer.start()

    logger.info("Matching Engine consuming from ride_requests.v1")

    try:
        await consumer.consume(handle_ride_request)
    except KeyboardInterrupt:
        logger.info("Shutting down Matching Engine")
    finally:
        await consumer.stop()
        await kafka_producer.stop()
        await redis_manager.disconnect()
        await db_manager.disconnect()


if __name__ == "__main__":
    asyncio.run(main())





