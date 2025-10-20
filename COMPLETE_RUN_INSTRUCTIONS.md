# 🚀 RideGrid Complete Run Instructions

## 🎯 Quick Start (Choose Your Adventure!)

### Option 1: 🐳 Docker Everything (Recommended)
```bash
# Navigate to project
cd /Users/vasupatel/Desktop/RIdeGrid

# Run the intelligent setup script
chmod +x scripts/setup.sh
./scripts/setup.sh
```

### Option 2: 🖥️ Local Development
```bash
# Navigate to project
cd /Users/vasupatel/Desktop/RIdeGrid

# Run local setup
chmod +x scripts/setup.sh
./scripts/setup.sh
```

### Option 3: 🎨 Frontend Only (Ultra-Creative UI Demo)
```bash
# Navigate to frontend
cd /Users/vasupatel/Desktop/RIdeGrid/web/ops-console

# Install dependencies
npm install

# Start the ultra-creative frontend
npm run dev
```

---

## 🐳 Docker Setup (Full System)

### Prerequisites
- Docker Desktop installed
- Docker Compose available

### Step 1: Start All Services
```bash
cd /Users/vasupatel/Desktop/RIdeGrid
./scripts/setup.sh
```

### Step 2: Access the Services
- **Frontend (Ultra-Creative UI)**: http://localhost:3000
- **Gateway API**: http://localhost:8000
- **Telemetry Ingest**: http://localhost:8001
- **Matching Engine**: http://localhost:8002
- **Assignment Orchestrator**: http://localhost:8003
- **State Query**: http://localhost:8004
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3001
- **Redis**: localhost:6379
- **PostgreSQL**: localhost:5432
- **Redpanda (Kafka)**: localhost:9092

---

## 🖥️ Local Development Setup

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker (for infrastructure services)

### Step 1: Install Python Dependencies
```bash
# Install shared libraries
cd /Users/vasupatel/Desktop/RIdeGrid/libs/ridegrid-common
pip install -e .

# Install service dependencies
cd /Users/vasupatel/Desktop/RIdeGrid/services/gateway
pip install -r requirements.txt

cd /Users/vasupatel/Desktop/RIdeGrid/services/telemetry-ingest
pip install -r requirements.txt

cd /Users/vasupatel/Desktop/RIdeGrid/services/matching-engine
pip install -r requirements.txt

cd /Users/vasupatel/Desktop/RIdeGrid/services/assignment-orchestrator
pip install -r requirements.txt

cd /Users/vasupatel/Desktop/RIdeGrid/services/state-query
pip install -r requirements.txt
```

### Step 2: Generate Protobuf Code
```bash
cd /Users/vasupatel/Desktop/RIdeGrid
mkdir -p libs/ridegrid-proto/ridegrid_proto
python -m grpc_tools.protoc \
  --proto_path=proto \
  --python_out=libs/ridegrid-proto/ridegrid_proto \
  --grpc_python_out=libs/ridegrid-proto/ridegrid_proto \
  proto/ridegrid.proto
```

### Step 3: Install Frontend Dependencies
```bash
cd /Users/vasupatel/Desktop/RIdeGrid/web/ops-console
npm install
```

### Step 4: Start Infrastructure Services
```bash
cd /Users/vasupatel/Desktop/RIdeGrid/deploy/docker-compose
docker-compose up -d postgres redis redpanda otel-collector prometheus grafana
```

### Step 5: Initialize Database
```bash
cd /Users/vasupatel/Desktop/RIdeGrid/deploy/docker-compose
docker-compose exec -T postgres psql -U ridegrid -d ridegrid < init-db.sql
```

### Step 6: Start Backend Services
```bash
# Terminal 1 - Gateway
cd /Users/vasupatel/Desktop/RIdeGrid/services/gateway
python main.py

# Terminal 2 - Telemetry Ingest
cd /Users/vasupatel/Desktop/RIdeGrid/services/telemetry-ingest
python main.py

# Terminal 3 - Matching Engine
cd /Users/vasupatel/Desktop/RIdeGrid/services/matching-engine
python main.py

# Terminal 4 - Assignment Orchestrator
cd /Users/vasupatel/Desktop/RIdeGrid/services/assignment-orchestrator
python main.py

# Terminal 5 - State Query
cd /Users/vasupatel/Desktop/RIdeGrid/services/state-query
python main.py
```

### Step 7: Start Frontend
```bash
cd /Users/vasupatel/Desktop/RIdeGrid/web/ops-console
npm run dev
```

---

## 🎨 Frontend Only (Ultra-Creative UI)

### Quick Demo Mode
```bash
cd /Users/vasupatel/Desktop/RIdeGrid/web/ops-console
npm install
npm run dev
```

**Access the ultra-creative UI at: http://localhost:3000**

### What You'll See:
- 🧠 **Quantum Neural Network Background** with real-time animations
- ⚛️ **Particle Swarm System** with 5 different particle types
- 🌌 **Holographic Text Effects** with shifting gradients
- 🎭 **3D Card Transformations** on hover
- 🚀 **Consciousness-Level Animations** throughout
- 🌈 **Quantum Field Effects** that follow your mouse
- 💫 **Matrix Rain Effect** with cascading binary code
- 🎨 **Cyberpunk Glass Morphism** with advanced effects

---

## 🔧 Development Commands

### Backend Services
```bash
# Start all services
make dev:up

# Stop all services
make dev:down

# Run tests
make test

# Run linting
make lint

# Type checking
make typecheck
```

### Frontend
```bash
# Development server
npm run dev

# Build for production
npm run build

# Start production server
npm start

# Run tests
npm test

# Lint code
npm run lint
```

