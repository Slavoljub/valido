# 🗄️ Database Management Guide

## Overview

The Database Management system provides comprehensive tools for maintaining, backing up, and restoring ValidoAI databases. This guide covers all aspects of database operations including PostgreSQL setup, connection management, backup strategies, restore procedures, maintenance tasks, and troubleshooting.

## 🚀 PostgreSQL Setup & Configuration

### Prerequisites

- **PostgreSQL 17+** installed and running
- **pgAdmin 4** (optional, for database management)
- **psql command line tool**
- **Database user privileges** (superuser access required for setup)

### Connection Information

```bash
# PostgreSQL Connection Details
Host: localhost (or your PostgreSQL server IP)
Port: 5432 (default PostgreSQL port)
Database: ai_valido_online
Username: postgres
Password: postgres

# Connection Commands
psql -h localhost -p 5432 -U postgres -d ai_valido_online
# When prompted for password, enter: postgres

# Alternative connection string for applications
postgresql://postgres:postgres@localhost:5432/ai_valido_online
```

### Database Creation

#### Option 1: Using psql Command Line

```bash
# Connect to PostgreSQL as superuser
psql -h localhost -p 5432 -U postgres

# Create database with full Unicode support
CREATE DATABASE ai_valido_online
    WITH
    OWNER = postgres
    ENCODING = 'UTF8'
    LC_COLLATE = 'C.UTF-8'
    LC_CTYPE = 'C.UTF-8'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1
    TEMPLATE = template0;

# Exit psql
\q
```

#### Option 2: Using PowerShell (Windows)

```powershell
# Connect and create database
& 'C:\Program Files\PostgreSQL\17\bin\psql.exe' -h localhost -p 5432 -U postgres -c "
CREATE DATABASE ai_valido_online
    WITH
    OWNER = postgres
    ENCODING = 'UTF8'
    LC_COLLATE = 'C.UTF-8'
    LC_CTYPE = 'C.UTF-8'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1
    TEMPLATE = template0;"
```

#### Option 3: Using pgAdmin

1. Open pgAdmin 4
2. Right-click "Databases" → "Create" → "Database"
3. Enter database name: `ai_valido_online`
4. Set owner to: `postgres`
5. Set encoding to: `UTF8`
6. Set collation to: `C.UTF-8`
7. Set character type to: `C.UTF-8`
8. Click "Save"

### Schema Setup

#### Execute Structure File

```bash
# Using psql
psql -h localhost -p 5432 -U postgres -d ai_valido_online -f Postgres_ai_valido_master_structure.sql

# Using PowerShell (Windows)
& 'C:\Program Files\PostgreSQL\17\bin\psql.exe' -h localhost -p 5432 -U postgres -d ai_valido_online -f Postgres_ai_valido_master_structure.sql
```

#### Execute Data File

```bash
# Using psql
psql -h localhost -p 5432 -U postgres -d ai_valido_online -f Postgres_ai_valido_master_data.sql

# Using PowerShell (Windows)
& 'C:\Program Files\PostgreSQL\17\bin\psql.exe' -h localhost -p 5432 -U postgres -d ai_valido_online -f Postgres_ai_valido_master_data.sql
```

### Database Features

#### Enabled Extensions

- **pgvector**: Vector embeddings for AI similarity search
- **pg_trgm**: Text similarity and fuzzy matching
- **pgcrypto**: Encryption and hashing functions
- **uuid-ossp**: UUID generation
- **pg_stat_statements**: Query performance monitoring
- **pg_buffercache**: Buffer cache inspection
- **pg_prewarm**: Cache prewarming
- **unaccent**: Text normalization for international characters
- **pg_similarity**: Advanced similarity functions
- **btree_gist**: GiST index support
- **btree_gin**: GIN index support
- **pg_freespacemap**: Free space mapping
- **timescaledb**: Time-series data optimization
- **postgis**: Geographic data support
- **pg_cron**: Job scheduling
- **pg_repack**: Online table reorganization

#### Unicode Support

The database is configured with full UTF-8 Unicode support for:

- **Serbian Cyrillic**: ћ, ђ, ш, ж, ч, џ, љ, њ, ъ, ѣ
- **Arabic**: أ, ب, ت, ث, ج, ح, خ, د, ذ, ر, ز, س, ش, ص, ض, ط, ظ, ع, غ, ف, ق, ك, ل, م, ن, ه, و, ي
- **Chinese/Japanese/Korean (CJK)**: 中文, 日本語, 한국어
- **Devanagari**: हिन्दी, संस्कृत
- **European Languages**: français, español, deutsch, italiano, português
- **All Unicode Scripts**: Full international character support

