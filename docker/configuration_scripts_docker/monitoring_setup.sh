#!/bin/bash

# ValidoAI Monitoring Setup Script
# This script sets up Grafana and Prometheus for monitoring ValidoAI services

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}✅ $1${NC}"
}

error() {
    echo -e "${RED}❌ $1${NC}"
}

warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

log "🚀 Starting ValidoAI Monitoring Setup..."

# Step 1: Check if monitoring services are running
log "🔍 Step 1: Checking monitoring services status..."
if docker ps | grep -q "prometheus_ai_valido"; then
    success "Prometheus is running"
else
    error "Prometheus is not running"
    exit 1
fi

if docker ps | grep -q "grafana_ai_valido"; then
    success "Grafana is running"
else
    error "Grafana is not running"
    exit 1
fi

# Step 2: Wait for services to be ready
log "⏳ Step 2: Waiting for services to be ready..."
max_attempts=30
attempt=0

# Wait for Prometheus
while [ $attempt -lt $max_attempts ]; do
    if curl -s http://localhost:9090/-/ready > /dev/null 2>&1; then
        success "Prometheus is ready!"
        break
    fi
    attempt=$((attempt + 1))
    log "Waiting for Prometheus... (attempt $attempt/$max_attempts)"
    sleep 5
done

if [ $attempt -eq $max_attempts ]; then
    error "Prometheus failed to start within expected time"
    exit 1
fi

# Wait for Grafana
attempt=0
while [ $attempt -lt $max_attempts ]; do
    if curl -s http://localhost:3000/api/health > /dev/null 2>&1; then
        success "Grafana is ready!"
        break
    fi
    attempt=$((attempt + 1))
    log "Waiting for Grafana... (attempt $attempt/$max_attempts)"
    sleep 5
done

if [ $attempt -eq $max_attempts ]; then
    error "Grafana failed to start within expected time"
    exit 1
fi

# Step 3: Display access information
log "📋 Step 3: Monitoring Access Information"
echo ""
echo "🌐 Monitoring Services:"
echo "   • Prometheus: http://localhost:9090"
echo "   • Grafana: http://localhost:3000"
echo ""
echo "👤 Grafana Credentials:"
echo "   • Username: admin"
echo "   • Password: valido123!"
echo ""

# Step 4: Test Prometheus targets
log "🧪 Step 4: Testing Prometheus targets..."
if curl -s http://localhost:9090/api/v1/targets | grep -q "up"; then
    success "Prometheus targets are configured"
else
    warning "Some Prometheus targets may not be up"
fi

# Step 5: Display monitoring features
log "📊 Step 5: Monitoring Features Available"
echo ""
echo "📈 Monitoring Capabilities:"
echo "   • Docker container metrics (CPU, Memory, Network)"
echo "   • Database service monitoring"
echo "   • Jenkins CI metrics"
echo "   • Custom ValidoAI dashboards"
echo "   • Real-time alerts and notifications"
echo ""

# Step 6: Optional: Open monitoring interfaces
log "🌐 Step 6: Opening monitoring interfaces..."
if command -v xdg-open > /dev/null 2>&1; then
    # Linux
    xdg-open http://localhost:3000 > /dev/null 2>&1 &
    xdg-open http://localhost:9090 > /dev/null 2>&1 &
elif command -v open > /dev/null 2>&1; then
    # macOS
    open http://localhost:3000 > /dev/null 2>&1 &
    open http://localhost:9090 > /dev/null 2>&1 &
elif command -v start > /dev/null 2>&1; then
    # Windows
    start http://localhost:3000 > /dev/null 2>&1 &
    start http://localhost:9090 > /dev/null 2>&1 &
fi

success "ValidoAI Monitoring Setup completed!"
log "🎉 Grafana and Prometheus are ready for monitoring!"

echo ""
log "📖 Next Steps:"
echo "   1. Open Grafana at http://localhost:3000"
echo "   2. Login with admin/valido123!"
echo "   3. Explore the pre-configured ValidoAI dashboard"
echo "   4. Add additional data sources as needed"
echo "   5. Create custom dashboards for your services"
echo ""

log "🔧 Useful Commands:"
echo "   • Check Prometheus targets: curl http://localhost:9090/api/v1/targets"
echo "   • View Prometheus metrics: curl http://localhost:9090/metrics"
echo "   • Check Grafana health: curl http://localhost:3000/api/health"
echo "   • View service logs: docker-compose logs prometheus grafana"
echo ""
