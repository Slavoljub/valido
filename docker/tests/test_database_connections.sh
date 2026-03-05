#!/bin/bash

# TDD Test: Database Connection Validation
# This test validates that all database services can be started and connected to

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

# Function to test database connection
test_database_connection() {
    local service="$1"
    local port="$2"
    local test_command="$3"
    local expected_result="$4"
    
    if wait_for_service "$service" "$port" && eval "$test_command" >/dev/null 2>&1; then
        print_test_result "$service Connection" "PASS" "$expected_result"
    else
        print_test_result "$service Connection" "FAIL" "Expected: $expected_result"
    fi
}

echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}Database Connection TDD Tests${NC}"
echo -e "${BLUE}================================${NC}"

# Start database services
echo "Starting database services for testing..."
cd docker
docker-compose --profile databases up -d

# Wait for services to start
echo "Waiting for services to start..."
sleep 10

# Test PostgreSQL connection
test_database_connection "PostgreSQL" "5432" \
    "docker-compose exec -T postgresql pg_isready -U postgres" \
    "PostgreSQL should be accessible"

# Test MySQL connection
test_database_connection "MySQL" "3306" \
    "docker-compose exec -T mysql mysqladmin ping -h localhost -u root -proot" \
    "MySQL should be accessible"

# Test MongoDB connection
test_database_connection "MongoDB" "27017" \
    "docker-compose exec -T mongodb mongosh --eval 'db.adminCommand(\"ping\")'" \
    "MongoDB should be accessible"

# Test Redis connection
test_database_connection "Redis" "6379" \
    "docker-compose exec -T redis redis-cli -a redis123 ping" \
    "Redis should be accessible"

# Test Elasticsearch connection
test_database_connection "Elasticsearch" "9200" \
    "curl -f http://localhost:9200/_cluster/health" \
    "Elasticsearch should be accessible"

# Test Neo4j connection
test_database_connection "Neo4j" "7474" \
    "curl -f http://localhost:7474/browser/" \
    "Neo4j should be accessible"

# Test InfluxDB connection
test_database_connection "InfluxDB" "8086" \
    "curl -f http://localhost:8086/health" \
    "InfluxDB should be accessible"

# Test ClickHouse connection
test_database_connection "ClickHouse" "8123" \
    "curl -f http://localhost:8123/ping" \
    "ClickHouse should be accessible"

# Test Weaviate connection
test_database_connection "Weaviate" "8080" \
    "curl -f http://localhost:8080/v1/.well-known/ready" \
    "Weaviate should be accessible"

# Test Qdrant connection
test_database_connection "Qdrant" "6333" \
    "curl -f http://localhost:6333/health" \
    "Qdrant should be accessible"

# Test ChromaDB connection
test_database_connection "ChromaDB" "8000" \
    "curl -f http://localhost:8000/api/v1/heartbeat" \
    "ChromaDB should be accessible"

# Test database creation and basic operations
echo "Testing database operations..."

# PostgreSQL operations
if docker-compose exec -T postgresql psql -U postgres -d ai_valido_online -c "SELECT 1;" >/dev/null 2>&1; then
    print_test_result "PostgreSQL Operations" "PASS" "PostgreSQL should support basic operations"
else
    print_test_result "PostgreSQL Operations" "FAIL" "PostgreSQL basic operations failed"
fi

# MySQL operations
if docker-compose exec -T mysql mysql -u root -proot -e "SELECT 1;" >/dev/null 2>&1; then
    print_test_result "MySQL Operations" "PASS" "MySQL should support basic operations"
else
    print_test_result "MySQL Operations" "FAIL" "MySQL basic operations failed"
fi

# MongoDB operations
if docker-compose exec -T mongodb mongosh --eval "db.test.insertOne({test: 'data'})" >/dev/null 2>&1; then
    print_test_result "MongoDB Operations" "PASS" "MongoDB should support basic operations"
else
    print_test_result "MongoDB Operations" "FAIL" "MongoDB basic operations failed"
fi

# Redis operations
if docker-compose exec -T redis redis-cli -a redis123 SET test_key "test_value" >/dev/null 2>&1; then
    print_test_result "Redis Operations" "PASS" "Redis should support basic operations"
else
    print_test_result "Redis Operations" "FAIL" "Redis basic operations failed"
fi

# Test database persistence
echo "Testing database persistence..."

# Create test data
docker-compose exec -T postgresql psql -U postgres -d ai_valido_online -c "CREATE TABLE IF NOT EXISTS test_persistence (id SERIAL PRIMARY KEY, data TEXT); INSERT INTO test_persistence (data) VALUES ('persistence_test');" >/dev/null 2>&1

# Restart service
docker-compose restart postgresql
sleep 5

# Check if data persists
if docker-compose exec -T postgresql psql -U postgres -d ai_valido_online -c "SELECT COUNT(*) FROM test_persistence;" | grep -q "1"; then
    print_test_result "Database Persistence" "PASS" "Database data should persist across restarts"
else
    print_test_result "Database Persistence" "FAIL" "Database data did not persist"
fi

# Stop services
echo "Stopping database services..."
docker-compose --profile databases down

echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}Test Summary${NC}"
echo -e "${BLUE}================================${NC}"
echo "Total Tests: $TOTAL_TESTS"
echo -e "Passed: ${GREEN}$PASSED_TESTS${NC}"
echo -e "Failed: ${RED}$FAILED_TESTS${NC}"

if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "${GREEN}All database connection tests passed!${NC}"
    exit 0
else
    echo -e "${RED}Some database connection tests failed. Please check the database configurations.${NC}"
    exit 1
fi
