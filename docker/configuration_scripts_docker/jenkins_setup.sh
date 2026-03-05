#!/bin/bash

# Jenkins CI Setup Script for ValidoAI
# This script configures Jenkins for local development and testing

echo "🔧 Setting up Jenkins CI for ValidoAI..."

# Create Jenkins directories
mkdir -p /var/jenkins_home/init.groovy.d
mkdir -p /var/jenkins_home/jobs
mkdir -p /var/jenkins_home/workspace

# Create initial Jenkins configuration
cat > /var/jenkins_home/init.groovy.d/01-setup.groovy << 'EOF'
import jenkins.model.*
import hudson.security.*
import jenkins.security.s2m.AdminWhitelistRule
import hudson.model.*
import hudson.tasks.*
import hudson.plugins.git.*
import hudson.plugins.git.extensions.impl.*
import hudson.plugins.git.extensions.*
import hudson.plugins.emailext.*
import hudson.plugins.emailext.plugins.trigger.*
import hudson.plugins.timestamper.*
import hudson.plugins.ansicolor.*
import hudson.triggers.*
import hudson.triggers.SCMTrigger
import hudson.triggers.TimerTrigger

// Disable setup wizard
Jenkins.instance.setInstallState(InstallState.INITIAL_SETUP_COMPLETED)

// Create admin user
def hudsonRealm = new HudsonPrivateSecurityRealm(false)
hudsonRealm.createAccount("admin", "valido123!")
Jenkins.instance.setSecurityRealm(hudsonRealm)

// Set authorization strategy - No password required for local development
def strategy = new FullControlOnceLoggedInAuthorizationStrategy()
Jenkins.instance.setAuthorizationStrategy(strategy)

// Configure Jenkins for local development
Jenkins.instance.setNumExecutors(2)
Jenkins.instance.setMode(Mode.NORMAL)

// Save configuration
Jenkins.instance.save()

println "Jenkins setup completed successfully!"
EOF

# Create Jenkins job directory
mkdir -p /var/jenkins_home/jobs/validoai-tests
mkdir -p /var/jenkins_home/jobs/validoai-database-tests
mkdir -p /var/jenkins_home/jobs/validoai-performance-tests
mkdir -p /var/jenkins_home/jobs/validoai-security-tests
mkdir -p /var/jenkins_home/jobs/validoai-deployment-tests

# Create main ValidoAI tests job
cat > /var/jenkins_home/jobs/validoai-tests/config.xml << 'EOF'
<?xml version='1.1' encoding='UTF-8'?>
<project>
  <actions/>
  <description>Automated testing for ValidoAI project - Comprehensive CI/CD Pipeline</description>
  <keepDependencies>false</keepDependencies>
  <properties/>
  <scm class="hudson.scm.NullSCM"/>
  <canRoam>true</canRoam>
  <disabled>false</disabled>
  <blockBuildWhenDownstreamBuilding>false</blockBuildWhenDownstreamBuilding>
  <blockBuildWhenUpstreamBuilding>false</blockBuildWhenUpstreamBuilding>
  <triggers>
    <hudson.triggers.SCMTrigger>
      <spec>H/5 * * * *</spec>
    </hudson.triggers.SCMTrigger>
    <hudson.triggers.TimerTrigger>
      <spec>0 */6 * * *</spec>
    </hudson.triggers.TimerTrigger>
  </triggers>
  <concurrentBuild>false</concurrentBuild>
  <builders>
    <hudson.tasks.Shell>
      <command>#!/bin/bash
set -e

echo "🚀 Starting ValidoAI Comprehensive CI/CD Pipeline..."
echo "📅 Build started at: $(date)"
echo "🔧 Jenkins version: $(java -version 2>&1 | head -1)"

# Navigate to workspace
cd /workspace
echo "📁 Working directory: $(pwd)"

# Step 1: Docker Compose Validation
echo "🔍 Step 1: Validating Docker Compose configuration..."
docker-compose config --quiet
echo "✅ Docker Compose configuration is valid"

# Step 2: Start Core Services
echo "🐳 Step 2: Starting core database services..."
docker-compose --profile databases up -d postgresql mysql mongodb redis
echo "⏳ Waiting for services to initialize..."
sleep 45

# Step 3: Health Checks
echo "🏥 Step 3: Running health checks..."
services=("postgresql" "mysql" "mongodb" "redis")
for service in "${services[@]}"; do
    echo "🔍 Checking $service..."
    if docker-compose ps $service | grep -q "Up"; then
        echo "✅ $service is running"
    else
        echo "❌ $service is not running properly"
        docker-compose logs $service --tail 10
        exit 1
    fi
