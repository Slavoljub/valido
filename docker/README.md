# ValidoAI Docker Setup

## Overview

This Docker setup provides a comprehensive development environment for ValidoAI with support for multiple database types, management interfaces, CI/CD automation, and cross-platform compatibility. The setup includes advanced Redis features, unified credentials, Jenkins CI with automated testing, and the latest database versions.

## 🚀 **Current Status: All Services Operational** ✅

### **Running Services**
- ✅ **Jenkins CI** - Automated testing and CI/CD pipeline
- ✅ **PostgreSQL 17** - Advanced SQL database with extensions
- ✅ **MySQL 8.4** - Latest stable MySQL version
- ✅ **MongoDB 8.0** - NoSQL document database
- ✅ **Redis Stack** - Advanced Redis with JSON, Search, Time Series, Graph, ML modules

### **CI/CD Features**
- ✅ **5 Automated CI Jobs** - Comprehensive testing pipeline
- ✅ **Password-Free Local Development** - Pre-configured Jenkins
- ✅ **Real-time Monitoring** - Service health and performance tracking
- ✅ **Automated Testing** - Database connectivity and functionality tests

### **Monitoring Features**
- ✅ **Grafana & Prometheus** - Advanced monitoring and visualization
- ✅ **Password-Free Access** - Pre-configured admin credentials
- ✅ **Custom Dashboards** - ValidoAI-specific monitoring panels
- ✅ **Real-time Metrics** - CPU, Memory, Network, and Database monitoring

## 🏗️ Architecture

### Single Shared Volume Design
- **One shared volume** (`shared_data`) for all databases
- **Easy backup/restore** - single directory contains all database data
- **Simplified management** - no need to manage multiple volume mounts
- **Cross-platform compatibility** - works on Linux, macOS, and Windows

### Service Categories
- **Application Services**: Main ValidoAI application (`py_ai_valido_dev`)
- **Database Services**: SQL, NoSQL, Time-series, Graph, Vector, and Cloud databases
- **Management Services**: Admin interfaces for database management
- **Proxy Services**: Nginx reverse proxy

## 🚀 Quick Start

### Prerequisites
- Docker Desktop (Windows/macOS) or Docker Engine (Linux)
- Docker Compose
- Git Bash, WSL, or PowerShell (Windows)
- Minimum 8GB RAM, 4 CPU cores (16GB+ recommended)

### Initial Setup
```bash
# Navigate to project root
cd /path/to/ai.valido.online

# Initialize Docker environment
./docker/docker-run init

# Start application with database
./docker/docker-run up app
./docker/docker-run up databases
```

## 📁 Directory Structure

```
docker/
├── docker-compose.yml          # Main Docker Compose configuration
├── Dockerfile                  # Application Dockerfile
├── nginx.conf                  # Nginx configuration
├── docker-run                  # Unified management script
├── README.md                   # This file
├── database/                   # Shared database storage
├── tests/                      # TDD test suite
│   ├── test_docker_environment.sh
│   ├── test_database_connections.sh
│   ├── test_service_health.sh
│   ├── test_backup_restore.sh
│   └── test_cross_platform.sh
└── configuration_scripts_docker/  # Database initialization scripts
    ├── postgres_extensions_install.sh
    ├── postgres_performance_optimize.sh
    ├── mysql_optimize.sh
    ├── mongodb_init.js
    └── redis.conf
```

## 🛠️ Management Commands

### Unified Docker Management Script
```bash
# Start services with profiles
./docker/docker-run up app          # Start application
./docker/docker-run up databases    # Start all databases
./docker/docker-run up management   # Start management interfaces
./docker/docker-run up nginx        # Start reverse proxy

# Service management
./docker/docker-run down            # Stop all services
./docker/docker-run restart         # Restart all services
./docker/docker-run logs [service]  # View logs
./docker/docker-run ps              # Show service status

# Testing
./docker/docker-run test            # Run all tests
./docker/docker-run tdd             # Run TDD test suite

# Backup and restore
./docker/docker-run backup          # Create database backup
./docker/docker-run restore <path>  # Restore from backup

# Maintenance
./docker/docker-run clean           # Clean up Docker resources
./docker/docker-run init            # Initialize environment
```

