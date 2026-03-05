#!/bin/bash

# ValidoAI Quick CI Start Script
# This script quickly sets up and starts Jenkins CI for local development

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

log "🚀 Starting ValidoAI Quick CI Setup..."

# Step 1: Check if Jenkins is running
log "🔍 Step 1: Checking Jenkins status..."
if docker ps | grep -q "jenkins_ai_valido"; then
    success "Jenkins is already running"
else
    log "Starting Jenkins..."
    docker-compose --profile ci up -d jenkins
    sleep 30
fi

# Step 2: Wait for Jenkins to be ready
log "⏳ Step 2: Waiting for Jenkins to be ready..."
max_attempts=30
attempt=0
while [ $attempt -lt $max_attempts ]; do
    if curl -s http://localhost:8085/login > /dev/null 2>&1; then
        success "Jenkins is ready!"
        break
    fi
    attempt=$((attempt + 1))
    log "Waiting for Jenkins... (attempt $attempt/$max_attempts)"
    sleep 10
done

if [ $attempt -eq $max_attempts ]; then
    error "Jenkins failed to start within expected time"
    exit 1
fi

# Step 3: Start core services for testing
log "🐳 Step 3: Starting core services..."
docker-compose --profile databases up -d postgresql mysql mongodb redis
sleep 30

# Step 4: Run quick health check
log "🏥 Step 4: Running quick health check..."
services=("postgresql" "mysql" "mongodb" "redis")
all_healthy=true

for service in "${services[@]}"; do
    if docker-compose ps $service | grep -q "Up"; then
        success "$service is running"
    else
        error "$service is not running"
        all_healthy=false
    fi
done

if [ "$all_healthy" = false ]; then
    warning "Some services are not healthy, but continuing with CI setup..."
fi

# Step 5: Display Jenkins access information
log "📋 Step 5: Jenkins Access Information"
echo ""
echo "🌐 Jenkins URL: http://localhost:8085"
echo "👤 Username: admin"
echo "🔑 Password: valido123!"
echo ""
echo "📊 Available CI Jobs:"
echo "   • validoai-tests - Comprehensive testing"
echo "   • validoai-database-tests - Database connectivity tests"
echo "   • validoai-performance-tests - Performance testing"
echo "   • validoai-security-tests - Security testing"
echo "   • validoai-deployment-tests - Deployment testing"
echo ""

# Step 6: Run a quick example test
log "🧪 Step 6: Running quick example test..."
if [ -f "configuration_scripts_docker/ci_test_runner.sh" ]; then
    log "Running comprehensive CI test..."
    bash configuration_scripts_docker/ci_test_runner.sh
    success "Quick test completed!"
else
    warning "CI test runner not found, skipping quick test"
fi

# Step 7: Display next steps
log "📖 Step 7: Next Steps"
echo ""
echo "🎯 To get started with CI:"
echo "   1. Open http://localhost:8085 in your browser"
echo "   2. Login with admin/valido123!"
echo "   3. Click on any job to run it manually"
echo "   4. Jobs will also run automatically based on their schedules"
echo ""
echo "🔧 Manual test commands:"
echo "   • Run comprehensive tests: bash configuration_scripts_docker/ci_test_runner.sh"
echo "   • Check service status: docker-compose ps"
echo "   • View service logs: docker-compose logs [service-name]"
echo ""

success "ValidoAI Quick CI Setup completed!"
log "🎉 Jenkins CI is ready for local development!"

# Optional: Open Jenkins in browser
if command -v xdg-open > /dev/null 2>&1; then
    # Linux
    xdg-open http://localhost:8085 > /dev/null 2>&1 &
elif command -v open > /dev/null 2>&1; then
    # macOS
    open http://localhost:8085 > /dev/null 2>&1 &
elif command -v start > /dev/null 2>&1; then
    # Windows
    start http://localhost:8085 > /dev/null 2>&1 &
fi

echo ""
log "🌐 Jenkins should open in your browser automatically"
log "📊 Monitor your CI jobs and test results!"
