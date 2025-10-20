# RideGrid Architecture

## System Overview

RideGrid is a distributed ride-hailing platform built on event-driven microservices architecture with CQRS pattern, exactly-once semantics, and real-time streaming capabilities.

## Core Principles

1. **Event-Driven Architecture** - All inter-service communication via Kafka topics
2. **CQRS (Command Query Responsibility Segregation)** - Separate read/write models
3. **Exactly-Once Semantics** - Transactional outbox/inbox patterns
4. **Idempotency** - All operations are idempotent with deduplication
5. **Real-Time Streaming** - gRPC streaming for driver telemetry
6. **Observability-First** - OpenTelemetry for traces, metrics, and logs

## Service Architecture

### 1. Gateway Service (FastAPI + gRPC)

**Responsibilities:**
- Expose REST API for riders and drivers
- Handle authentication and authorization (JWT)
- Rate limiting with Redis token bucket
- Transactional outbox pattern for Kafka publishing
- Request validation and correlation ID tracking

**Key Endpoints:**
- `POST /api/rides` - Create ride request
- `GET /api/rides/{id}` - Get ride details
- `POST /api/rides/{id}/cancel` - Cancel ride

**Flow:**
1. Receive HTTP request
2. Validate payload with Pydantic
3. Check rate limits (Redis)
4. Begin database transaction
5. Insert ride record
6. Insert message to outbox table
7. Commit transaction
8. Background task relays outbox → Kafka

### 2. Telemetry Ingest Service (gRPC Streaming)

**Responsibilities:**
- Accept driver location streams via gRPC
- Store latest location in Redis geo-spatial index
- Batch and publish to Kafka `driver_telemetry.v1` topic
- Handle backpressure and circuit breaking

**Flow:**
1. Driver connects via gRPC stream
2. Receive location updates
3. Update Redis GEOSET (`drivers:geo`)
4. Update Redis hash (`driver:state:{id}`)
5. Add to batch buffer
6. Flush batch to Kafka when size or timeout reached

**Performance:**
- Batch size: 50 messages
- Batch timeout: 1 second
- Redis TTL: 5 minutes

### 3. Matching Engine (Kafka Consumer)

**Responsibilities:**
- Consume `ride_requests.v1` topic
- Find nearby available drivers
- Calculate ETA and surge pricing
- Publish candidates to `candidate_matches.v1` topic

**Matching Strategy:**
1. Try Redis geo-search (hot path) - O(log N)
2. Fallback to PostGIS query (cold path)
3. Filter by:
   - Driver status = IDLE
   - Vehicle capacity ≥ passenger count
   - Within 5km radius
4. Rank by distance (closest first)
5. Calculate ETA: distance_km / 40 km/h
6. Apply surge multiplier
7. Publish top 10 candidates

**Idempotency:**
- Redis memo with 10-minute TTL
- Postgres unique constraint on `(ride_id, driver_id)`

### 4. Assignment Orchestrator (Kafka Consumer)

**Responsibilities:**
- Consume `candidate_matches.v1` topic
- Simulate driver acceptance/rejection
- Update ride and driver status transactionally
- Publish events to `ride_events.v1` and `assignments.v1`

**Exactly-Once Semantics:**
1. Begin database transaction
2. Check inbox for duplicate message
3. Check ride availability
4. Insert assignment record
5. Update ride status
6. Update driver status
7. Insert events to outbox
8. Mark message as processed in inbox
9. Commit transaction
10. Background task relays outbox → Kafka

**Assignment Logic:**
- Auto-accept rank 1 driver
- Wait for driver response (future enhancement)
- Timeout after 30 seconds
- Re-publish to matching if no acceptance

### 5. State Query Service (FastAPI + WebSocket/SSE)

**Responsibilities:**
- Consume `ride_events.v1` topic
- Update CQRS read models (`ride_summaries`, `driver_states`)
- Expose REST API for queries
- Stream real-time updates via WebSocket/SSE

**Read Models:**
```sql
ride_summaries (
  ride_id, rider_id, driver_id, driver_name,
  origin_lat, origin_lon, dest_lat, dest_lon,
  status, surge_multiplier, eta_seconds, estimated_fare,
  created_at, updated_at
)

driver_states (
  driver_id, name, status, current_ride_id,
  location_lat, location_lon, last_seen, updated_at
)
```

**Real-Time Streaming:**
- WebSocket: `/ws/rides/{id}` - Single ride updates
- WebSocket: `/ws/rides` - All ride updates
- SSE: `/api/rides/{id}/stream` - Server-Sent Events fallback

## Data Flow

### Ride Request Flow

```
1. Rider → Gateway (REST)
   POST /api/rides

2. Gateway → PostgreSQL
   INSERT INTO rides
   INSERT INTO outbox_messages

3. Outbox Relay → Kafka
   Topic: ride_requests.v1
   Key: ride_id

4. Kafka → Matching Engine
   Find nearby drivers

5. Matching Engine → Kafka
   Topic: candidate_matches.v1
   Key: ride_id

6. Kafka → Assignment Orchestrator
   Process candidates

7. Assignment Orchestrator → PostgreSQL
   UPDATE rides SET driver_id, status
   INSERT INTO assignments
   INSERT INTO outbox_messages (ride_events)

8. Outbox Relay → Kafka
   Topic: ride_events.v1
   Event: DRIVER_ASSIGNED

9. Kafka → State Query
   UPDATE ride_summaries
   WebSocket broadcast to clients

10. State Query → Rider (WebSocket)
    Real-time ride status update
```