## 🗄️ Database Services

### SQL Databases
- **PostgreSQL 17** (Port: 5432)
  - Extensions: pgvector, PostGIS, TimescaleDB, pg_stat_statements, pg_buffercache, pg_similarity, pg_trgm, pg_cron, pg_stat_monitor, pg_repack, pg_partman, pg_qualstats, pg_stat_kcache, pg_wait_sampling, auto_explain, pg_hint_plan, pg_visibility, pg_freespacemap, pg_prewarm
  - Performance optimized configuration
  - Container: `postgresql_ai_valido`
- **MySQL 8.4** (Port: 3306)
  - Optimized for AI workloads
  - Container: `mysql_ai_valido`
- **MSSQL 2022** (Port: 1433)
  - Developer edition
  - Container: `mssql_ai_valido`

### NoSQL Databases
- **MongoDB 8.1** (Port: 27017)
  - Container: `mongodb_ai_valido`
- **Redis Stack** (Port: 6379, 8001)
  - **Advanced Features**:
    - **RedisJSON**: JSON data type support
    - **RedisSearch**: Full-text search capabilities
    - **RedisTimeSeries**: Time-series data support
    - **RedisBloom**: Bloom filters and probabilistic data structures
    - **RedisGraph**: Graph database functionality
    - **RedisML**: Machine learning model serving
  - **RedisInsight**: GUI management interface on port 8001
  - Container: `redis_ai_valido`
- **Cassandra 5.1** (Port: 9042, 7000, 7001, 9160)
  - Container: `cassandra_ai_valido`
- **CouchDB 3.4** (Port: 5984)
  - Container: `couchdb_ai_valido`
- **Couchbase 7.7** (Port: 8091-8096, 11210)
  - Container: `couchbase_ai_valido`

### Time-Series Databases
- **InfluxDB 2.8** (Port: 8086)
  - Container: `influxdb_ai_valido`
- **ClickHouse 24.8** (Port: 8123, 9000)
  - Container: `clickhouse_ai_valido`

### Graph Databases
- **Neo4j 5.18** (Port: 7474, 7687)
  - Plugins: APOC, Graph Data Science, Neo4j Streams, n10s, apoc-extended
  - Container: `neo4j_ai_valido`
- **ArangoDB 3.13** (Port: 8529)
  - Container: `arangodb_ai_valido`
- **OrientDB 3.3** (Port: 2424, 2480)
  - Container: `orientdb_ai_valido`

### Search Engines
- **Elasticsearch 8.12.0** (Port: 9200, 9300)
  - Container: `validoai_elasticsearch`

### Vector Databases
- **Weaviate 1.24.0** (Port: 8080)
  - Multiple vectorizer modules enabled
  - Container: `validoai_weaviate`
- **Qdrant** (Port: 6333, 6334)
  - Container: `validoai_qdrant`
- **ChromaDB** (Port: 8000)
  - Container: `validoai_chromadb`
- **Milvus v2.4.0** (Port: 19530, 9091)
  - Container: `validoai_milvus`

### Cloud Database Emulators
- **DynamoDB Local** (Port: 8000)
  - Container: `validoai_dynamodb`
- **CosmosDB Emulator** (Port: 8081)
  - Container: `validoai_cosmosdb`
- **Firestore Emulator** (Port: 8080)
  - Container: `validoai_firestore`

## 🖥️ Management Interfaces

- **Jenkins CI** (Port: 8085) - Automated testing and CI/CD pipeline
- **Grafana** (Port: 3000) - Advanced monitoring and visualization (admin/valido123!)
- **Prometheus** (Port: 9090) - Metrics collection and alerting
- **RedisInsight** (Port: 8001) - Redis GUI with advanced features
- **pgAdmin** (Port: 5050) - PostgreSQL management
- **phpMyAdmin** (Port: 8081) - MySQL management
- **Mongo Express** (Port: 8082) - MongoDB management
- **Redis Commander** (Port: 8083) - Redis management
- **ElasticVue** (Port: 8084) - Elasticsearch management
- **Adminer** (Port: 8080) - Universal database admin

