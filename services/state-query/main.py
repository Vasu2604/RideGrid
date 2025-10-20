"""State Query Service - CQRS read models with WebSocket/SSE support."""

import asyncio
import json
import os
import sys
from datetime import datetime, timezone
from typing import Dict, List, Set

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse

# Add libs to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../libs/ridegrid-common/src"))

from ridegrid_common import (
    DatabaseManager,
    RedisManager,
    KafkaConsumer,
    setup_logging,
    get_logger,
    init_metrics_collector,
    add_ridegrid_middleware,
    Settings,
    NotFoundError,
)


# Pydantic models
class RideSummary(BaseModel):
    ride_id: str
    rider_id: str
    driver_id: str | None
    driver_name: str | None
    origin_lat: float
    origin_lon: float
    dest_lat: float
    dest_lon: float
    ride_type: str
    status: str
    surge_multiplier: float
    estimated_fare: str | None
    eta_seconds: int | None
    created_at: datetime
    updated_at: datetime


class DriverState(BaseModel):
    driver_id: str
    name: str | None
    status: str
    current_ride_id: str | None
    location_lat: float | None
    location_lon: float | None
    last_seen: datetime | None
    updated_at: datetime


# Global state
db_manager: DatabaseManager = None
redis_manager: RedisManager = None
settings: Settings = None

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        self.logger = get_logger(__name__)

    async def connect(self, websocket: WebSocket, channel: str):
        await websocket.accept()
        if channel not in self.active_connections:
            self.active_connections[channel] = set()
        self.active_connections[channel].add(websocket)
        self.logger.info("WebSocket connected", channel=channel, total=len(self.active_connections[channel]))

    def disconnect(self, websocket: WebSocket, channel: str):
        if channel in self.active_connections:
            self.active_connections[channel].discard(websocket)
            self.logger.info("WebSocket disconnected", channel=channel, total=len(self.active_connections[channel]))

    async def broadcast(self, channel: str, message: dict):
        if channel not in self.active_connections:
            return

        disconnected = set()
        for connection in self.active_connections[channel]:
            try:
                await connection.send_json(message)
            except Exception as e:
                self.logger.error("Error sending WebSocket message", error=str(e))
                disconnected.add(connection)

        # Clean up disconnected clients
        for connection in disconnected:
            self.active_connections[channel].discard(connection)


manager = ConnectionManager()


async def lifespan(app: FastAPI):
    """Lifecycle manager."""
    global db_manager, redis_manager, settings

    # Load settings
    settings = Settings(service_name="ridegrid-state-query")

    # Setup logging
    setup_logging(
        service_name=settings.service_name,
        log_level=settings.log_level,
        otel_endpoint=settings.otel_exporter_otlp_endpoint,
        enable_json=settings.is_production,
    )
    logger = get_logger(__name__)
    logger.info("Starting State Query service", environment=settings.environment)

    # Initialize metrics
    init_metrics_collector(settings.service_name, enable_otel=bool(settings.otel_exporter_otlp_endpoint))

    # Connect to databases
    db_manager = DatabaseManager(settings.database_url)
    await db_manager.connect()

    redis_manager = RedisManager(settings.redis_url)
    await redis_manager.connect()

    # Start event consumer for CQRS read model updates
    event_consumer_task = asyncio.create_task(consume_ride_events())

    logger.info("State Query service started successfully")

    yield

    # Shutdown
    logger.info("Shutting down State Query service")
    event_consumer_task.cancel()
    await redis_manager.disconnect()
    await db_manager.disconnect()


app = FastAPI(
    title="RideGrid State Query API",
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


# REST endpoints
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "ridegrid-state-query", "version": "1.0.0"}


@app.get("/healthz")
async def healthz():
    return {"status": "ok"}


@app.get("/api/rides/{ride_id}", response_model=RideSummary)
async def get_ride_summary(ride_id: str):
    """Get ride summary from read model."""
    row = await db_manager.fetchrow(
        "SELECT * FROM ride_summaries WHERE ride_id = $1",
        ride_id,
    )

    if not row:
        raise NotFoundError("Ride", ride_id)

    return RideSummary(**dict(row))


@app.get("/api/rides", response_model=List[RideSummary])
async def get_rides(
    rider_id: str | None = None,
    driver_id: str | None = None,
    status: str | None = None,
    limit: int = 50,
    offset: int = 0,
):
    """Get rides with filters."""
    query = "SELECT * FROM ride_summaries WHERE 1=1"
    params = []
    param_idx = 1

    if rider_id:
        query += f" AND rider_id = ${param_idx}"
        params.append(rider_id)
        param_idx += 1

    if driver_id:
        query += f" AND driver_id = ${param_idx}"
        params.append(driver_id)
        param_idx += 1

    if status:
        query += f" AND status = ${param_idx}"
        params.append(status)
        param_idx += 1

    query += f" ORDER BY created_at DESC LIMIT ${param_idx} OFFSET ${param_idx + 1}"
    params.extend([limit, offset])

    rows = await db_manager.fetch(query, *params)
    return [RideSummary(**dict(row)) for row in rows]


