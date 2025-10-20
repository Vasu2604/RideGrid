#!/bin/bash

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}"
echo "======================================"
echo "  RideGrid - Starting All Services"
echo "======================================"
echo -e "${NC}"

# Start infrastructure
echo -e "${YELLOW}Starting infrastructure services...${NC}"
cd deploy/docker-compose
docker-compose up -d postgres redis redpanda otel-collector prometheus grafana
echo -e "${GREEN}✓ Infrastructure started${NC}"

# Wait for services
echo ""
echo -e "${YELLOW}Waiting for services to be ready...${NC}"
sleep 5

# Initialize database if needed
echo -e "${YELLOW}Initializing database...${NC}"
docker-compose exec -T postgres psql -U ridegrid -d ridegrid < init-db.sql 2>/dev/null || echo "Database already initialized"
echo -e "${GREEN}✓ Database ready${NC}"

cd ../..

# Start Python services in background
echo ""
echo -e "${YELLOW}Starting Python services...${NC}"

# Gateway
cd services/gateway
python main.py > ../../logs/gateway.log 2>&1 &
GATEWAY_PID=$!
echo -e "${GREEN}✓ Gateway started (PID: $GATEWAY_PID)${NC}"
cd ../..

# Telemetry Ingest
cd services/telemetry-ingest
python main.py > ../../logs/telemetry.log 2>&1 &
TELEMETRY_PID=$!
echo -e "${GREEN}✓ Telemetry Ingest started (PID: $TELEMETRY_PID)${NC}"
cd ../..

# Matching Engine
cd services/matching-engine
python main.py > ../../logs/matching.log 2>&1 &
MATCHING_PID=$!
echo -e "${GREEN}✓ Matching Engine started (PID: $MATCHING_PID)${NC}"
cd ../..

# Assignment Orchestrator
cd services/assignment-orchestrator
python main.py > ../../logs/assignment.log 2>&1 &
ASSIGNMENT_PID=$!
echo -e "${GREEN}✓ Assignment Orchestrator started (PID: $ASSIGNMENT_PID)${NC}"
cd ../..

# State Query
cd services/state-query
python main.py > ../../logs/state-query.log 2>&1 &
STATE_PID=$!
echo -e "${GREEN}✓ State Query started (PID: $STATE_PID)${NC}"
cd ../..

# Start frontend
echo ""
echo -e "${YELLOW}Starting frontend...${NC}"
cd web/ops-console
npm run dev > ../../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
echo -e "${GREEN}✓ Frontend started (PID: $FRONTEND_PID)${NC}"
cd ../..

# Save PIDs
mkdir -p .pids
echo $GATEWAY_PID > .pids/gateway.pid
echo $TELEMETRY_PID > .pids/telemetry.pid
echo $MATCHING_PID > .pids/matching.pid
echo $ASSIGNMENT_PID > .pids/assignment.pid
echo $STATE_PID > .pids/state.pid
echo $FRONTEND_PID > .pids/frontend.pid

echo ""
echo -e "${BLUE}======================================"
echo "  All Services Started!"
echo "======================================${NC}"
echo ""
echo -e "${GREEN}Services are available at:${NC}"
echo ""
echo -e "  Frontend:         ${YELLOW}http://localhost:3000${NC}"
echo -e "  Gateway API:      ${YELLOW}http://localhost:8001${NC}"
echo -e "  State Query API:  ${YELLOW}http://localhost:8003${NC}"
echo -e "  Grafana:          ${YELLOW}http://localhost:3001${NC} (admin/admin)"
echo -e "  Prometheus:       ${YELLOW}http://localhost:9090${NC}"
echo -e "  Kafka UI:         ${YELLOW}http://localhost:8080${NC}"
echo ""
echo -e "${GREEN}View logs:${NC}"
echo -e "  tail -f logs/gateway.log"
echo -e "  tail -f logs/frontend.log"
echo ""
echo -e "${GREEN}Stop all services:${NC}"
echo -e "  ./scripts/stop-all.sh"
echo ""





