#!/bin/bash

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo "======================================"
echo "  RideGrid Setup Script"
echo "======================================"
echo -e "${NC}"

# Detect deployment mode
USE_DOCKER=false
USE_LOCAL=false

echo "Checking prerequisites..."
echo ""

# Check Docker
if command -v docker &> /dev/null && command -v docker-compose &> /dev/null; then
    echo -e "${GREEN}✓ Docker & Docker Compose found${NC}"
    USE_DOCKER=true
else
    echo -e "${YELLOW}! Docker not found - will use local setup${NC}"
fi

# Check Python
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    echo -e "${GREEN}✓ Python $PYTHON_VERSION found${NC}"
    USE_LOCAL=true
else
    echo -e "${YELLOW}! Python 3 not found${NC}"
fi

# Check Node.js
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo -e "${GREEN}✓ Node.js $NODE_VERSION found${NC}"
else
    echo -e "${YELLOW}! Node.js not found${NC}"
fi

echo ""

# Determine deployment strategy
if [ "$USE_DOCKER" = true ]; then
    echo -e "${BLUE}=== Docker Deployment Mode ===${NC}"
    echo ""
    
    # Build Docker images
    echo -e "${YELLOW}Building Docker images...${NC}"
    
    # Build all service images
    docker build -t ridegrid/gateway:latest -f services/gateway/Dockerfile services/gateway 2>/dev/null &
    docker build -t ridegrid/telemetry-ingest:latest -f services/telemetry-ingest/Dockerfile services/telemetry-ingest 2>/dev/null &
    docker build -t ridegrid/matching-engine:latest -f services/matching-engine/Dockerfile services/matching-engine 2>/dev/null &
    docker build -t ridegrid/assignment-orchestrator:latest -f services/assignment-orchestrator/Dockerfile services/assignment-orchestrator 2>/dev/null &
    docker build -t ridegrid/state-query:latest -f services/state-query/Dockerfile services/state-query 2>/dev/null &
    docker build -t ridegrid/ops-console:latest -f web/ops-console/Dockerfile web/ops-console 2>/dev/null &
    
    wait
    echo -e "${GREEN}✓ Docker images built${NC}"
    
    # Start all services via Docker Compose
    echo ""
    echo -e "${YELLOW}Starting all services with Docker Compose...${NC}"
    cd deploy/docker-compose
    docker-compose up -d
    cd ../..
    echo -e "${GREEN}✓ All services started in Docker${NC}"
    
    echo ""
    echo -e "${BLUE}======================================"
    echo "  Docker Deployment Complete!"
    echo "======================================${NC}"
    echo ""
    echo -e "${GREEN}Services available at:${NC}"
    echo ""
    echo -e "  Frontend:         ${YELLOW}http://localhost:3000${NC}"
    echo -e "  Gateway API:      ${YELLOW}http://localhost:8001${NC}"
    echo -e "  State Query API:  ${YELLOW}http://localhost:8003${NC}"
    echo -e "  Grafana:          ${YELLOW}http://localhost:3001${NC} (admin/admin)"
    echo -e "  Prometheus:       ${YELLOW}http://localhost:9090${NC}"
    echo -e "  Kafka UI:         ${YELLOW}http://localhost:8080${NC}"
    echo ""
    echo -e "${GREEN}View logs:${NC}"
    echo -e "  cd deploy/docker-compose && docker-compose logs -f"
    echo ""
    echo -e "${GREEN}Stop all services:${NC}"
    echo -e "  cd deploy/docker-compose && docker-compose down"
    echo ""