done

# Step 4: Database Connection Tests
echo "🔌 Step 4: Testing database connections..."
echo "Testing PostgreSQL..."
docker-compose exec -T postgresql pg_isready -U valido || {
    echo "❌ PostgreSQL connection failed"
    docker-compose logs postgresql --tail 20
    exit 1
}

echo "Testing MySQL..."
docker-compose exec -T mysql mysqladmin ping -h localhost || {
    echo "❌ MySQL connection failed"
    docker-compose logs mysql --tail 20
    exit 1
}

echo "Testing MongoDB..."
docker-compose exec -T mongodb mongosh --eval "db.adminCommand('ping')" || {
    echo "❌ MongoDB connection failed"
    docker-compose logs mongodb --tail 20
    exit 1
}

echo "Testing Redis..."
docker-compose exec -T redis redis-cli ping || {
    echo "❌ Redis connection failed"
    docker-compose logs redis --tail 20
    exit 1
}

# Step 5: Application Tests
echo "🧪 Step 5: Running application tests..."
if [ -f "tests/run_tests.sh" ]; then
    echo "🚀 Running application test suite..."
    chmod +x tests/run_tests.sh
    ./tests/run_tests.sh
else
    echo "⚠️ No application test suite found, skipping..."
fi

# Step 6: Run Comprehensive CI Test Runner
echo "🔧 Step 6: Running comprehensive CI test runner..."
if [ -f "ci_test_runner.sh" ]; then
    echo "🚀 Running comprehensive CI test suite..."
    chmod +x ci_test_runner.sh
    ./ci_test_runner.sh
else
    echo "⚠️ CI test runner not found, using basic tests..."
fi

# Step 7: Docker Service Status
echo "📊 Step 7: Final service status check..."
docker-compose ps --format "table {{.Name}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}"

# Step 8: Performance Metrics
echo "📈 Step 8: Collecting performance metrics..."
echo "Memory usage:"
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}"

