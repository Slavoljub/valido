#!/bin/bash

# TDD Test: Service Health Validation
# This test validates that all services are healthy and responding correctly

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test counters
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Function to print test results
print_test_result() {
    local test_name="$1"
    local result="$2"
    local message="$3"
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    if [ "$result" = "PASS" ]; then
        echo -e "${GREEN}✓ PASS${NC} $test_name: $message"
        PASSED_TESTS=$((PASSED_TESTS + 1))
    else
        echo -e "${RED}✗ FAIL${NC} $test_name: $message"
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi
}

# Function to wait for service to be ready
wait_for_service() {
    local service="$1"
    local port="$2"
    local max_attempts=30
    local attempt=1
    
    echo "Waiting for $service to be ready on port $port..."
    
    while [ $attempt -le $max_attempts ]; do
        if nc -z localhost $port 2>/dev/null; then
            echo "$service is ready!"
            return 0
        fi
        
        echo "Attempt $attempt/$max_attempts: $service not ready yet..."
        sleep 2
        attempt=$((attempt + 1))
    done
    
    echo "$service failed to start within expected time"
    return 1
}

# Function to test service health
test_service_health() {
    local service="$1"
    local port="$2"
    local health_check="$3"
    local expected_result="$4"
    
    if wait_for_service "$service" "$port" && eval "$health_check" >/dev/null 2>&1; then
        print_test_result "$service Health" "PASS" "$expected_result"
    else
        print_test_result "$service Health" "FAIL" "Expected: $expected_result"
    fi
}

echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}Service Health TDD Tests${NC}"
echo -e "${BLUE}================================${NC}"

# Start all services
echo "Starting all services for health testing..."
cd docker
docker-compose up -d

# Wait for services to start
echo "Waiting for services to start..."
sleep 15

# Test service health checks
echo "Testing service health..."

# PostgreSQL health
test_service_health "PostgreSQL" "5432" \
    "docker-compose exec -T postgresql pg_isready -U postgres" \
    "PostgreSQL should be healthy"

# MySQL health
test_service_health "MySQL" "3306" \
    "docker-compose exec -T mysql mysqladmin ping -h localhost -u root -proot" \
    "MySQL should be healthy"

# MongoDB health
test_service_health "MongoDB" "27017" \
    "docker-compose exec -T mongodb mongosh --eval 'db.adminCommand(\"ping\")'" \
    "MongoDB should be healthy"

# Redis health
test_service_health "Redis" "6379" \
    "docker-compose exec -T redis redis-cli -a redis123 ping" \
    "Redis should be healthy"

# Elasticsearch health
test_service_health "Elasticsearch" "9200" \
    "curl -f http://localhost:9200/_cluster/health" \
    "Elasticsearch should be healthy"

# Neo4j health
test_service_health "Neo4j" "7474" \
    "curl -f http://localhost:7474/browser/" \
    "Neo4j should be healthy"

# InfluxDB health
test_service_health "InfluxDB" "8086" \
    "curl -f http://localhost:8086/health" \
    "InfluxDB should be healthy"

# ClickHouse health
test_service_health "ClickHouse" "8123" \
    "curl -f http://localhost:8123/ping" \
    "ClickHouse should be healthy"

# Weaviate health
test_service_health "Weaviate" "8080" \
    "curl -f http://localhost:8080/v1/.well-known/ready" \
    "Weaviate should be healthy"

# Qdrant health
test_service_health "Qdrant" "6333" \
    "curl -f http://localhost:6333/health" \
    "Qdrant should be healthy"

# ChromaDB health
test_service_health "ChromaDB" "8000" \
    "curl -f http://localhost:8000/api/v1/heartbeat" \
    "ChromaDB should be healthy"

# Test service logs for errors
echo "Checking service logs for errors..."

# Check for error patterns in logs
services=("postgresql" "mysql" "mongodb" "redis" "elasticsearch" "neo4j" "influxdb" "clickhouse" "weaviate" "qdrant" "chromadb")

for service in "${services[@]}"; do
    if docker-compose logs "$service" 2>&1 | grep -i "error\|fatal\|exception" >/dev/null; then
        print_test_result "$service Logs" "FAIL" "$service should not have errors in logs"
    else
        print_test_result "$service Logs" "PASS" "$service should have clean logs"
    fi
done

# Test service resource usage
echo "Testing service resource usage..."

# Check if services are using reasonable resources
for service in "${services[@]}"; do
    if docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}" | grep "$service" >/dev/null; then
        print_test_result "$service Resources" "PASS" "$service should be using resources"
    else
        print_test_result "$service Resources" "FAIL" "$service should be running and using resources"
    fi
done

# Test service restart capability
echo "Testing service restart capability..."

# Test restarting a service
docker-compose restart postgresql
sleep 5

if docker-compose exec -T postgresql pg_isready -U postgres >/dev/null 2>&1; then
    print_test_result "Service Restart" "PASS" "Services should restart successfully"
else
    print_test_result "Service Restart" "FAIL" "Services should restart without issues"
fi

# Test service scaling (if supported)
echo "Testing service scaling..."

# Test scaling a service
if docker-compose up -d --scale redis=2 2>/dev/null; then
    print_test_result "Service Scaling" "PASS" "Services should support scaling"
    # Scale back down
    docker-compose up -d --scale redis=1
else
    print_test_result "Service Scaling" "FAIL" "Services should support scaling"
fi

# Test service networking
echo "Testing service networking..."

# Test inter-service communication
if docker-compose exec postgresql ping -c 1 redis >/dev/null 2>&1; then
    print_test_result "Service Networking" "PASS" "Services should communicate with each other"
else
    print_test_result "Service Networking" "FAIL" "Services should be able to communicate"
fi

# Test service configuration
echo "Testing service configuration..."

# Check if services are using correct configurations
if docker-compose exec postgresql psql -U postgres -c "SHOW shared_preload_libraries;" | grep -q "pgvector"; then
    print_test_result "Service Configuration" "PASS" "Services should use correct configurations"
else
    print_test_result "Service Configuration" "FAIL" "Services should be properly configured"
fi

# Test service security
echo "Testing service security..."

# Check if services are not exposed to external networks unnecessarily
if docker network inspect validoai_network | grep -q "172.20.0.0/16"; then
    print_test_result "Service Security" "PASS" "Services should be in isolated network"
else
    print_test_result "Service Security" "FAIL" "Services should be properly isolated"
fi

# Stop all services
echo "Stopping all services..."
docker-compose down

echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}Test Summary${NC}"
echo -e "${BLUE}================================${NC}"
echo "Total Tests: $TOTAL_TESTS"
echo -e "Passed: ${GREEN}$PASSED_TESTS${NC}"
echo -e "Failed: ${RED}$FAILED_TESTS${NC}"

if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "${GREEN}All service health tests passed!${NC}"
    exit 0
else
    echo -e "${RED}Some service health tests failed. Please check the service configurations.${NC}"
    exit 1
fi