### Load Testing
```bash
# Run k6 load tests
make load

# Generate performance report
make report
```

---

## 🐳 Docker Commands

### Start All Services
```bash
cd /Users/vasupatel/Desktop/RIdeGrid/deploy/docker-compose
docker-compose up -d
```

### Stop All Services
```bash
cd /Users/vasupatel/Desktop/RIdeGrid/deploy/docker-compose
docker-compose down
```

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f gateway
docker-compose logs -f ops-console
```

### Rebuild Services
```bash
# Rebuild all
docker-compose build

# Rebuild specific service
docker-compose build gateway
docker-compose build ops-console
```

---

## 🎯 Service Endpoints

### Frontend (Ultra-Creative UI)
- **URL**: http://localhost:3000
- **Features**: Quantum neural network, particle systems, holographic effects

### Backend Services
- **Gateway**: http://localhost:8000
  - REST API for ride requests
  - JWT authentication
  - Kafka event publishing

- **Telemetry Ingest**: http://localhost:8001
  - gRPC streaming for driver locations
  - Redis geo-indexing
  - Kafka telemetry streaming

- **Matching Engine**: http://localhost:8002
  - Kafka consumer for ride requests
  - Redis/PostGIS matching algorithms
  - Candidate match publishing

- **Assignment Orchestrator**: http://localhost:8003
  - Kafka consumer for candidate matches
  - Postgres transaction management
  - Ride event publishing

- **State Query**: http://localhost:8004
  - CQRS read models
  - WebSocket/SSE streams
  - Real-time UI updates

### Infrastructure Services
- **PostgreSQL**: localhost:5432
  - Database: ridegrid
  - User: ridegrid
  - Password: ridegrid

- **Redis**: localhost:6379
  - Geo-indexing for drivers
  - Token buckets for rate limiting
  - Idempotency tracking

- **Redpanda (Kafka)**: localhost:9092
  - Topics: ride_requests, driver_telemetry, candidate_matches, assignments, ride_events

- **Prometheus**: http://localhost:9090
  - Metrics collection
  - Service monitoring

- **Grafana**: http://localhost:3001
  - Dashboards: admin/admin
  - RideGrid overview dashboard

---

## 🚀 Production Deployment

### Kubernetes Deployment
```bash
# Install Helm charts
helm install ridegrid ./helm/ridegrid

# Upgrade deployment
helm upgrade ridegrid ./helm/ridegrid

# Uninstall
helm uninstall ridegrid
```

### Environment Variables
```bash
# Database
DATABASE_URL=postgresql://ridegrid:ridegrid@postgres:5432/ridegrid

# Redis
REDIS_URL=redis://redis:6379

# Kafka
KAFKA_BOOTSTRAP_SERVERS=redpanda:9092

# Service URLs
GATEWAY_URL=http://gateway:8000
TELEMETRY_INGEST_URL=http://telemetry-ingest:8001
MATCHING_ENGINE_URL=http://matching-engine:8002
ASSIGNMENT_ORCHESTRATOR_URL=http://assignment-orchestrator:8003
STATE_QUERY_URL=http://state-query:8004
```

---

## 🎨 Ultra-Creative UI Features

### Visual Effects
- **Quantum Neural Network**: Real-time SVG visualization
- **Particle Swarm System**: 5 different particle types
- **Holographic Text**: Shifting gradient effects
- **3D Transformations**: Interactive hover effects
- **Matrix Rain**: Cascading binary code
- **Cyberpunk Grid**: Animated background patterns

### Interactive Elements
- **Mouse Tracking**: Quantum field effects follow cursor
- **Neural Activity**: Real-time node connections
- **Particle Generation**: Dynamic particle creation
- **Holographic Overlays**: Interactive card effects
- **Consciousness Cards**: 3D transformation animations

### Animation System
- **20+ Custom Animations**: Quantum physics-inspired
- **Neural Network Flow**: Real-time connection updates
- **Particle Systems**: GPU-accelerated effects
- **Holographic Shifts**: Color gradient transitions
- **Reality Warping**: Time distortion effects

---

## 🔍 Troubleshooting

### Common Issues

1. **Port Conflicts**
   ```bash
   # Check what's using ports
   lsof -i :3000
   lsof -i :8000
   
   # Kill processes if needed
   pkill -f "next dev"
   pkill -f "uvicorn"
   ```

2. **Docker Issues**
   ```bash
   # Reset Docker
   docker-compose down -v
   docker system prune -a
   docker-compose up -d
   ```

3. **Database Connection**
   ```bash
   # Check PostgreSQL
   docker-compose exec postgres psql -U ridegrid -d ridegrid -c "SELECT 1;"
   ```

4. **Frontend Build Issues**
   ```bash
   # Clear Next.js cache
   rm -rf .next
   npm run dev
   ```

### Health Checks
```bash
# Check all services
curl http://localhost:3000  # Frontend
curl http://localhost:8000/health  # Gateway
curl http://localhost:8001/health  # Telemetry
curl http://localhost:8002/health  # Matching
curl http://localhost:8003/health  # Assignment
curl http://localhost:8004/health  # State Query
```

---

## 🎉 Success! You're Ready to Experience the Quantum Revolution!

Visit **http://localhost:3000** to see the ultra-creative RideGrid interface with:
- 🧠 Quantum neural network backgrounds
- ⚛️ Particle swarm systems
- 🌌 Holographic text effects
- 🎭 3D card transformations
- 🚀 Consciousness-level animations
- 🌈 Quantum field effects
- 💫 Matrix rain effects
- 🎨 Cyberpunk glass morphism

**Welcome to the future of distributed ride-hailing! 🌌⚛️🧠✨**
