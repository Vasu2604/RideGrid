# RideGrid Deployment Options

This guide explains the different ways to deploy and run RideGrid based on what tools you have available.

## 🐳 Option 1: Docker-Only Deployment (Recommended)

**Best for:** Quick start, demo, production-like environment

**Prerequisites:**
- Docker Desktop or Docker Engine
- Docker Compose

**Steps:**

1. **Run the setup script:**
   ```bash
   ./scripts/setup.sh
   ```
   
   The script will automatically detect Docker and build all images.

2. **Everything runs in containers:**
   - All Python services (gateway, telemetry, matching, assignment, state-query)
   - Frontend (Next.js)
   - Infrastructure (PostgreSQL, Redis, Kafka, Prometheus, Grafana)

3. **Access the application:**
   - Frontend: http://localhost:3000
   - Gateway API: http://localhost:8001
   - Grafana: http://localhost:3001 (admin/admin)

4. **View logs:**
   ```bash
   cd deploy/docker-compose
   docker-compose logs -f
   ```

5. **Stop everything:**
   ```bash
   cd deploy/docker-compose
   docker-compose down
   ```

---

## 💻 Option 2: Local Development Mode

**Best for:** Active development, debugging, code changes

**Prerequisites:**
- Python 3.11+
- Node.js 20+
- (Optional) Docker for infrastructure

**Steps:**

1. **Run the setup script:**
   ```bash
   ./scripts/setup.sh
   ```
   
   The script will detect your local Python/Node and set up dependencies.

2. **Start infrastructure (if Docker available):**
   ```bash
   cd deploy/docker-compose
   docker-compose up -d postgres redis redpanda otel-collector prometheus grafana
   ```

3. **Start Python services:**
   ```bash
   # Terminal 1 - Gateway
   cd services/gateway
   python3 main.py

   # Terminal 2 - Telemetry Ingest
   cd services/telemetry-ingest
   python3 main.py

   # Terminal 3 - Matching Engine
   cd services/matching-engine
   python3 main.py

   # Terminal 4 - Assignment Orchestrator
   cd services/assignment-orchestrator
   python3 main.py

   # Terminal 5 - State Query
   cd services/state-query
   python3 main.py
   ```

4. **Start frontend:**
   ```bash
   # Terminal 6 - Frontend
   cd web/ops-console
   npm run dev
   ```

5. **Or use the convenience script:**
   ```bash
   ./scripts/start-all.sh
   ```

6. **Stop all services:**
   ```bash
   ./scripts/stop-all.sh
   ```

---

## 🔄 Option 3: Hybrid Mode

**Best for:** Debugging specific services while running others in Docker

**Prerequisites:**
- Docker + Docker Compose
- Python 3.11+ (for services you want to debug)

**Steps:**

1. **Start infrastructure and most services in Docker:**
   ```bash
   cd deploy/docker-compose
   docker-compose up -d postgres redis redpanda otel-collector prometheus grafana
   ```

2. **Stop the service you want to debug:**
   ```bash
   docker-compose stop gateway
   ```

3. **Run that service locally:**
   ```bash
   cd ../../services/gateway
   export DATABASE_URL=postgresql://ridegrid:ridegrid_dev@localhost:5432/ridegrid
   export REDIS_URL=redis://localhost:6379
   export KAFKA_BOOTSTRAP_SERVERS=localhost:19092
   python3 main.py
   ```

---

## ☸️ Option 4: Kubernetes Deployment

**Best for:** Production deployment, scaling, high availability

**Prerequisites:**
- Kubernetes cluster (kind, minikube, GKE, EKS, AKS)
- kubectl configured
- Helm 3+

**Steps:**

1. **Build and push images:**
   ```bash
   # Using Docker
   make build
   
   # Tag and push to your registry
   docker tag ridegrid/gateway:latest your-registry/ridegrid/gateway:latest
   docker push your-registry/ridegrid/gateway:latest
   # Repeat for all services...
   ```

2. **Install with Helm:**
   ```bash
   helm install ridegrid helm/ridegrid \
     --set global.imageRegistry=your-registry \
     --set postgresql.auth.password=your-secure-password \
     --create-namespace \
     --namespace ridegrid
   ```

3. **Access the application:**
   ```bash
   kubectl port-forward -n ridegrid svc/ridegrid-ops-console 3000:3000
   ```