## 🔄 CI/CD Pipeline

### **Jenkins CI Configuration**
- **URL**: http://localhost:8085
- **Credentials**: admin/valido123!
- **Features**: Pre-configured admin user, no setup wizard required

### **Automated CI Jobs**

#### 1. **validoai-tests** (Main Comprehensive Tests)
- **Schedule**: Every 5 minutes + Every 6 hours
- **Purpose**: Full system testing including all services
- **Tests**: Environment validation, Docker Compose validation, service startup, health checks, database connections, application tests, performance metrics

#### 2. **validoai-database-tests** (Database Focused)
- **Schedule**: Every 10 minutes
- **Purpose**: Database connectivity and functionality
- **Tests**: PostgreSQL, MySQL, MongoDB, Redis connectivity and operations

#### 3. **validoai-performance-tests** (Performance Testing)
- **Schedule**: Every 2 hours
- **Purpose**: Performance and load testing
- **Tests**: Baseline metrics, database performance, memory/CPU monitoring, response times

#### 4. **validoai-security-tests** (Security Testing)
- **Schedule**: Daily at midnight
- **Purpose**: Security and vulnerability assessment
- **Tests**: Port security, container security, password verification, network isolation

#### 5. **validoai-deployment-tests** (Deployment Testing)
- **Schedule**: Every 4 hours
- **Purpose**: Infrastructure and deployment validation
- **Tests**: Docker Compose validation, service deployment, volume mounts, network connectivity

### **CI Management Commands**
```bash
# Quick CI setup
bash configuration_scripts_docker/quick_ci_start.sh

# Run comprehensive tests
bash configuration_scripts_docker/ci_test_runner.sh

# Access Jenkins
# URL: http://localhost:8085
# Username: admin
# Password: valido123!
```

### **CI Documentation**
- **CI Setup Guide**: `CI_SETUP_GUIDE.md` - Quick start and usage guide
- **CI Documentation**: `README_CI.md` - Detailed technical documentation
- **Service Status**: `SERVICE_STATUS_REPORT.md` - Current service status and health

## 📊 Monitoring & Observability

### **Grafana & Prometheus Setup**
- **Grafana**: http://localhost:3000 (admin/valido123!)
- **Prometheus**: http://localhost:9090
- **Features**: Real-time monitoring, custom dashboards, alerting

### **Monitoring Commands**
```bash
# Start monitoring services
docker-compose --profile monitoring up -d

# Run monitoring setup
bash configuration_scripts_docker/monitoring_setup.sh

# Check monitoring status
docker-compose ps prometheus grafana

# View monitoring logs
docker-compose logs prometheus grafana
```

### **Available Metrics**
- **Docker Containers**: CPU, Memory, Network I/O
- **Database Services**: Connection status, query performance
- **Jenkins CI**: Build status, job execution metrics
- **System Resources**: Host machine performance
- **Custom Metrics**: ValidoAI-specific application metrics

## 🔧 Configuration

### Unified Credentials
**All databases use the same credentials for easy management:**

- **Username**: `valido`
- **Password**: `valido123!`
- **No password required** for Redis (local development)

### Environment Variables
```bash
# PostgreSQL
POSTGRES_DB=ai_valido_online
POSTGRES_USER=valido
POSTGRES_PASSWORD=valido123!

# MySQL
MYSQL_ROOT_PASSWORD=valido123!
MYSQL_DATABASE=ai_valido_online
MYSQL_USER=valido
MYSQL_PASSWORD=valido123!

# MongoDB
MONGO_INITDB_ROOT_USERNAME=valido
MONGO_INITDB_ROOT_PASSWORD=valido123!

# Redis
# No password required for local development
```

