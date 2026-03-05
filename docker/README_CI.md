# ValidoAI Jenkins CI/CD Documentation

## 🚀 Overview

This document provides comprehensive information about the Jenkins CI/CD setup for the ValidoAI project. The CI system is designed to run automated tests, validate Docker services, and ensure code quality.

## 📋 Table of Contents

1. [Jenkins Setup](#jenkins-setup)
2. [CI/CD Pipeline](#cicd-pipeline)
3. [Test Runner Scripts](#test-runner-scripts)
4. [Database Testing](#database-testing)
5. [Troubleshooting](#troubleshooting)
6. [Usage Examples](#usage-examples)

## 🔧 Jenkins Setup

### Container Information
- **Image**: `jenkins/jenkins:latest` (Latest stable version)
- **Container Name**: `jenkins_ai_valido`
- **Ports**: 
  - `8085:8080` (Web UI)
  - `50000:50000` (Agent communication)
- **Credentials**: 
  - Username: `admin`
  - Password: `valido123!`

### Access Jenkins
```bash
# Web Interface
http://localhost:8085

# Login with:
# Username: admin
# Password: valido123!
```

### Jenkins Configuration
- **Pre-configured admin user** (no setup wizard needed)
- **Docker socket access** for container management
- **Workspace mounted** from project root
- **Automatic job creation** for ValidoAI testing

## 🔄 CI/CD Pipeline

### Automated Jobs

#### 1. ValidoAI Tests Job
- **Name**: `validoai-tests`
- **Description**: Comprehensive CI/CD Pipeline for ValidoAI
- **Triggers**: 
  - SCM polling every 5 minutes
  - Scheduled every 6 hours
- **Build Steps**:
  1. Environment validation
  2. Docker Compose validation
  3. Core service startup (PostgreSQL, MySQL, MongoDB, Redis)
  4. Health checks
  5. Database connection tests
  6. Application tests (if available)
  7. Performance metrics collection

### Pipeline Steps

#### Step 1: Environment Validation
```bash
# Validates Docker and Docker Compose availability
docker --version
docker-compose --version
```

#### Step 2: Docker Compose Validation
```bash
# Validates docker-compose.yml configuration
docker-compose config --quiet
```

#### Step 3: Core Service Startup
```bash
# Starts core database services
docker-compose --profile databases up -d postgresql mysql mongodb redis
```

#### Step 4: Health Checks
```bash
# Checks if all services are running properly
docker-compose ps postgresql mysql mongodb redis
```

#### Step 5: Database Connection Tests
```bash
# Tests database connectivity
docker-compose exec -T postgresql pg_isready -U valido
docker-compose exec -T mysql mysqladmin ping -h localhost
docker-compose exec -T mongodb mongosh --eval "db.adminCommand('ping')"
docker-compose exec -T redis redis-cli ping
```

#### Step 6: Application Tests
```bash
# Runs application test suite if available
if [ -f "tests/run_tests.sh" ]; then
    chmod +x tests/run_tests.sh
    ./tests/run_tests.sh
fi
```

#### Step 7: Performance Metrics
```bash
# Collects performance metrics
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}"
```

## 🧪 Test Runner Scripts

### 1. CI Test Runner (`ci_test_runner.sh`)

A comprehensive test runner that performs:

- **Environment validation**
- **Docker Compose validation**
- **Service health checks**
- **Database functionality tests**
- **Network connectivity tests**
- **Performance metrics collection**
- **Test report generation**

#### Usage
```bash
# Make executable
chmod +x configuration_scripts_docker/ci_test_runner.sh

# Run tests
./configuration_scripts_docker/ci_test_runner.sh
```

#### Features
- **Colored output** for better readability
- **Detailed logging** with timestamps
- **Comprehensive error handling**
- **Test report generation**
- **Performance metrics collection**

### 2. Jenkins Setup Script (`jenkins_setup.sh`)

Configures Jenkins with:

- **Admin user creation**
- **Job configuration**
- **Test runner scripts**
- **Docker integration**

## 🗄️ Database Testing

### Supported Databases

#### 1. PostgreSQL 17
- **Port**: 5432
- **Credentials**: valido/valido123!
- **Database**: ai_valido_online
- **Extensions**: pg_stat_statements, pg_buffercache, pg_trgm

#### 2. MySQL 8.4
- **Port**: 3306
- **Credentials**: valido/valido123!
- **Database**: ai_valido_online

#### 3. MongoDB 8.0
- **Port**: 27017
- **Credentials**: valido/valido123!
- **Database**: ai_valido_online

#### 4. Redis Stack
- **Port**: 6379
- **Features**: JSON, Search, Time Series, Bloom, Graph, ML modules
- **RedisInsight**: Port 8001

### Database Tests

#### Connection Tests
```bash
# PostgreSQL
docker-compose exec -T postgresql pg_isready -U valido

# MySQL
docker-compose exec -T mysql mysqladmin ping -h localhost

# MongoDB
docker-compose exec -T mongodb mongosh --eval "db.adminCommand('ping')"

# Redis
docker-compose exec -T redis redis-cli ping
```

#### Functionality Tests
```bash
# PostgreSQL
docker-compose exec -T postgresql psql -U valido -d ai_valido_online -c "SELECT version();"

# MySQL
docker-compose exec -T mysql mysql -u valido -pvalido123! -e "SELECT VERSION();"

# MongoDB
docker-compose exec -T mongodb mongosh --eval "db.runCommand({ping: 1})"

# Redis
docker-compose exec -T redis redis-cli set test_key "test_value"
docker-compose exec -T redis redis-cli get test_key
```

## 🔧 Troubleshooting

### Common Issues

#### 1. PostgreSQL Extension Errors
**Problem**: `FATAL: could not access file "pgvector": No such file or directory`

**Solution**: Use only basic extensions available in Alpine image:
```yaml
command: >
  postgres
  -c 'shared_preload_libraries=pg_stat_statements,pg_buffercache,pg_trgm'
```

#### 2. Network Issues
**Problem**: `failed to set up container networking`

**Solution**: Clean up networks and containers:
```bash
docker-compose down --remove-orphans
docker network prune -f
docker rm -f $(docker ps -aq)
```

#### 3. Volume Permission Issues
**Problem**: Permission denied on database volumes

**Solution**: Create directories with proper permissions:
```bash
mkdir -p database/postgresql database/mysql database/mongodb database/redis
```

#### 4. Jenkins Startup Issues
**Problem**: Jenkins container fails to start

**Solution**: Check logs and restart:
```bash
docker-compose logs jenkins
docker-compose restart jenkins
```

### Health Check Commands

#### Check Service Status
```bash
# All services
docker-compose ps

# Specific service
docker-compose ps postgresql

# Service logs
docker-compose logs postgresql --tail 20
```

#### Check Network Connectivity
```bash
# List networks
docker network ls

# Inspect network
docker network inspect py_ai_valido_validoai_network
```

#### Check Volume Mounts
```bash
# List volumes
docker volume ls

# Inspect volume
docker volume inspect py_ai_valido_postgresql_data
```

## 📖 Usage Examples

### 1. Start Jenkins CI
```bash
# Start Jenkins with CI profile
docker-compose --profile ci up -d jenkins

# Access Jenkins
open http://localhost:8085
```

### 2. Run Manual Tests
```bash
# Run comprehensive CI tests
./configuration_scripts_docker/ci_test_runner.sh

# Run specific database tests
docker-compose exec -T postgresql pg_isready -U valido
```

### 3. Monitor Services
```bash
# Check all running services
docker ps --format "table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}"

# Monitor resource usage
docker stats --no-stream
```

### 4. View Test Reports
```bash
# Check test report
cat test_report.txt

# View Jenkins build logs
# Access via Jenkins web interface
```

## 🔄 Continuous Integration Workflow

### 1. Automated Testing
- **Trigger**: Code changes or scheduled runs
- **Duration**: ~2-3 minutes
- **Scope**: Core services and database connectivity

### 2. Test Results
- **Success**: All services healthy, databases connected
- **Failure**: Detailed error logs and service status
- **Reports**: Generated test reports with metrics

### 3. Notifications
- **Email alerts** on test failures
- **Jenkins dashboard** for real-time monitoring
- **Build history** for trend analysis

## 📊 Performance Metrics

### Resource Monitoring
- **CPU Usage**: Per container metrics
- **Memory Usage**: Real-time memory consumption
- **Network I/O**: Container network statistics
- **Disk I/O**: Volume and storage metrics

### Health Indicators
- **Service Status**: Running/Stopped/Healthy
- **Response Time**: Database connection latency
- **Error Rates**: Failed connection attempts
- **Uptime**: Service availability metrics

## 🛠️ Maintenance

### Regular Tasks
1. **Update Jenkins plugins** (monthly)
2. **Clean up old builds** (weekly)
3. **Monitor disk space** (daily)
4. **Review test reports** (after each build)

### Backup Procedures
```bash
# Backup Jenkins configuration
docker cp jenkins_ai_valido:/var/jenkins_home jenkins_backup

# Backup test reports
cp test_report.txt test_reports/$(date +%Y%m%d_%H%M%S)_report.txt
```

## 📞 Support

### Getting Help
1. **Check logs**: `docker-compose logs [service-name]`
2. **Review documentation**: This README file
3. **Run diagnostics**: `./configuration_scripts_docker/ci_test_runner.sh`
4. **Contact support**: Create issue in project repository

### Useful Commands
```bash
# Quick health check
docker-compose ps

# Service logs
docker-compose logs [service-name] --tail 50

# Restart service
docker-compose restart [service-name]

# Full reset
docker-compose down --remove-orphans && docker-compose up -d
```

---

**Last Updated**: August 28, 2025  
**Version**: 1.0  
**Maintainer**: ValidoAI Development Team
