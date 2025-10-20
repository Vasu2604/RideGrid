"""Gateway service - FastAPI REST + gRPC with transactional outbox."""

import asyncio
import os
import sys
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import Depends, FastAPI, HTTPException, Header, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Add libs to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../libs/ridegrid-common/src"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../libs/ridegrid-proto"))

from ridegrid_common import (
    DatabaseManager,
    OutboxManager,
    RedisManager,
    KafkaProducer,
    setup_logging,
    get_logger,
    init_metrics_collector,
    add_ridegrid_middleware,
    Settings,
    RideGridError,
    NotFoundError,
    UnauthorizedError,
    RateLimitError,
)

# Pydantic models
class Location(BaseModel):
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)


class CreateRideRequest(BaseModel):
    rider_id: str
    origin: Location
    destination: Location
    ride_type: str = "ECONOMY"
    passenger_count: int = Field(default=1, ge=1, le=6)
    payment_method_id: str


class RideResponse(BaseModel):
    ride_id: str
    rider_id: str
    driver_id: Optional[str] = None
    origin: Location
    destination: Location
    ride_type: str
    status: str
    surge_multiplier: float
    estimated_fare: Optional[str] = None
    eta_seconds: Optional[int] = None
    created_at: datetime
    updated_at: datetime


class DriverStatusUpdate(BaseModel):
    driver_id: str
    status: str
    location: Optional[Location] = None


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    timestamp: datetime


