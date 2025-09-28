#!/bin/bash

# Email Campaign Backend Stop Script
# This script stops the FastAPI backend server

set -e  # Exit on any error

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}🛑 Stopping Email Campaign Backend...${NC}"

# Find and kill uvicorn processes
PIDS=$(pgrep -f "uvicorn app.main:app" 2>/dev/null || true)

if [ -z "$PIDS" ]; then
    echo -e "${YELLOW}⚠️  No backend server processes found running.${NC}"
    exit 0
fi

echo -e "${BLUE}📋 Found running processes: $PIDS${NC}"

# Kill the processes gracefully first
for PID in $PIDS; do
    echo -e "${BLUE}🔄 Stopping process $PID...${NC}"
    kill "$PID" 2>/dev/null || true
done

# Wait a moment for graceful shutdown
sleep 2

# Check if any processes are still running and force kill if necessary
REMAINING_PIDS=$(pgrep -f "uvicorn app.main:app" 2>/dev/null || true)

if [ -n "$REMAINING_PIDS" ]; then
    echo -e "${YELLOW}⚠️  Some processes still running, force killing...${NC}"
    for PID in $REMAINING_PIDS; do
        echo -e "${BLUE}💀 Force killing process $PID...${NC}"
        kill -9 "$PID" 2>/dev/null || true
    done
fi

# Final check
sleep 1
FINAL_CHECK=$(pgrep -f "uvicorn app.main:app" 2>/dev/null || true)

if [ -z "$FINAL_CHECK" ]; then
    echo -e "${GREEN}✅ Backend server stopped successfully!${NC}"
else
    echo -e "${RED}❌ Some processes may still be running. You may need to stop them manually.${NC}"
    exit 1
fi