### Driver Telemetry Flow

```
1. Driver App → Telemetry Ingest (gRPC Stream)
   StreamDriverTelemetry

2. Telemetry Ingest → Redis
   GEOADD drivers:geo lon lat driver_id
   HSET driver:state:{id} lat lon heading speed status

3. Telemetry Ingest → Kafka (batched)
   Topic: driver_telemetry.v1
   Key: driver_id

4. Kafka → Matching Engine
   Update hot cache for matching
```

## Kafka Topics

| Topic | Partitions | Key | Purpose |
|-------|------------|-----|---------|
| `ride_requests.v1` | 48 | ride_id | Ride creation events |
| `driver_telemetry.v1` | 96 | driver_id | Driver location updates |
| `candidate_matches.v1` | 48 | ride_id | Matching results |
| `assignments.v1` | 48 | ride_id | Driver assignments |
| `ride_events.v1` | 24 | ride_id | Ride lifecycle events |
| `dlq.no_drivers_available` | 12 | ride_id | Dead letter queue |

## Database Schema

### Core Tables

**rides** - Ride requests and state
- Primary key: `ride_id`
- Indexes: `(status, created_at)`, rider_id, driver_id
- Geo columns: origin, destination (PostGIS GEOGRAPHY)

**drivers** - Driver profiles and location
- Primary key: `driver_id`
- Indexes: status, GIST(location), last_seen
- Geo column: location (PostGIS GEOGRAPHY Point)

**assignments** - Driver-ride assignments
- Unique: `(ride_id, driver_id)`
- Tracks acceptance, ETA, fare

**outbox_messages** - Transactional outbox
- Published via background relay
- Cleanup after 7 days

**inbox_messages** - Exactly-once deduplication
- Unique: `(message_id, source)`
- Cleanup after 7 days

## Observability

### Distributed Tracing (OpenTelemetry)

Trace spans:
- Gateway: HTTP request → DB transaction → Kafka publish
- Matching: Kafka consume → Redis query → PostGIS fallback
- Assignment: Kafka consume → DB transaction → Event publish
- State Query: Event consume → Read model update → WebSocket broadcast

Baggage propagation:
- `ride_id`
- `driver_id`
- `correlation_id`

### Metrics (Prometheus)

**Application Metrics:**
- `http_requests_total{service, method, endpoint, status}`
- `http_request_duration_seconds{service, method, endpoint}`
- `grpc_requests_total{service, method, status}`
- `kafka_messages_produced_total{topic}`
- `kafka_messages_consumed_total{topic, group}`
- `kafka_consumer_lag{topic, partition, group}`
- `matching_duration_seconds` - Time to find matches
- `drivers_active` - Current active drivers
- `rides_created_total{ride_type}` - Rides by type

**Infrastructure Metrics:**
- `db_connections_active{service}`
- `db_query_duration_seconds{operation}`
- `redis_operations_total{operation, status}`
- `redis_operation_duration_seconds{operation}`

### Logging (Structured JSON)

All services use `structlog` with:
- Correlation ID
- Request ID
- User ID
- Service name
- Log level
- Timestamp (ISO 8601)

## Resilience Patterns

### Circuit Breaker
- Redis failures → Fallback to PostgreSQL
- PostgreSQL failures → Return cached data
- Kafka failures → Store in local buffer

### Retry with Exponential Backoff
- Database queries: 3 retries, 1-10 second wait
- Kafka publish: 3 retries, 1-10 second wait
- External services: 3 retries, 1-10 second wait

### Rate Limiting
- Per-client token bucket (Redis sorted set)
- 100 requests per 60 seconds
- Return 429 Too Many Requests

### Backpressure
- Bounded queues for Kafka consumers
- Adaptive batch sizes
- Flow control in gRPC streams

## Scaling Considerations

### Horizontal Scaling
- All services are stateless
- Can scale independently
- KEDA autoscaling on Kafka lag

### Data Partitioning
- Kafka partitions by ride_id or driver_id
- PostgreSQL sharding by geography (future)
- Redis cluster mode (future)

### Caching Strategy
- Redis for hot data (active rides, driver locations)
- PostgreSQL for source of truth
- Read replicas for query scaling

## Security

### Authentication & Authorization
- JWT tokens for API authentication
- Service-to-service mTLS (production)
- API key for internal services

### Data Protection
- TLS for all external communication
- Encryption at rest for sensitive data
- PII masking in logs

### Network Security
- Private VPC for services
- Ingress only via API Gateway
- Network policies in Kubernetes

## Next Steps

1. **Multi-Region Deployment** - Cross-region replication
2. **Advanced Matching** - ML-based ETA and surge prediction
3. **Driver Pool Management** - Optimization algorithms
4. **Real-Time Analytics** - Stream processing with Flink
5. **Blue-Green Deployments** - Zero-downtime updates





