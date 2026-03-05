#!/bin/bash
# Start ValidoAI with Uvicorn (High-performance ASGI server)

set -e

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '#' | sed 's/\r$//' | awk '/^[A-Z_][A-Z0-9_]*=/ {print}')
fi

# Set default values
export SERVER_TYPE=${SERVER_TYPE:-uvicorn}
export HOST=${HOST:-0.0.0.0}
export PORT=${PORT:-5000}
export WORKERS=${WORKERS:-4}
export FLASK_ENV=${FLASK_ENV:-production}
export DEBUG_MODE=${DEBUG_MODE:-false}

echo "🚀 Starting ValidoAI with Uvicorn..."
echo "   Server: $SERVER_TYPE"
echo "   Host: $HOST"
echo "   Port: $PORT"
echo "   Workers: $WORKERS"
echo "   Environment: $FLASK_ENV"

# Start the server
exec python scripts/run_production_server.py
