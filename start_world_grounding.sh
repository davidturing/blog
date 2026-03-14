#!/bin/bash

# World Grounding & Proactive Exploration System - Startup Script
# Optimized for Mac mini M4

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Starting World Grounding & Proactive Exploration System${NC}"
echo -e "${YELLOW}Optimized for Mac mini M4 (ANE, low memory, background operation)${NC}"
echo

# Check if running on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo -e "${RED}⚠️  Warning: This system is optimized for macOS (Mac mini M4).${NC}"
    echo -e "${YELLOW}   Some features (ANE acceleration) may not be available on other platforms.${NC}"
    echo
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment
echo -e "${GREEN}Activating virtual environment...${NC}"
source venv/bin/activate

# Install dependencies if requirements.txt is newer than .installed file
if [ ! -f ".installed" ] || [ "requirements.txt" -nt ".installed" ]; then
    echo -e "${GREEN}Installing/updating dependencies...${NC}"
    pip install --upgrade pip
    pip install -r requirements.txt
    touch .installed
else
    echo -e "${GREEN}Dependencies are up to date.${NC}"
fi

# Create necessary directories
mkdir -p config data memory sensors/embedding sensors/distiller sensors/sandbox sensors/cpep

# Check Docker availability
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed or not in PATH.${NC}"
    echo -e "${YELLOW}Sandbox validation will be disabled. Please install Docker Desktop for Mac.${NC}"
    echo
else
    echo -e "${GREEN}✅ Docker is available for sandbox validation.${NC}"
fi

# Check ANE availability (Apple Neural Engine)
if [[ "$OSTYPE" == "darwin"* ]]; then
    if sysctl -n hw.optional.neon 2>/dev/null | grep -q "1"; then
        echo -e "${GREEN}✅ Apple Neural Engine (ANE) is available for acceleration.${NC}"
    else
        echo -e "${YELLOW}⚠️  ANE acceleration may not be available on this system.${NC}"
    fi
fi

echo
echo -e "${GREEN}🚀 Starting World Grounding system...${NC}"
echo -e "${YELLOW}The system will run in the background and execute during configured time windows (02:00-06:00).${NC}"
echo -e "${YELLOW}Daily reports will be generated at 08:00 in the memory/ directory.${NC}"
echo

# Start the main watcher
python3 -m sensors.external_watcher

echo -e "${GREEN}✅ World Grounding system started successfully!${NC}"
echo -e "${YELLOW}Check logs for detailed information.${NC}"