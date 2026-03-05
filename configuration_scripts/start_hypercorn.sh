#!/bin/bash
# Start ValidoAI with Hypercorn (HTTP/2.0 + HTTP/3.0 support)

set -e

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '#' | sed 's/\r$//' | awk '/^[A-Z_][A-Z0-9_]*=/ {print}')
fi

# Set default values
export SERVER_TYPE=${SERVER_TYPE:-hypercorn}
export HOST=${HOST:-0.0.0.0}
export HTTP_PORT=${HTTP_PORT:-5000}
export HTTPS_PORT=${HTTPS_PORT:-5001}
export FLASK_ENV=${FLASK_ENV:-production}
export DEBUG_MODE=${DEBUG_MODE:-false}

echo "🚀 Starting ValidoAI with Hypercorn..."
echo "   Server: $SERVER_TYPE"
echo "   Host: $HOST"
echo "   HTTP Port: $HTTP_PORT"
echo "   HTTPS Port: $HTTPS_PORT"
echo "   Environment: $FLASK_ENV"

# Check if SSL is enabled
if [ "$SSL_ENABLED" = "true" ] && [ -f "certs/certificate.pem" ] && [ -f "certs/private.key" ]; then
    echo "   SSL: Enabled"
else
    echo "   SSL: Disabled (using HTTP only)"
fi

# Start the server
exec python scripts/run_production_server.py