@app.get("/api/drivers/{driver_id}", response_model=DriverState)
async def get_driver_state(driver_id: str):
    """Get driver state from read model."""
    row = await db_manager.fetchrow(
        "SELECT * FROM driver_states WHERE driver_id = $1",
        driver_id,
    )

    if not row:
        raise NotFoundError("Driver", driver_id)

    return DriverState(**dict(row))


# WebSocket endpoint for real-time ride updates
@app.websocket("/ws/rides/{ride_id}")
async def websocket_ride_updates(websocket: WebSocket, ride_id: str):
    """Stream real-time ride updates via WebSocket."""
    channel = f"ride:{ride_id}"
    await manager.connect(websocket, channel)

    try:
        # Send initial state
        ride = await get_ride_summary(ride_id)
        await websocket.send_json({
            "type": "initial_state",
            "data": ride.model_dump(mode="json"),
        })

        # Keep connection alive and handle incoming messages
        while True:
            data = await websocket.receive_text()
            # Echo back (in real system, could handle commands)
            await websocket.send_json({"type": "ack", "message": "received"})

    except WebSocketDisconnect:
        manager.disconnect(websocket, channel)


# WebSocket endpoint for all rides
@app.websocket("/ws/rides")
async def websocket_all_rides(websocket: WebSocket):
    """Stream all ride updates via WebSocket."""
    channel = "rides:all"
    await manager.connect(websocket, channel)

    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_json({"type": "ack", "message": "received"})

    except WebSocketDisconnect:
        manager.disconnect(websocket, channel)


# SSE endpoint for ride updates
@app.get("/api/rides/{ride_id}/stream")
async def sse_ride_updates(ride_id: str):
    """Stream ride updates via Server-Sent Events."""
    
    async def event_generator():
        # Send initial state
        try:
            ride = await get_ride_summary(ride_id)
            yield {
                "event": "initial_state",
                "data": json.dumps(ride.model_dump(mode="json")),
            }
        except NotFoundError:
            yield {
                "event": "error",
                "data": json.dumps({"error": "Ride not found"}),
            }
            return

        # Stream updates from Redis pub/sub
        pubsub = redis_manager.client.pubsub()
        await pubsub.subscribe(f"ride:{ride_id}")

        try:
            async for message in pubsub.listen():
                if message["type"] == "message":
                    yield {
                        "event": "update",
                        "data": message["data"],
                    }
        finally:
            await pubsub.unsubscribe(f"ride:{ride_id}")

    return EventSourceResponse(event_generator())


# Background task to consume ride events and update read models
async def consume_ride_events():
    """Consume ride events and update CQRS read models."""
    logger = get_logger(__name__)
    logger.info("Starting ride events consumer")

    async def handle_ride_event(value: dict, topic: str, key: str):
        event_type = value.get("event_type")
        ride_id = value.get("ride_id")

        logger.debug("Processing ride event", ride_id=ride_id, event_type=event_type)

        try:
            if event_type == "DRIVER_ASSIGNED":
                # Update ride summary
                await db_manager.execute(
                    """
                    UPDATE ride_summaries
                    SET driver_id = $1, driver_name = $2, status = 'DRIVER_ASSIGNED',
                        eta_seconds = $3, estimated_fare = $4, updated_at = $5
                    WHERE ride_id = $6
                    """,
                    value.get("driver_id"),
                    value.get("driver_name"),
                    value.get("eta_seconds"),
                    value.get("estimated_fare"),
                    datetime.now(timezone.utc),
                    ride_id,
                )

                # Broadcast to WebSocket clients
                await manager.broadcast(f"ride:{ride_id}", {
                    "type": "ride_update",
                    "event": event_type,
                    "data": value,
                })
                await manager.broadcast("rides:all", {
                    "type": "ride_update",
                    "ride_id": ride_id,
                    "event": event_type,
                    "data": value,
                })

                # Publish to Redis for SSE
                await redis_manager.client.publish(f"ride:{ride_id}", json.dumps(value))

        except Exception as e:
            logger.error("Error processing ride event", ride_id=ride_id, error=str(e))

    consumer = KafkaConsumer(
        settings.kafka_bootstrap_servers,
        ["ride_events.v1"],
        group_id="state-query-group",
        enable_auto_commit=True,
    )
    await consumer.start()

    try:
        await consumer.consume(handle_ride_event)
    except asyncio.CancelledError:
        logger.info("Ride events consumer cancelled")
    finally:
        await consumer.stop()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)