### Database Structure

#### Core Tables

- **companies**: Multi-tenant company management
- **users**: User management with role-based access
- **customers**: Customer relationship management
- **products**: Product catalog with categories
- **invoices**: Financial document management
- **payments**: Payment processing and tracking
- **audit_logs**: Complete audit trail
- **chat_sessions**: Chat conversation management
- **ai_models**: AI model registry and management
- **customer_feedback**: Customer feedback with sentiment analysis
- **vector_embeddings**: AI embeddings for similarity search

#### AI Integration Features

- **Sentiment Analysis**: Real-time customer feedback analysis
- **Vector Embeddings**: AI-powered similarity search
- **Automated Insights**: Business intelligence generation
- **Multi-language Support**: Full international language support
- **Performance Monitoring**: AI model performance tracking

## 🎯 Quick Start Guide

### Step 1: Verify PostgreSQL Installation

```bash
# Check PostgreSQL version
psql --version

# Check if PostgreSQL service is running
# Windows: services.msc → PostgreSQL
# Linux: sudo systemctl status postgresql
```

### Step 2: Create Database

```bash
# Connect to PostgreSQL
psql -h localhost -p 5432 -U postgres

# Create database
CREATE DATABASE ai_valido_online
    WITH
    OWNER = postgres
    ENCODING = 'UTF8'
    LC_COLLATE = 'C.UTF-8'
    LC_CTYPE = 'C.UTF-8'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1
    TEMPLATE = template0;

# Exit
\q
```

### Step 3: Execute Schema Files

```bash
# Execute structure file
psql -h localhost -p 5432 -U postgres -d ai_valido_online -f Postgres_ai_valido_master_structure.sql

# Execute data file
psql -h localhost -p 5432 -U postgres -d ai_valido_online -f Postgres_ai_valido_master_data.sql
```

### Step 4: Verify Installation

```bash
# Connect to database
psql -h localhost -p 5432 -U postgres -d ai_valido_online

# Check tables
\d

# Check extensions
\dx

# Check data
SELECT COUNT(*) FROM companies;
SELECT COUNT(*) FROM users;
SELECT COUNT(*) FROM customer_feedback;

# Exit
\q
```

### Step 5: Configure Application

Update your `.env` file with database connection:

```env
# Database Configuration
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/ai_valido_online
DB_HOST=localhost
DB_PORT=5432
DB_NAME=ai_valido_online
DB_USER=postgres
DB_PASSWORD=postgres

# AI Configuration
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

### One-Command Setup Script

For Windows PowerShell users, create a new file called `setup_database.ps1`:

```powershell
# ValidoAI Database Setup Script
param(
    [string]$PostgresPath = "C:\Program Files\PostgreSQL\17\bin",
    [string]$DatabaseName = "ai_valido_online",
    [string]$Username = "postgres",
    [string]$Password = "postgres"
)

# Add PostgreSQL to PATH
$env:PATH = "$PostgresPath;$env:PATH"

Write-Host "🚀 Setting up ValidoAI Database..." -ForegroundColor Green