### Database Connection URLs
```bash
# PostgreSQL
postgresql://valido:valido123!@localhost:5432/ai_valido_online

# MySQL
mysql://valido:valido123!@localhost:3306/ai_valido_online

# MongoDB
mongodb://valido:valido123!@localhost:27017/ai_valido_online

# Redis
redis://localhost:6379
```

## 🚀 Redis Advanced Features

### JSON Support
```bash
# Store and query JSON data
JSON.SET user:1 . '{"name":"John","age":30,"city":"New York"}'
JSON.GET user:1 .name
JSON.ARRAPPEND user:1 .hobbies '"reading"'
```

### Search Capabilities
```bash
# Create search indexes
FT.CREATE idx:users ON JSON PREFIX 1 user: SCHEMA $.name AS name TEXT $.age AS age NUMERIC
FT.SEARCH idx:users "@name:John"
```

### Time Series Data
```bash
# Store time-series data
TS.CREATE sensor:temp RETENTION 86400000
TS.ADD sensor:temp 1640995200000 23.5
TS.RANGE sensor:temp 1640995200000 1641081600000
```

### Bloom Filters
```bash
# Create bloom filters for efficient membership testing
BF.RESERVE users:emails 0.01 1000
BF.ADD users:emails "user@example.com"
BF.EXISTS users:emails "user@example.com"
```

### Graph Database
```bash
# Create and query graph data
GRAPH.QUERY social "CREATE (alice:Person {name: 'Alice'})"
GRAPH.QUERY social "MATCH (p:Person) RETURN p.name"
```

### Machine Learning
```bash
# Serve ML models
ML.MODEL_SET model:1 TORCH BLOB <model_blob> INPUTS input1 input2 OUTPUTS output1
ML.MODEL_RUN model:1 input1_value input2_value
```

## 🧪 Testing

### TDD Test Suite
The Docker setup includes a comprehensive TDD test suite:

1. **Environment Tests** (`test_docker_environment.sh`)
   - Docker installation verification
   - Docker Compose availability
   - Network configuration

2. **Database Tests** (`test_database_connections.sh`)
   - Database connectivity
   - Basic CRUD operations
   - Data persistence

3. **Health Tests** (`test_service_health.sh`)
   - Service health checks
   - Resource monitoring
   - Inter-service communication

4. **Backup Tests** (`test_backup_restore.sh`)
   - Backup functionality
   - Restore operations
   - Data integrity

5. **Cross-Platform Tests** (`test_cross_platform.sh`)
   - OS compatibility
   - Path handling
   - File permissions

### Running Tests
```bash
# Run all tests
./docker/docker-run test

# Run TDD test suite
./docker/docker-run tdd

# Run specific test
./docker/tests/test_docker_environment.sh
```

## 💾 Backup and Restore

### Single Volume Backup
All database data is stored in the shared volume, making backup simple:

```bash
# Create backup
./docker/docker-run backup

# Restore from backup
./docker/docker-run restore /path/to/backup
```

### Backup Location
- **Backup Directory**: `data/backups/YYYYMMDD_HHMMSS/`
- **Database Data**: `docker/database/`
- **Shared Data**: `data/shared_databases/`

## 🔒 Security

### Default Credentials
⚠️ **Change these in production!**

- **All Databases**: `valido/valido123!`
- **Redis**: No password (local development)
- **pgAdmin**: `valido@validoai.com/valido123!`

### Security Best Practices
1. Use environment variables for sensitive data
2. Change default passwords in production
3. Enable SSL/TLS in production
4. Use Docker secrets for sensitive configuration
5. Regular security updates

## 🚀 Performance Optimization

### PostgreSQL Optimizations
- Shared buffers: 2GB
- Work memory: 256MB
- Effective cache size: 6GB
- Parallel workers: 8
- Multiple extensions for performance monitoring

### Redis Optimizations
- Max memory: 4GB
- Memory policy: allkeys-lru
- Append-only persistence enabled
- IO threads: 4
- Advanced modules for JSON, Search, Time Series, Graph, and ML

