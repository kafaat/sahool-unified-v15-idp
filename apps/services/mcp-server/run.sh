#!/bin/bash
# SAHOOL MCP Server Startup Script

set -e

# Configuration
PORT=${MCP_SERVER_PORT:-8200}
HOST=${MCP_SERVER_HOST:-0.0.0.0}
LOG_LEVEL=${LOG_LEVEL:-INFO}
SAHOOL_API_URL=${SAHOOL_API_URL:-http://localhost:8000}

echo "======================================"
echo "SAHOOL MCP Server"
echo "======================================"
echo "Port: $PORT"
echo "Host: $HOST"
echo "Log Level: $LOG_LEVEL"
echo "SAHOOL API: $SAHOOL_API_URL"
echo "======================================"

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Install dependencies if needed
if [ ! -f ".deps_installed" ]; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
    touch .deps_installed
fi

# Run server
echo "Starting MCP server..."
cd src
python -m uvicorn main:app --host "$HOST" --port "$PORT" --log-level "$LOG_LEVEL"
