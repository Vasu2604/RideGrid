# Getting Started with RideGrid

Welcome to RideGrid - a production-ready distributed ride-hailing platform!

## 🚀 Quickest Way to Get Started

### Option 1: Automated Setup (Recommended)

```bash
# Run the setup script
./scripts/setup.sh

# Start all services
./scripts/start-all.sh

# Access the application
open http://localhost:3000
```

### Option 2: Using Make Commands

```bash
# Install dependencies
make install

# Generate protobuf code
make proto

# Start development environment
make dev-up

# View logs
make dev-logs
```

### Option 3: Manual Setup

See detailed steps in the main [README.md](README.md)

## 📋 What Gets Started

When you run the startup script, the following services will be launched:

### Infrastructure Services
- ✅ **PostgreSQL** (port 5432) - Main database with PostGIS
- ✅ **Redis** (port 6379) - Caching and geo-spatial queries
- ✅ **Redpanda/Kafka** (port 19092) - Event streaming
- ✅ **OpenTelemetry Collector** (port 4317) - Observability
- ✅ **Prometheus** (port 9090) - Metrics collection
- ✅ **Grafana** (port 3001) - Dashboards

### Application Services
- ✅ **Gateway** (port 8001) - REST API + gRPC
- ✅ **Telemetry Ingest** (port 8002) - gRPC streaming
- ✅ **Matching Engine** - Kafka consumer
- ✅ **Assignment Orchestrator** - Kafka consumer
- ✅ **State Query** (port 8003) - CQRS + WebSocket
- ✅ **Ops Console** (port 3000) - Next.js frontend

## 🌐 Service Endpoints

| Service | URL | Credentials |
|---------|-----|-------------|
| **Frontend** | http://localhost:3000 | N/A |
| **Gateway API** | http://localhost:8001 | N/A |
| **State Query API** | http://localhost:8003 | N/A |
| **Grafana** | http://localhost:3001 | admin/admin |
| **Prometheus** | http://localhost:9090 | N/A |
| **Kafka UI** | http://localhost:8080 | N/A |
| **Adminer** | http://localhost:8082 | server: postgres<br>user: ridegrid<br>password: ridegrid_dev |

## 🧪 Testing the System

### 1. Create a Ride Request

```bash
curl -X POST http://localhost:8001/api/rides \
  -H "Content-Type: application/json" \
  -d '{
    "rider_id": "rider_test_001",
    "origin": {
      "latitude": 37.7749,
      "longitude": -122.4194
    },
    "destination": {
      "latitude": 37.7849,
      "longitude": -122.4094
    },
    "ride_type": "ECONOMY",
    "passenger_count": 1,
    "payment_method_id": "pm_test_123"
  }'
```

### 2. Get Ride Details

```bash
# Replace {ride_id} with the ID from the previous response
curl http://localhost:8001/api/rides/{ride_id}
```

### 3. View in Frontend

1. Open http://localhost:3000
2. Navigate to Dashboard
3. See real-time updates

### 4. Run Load Tests

```bash
# REST API load test
make load-test

# Or directly with k6
k6 run load/k6/load-test.js
```

### 5. View Metrics

1. Open Grafana: http://localhost:3001
2. Login: admin/admin
3. Navigate to "RideGrid - System Overview" dashboard
4. See real-time metrics

## 📊 Sample Data

The system comes pre-loaded with sample data:

**Riders:**
- rider_001 - Alice Johnson
- rider_002 - Bob Smith
- rider_003 - Carol White

**Drivers:** (San Francisco area)
- driver_001 - David Brown (Toyota Camry)
- driver_002 - Emma Davis (Honda Accord)
- driver_003 - Frank Wilson (Tesla Model 3)
- driver_004 - Grace Lee (Nissan Altima)
- driver_005 - Henry Martinez (Ford Fusion)

## 🔍 Monitoring & Debugging

### View Service Logs

```bash
# All services
make dev-logs

# Specific service
tail -f logs/gateway.log
tail -f logs/matching.log
tail -f logs/frontend.log
```

### Check Service Health

```bash
# Gateway
curl http://localhost:8001/health

# State Query
curl http://localhost:8003/health
```

### View Kafka Topics

```bash
# Using Kafka UI
open http://localhost:8080

# Or using rpk CLI
docker exec -it ridegrid-redpanda rpk topic list
```

### Query Database

```bash
# Using Adminer
open http://localhost:8082

# Or using psql
docker exec -it ridegrid-postgres psql -U ridegrid -d ridegrid
```

## 🛑 Stopping Services

### Stop All Services

```bash
./scripts/stop-all.sh
```

### Stop Infrastructure Only

```bash
make dev-down
```

## 🐛 Troubleshooting

### Services Won't Start

1. Check if ports are already in use:
   ```bash
   lsof -i :3000,8001,8003,5432,6379,19092
   ```

2. Clean up and restart:
   ```bash
   make clean
   make dev-down
   make dev-up
   ```

### Database Connection Errors

1. Check PostgreSQL is running:
   ```bash
   docker ps | grep postgres
   ```

2. Reinitialize database:
   ```bash
   docker exec -it ridegrid-postgres psql -U ridegrid -d ridegrid < deploy/docker-compose/init-db.sql
   ```

### Kafka Connection Errors

1. Check Redpanda is healthy:
   ```bash
   docker exec -it ridegrid-redpanda rpk cluster health
   ```

2. Restart Redpanda:
   ```bash
   docker restart ridegrid-redpanda
   ```

### Frontend Build Errors

1. Clear cache and reinstall:
   ```bash
   cd web/ops-console
   rm -rf node_modules .next
   npm install
   npm run dev
   ```

## 📚 Next Steps

1. **Explore the Code**
   - Check out `services/` for backend services
   - Look at `web/ops-console/` for frontend
   - Review `libs/ridegrid-common/` for shared utilities

2. **Read the Documentation**
   - [Architecture Guide](docs/architecture.md)
   - [API Documentation](docs/api.md)
   - [Deployment Guide](docs/deployment.md)

3. **Run the Tests**
   ```bash
   make test
   make test-integration
   make load-test
   ```

4. **Deploy to Kubernetes**
   ```bash
   make deploy-k8s
   ```

## 🤝 Need Help?

- 📖 [Full Documentation](docs/)
- 🐛 [Troubleshooting Guide](docs/troubleshooting.md)
- 💬 Open an issue on GitHub

## 🎉 You're Ready!

Your RideGrid platform is now running. Enjoy exploring the distributed systems architecture!

---

**Quick Links:**
- [README](README.md) | [Architecture](docs/architecture.md) | [Project Summary](PROJECT_SUMMARY.md)





