#!/bin/bash

# Email Campaign Backend Startup Script
# This script starts the FastAPI backend server

set -e  # Exit on any error

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo -e "${BLUE}🚀 Starting Email Campaign Backend...${NC}"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${RED}❌ Virtual environment not found. Please run setup first:${NC}"
    echo "   python -m venv venv"
    echo "   source venv/bin/activate"
    echo "   pip install -r requirements.txt"
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  .env file not found. Copying from .env.example...${NC}"
    cp .env.example .env
    echo -e "${YELLOW}📝 Please edit .env with your credentials before running again.${NC}"
    exit 1
fi

# Check if credentials.json exists
if [ ! -f "credentials.json" ]; then
    echo -e "${YELLOW}⚠️  credentials.json not found. Please set up Google Sheets credentials:${NC}"
    echo "   1. Follow instructions in GOOGLE_SHEETS_SETUP.md"
    echo "   2. Copy your service account credentials to credentials.json"
    exit 1
fi

# Activate virtual environment
echo -e "${BLUE}📦 Activating virtual environment...${NC}"
source venv/bin/activate

# Check if required packages are installed
if ! python -c "import fastapi, uvicorn" 2>/dev/null; then
    echo -e "${RED}❌ Required packages not installed. Installing...${NC}"
    pip install -r requirements.txt
fi

# Set default values
HOST=${HOST:-0.0.0.0}
PORT=${PORT:-8000}
RELOAD=${RELOAD:-true}

echo -e "${GREEN}✅ Environment ready!${NC}"
echo -e "${BLUE}📋 Starting FastAPI server...${NC}"
echo -e "${BLUE}   Host: ${HOST}${NC}"
echo -e "${BLUE}   Port: ${PORT}${NC}"
echo -e "${BLUE}   Reload: ${RELOAD}${NC}"
echo -e "${BLUE}   Docs: http://localhost:${PORT}/docs${NC}"
echo ""

# Start the server
if [ "$RELOAD" = "true" ]; then
    uvicorn app.main:app --host "$HOST" --port "$PORT" --reload
else
    uvicorn app.main:app --host "$HOST" --port "$PORT"
fi