4. **Monitor with Grafana:**
   ```bash
   kubectl port-forward -n ridegrid svc/ridegrid-grafana 3001:3000
   ```

---

## 🚨 Troubleshooting by Deployment Mode

### Docker Deployment Issues

**Problem: "Cannot connect to Docker daemon"**
```bash
# Start Docker Desktop or Docker service
sudo systemctl start docker  # Linux
# or open Docker Desktop on Mac/Windows
```

**Problem: "Port already in use"**
```bash
# Find and kill process using the port
lsof -ti:3000 | xargs kill -9  # Replace 3000 with your port
```

**Problem: "Build failed"**
```bash
# Clean Docker cache and rebuild
docker system prune -a
cd deploy/docker-compose
docker-compose build --no-cache
```

### Local Development Issues

**Problem: "Module not found"**
```bash
# Reinstall dependencies
pip3 install -r backend/requirements.txt
pip3 install -e libs/ridegrid-common
```

**Problem: "Cannot connect to database"**
```bash
# Make sure infrastructure is running
cd deploy/docker-compose
docker-compose ps
docker-compose up -d postgres redis redpanda
```

**Problem: "Protobuf import errors"**
```bash
# Regenerate protobuf code
pip3 install grpcio-tools
python3 -m grpc_tools.protoc --proto_path=proto \
  --python_out=libs/ridegrid-proto/ridegrid_proto \
  --grpc_python_out=libs/ridegrid-proto/ridegrid_proto \
  proto/ridegrid.proto
```

### Frontend Issues

**Problem: "npm install fails"**
```bash
# Clear cache and reinstall
cd web/ops-console
rm -rf node_modules package-lock.json
npm cache clean --force
npm install
```

**Problem: "Build fails"**
```bash
# Check Node version (need 20+)
node --version

# Update Node if needed
nvm install 20  # if using nvm
```

---

## 📊 Comparison Table

| Feature | Docker-Only | Local Dev | Hybrid | Kubernetes |
|---------|------------|-----------|--------|------------|
| **Setup Time** | ⚡ Fast | 🕐 Medium | 🕐 Medium | 🕑 Slow |
| **Resource Usage** | 🔥 High | 💚 Low | 🔶 Medium | 🔥 Very High |
| **Best For** | Demo, Quick Start | Active Development | Debugging | Production |
| **Hot Reload** | ❌ No | ✅ Yes | ✅ Yes (for local) | ❌ No |
| **Isolation** | ✅ Full | ⚠️ Partial | ⚠️ Partial | ✅ Full |
| **Debugging** | ⚠️ Limited | ✅ Full | ✅ Full | ⚠️ Limited |
| **Scalability** | ❌ Limited | ❌ None | ❌ Limited | ✅ Full |

---

## 🎯 Recommended Approach

**For first time setup:**
1. Run `./scripts/setup.sh`
2. Let it auto-detect and configure
3. Access http://localhost:3000

**For development:**
1. Use Local Dev or Hybrid mode
2. Run only changed services locally
3. Keep infrastructure in Docker

**For production:**
1. Use Kubernetes deployment
2. Configure Argo Rollouts for canary
3. Enable KEDA autoscaling
4. Set up monitoring and alerts

---

## 📝 Quick Reference

### Docker Commands
```bash
# Build all images
make build

# Start with Docker Compose
cd deploy/docker-compose && docker-compose up -d

# View logs
docker-compose logs -f gateway

# Stop everything
docker-compose down
```

### Local Commands
```bash
# Install dependencies
make install

# Generate protobuf
make proto

# Start local services
./scripts/start-all.sh

# Stop local services
./scripts/stop-all.sh
```

### Kubernetes Commands
```bash
# Deploy
make deploy-k8s

# Check status
kubectl get pods -n ridegrid

# View logs
kubectl logs -n ridegrid -l app=gateway -f

# Delete deployment
helm uninstall ridegrid -n ridegrid
```

---

## 🆘 Still Having Issues?

1. Check [GETTING_STARTED.md](GETTING_STARTED.md) for detailed setup
2. Review [docs/troubleshooting.md](docs/troubleshooting.md) for common issues
3. Run diagnostics:
   ```bash
   # Check what's available
   docker --version
   docker-compose --version
   python3 --version
   node --version
   kubectl version --client
   ```

4. Open an issue on GitHub with:
   - Your OS and versions
   - Deployment mode you're trying
   - Full error message
   - Steps to reproduce