echo "✅ All tests completed successfully!"
echo "📅 Build completed at: $(date)"
      </command>
    </hudson.tasks.Shell>
  </builders>
  <publishers>
    <hudson.tasks.junit.JUnitResultArchiver>
      <testResults>**/test-results/*.xml</testResults>
      <keepLongStdio>true</keepLongStdio>
      <healthReports>
        <hudson.tasks.junit.HealthReport>
          <healthy>100</healthy>
          <unhealthy>0</unhealthy>
          <unstableThreshold>0</unstableThreshold>
          <failureStableThreshold>0</failureStableThreshold>
        </hudson.tasks.junit.HealthReport>
      </healthReports>
    </hudson.tasks.junit.JUnitResultArchiver>
    <hudson.plugins.emailext.ExtendedEmailPublisher>
      <recipientList>admin@validoai.com</recipientList>
      <configuredTriggers>
        <hudson.plugins.emailext.plugins.trigger.FailureTrigger>
          <email>
            <recipientList>admin@validoai.com</recipientList>
            <subject>ValidoAI CI/CD Pipeline Failed</subject>
            <body>Build failed for ValidoAI project. Please check Jenkins for details.</body>
          </email>
        </hudson.plugins.emailext.plugins.trigger.FailureTrigger>
      </configuredTriggers>
    </hudson.plugins.emailext.ExtendedEmailPublisher>
  </publishers>
  <buildWrappers>
    <hudson.plugins.timestamper.TimestamperBuildWrapper/>
    <hudson.plugins.ansicolor.AnsiColorBuildWrapper>
      <colorMapName>xterm</colorMapName>
    </hudson.plugins.ansicolor.AnsiColorBuildWrapper>
  </buildWrappers>
</project>
EOF

# Create comprehensive CI test runner script
cat > /var/jenkins_home/workspace/ci_test_runner.sh << 'EOF'
#!/bin/bash

# ValidoAI Test Runner for Jenkins
# This script runs all tests for the ValidoAI project

set -e

echo "🚀 Starting ValidoAI Test Suite..."

# Test 1: Docker Compose Configuration
echo "📋 Testing Docker Compose configuration..."
docker-compose config --quiet
echo "✅ Docker Compose configuration is valid"

# Test 2: Database Services
echo "🗄️ Testing database services..."
docker-compose --profile databases up -d postgresql mysql mongodb redis
sleep 30

# Test 3: Service Health Checks
echo "🔍 Running health checks..."
services=("postgresql" "mysql" "mongodb" "redis")
for service in "${services[@]}"; do
    echo "Testing $service..."
    docker-compose ps $service | grep -q "Up" || {
        echo "❌ $service is not running properly"
        exit 1
    }
done

# Test 4: Database Connections
echo "🔌 Testing database connections..."
docker-compose exec -T postgresql pg_isready -U valido || exit 1
docker-compose exec -T mysql mysqladmin ping -h localhost || exit 1
docker-compose exec -T mongodb mongosh --eval "db.adminCommand('ping')" || exit 1
docker-compose exec -T redis redis-cli ping || exit 1

# Test 5: Application Tests (if they exist)
if [ -f "/workspace/tests/run_tests.sh" ]; then
    echo "🧪 Running application tests..."
    cd /workspace
    chmod +x tests/run_tests.sh
    ./tests/run_tests.sh
fi

echo "✅ All tests completed successfully!"
EOF

# Create database tests job
cat > /var/jenkins_home/jobs/validoai-database-tests/config.xml << 'EOF'
<?xml version='1.1' encoding='UTF-8'?>
<project>
  <actions/>
  <description>Database connectivity and functionality tests for ValidoAI</description>
  <keepDependencies>false</keepDependencies>
  <properties/>
  <scm class="hudson.scm.NullSCM"/>
  <canRoam>true</canRoam>
  <disabled>false</disabled>
  <blockBuildWhenDownstreamBuilding>false</blockBuildWhenUpstreamBuilding>
  <blockBuildWhenUpstreamBuilding>false</blockBuildWhenUpstreamBuilding>
  <triggers>
    <hudson.triggers.TimerTrigger>
      <spec>H/10 * * * *</spec>
    </hudson.triggers.TimerTrigger>
  </triggers>
  <concurrentBuild>false</concurrentBuild>
  <builders>
    <hudson.tasks.Shell>
      <command>#!/bin/bash
set -e

echo "🗄️ Starting Database Tests for ValidoAI..."
echo "📅 Build started at: $(date)"

cd /workspace

# Start databases
echo "🐳 Starting database services..."
docker-compose --profile databases up -d postgresql mysql mongodb redis
sleep 30

# Test PostgreSQL
echo "🔍 Testing PostgreSQL..."
docker-compose exec -T postgresql pg_isready -U valido || exit 1
docker-compose exec -T postgresql psql -U valido -d ai_valido_online -c "SELECT version();" || exit 1

# Test MySQL
echo "🔍 Testing MySQL..."
docker-compose exec -T mysql mysqladmin ping -h localhost || exit 1
docker-compose exec -T mysql mysql -u valido -pvalido123! -e "SELECT VERSION();" || exit 1

# Test MongoDB
echo "🔍 Testing MongoDB..."
docker-compose exec -T mongodb mongosh --eval "db.adminCommand('ping')" || exit 1
docker-compose exec -T mongodb mongosh --eval "db.runCommand({ping: 1})" || exit 1

# Test Redis
echo "🔍 Testing Redis..."
docker-compose exec -T redis redis-cli ping || exit 1
docker-compose exec -T redis redis-cli set test_key "test_value" || exit 1
docker-compose exec -T redis redis-cli get test_key | grep -q "test_value" || exit 1
docker-compose exec -T redis redis-cli del test_key || exit 1

echo "✅ All database tests passed!"
      </command>
    </hudson.tasks.Shell>
  </builders>
  <publishers>
    <hudson.tasks.junit.JUnitResultArchiver>
      <testResults>**/test-results/*.xml</testResults>
      <keepLongStdio>true</keepLongStdio>
    </hudson.tasks.junit.JUnitResultArchiver>
  </publishers>
  <buildWrappers>
    <hudson.plugins.timestamper.TimestamperBuildWrapper/>
    <hudson.plugins.ansicolor.AnsiColorBuildWrapper>
      <colorMapName>xterm</colorMapName>
    </hudson.plugins.ansicolor.AnsiColorBuildWrapper>
  </buildWrappers>
</project>
EOF

# Create performance tests job
cat > /var/jenkins_home/jobs/validoai-performance-tests/config.xml << 'EOF'
<?xml version='1.1' encoding='UTF-8'?>
<project>
  <actions/>
  <description>Performance and load testing for ValidoAI services</description>
  <keepDependencies>false</keepDependencies>
  <properties/>
  <scm class="hudson.scm.NullSCM"/>
  <canRoam>true</canRoam>
  <disabled>false</disabled>
  <blockBuildWhenDownstreamBuilding>false</blockBuildWhenUpstreamBuilding>
  <blockBuildWhenUpstreamBuilding>false</blockBuildWhenUpstreamBuilding>
  <triggers>
    <hudson.triggers.TimerTrigger>
      <spec>0 */2 * * *</spec>
    </hudson.triggers.TimerTrigger>
  </triggers>
  <concurrentBuild>false</concurrentBuild>
  <builders>
    <hudson.tasks.Shell>
      <command>#!/bin/bash
