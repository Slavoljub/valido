#!/bin/bash

# TDD Test: Docker Environment Validation
# This test validates that the Docker environment is properly configured

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

# Function to run a test
run_test() {
    local test_name="$1"
    local test_command="$2"
    local expected_result="$3"
    
    if eval "$test_command" >/dev/null 2>&1; then
        print_test_result "$test_name" "PASS" "$expected_result"
    else
        print_test_result "$test_name" "FAIL" "Expected: $expected_result"
    fi
}

echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}Docker Environment TDD Tests${NC}"
echo -e "${BLUE}================================${NC}"

# Test 1: Docker is installed and accessible
run_test "Docker Installation" "docker --version" "Docker should be installed and accessible"

# Test 2: Docker daemon is running
run_test "Docker Daemon" "docker info" "Docker daemon should be running"

# Test 3: Docker Compose is available
run_test "Docker Compose" "docker-compose --version" "Docker Compose should be available"

# Test 4: Docker network exists
run_test "Docker Network" "docker network ls | grep validoai_network" "ValidoAI network should exist"

# Test 5: Required directories exist
run_test "Project Directories" "[ -d 'docker' ] && [ -d 'data' ] && [ -d 'configuration_scripts' ]" "Required project directories should exist"

# Test 6: Docker Compose file exists
run_test "Docker Compose File" "[ -f 'docker/docker-compose.yml' ]" "Docker Compose file should exist"

# Test 7: Dockerfile exists
run_test "Dockerfile" "[ -f 'docker/Dockerfile' ]" "Dockerfile should exist"

# Test 8: Nginx configuration exists
run_test "Nginx Config" "[ -f 'docker/nginx.conf' ]" "Nginx configuration should exist"

# Test 9: Database directories exist
run_test "Database Directories" "[ -d 'docker/database' ]" "Database directories should exist"

# Test 10: Test directory exists
run_test "Test Directory" "[ -d 'docker/tests' ]" "Test directory should exist"

# Test 11: Docker can pull images
run_test "Docker Image Pull" "docker pull hello-world:latest" "Docker should be able to pull images"

# Test 12: Docker can run containers
run_test "Docker Container Run" "docker run --rm hello-world:latest" "Docker should be able to run containers"

# Test 13: Docker Compose can parse configuration
run_test "Docker Compose Config" "cd docker && docker-compose config" "Docker Compose should parse configuration correctly"

# Test 14: Environment variables are set
run_test "Environment Variables" "[ -n \"\$DOCKER_COMPOSE_DIR\" ] && [ -n \"\$PROJECT_ROOT\" ]" "Environment variables should be set"

# Test 15: Cross-platform compatibility
run_test "Cross-Platform Support" "uname -s" "Should detect operating system"

echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}Test Summary${NC}"
echo -e "${BLUE}================================${NC}"
echo "Total Tests: $TOTAL_TESTS"
echo -e "Passed: ${GREEN}$PASSED_TESTS${NC}"
echo -e "Failed: ${RED}$FAILED_TESTS${NC}"

if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "${GREEN}All tests passed! Docker environment is properly configured.${NC}"
    exit 0
else
    echo -e "${RED}Some tests failed. Please check the Docker environment configuration.${NC}"
    exit 1
fi