elif [ "$USE_LOCAL" = true ]; then
    echo -e "${BLUE}=== Local Development Mode ===${NC}"
    echo ""
    
    # Install Python dependencies
    if [ -f "backend/requirements.txt" ]; then
        echo -e "${YELLOW}Installing Python dependencies...${NC}"
        pip3 install -q -r backend/requirements.txt 2>/dev/null || pip3 install -r backend/requirements.txt
        pip3 install -q -e libs/ridegrid-common 2>/dev/null || pip3 install -e libs/ridegrid-common
        echo -e "${GREEN}✓ Python dependencies installed${NC}"
    fi
    
    # Install frontend dependencies
    if [ -d "web/ops-console" ] && command -v npm &> /dev/null; then
        echo -e "${YELLOW}Installing frontend dependencies...${NC}"
        cd web/ops-console && npm install --silent 2>/dev/null && cd ../..
        echo -e "${GREEN}✓ Frontend dependencies installed${NC}"
    fi
    
    # Generate protobuf code
    echo ""
    echo -e "${YELLOW}Generating protobuf code...${NC}"
    mkdir -p libs/ridegrid-proto/ridegrid_proto
    python3 -m grpc_tools.protoc --proto_path=proto \
      --python_out=libs/ridegrid-proto/ridegrid_proto \
      --grpc_python_out=libs/ridegrid-proto/ridegrid_proto \
      --pyi_out=libs/ridegrid-proto/ridegrid_proto \
      proto/ridegrid.proto 2>/dev/null || echo "Protobuf generation skipped (grpcio-tools may not be installed)"
    echo -e "${GREEN}✓ Protobuf code generated${NC}"
    
    # Start infrastructure if Docker is available
    if [ "$USE_DOCKER" = true ]; then
        echo ""
        echo -e "${YELLOW}Starting infrastructure services with Docker...${NC}"
        cd deploy/docker-compose
        docker-compose up -d postgres redis redpanda otel-collector prometheus grafana
        cd ../..
        echo -e "${GREEN}✓ Infrastructure services started${NC}"
        
        echo ""
        echo -e "${YELLOW}Waiting for services to be ready...${NC}"
        sleep 5
        
        echo -e "${YELLOW}Initializing database...${NC}"
        cd deploy/docker-compose
        docker-compose exec -T postgres psql -U ridegrid -d ridegrid < init-db.sql 2>/dev/null || echo "Database already initialized"
        cd ../..
        echo -e "${GREEN}✓ Database initialized${NC}"
    fi
    
    echo ""
    echo -e "${BLUE}======================================"
    echo "  Local Setup Complete!"
    echo "======================================${NC}"
    echo ""
    echo -e "${GREEN}Next steps:${NC}"
    echo ""
    echo "1. Start the services:"
    echo "   ${YELLOW}./scripts/start-all.sh${NC}  (starts all Python services + frontend)"
    echo ""
    echo "2. Or start services individually:"
    echo "   ${YELLOW}cd services/gateway && python3 main.py${NC}"
    echo "   ${YELLOW}cd services/matching-engine && python3 main.py${NC}"
    echo "   ${YELLOW}cd web/ops-console && npm run dev${NC}"
    echo ""
    echo "3. Access the application:"
    echo "   Frontend:    ${YELLOW}http://localhost:3000${NC}"
    echo "   Gateway API: ${YELLOW}http://localhost:8001${NC}"
    echo "   Grafana:     ${YELLOW}http://localhost:3001${NC} (admin/admin)"
    echo ""
    echo "4. Stop services:"
    echo "   ${YELLOW}./scripts/stop-all.sh${NC}"
    echo ""
    
else
    echo -e "${RED}======================================"
    echo "  Setup Failed"
    echo "======================================${NC}"
    echo ""
    echo -e "${RED}Neither Docker nor local dependencies found!${NC}"
    echo ""
    echo "Please install one of the following:"
    echo ""
    echo "Option 1 - Docker (Recommended):"
    echo "  • Docker Desktop: https://www.docker.com/products/docker-desktop"
    echo "  • Docker Compose: https://docs.docker.com/compose/install/"
    echo ""
    echo "Option 2 - Local Development:"
    echo "  • Python 3.11+: https://www.python.org/downloads/"
    echo "  • Node.js 20+: https://nodejs.org/"
    echo "  • PostgreSQL 15: https://www.postgresql.org/download/"
    echo "  • Redis 7: https://redis.io/download/"
    echo ""
    exit 1
fi

