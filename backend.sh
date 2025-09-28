#!/bin/bash

# Email Campaign Backend Control Script
# Usage: ./backend.sh [start|stop|restart|status]

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$SCRIPT_DIR/backend"

# Function to show usage
show_usage() {
    echo -e "${BLUE}Email Campaign Backend Control${NC}"
    echo ""
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  start    - Start the backend server"
    echo "  stop     - Stop the backend server"
    echo "  restart  - Restart the backend server"
    echo "  status   - Check if backend server is running"
    echo ""
    echo "Examples:"
    echo "  $0 start"
    echo "  $0 stop"
    echo "  $0 restart"
    echo "  $0 status"
}

# Function to check if server is running
check_status() {
    PIDS=$(pgrep -f "uvicorn app.main:app" 2>/dev/null || true)
    if [ -n "$PIDS" ]; then
        echo -e "${GREEN}✅ Backend server is running (PIDs: $PIDS)${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠️  Backend server is not running${NC}"
        return 1
    fi
}

# Function to start server
start_server() {
    if check_status > /dev/null 2>&1; then
        echo -e "${YELLOW}⚠️  Backend server is already running${NC}"
        check_status
        return 0
    fi
    
    echo -e "${BLUE}🚀 Starting backend server...${NC}"
    cd "$BACKEND_DIR" && ./start.sh
}

# Function to stop server
stop_server() {
    if ! check_status > /dev/null 2>&1; then
        echo -e "${YELLOW}⚠️  Backend server is not running${NC}"
        return 0
    fi
    
    echo -e "${BLUE}🛑 Stopping backend server...${NC}"
    cd "$BACKEND_DIR" && ./stop.sh
}

# Function to restart server
restart_server() {
    echo -e "${BLUE}🔄 Restarting backend server...${NC}"
    stop_server
    sleep 2
    start_server
}

# Main script logic
case "${1:-}" in
    start)
        start_server
        ;;
    stop)
        stop_server
        ;;
    restart)
        restart_server
        ;;
    status)
        check_status
        ;;
    "")
        show_usage
        exit 1
        ;;
    *)
        echo -e "${RED}❌ Unknown command: $1${NC}"
        echo ""
        show_usage
        exit 1
        ;;
esac