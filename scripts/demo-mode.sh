#!/bin/bash

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}"
echo "======================================"
echo "  RideGrid - Demo Mode"
echo "======================================"
echo -e "${NC}"
echo ""
echo -e "${YELLOW}Starting frontend with mock data...${NC}"
echo ""

cd web/ops-console

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}Installing frontend dependencies...${NC}"
    npm install
fi

echo ""
echo -e "${GREEN}Starting Next.js development server...${NC}"
echo ""
echo -e "${BLUE}The frontend will run with DEMO DATA${NC}"
echo -e "${YELLOW}Note: API calls will fail (that's OK for demo)${NC}"
echo ""
echo -e "${GREEN}Access the demo at:${NC}"
echo -e "  ${YELLOW}http://localhost:3000${NC}"
echo ""
echo -e "Press ${YELLOW}Ctrl+C${NC} to stop"
echo ""

npm run dev