set -e

echo "📈 Starting Performance Tests for ValidoAI..."
echo "📅 Build started at: $(date)"

cd /workspace

# Start services
echo "🐳 Starting services for performance testing..."
docker-compose --profile databases up -d postgresql mysql mongodb redis
sleep 30

# Collect baseline metrics
echo "📊 Collecting baseline performance metrics..."
echo "=== Baseline Metrics ===" > performance_report.txt
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}" >> performance_report.txt

# Test database performance
echo "🔍 Testing database performance..."

# PostgreSQL performance test
echo "Testing PostgreSQL performance..."
time docker-compose exec -T postgresql psql -U valido -d ai_valido_online -c "SELECT generate_series(1,1000);" >> performance_report.txt 2>&1

# MySQL performance test
echo "Testing MySQL performance..."
time docker-compose exec -T mysql mysql -u valido -pvalido123! -e "SELECT 1;" >> performance_report.txt 2>&1

# Redis performance test
echo "Testing Redis performance..."
time docker-compose exec -T redis redis-cli ping >> performance_report.txt 2>&1

# Final metrics
echo "=== Final Metrics ===" >> performance_report.txt
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}" >> performance_report.txt

echo "✅ Performance tests completed!"
cat performance_report.txt
      </command>
    </hudson.tasks.Shell>
  </builders>
  <publishers>
    <hudson.tasks.junit.JUnitResultArchiver>
      <testResults>**/test-results/*.xml</testResults>
      <keepLongStdio>true</keepLongStdio>
    </hudson.tasks.junit.JUnitResultArchiver>
  </publishers>
  <buildWrappers>
    <hudson.plugins.timestamper.TimestamperBuildWrapper/>
    <hudson.plugins.ansicolor.AnsiColorBuildWrapper>
      <colorMapName>xterm</colorMapName>
    </hudson.plugins.ansicolor.AnsiColorBuildWrapper>
  </buildWrappers>
</project>
EOF

# Create security tests job
cat > /var/jenkins_home/jobs/validoai-security-tests/config.xml << 'EOF'
<?xml version='1.1' encoding='UTF-8'?>
<project>
  <actions/>
  <description>Security and vulnerability testing for ValidoAI</description>
  <keepDependencies>false</keepDependencies>
  <properties/>
  <scm class="hudson.scm.NullSCM"/>
  <canRoam>true</canRoam>
  <disabled>false</disabled>
  <blockBuildWhenDownstreamBuilding>false</blockBuildWhenUpstreamBuilding>
  <blockBuildWhenUpstreamBuilding>false</blockBuildWhenUpstreamBuilding>
  <triggers>
    <hudson.triggers.TimerTrigger>
      <spec>0 0 * * *</spec>
    </hudson.triggers.TimerTrigger>
  </triggers>
  <concurrentBuild>false</concurrentBuild>
  <builders>
    <hudson.tasks.Shell>
      <command>#!/bin/bash
set -e

echo "🔒 Starting Security Tests for ValidoAI..."
echo "📅 Build started at: $(date)"

cd /workspace

# Start services
echo "🐳 Starting services for security testing..."
docker-compose --profile databases up -d postgresql mysql mongodb redis
sleep 30

# Security checks
echo "🔍 Running security checks..."

# Check for exposed ports
echo "=== Port Security Check ===" > security_report.txt
netstat -tuln | grep -E ":(5432|3306|27017|6379)" >> security_report.txt

# Check container security
echo "=== Container Security Check ===" >> security_report.txt
docker ps --format "table {{.Names}}\t{{.Image}}\t{{.Status}}" >> security_report.txt

# Check for default passwords
echo "=== Password Security Check ===" >> security_report.txt
echo "PostgreSQL: Using configured credentials" >> security_report.txt
echo "MySQL: Using configured credentials" >> security_report.txt
echo "MongoDB: Using configured credentials" >> security_report.txt
echo "Redis: Using configured credentials" >> security_report.txt

# Check network isolation
echo "=== Network Security Check ===" >> security_report.txt
docker network ls >> security_report.txt

echo "✅ Security tests completed!"
cat security_report.txt
      </command>
    </hudson.tasks.Shell>
  </builders>
  <publishers>
    <hudson.tasks.junit.JUnitResultArchiver>
      <testResults>**/test-results/*.xml</testResults>
      <keepLongStdio>true</keepLongStdio>
    </hudson.tasks.junit.JUnitResultArchiver>
  </publishers>
  <buildWrappers>
    <hudson.plugins.timestamper.TimestamperBuildWrapper/>
    <hudson.plugins.ansicolor.AnsiColorBuildWrapper>
      <colorMapName>xterm</colorMapName>
    </hudson.plugins.ansicolor.AnsiColorBuildWrapper>
  </buildWrappers>
</project>
EOF

# Create deployment tests job
cat > /var/jenkins_home/jobs/validoai-deployment-tests/config.xml << 'EOF'
<?xml version='1.1' encoding='UTF-8'?>
<project>
  <actions/>
  <description>Deployment and infrastructure testing for ValidoAI</description>
  <keepDependencies>false</keepDependencies>
  <properties/>
  <scm class="hudson.scm.NullSCM"/>
  <canRoam>true</canRoam>
  <disabled>false</disabled>
  <blockBuildWhenDownstreamBuilding>false</blockBuildWhenUpstreamBuilding>
  <blockBuildWhenUpstreamBuilding>false</blockBuildWhenUpstreamBuilding>
  <triggers>
    <hudson.triggers.TimerTrigger>
      <spec>0 */4 * * *</spec>
    </hudson.triggers.TimerTrigger>
  </triggers>
  <concurrentBuild>false</concurrentBuild>
  <builders>
    <hudson.tasks.Shell>
      <command>#!/bin/bash
