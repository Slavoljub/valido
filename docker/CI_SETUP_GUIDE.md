# ValidoAI Local CI Setup Guide

## 🚀 Quick Start

### 1. Start Jenkins CI
```bash
# Navigate to docker directory
cd docker

# Start Jenkins with CI profile
docker-compose --profile ci up -d jenkins

# Wait for Jenkins to be ready (about 30-60 seconds)
```

### 2. Access Jenkins
- **URL**: http://localhost:8085
- **Username**: `admin`
- **Password**: `valido123!`

### 3. Run Quick Setup
```bash
# Run the quick CI setup script
bash configuration_scripts_docker/quick_ci_start.sh
```

## 📊 Available CI Jobs

### 1. **validoai-tests** (Main Comprehensive Tests)
- **Schedule**: Every 5 minutes + Every 6 hours
- **Purpose**: Full system testing including all services
- **Duration**: ~2-3 minutes
- **Tests**:
  - Environment validation
  - Docker Compose validation
  - Core service startup
  - Health checks
  - Database connections
  - Application tests
  - Performance metrics

### 2. **validoai-database-tests** (Database Focused)
- **Schedule**: Every 10 minutes
- **Purpose**: Database connectivity and functionality
- **Duration**: ~1-2 minutes
- **Tests**:
  - PostgreSQL connectivity and queries
  - MySQL connectivity and queries
  - MongoDB connectivity and operations
  - Redis connectivity and operations

### 3. **validoai-performance-tests** (Performance Testing)
- **Schedule**: Every 2 hours
- **Purpose**: Performance and load testing
- **Duration**: ~3-5 minutes
- **Tests**:
  - Baseline performance metrics
  - Database query performance
  - Memory and CPU usage monitoring
  - Response time measurements

### 4. **validoai-security-tests** (Security Testing)
- **Schedule**: Daily at midnight
- **Purpose**: Security and vulnerability assessment
- **Duration**: ~2-3 minutes
- **Tests**:
  - Port security checks
  - Container security validation
  - Password security verification
  - Network isolation checks

### 5. **validoai-deployment-tests** (Deployment Testing)
- **Schedule**: Every 4 hours
- **Purpose**: Infrastructure and deployment validation
- **Duration**: ~2-3 minutes
- **Tests**:
  - Docker Compose configuration validation
  - Service deployment verification
  - Volume mount checks
  - Network connectivity validation

## 🔧 Manual Testing Commands

### Run Comprehensive Tests
```bash
# Run the full CI test suite
bash configuration_scripts_docker/ci_test_runner.sh
```

### Test Individual Services
```bash
# Test PostgreSQL
docker-compose exec -T postgresql pg_isready -U valido

# Test MySQL
docker-compose exec -T mysql mysqladmin ping -h localhost

# Test MongoDB
docker-compose exec -T mongodb mongosh --eval "db.adminCommand('ping')"

# Test Redis
docker-compose exec -T redis redis-cli ping
```

### Check Service Status
```bash
# All services
docker-compose ps

# Specific service
docker-compose ps postgresql

# Service logs
docker-compose logs postgresql --tail 20
```

## 🎯 CI Workflow

### 1. **Automated Testing**
- Jobs run automatically based on schedules
- No manual intervention required
- Results logged and archived

### 2. **Manual Testing**
- Click "Build Now" on any job
- Immediate execution
- Real-time console output

### 3. **Test Results**
- **Success**: Green build indicator
- **Failure**: Red build indicator with detailed logs
- **Reports**: Generated test reports with metrics

### 4. **Notifications**
- Build status displayed in Jenkins dashboard
- Console output for debugging
- Test reports for analysis

## 📈 Performance Monitoring

### Resource Metrics
- **CPU Usage**: Per container monitoring
- **Memory Usage**: Real-time memory consumption
- **Network I/O**: Container network statistics
- **Disk I/O**: Volume and storage metrics

### Health Indicators
- **Service Status**: Running/Stopped/Healthy
- **Response Time**: Database connection latency
- **Error Rates**: Failed connection attempts
- **Uptime**: Service availability metrics

## 🔒 Security Features

### Password-Free Local Development
- **Pre-configured admin user**: No setup wizard
- **Local access only**: No external authentication required
- **Docker socket access**: For container management
- **Workspace mounting**: Direct access to project files

### Security Checks
- **Port exposure validation**
- **Container security verification**
- **Network isolation testing**
- **Credential security validation**

## 🛠️ Troubleshooting

### Common Issues

#### 1. Jenkins Not Starting
```bash
# Check Jenkins logs
docker-compose logs jenkins

# Restart Jenkins
docker-compose restart jenkins

# Check if port 8085 is available
netstat -tuln | grep 8085
```

#### 2. Jobs Not Running
```bash
# Check Jenkins configuration
docker-compose exec jenkins_ai_valido cat /var/jenkins_home/config.xml

# Restart Jenkins to reload configuration
docker-compose restart jenkins
```

#### 3. Database Connection Failures
```bash
# Check database logs
docker-compose logs postgresql
docker-compose logs mysql
docker-compose logs mongodb
docker-compose logs redis

# Restart databases
docker-compose restart postgresql mysql mongodb redis
```

#### 4. Network Issues
```bash
# Clean up networks
docker network prune -f

# Restart all services
docker-compose down --remove-orphans
docker-compose up -d
```

### Health Check Commands

#### Service Status
```bash
# Quick health check
docker-compose ps

# Detailed service information
docker-compose ps --format "table {{.Name}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}"
```

#### Log Analysis
```bash
# Recent logs
docker-compose logs --tail 50

# Follow logs in real-time
docker-compose logs -f

# Service-specific logs
docker-compose logs postgresql --tail 20
```

## 📋 Best Practices

### 1. **Regular Monitoring**
- Check Jenkins dashboard daily
- Review test results weekly
- Monitor resource usage regularly

### 2. **Maintenance**
- Update Jenkins plugins monthly
- Clean up old builds weekly
- Monitor disk space daily

### 3. **Testing Strategy**
- Run comprehensive tests before deployments
- Use specific job types for targeted testing
- Monitor performance trends over time

### 4. **Documentation**
- Keep test results for analysis
- Document any configuration changes
- Maintain troubleshooting guides

## 🎉 Getting Started Checklist

- [ ] Jenkins is running and accessible
- [ ] All CI jobs are created and visible
- [ ] Core services (databases) are healthy
- [ ] Manual test execution works
- [ ] Automated schedules are active
- [ ] Test reports are being generated
- [ ] Performance monitoring is active
- [ ] Security checks are running

## 📞 Support

### Getting Help
1. **Check logs**: `docker-compose logs [service-name]`
2. **Review documentation**: This guide and README_CI.md
3. **Run diagnostics**: `bash configuration_scripts_docker/ci_test_runner.sh`
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