# Global state
db_manager: DatabaseManager = None
outbox_manager: OutboxManager = None
redis_manager: RedisManager = None
kafka_producer: KafkaProducer = None
settings: Settings = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager for startup and shutdown."""
    global db_manager, outbox_manager, redis_manager, kafka_producer, settings

    # Load settings
    settings = Settings(service_name="ridegrid-gateway")

    # Setup logging
    setup_logging(
        service_name=settings.service_name,
        log_level=settings.log_level,
        otel_endpoint=settings.otel_exporter_otlp_endpoint,
        enable_json=settings.is_production,
    )
    logger = get_logger(__name__)
    logger.info("Starting Gateway service", environment=settings.environment)

    # Initialize metrics
    init_metrics_collector(settings.service_name, enable_otel=bool(settings.otel_exporter_otlp_endpoint))

    # Connect to databases
    db_manager = DatabaseManager(settings.database_url)
    await db_manager.connect()

    outbox_manager = OutboxManager(db_manager)

    redis_manager = RedisManager(settings.redis_url)
    await redis_manager.connect()

    # Start Kafka producer
    kafka_producer = KafkaProducer(
        settings.kafka_bootstrap_servers,
        enable_idempotence=True,
    )
    await kafka_producer.start()

    # Start outbox relay background task
    outbox_relay_task = asyncio.create_task(relay_outbox_messages())

    logger.info("Gateway service started successfully")

    yield

    # Shutdown
    logger.info("Shutting down Gateway service")
    outbox_relay_task.cancel()
    await kafka_producer.stop()
    await redis_manager.disconnect()
    await db_manager.disconnect()


app = FastAPI(
    title="RideGrid Gateway API",
    version="1.0.0",
    lifespan=lifespan,
)

# Add middleware
add_ridegrid_middleware(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins.split(",") if settings else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Dependency for rate limiting
async def check_rate_limit(
    x_client_id: Optional[str] = Header(None),
    x_forwarded_for: Optional[str] = Header(None),
):
    """Check rate limit for incoming requests."""
    client_id = x_client_id or x_forwarded_for or "anonymous"
    key = f"rate_limit:{client_id}"

    allowed, remaining = await redis_manager.check_rate_limit(
        key,
        max_requests=settings.rate_limit_requests,
        window_seconds=settings.rate_limit_window_seconds,
    )

    if not allowed:
        raise RateLimitError("Rate limit exceeded. Please try again later.")

    return {"client_id": client_id, "remaining": remaining}


# Health check
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        service="ridegrid-gateway",
        version="1.0.0",
        timestamp=datetime.now(timezone.utc),
    )


@app.get("/healthz")
async def healthz():
    """Kubernetes health check."""
    return {"status": "ok"}


# Ride endpoints
@app.post("/api/rides", response_model=RideResponse, dependencies=[Depends(check_rate_limit)])
async def create_ride(request: CreateRideRequest):
    """Create a new ride request."""
    logger = get_logger(__name__)

    ride_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)

    try:
        async with db_manager.pool.acquire() as conn:
            async with conn.transaction():
                # Insert ride
                await conn.execute(
                    """
                    INSERT INTO rides (
                        ride_id, rider_id, origin, destination, ride_type,
                        status, surge_multiplier, passenger_count, payment_method_id,
                        created_at, updated_at
                    ) VALUES ($1, $2, ST_SetSRID(ST_MakePoint($3, $4), 4326),
                              ST_SetSRID(ST_MakePoint($5, $6), 4326), $7, $8, $9, $10, $11, $12, $13)
                    """,
                    ride_id,
                    request.rider_id,
                    request.origin.longitude,
                    request.origin.latitude,
                    request.destination.longitude,
                    request.destination.latitude,
                    request.ride_type,
                    "REQUESTED",
                    1.0,  # TODO: Calculate surge
                    request.passenger_count,
                    request.payment_method_id,
                    now,
                    now,
                )

                # Add to outbox for Kafka publishing
                await outbox_manager.insert_message(
                    conn,
                    topic="ride_requests.v1",
                    key=ride_id,
                    payload={
                        "ride_id": ride_id,
                        "rider_id": request.rider_id,
                        "origin": {"lat": request.origin.latitude, "lon": request.origin.longitude},
                        "destination": {"lat": request.destination.latitude, "lon": request.destination.longitude},
                        "ride_type": request.ride_type,
                        "passenger_count": request.passenger_count,
                        "payment_method_id": request.payment_method_id,
                        "timestamp": now.isoformat(),
                    },
                )

        logger.info("Ride created", ride_id=ride_id, rider_id=request.rider_id)

        return RideResponse(
            ride_id=ride_id,
            rider_id=request.rider_id,
            origin=request.origin,
            destination=request.destination,
            ride_type=request.ride_type,
            status="REQUESTED",
            surge_multiplier=1.0,
            created_at=now,
            updated_at=now,
        )

    except Exception as e:
        logger.error("Failed to create ride", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to create ride: {str(e)}")


@app.get("/api/rides/{ride_id}", response_model=RideResponse)
async def get_ride(ride_id: str):
    """Get ride details."""
    logger = get_logger(__name__)

    row = await db_manager.fetchrow(
        """
        SELECT ride_id, rider_id, driver_id, 
               ST_X(origin::geometry) as origin_lon, ST_Y(origin::geometry) as origin_lat,
               ST_X(destination::geometry) as dest_lon, ST_Y(destination::geometry) as dest_lat,
               ride_type, status, surge_multiplier, estimated_fare, eta_seconds,
               created_at, updated_at
        FROM rides WHERE ride_id = $1
        """,
        ride_id,
    )

    if not row:
        raise NotFoundError("Ride", ride_id)

    return RideResponse(
        ride_id=row["ride_id"],
        rider_id=row["rider_id"],
        driver_id=row["driver_id"],
        origin=Location(latitude=row["origin_lat"], longitude=row["origin_lon"]),
        destination=Location(latitude=row["dest_lat"], longitude=row["dest_lon"]),
        ride_type=row["ride_type"],
        status=row["status"],
        surge_multiplier=row["surge_multiplier"],
        estimated_fare=row["estimated_fare"],
        eta_seconds=row["eta_seconds"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


@app.post("/api/rides/{ride_id}/cancel", response_model=RideResponse)
async def cancel_ride(ride_id: str, reason: str = "User cancelled"):
    """Cancel a ride."""
    logger = get_logger(__name__)

    try:
        async with db_manager.pool.acquire() as conn:
            async with conn.transaction():
                # Update ride status
                await conn.execute(
                    """
                    UPDATE rides
                    SET status = 'CANCELLED', cancelled_at = $1, updated_at = $1
                    WHERE ride_id = $2
                    """,
                    datetime.now(timezone.utc),
                    ride_id,
                )

                # Add to outbox
                await outbox_manager.insert_message(
                    conn,
                    topic="ride_events.v1",
                    key=ride_id,
                    payload={
                        "ride_id": ride_id,
                        "event_type": "RIDE_CANCELLED",
                        "reason": reason,
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    },
                )

        logger.info("Ride cancelled", ride_id=ride_id, reason=reason)

        return await get_ride(ride_id)

    except Exception as e:
        logger.error("Failed to cancel ride", ride_id=ride_id, error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to cancel ride: {str(e)}")


# Background task to relay outbox messages to Kafka
async def relay_outbox_messages():
    """Relay pending outbox messages to Kafka."""
    logger = get_logger(__name__)
    logger.info("Starting outbox relay task")

    while True:
        try:
            messages = await outbox_manager.get_pending_messages(limit=100)

            for msg in messages:
                try:
                    await kafka_producer.send(
                        topic=msg["topic"],
                        value=msg["payload"] if isinstance(msg["payload"], dict) else eval(msg["payload"]),
                        key=msg["key"],
                    )

                    async with db_manager.pool.acquire() as conn:
                        await outbox_manager.mark_published(conn, msg["message_id"])

                    logger.debug("Outbox message published", message_id=msg["message_id"], topic=msg["topic"])

                except Exception as e:
                    logger.error("Failed to publish outbox message", message_id=msg["message_id"], error=str(e))

            await asyncio.sleep(1)  # Poll every second

        except asyncio.CancelledError:
            logger.info("Outbox relay task cancelled")
            break
        except Exception as e:
            logger.error("Outbox relay error", error=str(e))
            await asyncio.sleep(5)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)