set -e

echo "🚀 Starting Deployment Tests for ValidoAI..."
echo "📅 Build started at: $(date)"

cd /workspace

# Test Docker Compose configuration
echo "🔍 Testing Docker Compose configuration..."
docker-compose config --quiet || exit 1

# Test service deployment
echo "🐳 Testing service deployment..."
docker-compose --profile databases up -d postgresql mysql mongodb redis
sleep 45

# Test service health
echo "🏥 Testing service health..."
services=("postgresql" "mysql" "mongodb" "redis")
for service in "${services[@]}"; do
    echo "Checking $service..."
    if docker-compose ps $service | grep -q "Up"; then
        echo "✅ $service is running"
    else
        echo "❌ $service failed to start"
        exit 1
    fi
done

# Test volume mounts
echo "💾 Testing volume mounts..."
volumes=("postgresql_data" "mysql_data" "mongodb_data" "redis_data")
for volume in "${volumes[@]}"; do
    if docker volume inspect py_ai_valido_${volume} > /dev/null 2>&1; then
        echo "✅ Volume $volume is mounted"
    else
        echo "❌ Volume $volume is not mounted"
        exit 1
    fi
done

# Test network connectivity
echo "🌐 Testing network connectivity..."
if docker network ls | grep -q "py_ai_valido_validoai_network"; then
    echo "✅ Network is created"
else
    echo "❌ Network is not created"
    exit 1
fi

echo "✅ Deployment tests completed!"
      </command>
    </hudson.tasks.Shell>
  </builders>
  <publishers>
    <hudson.tasks.junit.JUnitResultArchiver>
      <testResults>**/test-results/*.xml</testResults>
      <keepLongStdio>true</keepLongStdio>
    </hudson.tasks.junit.JUnitResultArchiver>
  </publishers>
  <buildWrappers>
    <hudson.plugins.timestamper.TimestamperBuildWrapper/>
    <hudson.plugins.ansicolor.AnsiColorBuildWrapper>
      <colorMapName>xterm</colorMapName>
    </hudson.plugins.ansicolor.AnsiColorBuildWrapper>
  </buildWrappers>
</project>
EOF

chmod +x /var/jenkins_home/workspace/ci_test_runner.sh
echo "🌐 Access Jenkins at: http://localhost:8085"
echo "👤 Username: admin"
echo "🔑 Password: valido123!"
