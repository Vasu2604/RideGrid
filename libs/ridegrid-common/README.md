# RideGrid Common Library

Shared utilities, middleware, and abstractions for all RideGrid services.

## Features

- **Structured Logging**: OpenTelemetry-integrated logging with correlation IDs
- **Metrics Collection**: Prometheus metrics with OTel export
- **Middleware Stack**: FastAPI middleware for tracing, metrics, and correlation
- **Error Handling**: Custom error classes with standardized responses
- **Database Utilities**: AsyncPG manager with outbox/inbox pattern
- **Redis Utilities**: Async Redis with geo operations and rate limiting
- **Kafka Utilities**: Idempotent producers and consumers with EOS support
- **Configuration**: Pydantic-based settings management

## Installation

```bash
pip install -e libs/ridegrid-common
```

## Usage

### Logging

```python
from ridegrid_common import setup_logging, get_logger

setup_logging(
    service_name="my-service",
    log_level="INFO",
    otel_endpoint="http://otel-collector:4317",
    enable_json=True
)

logger = get_logger(__name__)
logger.info("Service started", version="1.0.0")
```

### Metrics

```python
from ridegrid_common import init_metrics_collector

metrics = init_metrics_collector("my-service", enable_otel=True)
metrics.record_http_request("GET", "/api/rides", 200, 0.123)
```

### Middleware

```python
from fastapi import FastAPI
from ridegrid_common import add_ridegrid_middleware

app = FastAPI()
add_ridegrid_middleware(app)
```

### Database with Outbox Pattern

```python
from ridegrid_common import DatabaseManager, OutboxManager

db = DatabaseManager("postgresql://...")
await db.connect()

outbox = OutboxManager(db)

async with db.pool.acquire() as conn:
    async with conn.transaction():
        # Business logic
        await conn.execute("INSERT INTO rides ...")
        
        # Add to outbox for reliable publishing
        await outbox.insert_message(
            conn, 
            topic="ride_requests.v1",
            key=ride_id,
            payload={"ride_id": ride_id, ...}
        )
```

### Redis Geo Operations

```python
from ridegrid_common import RedisManager

redis = RedisManager("redis://localhost:6379")
await redis.connect()

# Add driver location
await redis.geoadd("drivers:geo", -122.4194, 37.7749, "driver_123")

# Find nearby drivers
nearby = await redis.georadius(
    "drivers:geo", -122.4194, 37.7749, 5, unit="km", count=10
)
```

### Kafka Producer/Consumer

```python
from ridegrid_common import KafkaProducer, KafkaConsumer

# Producer
producer = KafkaProducer(
    "localhost:9092",
    enable_idempotence=True,
    transactional_id="my-producer"
)
await producer.start()
await producer.send("ride_requests.v1", {"ride_id": "123"}, key="123")

# Consumer
async def handle_message(value, topic, key):
    print(f"Received: {value}")

consumer = KafkaConsumer(
    "localhost:9092",
    ["ride_requests.v1"],
    group_id="my-consumer"
)
await consumer.start()
await consumer.consume(handle_message)
```

## Development

```bash
# Install dev dependencies
pip install -e "libs/ridegrid-common[dev]"

# Run tests
pytest tests/

# Lint
ruff check .
black .

# Type check
mypy .
```





