# RideGrid - Quick Start Guide

## 🚀 Get Running in 2 Minutes

### Step 1: Clone and Navigate
```bash
cd /Users/vasupatel/Desktop/RIdeGrid
```

### Step 2: Run Setup
```bash
./scripts/setup.sh
```

**What happens:**
- ✅ Auto-detects Docker, Python, Node.js
- ✅ Chooses best deployment mode for you
- ✅ Builds images OR installs dependencies
- ✅ Starts all services

### Step 3: Access the App
Open your browser to:
- **Frontend**: http://localhost:3000
- **API**: http://localhost:8001
- **Grafana**: http://localhost:3001 (admin/admin)

---

## 🎯 What You'll See

### Landing Page (http://localhost:3000)
- Beautiful holographic grid theme
- KPI metrics showing performance
- Tech stack showcase
- Links to Dashboard and Simulator

### Dashboard
- Real-time ride metrics
- Throughput and latency charts
- Live event stream
- Active drivers count

### API Endpoints
```bash
# Create a ride
curl -X POST http://localhost:8001/api/rides \
  -H "Content-Type: application/json" \
  -d '{
    "rider_id": "test_rider",
    "origin": {"latitude": 37.7749, "longitude": -122.4194},
    "destination": {"latitude": 37.7849, "longitude": -122.4094},
    "ride_type": "ECONOMY",
    "passenger_count": 1,
    "payment_method_id": "pm_test"
  }'

# Get ride status
curl http://localhost:8001/api/rides/{ride_id}
```

---

## 🐳 If You Have Docker

**Easiest path - everything runs in containers:**

```bash
./scripts/setup.sh
# Opens Docker mode automatically
# All services start in containers
```

**Check it's running:**
```bash
cd deploy/docker-compose
docker-compose ps
```

**View logs:**
```bash
docker-compose logs -f gateway
docker-compose logs -f matching-engine
```

**Stop everything:**
```bash
docker-compose down
```

---

## 💻 If You Don't Have Docker (Local Mode)

**Prerequisites:**
- Python 3.11+
- Node.js 20+

**Setup will:**
1. Install Python dependencies
2. Install frontend dependencies  
3. Generate protobuf code
4. Prompt you to start services

**Start services:**
```bash
./scripts/start-all.sh
```

**Stop services:**
```bash
./scripts/stop-all.sh
```

---

## 🧪 Test It Works

### 1. Health Check
```bash
curl http://localhost:8001/health
# Should return: {"status":"healthy","service":"ridegrid-gateway",...}
```

### 2. Create Test Ride
```bash
curl -X POST http://localhost:8001/api/rides \
  -H "Content-Type: application/json" \
  -d '{
    "rider_id": "quickstart_test",
    "origin": {"latitude": 37.7749, "longitude": -122.4194},
    "destination": {"latitude": 37.7849, "longitude": -122.4094},
    "ride_type": "ECONOMY",
    "passenger_count": 1,
    "payment_method_id": "pm_test_123"
  }'
```

### 3. View in Browser
1. Go to http://localhost:3000/dashboard
2. See your ride appear in real-time
3. Check the live metrics update

---

## 📊 Run Load Tests

```bash
# Install k6 first (if not already)
brew install k6  # Mac
# or download from https://k6.io/docs/getting-started/installation/

# Run load test
k6 run load/k6/load-test.js
```

**What you'll see:**
- Throughput metrics
- Latency percentiles (p50, p95, p99)
- Success rate
- Performance report

---

## 🎨 Explore the Frontend

### Landing Page Features:
- **Hero Section**: Project overview with KPIs
- **Performance Metrics**: Real-time stats
- **Tech Stack**: Visual showcase
- **Navigation**: Dashboard, Simulator, Map, Traces

### Dashboard Features:
- **Live KPI Cards**: Total rides, queue depth, latency, active drivers
- **Charts**: Throughput over time, latency distribution
- **Event Feed**: Real-time ride events
- **WebSocket Indicator**: Shows live connection

---

## 📈 View Metrics in Grafana

1. Open http://localhost:3001
2. Login: `admin` / `admin`
3. Go to Dashboards
4. Select "RideGrid - System Overview"

**You'll see:**
- HTTP requests per second
- Request latency (p95)
- Kafka consumer lag
- Database performance
- Redis operations

---

## 🛑 Stopping Everything

### If Using Docker:
```bash
cd deploy/docker-compose
docker-compose down
```

### If Using Local Mode:
```bash
./scripts/stop-all.sh
```

---

## 🔧 Common Commands

```bash
# View all available commands
make help

# Build Docker images
make build

# Run tests
make test

# Run linters
make lint

# Format code
make format

# Open Grafana
make dashboard
```

---

## 📚 Next Steps

1. **Read the Docs**
   - [README.md](README.md) - Full documentation
   - [Architecture](docs/architecture.md) - System design
   - [Deployment Options](DEPLOYMENT_OPTIONS.md) - All deployment modes

2. **Explore the Code**
   - `services/` - Microservices (Python)
   - `web/ops-console/` - Frontend (Next.js)
   - `libs/ridegrid-common/` - Shared utilities

3. **Try Advanced Features**
   - Distributed tracing in Grafana
   - WebSocket streaming
   - Load testing with k6
   - Kubernetes deployment

4. **Customize**
   - Modify matching algorithms
   - Add new metrics
   - Enhance the UI
   - Deploy to production

---

## 🆘 Troubleshooting

### Setup script shows Docker error
**Solution**: Install Docker Desktop from https://docker.com
OR the script will automatically use local mode if Python/Node are available

### Port already in use
```bash
# Find and kill the process
lsof -ti:3000 | xargs kill -9  # Frontend
lsof -ti:8001 | xargs kill -9  # Gateway
```

### Services won't start
```bash
# Check prerequisites
docker --version
python3 --version
node --version

# View detailed logs
tail -f logs/gateway.log
```

### Frontend build fails
```bash
cd web/ops-console
rm -rf node_modules .next
npm install
npm run dev
```

---

## ✅ Success Checklist

- [ ] Setup script completed successfully
- [ ] http://localhost:3000 shows landing page
- [ ] http://localhost:8001/health returns healthy
- [ ] Can create a test ride via API
- [ ] Dashboard shows real-time updates
- [ ] Grafana dashboards display metrics

**All checked?** 🎉 **You're ready to explore RideGrid!**

---

## 💡 Pro Tips

1. **Use Docker mode** for quickest start - everything just works
2. **Use Local mode** for development - easier debugging
3. **Check Grafana** to see the system in action
4. **Run load tests** to see performance improvements
5. **Read PROJECT_SUMMARY.md** to understand what was built

---

**Need help?** Check [DEPLOYMENT_OPTIONS.md](DEPLOYMENT_OPTIONS.md) for detailed deployment guides.