### System Requirements
- **Minimum**: 8GB RAM, 4 CPU cores
- **Recommended**: 16GB RAM, 8 CPU cores
- **Production**: 32GB+ RAM, 16+ CPU cores

## 🔧 Troubleshooting

### Common Issues

1. **Port Conflicts**
   ```bash
   # Check port usage
   netstat -tulpn | grep :5432
   
   # Change ports in docker-compose.yml
   ```

2. **Permission Issues**
   ```bash
   # Fix file permissions
   chmod +x docker/docker-run
   chmod +x docker/tests/*.sh
   ```

3. **Volume Mount Issues**
   ```bash
   # Check volume mounts
   docker volume ls
   docker volume inspect docker_shared_data
   ```

4. **Service Health Issues**
   ```bash
   # Check service logs
   ./docker/docker-run logs postgresql
   
   # Check service status
   ./docker/docker-run ps
   ```

5. **Redis Module Issues**
   ```bash
   # Check Redis modules
   docker exec redis_ai_valido redis-cli MODULE LIST
   
   # Test JSON functionality
   docker exec redis_ai_valido redis-cli JSON.SET test . '"hello"'
   ```

### Log Locations
- **Application Logs**: `logs/app.log`
- **Docker Logs**: `logs/docker/`
- **Database Logs**: Available via `docker logs` command

## 📚 Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Redis Stack Documentation](https://redis.io/docs/stack/)
- [MongoDB Documentation](https://docs.mongodb.com/)

## 🤝 Contributing

1. Follow the existing directory structure
2. Add tests for new functionality
3. Update documentation
4. Test cross-platform compatibility

## 📄 License

This project is part of the ValidoAI platform.

---

## 🎯 Quick Reference

### **Current Status** ✅
- **All Core Services**: Running and Healthy
- **Jenkins CI**: Operational with 5 automated jobs
- **Database Connections**: All tested and working
- **Naming Convention**: All services follow `{service}_ai_valido` pattern

### **Main Containers**
- **Jenkins CI**: `jenkins_ai_valido` (Port: 8085)
- **PostgreSQL**: `postgresql_ai_valido` (Port: 5432)
- **MySQL**: `mysql_ai_valido` (Port: 3306)
- **MongoDB**: `mongodb_ai_valido` (Port: 27017)
- **Redis**: `redis_ai_valido` (Port: 6379, 8001)
- **Grafana**: `grafana_ai_valido` (Port: 3000)
- **Prometheus**: `prometheus_ai_valido` (Port: 9090)

### **Key Features**
- ✅ **Unified Credentials**: `valido/valido123!`
- ✅ **Redis Stack**: JSON, Search, Time Series, Graph, ML
- ✅ **Latest Versions**: All databases updated to latest stable
- ✅ **Jenkins CI**: Automated testing and CI/CD pipeline
- ✅ **Grafana & Prometheus**: Advanced monitoring and observability
- ✅ **Password-Free Local Development**: Pre-configured Jenkins and Grafana
- ✅ **Cross-Platform**: Works on Linux, macOS, Windows
- ✅ **TDD Support**: Comprehensive test suite
- ✅ **Management GUIs**: Jenkins CI, Grafana, Prometheus, RedisInsight, pgAdmin, phpMyAdmin, etc.

### **Quick Start Commands**
```bash
# Check all services
docker-compose ps

# Start Jenkins CI
docker-compose --profile ci up -d jenkins

# Start monitoring services
docker-compose --profile monitoring up -d

# Run quick CI setup
bash configuration_scripts_docker/quick_ci_start.sh

# Run monitoring setup
bash configuration_scripts_docker/monitoring_setup.sh

# Test database connections
docker-compose exec -T postgresql pg_isready -U valido
docker-compose exec -T mysql mysql -u valido -pvalido123! -e "SELECT VERSION();"
docker-compose exec -T mongodb mongosh --eval "db.adminCommand('ping')"
docker-compose exec -T redis redis-cli ping
```
