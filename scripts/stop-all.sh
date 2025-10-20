#!/bin/bash

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}Stopping all RideGrid services...${NC}"
echo ""

# Stop Python services
if [ -d ".pids" ]; then
    for pidfile in .pids/*.pid; do
        if [ -f "$pidfile" ]; then
            PID=$(cat "$pidfile")
            SERVICE=$(basename "$pidfile" .pid)
            if kill -0 "$PID" 2>/dev/null; then
                kill "$PID"
                echo -e "${GREEN}✓ Stopped $SERVICE (PID: $PID)${NC}"
            fi
            rm "$pidfile"
        fi
    done
    rmdir .pids 2>/dev/null
fi

# Stop infrastructure
echo ""
echo -e "${YELLOW}Stopping infrastructure services...${NC}"
cd deploy/docker-compose
docker-compose down
echo -e "${GREEN}✓ Infrastructure stopped${NC}"
cd ../..

echo ""
echo -e "${GREEN}All services stopped${NC}"





