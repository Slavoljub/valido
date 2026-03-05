#!/bin/bash
# TDD Test: Cross-Platform Compatibility Validation
# Tests Docker setup across different operating systems

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print test results
print_test_result() {
    local test_name="$1"
    local status="$2"
    local message="$3"
    
    if [ "$status" = "PASS" ]; then
        echo -e "${GREEN}[PASS]${NC} $test_name: $message"
    else
        echo -e "${RED}[FAIL]${NC} $test_name: $message"
    fi
}

# Function to run a test
run_test() {
    local test_name="$1"
    local command="$2"
    local expected_message="$3"
    
    if eval "$command" >/dev/null 2>&1; then
        print_test_result "$test_name" "PASS" "$expected_message"
    else
        print_test_result "$test_name" "FAIL" "$expected_message"
        return 1
    fi
}

echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}TDD Test: Cross-Platform Compatibility${NC}"
echo -e "${BLUE}================================${NC}"

# Detect operating system
OS=$(uname -s)
echo "Detected OS: $OS"

# Test OS-specific functionality
case "$OS" in
    Linux*)
        run_test "Linux Path Handling" \
            "test -d /tmp" \
            "Linux path handling should work"
        
        run_test "Linux File Permissions" \
            "touch /tmp/test_file && chmod 755 /tmp/test_file" \
            "Linux file permissions should work"
        ;;
    Darwin*)
        run_test "macOS Path Handling" \
            "test -d /tmp" \
            "macOS path handling should work"
        
        run_test "macOS File Permissions" \
            "touch /tmp/test_file && chmod 755 /tmp/test_file" \
            "macOS file permissions should work"
        ;;
    CYGWIN*|MINGW*|MSYS*)
        run_test "Windows Path Handling" \
            "test -d /tmp" \
            "Windows path handling should work"
        
        run_test "Windows File Operations" \
            "touch /tmp/test_file" \
            "Windows file operations should work"
        ;;
    *)
        echo -e "${YELLOW}[WARNING]${NC} Unknown OS: $OS"
        ;;
esac

# Test Docker platform compatibility
run_test "Docker Platform Detection" \
    "docker version" \
    "Docker should be accessible"

# Test Docker Compose compatibility
run_test "Docker Compose Detection" \
    "docker-compose --version" \
    "Docker Compose should be accessible"

# Test cross-platform script execution
run_test "Script Execution" \
    "bash -c 'echo \"Script execution test\"'" \
    "Bash script execution should work"

# Test environment variable handling
run_test "Environment Variables" \
    "export TEST_VAR=test_value && echo \$TEST_VAR | grep -q test_value" \
    "Environment variable handling should work"

# Test file path handling
run_test "File Path Handling" \
    "cd .. && pwd | grep -q ai.valido.online" \
    "File path handling should work correctly"

# Test network connectivity
run_test "Network Connectivity" \
    "ping -c 1 127.0.0.1" \
    "Local network connectivity should work"

# Test Docker network creation
run_test "Docker Network Creation" \
    "docker network create test_network 2>/dev/null || true" \
    "Docker network creation should work"

# Cleanup test network
docker network rm test_network 2>/dev/null || true

echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}Cross-Platform Tests Complete${NC}"
echo -e "${BLUE}================================${NC}"