try {
    # Create database
    Write-Host "📊 Creating database..." -ForegroundColor Yellow
    & psql -h localhost -p 5432 -U $Username -c "CREATE DATABASE $DatabaseName WITH OWNER = $Username ENCODING = 'UTF8' LC_COLLATE = 'C.UTF-8' LC_CTYPE = 'C.UTF-8' TABLESPACE = pg_default CONNECTION LIMIT = -1 TEMPLATE = template0;" -W

    # Execute structure file
    Write-Host "🏗️ Creating database structure..." -ForegroundColor Yellow
    & psql -h localhost -p 5432 -U $Username -d $DatabaseName -f "Postgres_ai_valido_master_structure.sql" -W

    # Execute data file
    Write-Host "📝 Loading sample data..." -ForegroundColor Yellow
    & psql -h localhost -p 5432 -U $Username -d $DatabaseName -f "Postgres_ai_valido_master_data.sql" -W

    Write-Host "✅ Database setup completed successfully!" -ForegroundColor Green
    Write-Host "🎉 You can now start using ValidoAI with PostgreSQL!" -ForegroundColor Green

} catch {
    Write-Host "❌ Error during setup: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
```

#### Usage:
```powershell
# Run the setup script
.\setup_database.ps1
```

### Linux/Mac Setup Script

For Linux/Mac users, create `setup_database.sh`:

```bash
#!/bin/bash

# ValidoAI Database Setup Script
DATABASE_NAME="ai_valido_online"
USERNAME="postgres"
PASSWORD="postgres"

echo "🚀 Setting up ValidoAI Database..."

# Create database
echo "📊 Creating database..."
PGPASSWORD=$PASSWORD psql -h localhost -p 5432 -U $USERNAME -c "CREATE DATABASE $DATABASE_NAME WITH OWNER = $USERNAME ENCODING = 'UTF8' LC_COLLATE = 'C.UTF-8' LC_CTYPE = 'C.UTF-8' TABLESPACE = pg_default CONNECTION LIMIT = -1 TEMPLATE = template0;"

if [ $? -eq 0 ]; then
    echo "✅ Database created successfully"
else
    echo "❌ Failed to create database"
    exit 1
fi

# Execute structure file
echo "🏗️ Creating database structure..."
PGPASSWORD=$PASSWORD psql -h localhost -p 5432 -U $USERNAME -d $DATABASE_NAME -f "Postgres_ai_valido_master_structure.sql"

if [ $? -eq 0 ]; then
    echo "✅ Database structure created successfully"
else
    echo "❌ Failed to create database structure"
    exit 1
fi

# Execute data file
echo "📝 Loading sample data..."
PGPASSWORD=$PASSWORD psql -h localhost -p 5432 -U $USERNAME -d $DATABASE_NAME -f "Postgres_ai_valido_master_data.sql"

if [ $? -eq 0 ]; then
    echo "✅ Sample data loaded successfully"
    echo "🎉 ValidoAI database setup completed!"
else
    echo "❌ Failed to load sample data"
    exit 1
fi
```

#### Usage:
```bash
# Make executable and run
chmod +x setup_database.sh
./setup_database.sh
```

## 🔧 Database Backup System

## 🎯 Features

### Backup & Restore System
- **Multi-Database Support**: app.db, sample.db, ticketing.db
- **Multiple Backup Types**: Full, incremental, schema-only
- **Automated Scheduling**: Configurable backup schedules
- **Compression Support**: Space-efficient backup storage
- **Backup History**: Complete audit trail of all operations

### Database Operations
- **Connection Testing**: Real-time database connectivity checks
- **Performance Monitoring**: Database performance metrics
- **Configuration Management**: Dynamic database settings
- **Environment Editor**: .env file management
- **Statistics Overview**: Comprehensive database statistics

## 🔧 Database Backup System

### Backup Types

#### 1. Full Backup
- **Description**: Complete database backup including all data and schema
- **Use Case**: Complete system backup, migration, disaster recovery
- **Size**: Largest backup size
- **Restore Time**: Fastest restore process

#### 2. Incremental Backup
- **Description**: Backup of only changed data since last backup
- **Use Case**: Regular maintenance, quick backups
- **Size**: Smallest backup size
- **Restore Time**: Requires base backup + all incremental backups

#### 3. Schema Only Backup
- **Description**: Backup of database structure without data
- **Use Case**: Structure preservation, development setup
- **Size**: Minimal size
- **Restore Time**: Fast, but requires data restoration separately

### Backup Process

#### Creating a Backup

1. **Access Database Settings**
   ```
   Navigation: Settings → Database → Backup & Restore Section
   ```

2. **Configure Backup Options**
   - **Database Selection**: Choose target database
   - **Backup Type**: Full, Incremental, or Schema Only
   - **Backup Name**: Optional custom name
   - **Include Data**: Toggle data inclusion (schema-only option)
   - **Compression**: Enable for smaller file sizes

3. **Execute Backup**
   - Click "Create Backup" button
   - Monitor progress in real-time
   - Receive notification upon completion

#### Backup Configuration Options

```javascript
// Example backup configuration
{
    database: "app",           // Target database
    type: "full",              // Backup type
    name: "monthly_backup",    // Custom name
    includeData: true,         // Include data
    compress: true            // Enable compression
}
```

### Backup History Management

#### Viewing Backup History
- **Location**: Backup History table in Database Settings
- **Information**: Name, database, type, size, date, actions
- **Actions**: Download, delete, restore from backup

#### Backup History Table Columns
- **Name**: Custom or auto-generated backup identifier
- **Database**: Source database (app, sample, ticketing)
- **Type**: Backup type (full, incremental, schema)
- **Size**: File size with human-readable format
- **Date**: Creation timestamp
- **Actions**: Available operations (download, delete, restore)

## 🔄 Database Restore System

### Restore Process

#### Preparing for Restore

1. **Select Backup File**
   - Browse available backups in history
   - Review backup details (date, size, type)
   - Confirm backup integrity

2. **Configure Restore Options**
   - **Target Database**: Choose destination database
   - **Drop Existing Tables**: Remove current data (optional)
   - **Create Backup**: Backup current state before restore (recommended)

#### Restore Warning System

The system displays prominent warnings before restore operations:
- **Data Loss Warning**: Current data will be replaced
- **Backup Recommendation**: Suggests creating backup first
- **Confirmation Required**: User must explicitly confirm restore

#### Executing Restore

1. **Confirmation Dialog**
   ```javascript
   // System confirmation prompt
   confirm('Are you sure you want to restore the database? This will replace existing data.')
   ```

2. **Restore Process**
   - System creates backup (if enabled)
   - Database connection is temporarily suspended
   - Backup data is applied to target database
   - Database connection is restored
   - User receives completion notification

3. **Post-Restore Actions**
   - Verify data integrity
   - Test application functionality
   - Review system logs for errors

### Restore Configuration

```javascript
// Example restore configuration
{
    backupFile: "backup_123.sql",
    targetDatabase: "app",
    dropExisting: true,           // Remove current tables
    createBackup: true            // Backup before restore
}
```

## 🛠️ Database Maintenance

### Connection Testing

#### Test All Databases
- **Location**: Database Connection Tests section
- **Function**: Tests connectivity to all configured databases
- **Display**: Real-time status for each database
- **Actions**: Individual database re-testing

#### Status Indicators
- **✅ Success**: Database connected and accessible
- **❌ Failed**: Connection error or database unavailable
- **⚠️ Warning**: Performance issues or slow response

### Environment Configuration

#### .env File Editor
- **Access**: Environment Configuration section
- **Features**: Real-time editing with syntax highlighting
- **Validation**: Automatic syntax checking
- **Backup**: Automatic backup before changes
- **Reload**: Refresh configuration without restart

#### Configuration Categories
- **Database Connections**: Host, port, credentials
- **API Keys**: External service integrations
- **Feature Flags**: Enable/disable system features
- **Performance Settings**: Optimization parameters

## 📊 Database Statistics

### System Overview
- **Total Databases**: Count of configured databases
- **Active Connections**: Current connection count
- **Total Tables**: Sum across all databases

### Individual Database Stats
- **Type**: Database engine (SQLite, PostgreSQL, MySQL)
- **Status**: Connection status
- **Tables**: Number of tables in database
- **Host**: Server address
- **Port**: Connection port

## 🔒 Security Considerations

### Access Control
- **Role-Based Access**: Different permissions for different user roles
- **Audit Logging**: Complete audit trail of all operations
- **Backup Encryption**: Secure backup file storage
- **Access Logging**: Detailed access tracking

### Backup Security
- **File Permissions**: Restricted access to backup files
- **Storage Location**: Secure backup storage path
- **Retention Policies**: Automatic cleanup of old backups
- **Encryption**: Optional backup file encryption

## 📈 Performance Optimization

### Backup Performance
- **Compression**: Reduce backup file size
- **Incremental Backups**: Faster backup creation
- **Parallel Processing**: Multi-threaded operations
- **I/O Optimization**: Optimized disk operations

### Restore Performance
- **Index Recreation**: Efficient index rebuilding
- **Batch Processing**: Optimized data insertion
- **Memory Management**: Efficient memory usage
- **Progress Tracking**: Real-time progress monitoring

## 🚨 Troubleshooting

### Common Issues

#### Backup Creation Fails
- **Check Disk Space**: Ensure sufficient storage space
- **Verify Permissions**: Confirm write permissions to backup directory
- **Database Lock**: Check for active database transactions
- **Network Issues**: Verify network connectivity for remote databases

#### Restore Operation Fails
- **Backup File Integrity**: Verify backup file is not corrupted
- **Database Permissions**: Confirm sufficient privileges
- **Space Requirements**: Ensure adequate space for restore operation
- **Version Compatibility**: Check backup file compatibility

#### Connection Issues
- **Network Connectivity**: Verify network connection
- **Database Service**: Check if database service is running
- **Credentials**: Validate username and password
- **Firewall Rules**: Check firewall configuration

### Error Messages

#### Common Error Codes
- **DB001**: Database connection failed
- **DB002**: Insufficient permissions
- **DB003**: Disk space insufficient
- **DB004**: Backup file corrupted
- **DB005**: Restore operation failed

## 📋 Best Practices

### Backup Strategy
1. **Regular Schedule**: Daily automated backups
2. **Multiple Locations**: Store backups in multiple locations
3. **Retention Policy**: Define backup retention periods
4. **Testing**: Regularly test backup restoration
5. **Documentation**: Document backup and restore procedures

### Maintenance Schedule
- **Daily**: Connection testing and basic monitoring
- **Weekly**: Full backup verification
- **Monthly**: Comprehensive system check
- **Quarterly**: Full disaster recovery drill
- **Yearly**: Complete system audit

### Monitoring
- **Performance Metrics**: Monitor database performance
- **Storage Usage**: Track disk space utilization
- **Error Rates**: Monitor error occurrence rates
- **Backup Success**: Verify backup completion status

## 🔧 API Reference

### Backup Endpoints

```
POST /api/database/backup
- Create new database backup
- Body: { database, type, name, includeData, compress }
- Returns: { success, backupName, fileSize }

GET /api/database/backups
- List all available backups
- Returns: { backups: [...] }

DELETE /api/database/backups/{id}
- Delete specific backup
- Returns: { success, message }
```

### Restore Endpoints

```
POST /api/database/restore
- Restore database from backup
- Body: { backupFile, targetDatabase, dropExisting, createBackup }
- Returns: { success, message }

GET /api/database/backups/{id}/download
- Download backup file
- Returns: file download
```

### Testing Endpoints

```
GET /api/database/test
- Test all database connections
- Returns: { results: { dbName: { status, message } } }

GET /api/database/test/{dbName}
- Test specific database connection
- Returns: { status, message }
```

## 📞 Support & Resources

### Documentation Links
- **Main Documentation**: `/docs/README.md`
- **API Reference**: `/docs/architecture/DATABASE_API_GUIDE.md`
- **Troubleshooting Guide**: Contact support team

### Support Channels
- **Email Support**: support@validoai.com
- **Issue Tracker**: GitHub repository issues
- **Community Forum**: User community discussions
- **Professional Services**: Enterprise support options

### Emergency Contacts
- **Critical Issues**: +381-XX-XXX-XXXX (24/7 support)
- **System Status**: status.validoai.com
- **Emergency Procedures**: Emergency response documentation

---

## 📋 Quick Reference

### Essential Commands

```bash
# Test connection
psql -h localhost -p 5432 -U postgres -d ai_valido_online

# Check tables
\d

# Check extensions
\dx

# View data counts
SELECT 'companies' as table_name, COUNT(*) as count FROM companies
UNION ALL
SELECT 'users', COUNT(*) FROM users
UNION ALL
SELECT 'customer_feedback', COUNT(*) FROM customer_feedback
UNION ALL
SELECT 'ai_models', COUNT(*) FROM ai_models;

# Test Unicode support
SELECT company_name FROM companies WHERE company_name ~ '[^\x00-\x7F]' LIMIT 5;
```

### Database URLs for Applications

```python
# SQLAlchemy
DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/ai_valido_online"

# Django
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'ai_valido_online',
        'USER': 'postgres',
        'PASSWORD': 'postgres',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# Node.js
const connectionString = "postgresql://postgres:postgres@localhost:5432/ai_valido_online";
```

### Troubleshooting

#### Common Issues

**Connection Refused:**
- Ensure PostgreSQL service is running
- Check if port 5432 is open
- Verify firewall settings

**Authentication Failed:**
- Confirm password is "postgres"
- Check user exists: `SELECT * FROM pg_roles WHERE rolname = 'postgres';`

**Database Doesn't Exist:**
- Run the database creation commands from this guide
- Check PostgreSQL logs for errors

**Unicode Issues:**
- Ensure database was created with UTF8 encoding
- Check client encoding: `SHOW client_encoding;`
- Set proper encoding if needed: `SET client_encoding = 'UTF8';`

---

*Effective database management is critical for business continuity and data protection. This guide provides comprehensive information for maintaining, backing up, and restoring ValidoAI databases with enterprise-grade reliability and security.*

**Last updated: December 2024**
**Database Version: 2.0.0**
**Management System: Enterprise Ready**
