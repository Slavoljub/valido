# ValidoAI PostgreSQL Database Setup

## 🚀 Complete AI-Powered Database Setup Guide

This guide provides comprehensive instructions for setting up the ValidoAI PostgreSQL database with full AI/ML integration capabilities.

## 📋 Table of Contents

- [Overview](#overview)
- [System Requirements](#system-requirements)
- [Quick Start](#quick-start)
- [Detailed Setup](#detailed-setup)
- [AI/ML Features](#aiml-features)
- [Database Schema](#database-schema)
- [API Reference](#api-reference)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)

## 📊 Overview

The ValidoAI PostgreSQL setup provides:

- **✅ 73+ Tables** - Complete business database schema
- **✅ 13 Extensions** - Full PostgreSQL extension support
- **✅ AI/ML Integration** - Vector embeddings, hybrid search, AI insights
- **✅ Cross-Platform** - Works on Windows, Linux, and macOS
- **✅ Production Ready** - Optimized for performance and scalability
- **✅ Comprehensive Data** - Sample data for all features

### Key Features

- **Financial Management**: Companies, invoices, chart of accounts, general ledger
- **AI-Powered Analytics**: Vector embeddings, semantic search, automated insights
- **Customer Management**: CRM, email campaigns, user management
- **Inventory & Products**: Multi-warehouse, stock management
- **Reporting & Analytics**: Comprehensive business intelligence
- **Security & Audit**: Row-level security, audit trails
- **Multi-tenancy**: Company-based data isolation

## 🔧 System Requirements

### Minimum Requirements

| Component | Version | Notes |
|-----------|---------|--------|
| PostgreSQL | 17+ | PostgreSQL 17 recommended |
| Memory | 4GB | 8GB+ recommended for AI features |
| Disk Space | 2GB | 5GB+ for sample data |
| OS | Windows 10+, Ubuntu 20.04+, macOS 12+ | |

### Operating System Support

- **✅ Windows**: Via PowerShell (with WSL for Linux compatibility)
- **✅ Linux**: Native bash support (Ubuntu, CentOS, RHEL, etc.)
- **✅ macOS**: Native bash support via Terminal

## 🚀 Quick Start

### Option 1: Automated Setup (Recommended)

```bash
# Make the script executable (Linux/macOS)
chmod +x validoai_master_setup.sh

# Run the complete setup
./validoai_master_setup.sh
```

```powershell
# Windows PowerShell
.\validoai_master_setup.sh
```

### Option 2: Manual Setup

1. **Install PostgreSQL 17**
2. **Create Database**
3. **Run Structure Script**
4. **Run Data Script**
5. **Verify Setup**

## 📦 Detailed Setup

### Step 1: Install PostgreSQL

#### Windows
```powershell
# Using Chocolatey
choco install postgresql17

# Or download from: https://www.postgresql.org/download/windows/
```

#### Linux (Ubuntu/Debian)
```bash
# Add PostgreSQL repository
sudo sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'
wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -

# Install PostgreSQL 17
sudo apt update
sudo apt install postgresql-17 postgresql-client-17
```

#### macOS
```bash
# Using Homebrew
brew install postgresql@17

# Start PostgreSQL service
brew services start postgresql@17
```

### Step 2: Configure Database

The master setup script will automatically:
- ✅ Create database `ai_valido_online`
- ✅ Install required extensions
- ✅ Apply database structure
- ✅ Load sample data
- ✅ Configure AI/ML functions

### Step 3: Verify Installation

```bash
# Check database status
psql -h localhost -U postgres -d ai_valido_online -c "SELECT version();"

# Check table count
psql -h localhost -U postgres -d ai_valido_online -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';"

# Check sample data
psql -h localhost -U postgres -d ai_valido_online -c "SELECT 'Companies' as table, COUNT(*) as count FROM companies UNION ALL SELECT 'Users', COUNT(*) FROM users UNION ALL SELECT 'Products', COUNT(*) FROM products;"
```

## 🧠 AI/ML Features

### Vector Embeddings
```sql
-- Generate embeddings for content
SELECT embedding('Your text content here');

-- Store with vector column
INSERT INTO ai_insights (title, summary, embedding_vector)
VALUES ('Title', 'Summary', embedding('Title Summary'));
```

### Hybrid Search
```sql
-- Perform semantic search
SELECT * FROM hybrid_search(
    'financial analysis query',
    'ai_insights',
    'title',
    'embedding_vector'
);
```

### AI Insights Generation
```sql
-- Generate automated insights
SELECT generate_ai_insight(
    company_uuid,
    user_uuid,
    'financial_analysis',
    '{"data": "financial metrics here"}'::jsonb
);
```

### Chat Context Management
```sql
-- Get conversation context
SELECT * FROM get_chat_context(chat_session_uuid, 10);
```

## 🗄️ Database Schema

### Core Tables

#### Business Entities
- `companies` - Company information and settings
- `users` - User accounts and authentication
- `products` - Product catalog and pricing
- `customers` - Customer information

#### Financial Management
- `chart_of_accounts` - Accounting chart structure
- `general_ledger` - General ledger transactions (partitioned)
- `invoices` - Customer invoices and billing
- `bank_accounts` - Bank account management

#### AI/ML Integration
- `ai_insights` - AI-generated insights (partitioned)
- `vector_embeddings` - Vector embeddings for search
- `ai_models` - AI model configurations
- `ai_prompt_templates` - Reusable prompt templates

#### Communication
- `chat_sessions` - Chat conversation sessions
- `chat_messages` - Individual chat messages
- `email_templates` - Email template management
- `notifications` - System notifications

### Key Relationships

```
companies (1) ──── (N) users
companies (1) ──── (N) products
companies (1) ──── (N) chart_of_accounts
companies (1) ──── (N) general_ledger
companies (1) ──── (N) invoices
companies (1) ──── (N) ai_insights
users (1) ───────── (N) chat_sessions
chat_sessions (1) ── (N) chat_messages
```

## 🔧 Configuration

### Environment Variables

```bash
# Database Configuration
export DB_HOST="localhost"
export DB_PORT="5432"
export DB_NAME="ai_valido_online"
export DB_USERNAME="postgres"
export DB_PASSWORD="postgres"

# AI/ML Configuration
export AI_EMBEDDING_MODEL="text-embedding-3-small"
export AI_LLM_MODEL="gpt-4"
export VECTOR_DIMENSION="1536"
```

### Command Line Options

```bash
# Skip certain setup steps
./validoai_master_setup.sh --skip-extensions --skip-sample-data

# Get help
./validoai_master_setup.sh --help
```

## 📊 Sample Data

The setup includes comprehensive sample data:

### Companies (4)
- ValidoAI Solutions (Serbia)
- TechCorp International (USA)
- EuroTech Solutions (Germany)
- GlobalSoft Ltd (UK)

### Users (5)
- Admin user
- Manager user
- Analyst user
- Sales user
- Developer user

### Products (3)
- AI Financial Suite
- Enterprise CRM with AI
- AI-Powered Analytics Platform

### Financial Data
- Chart of accounts with 3 main accounts
- General ledger transactions
- Customer invoices

### AI/ML Data
- Sample AI insights with different impact levels
- Chat conversations for testing
- Vector embeddings for semantic search

## 🔍 API Reference

### Database Functions

#### AI/ML Functions
```sql
-- Update embeddings for any table
SELECT update_content_embeddings('table_name', 'content_column', 'embedding_column');

-- Perform hybrid search
SELECT * FROM hybrid_search('search_term', 'table_name', 'content_column', 'embedding_column');

-- Generate AI insights
SELECT generate_ai_insight(company_uuid, user_uuid, 'insight_type', data_jsonb);

-- Get chat context
SELECT * FROM get_chat_context(session_uuid, limit_count);
```

#### Utility Functions
```sql
-- Validate database integrity
SELECT * FROM validate_database_integrity();

-- Create backup
SELECT create_full_backup();
```

### Key Tables Reference

#### Companies
```sql
SELECT
    companies_id,
    company_name,
    tax_id,
    city,
    country_id,
    default_currency,
    is_active
FROM companies;
```

#### Users
```sql
SELECT
    users_id,
    username,
    email,
    first_name,
    last_name,
    is_active,
    last_login_at
FROM users;
```

#### AI Insights
```sql
SELECT
    ai_insights_id,
    company_id,
    user_id,
    insight_type,
    title,
    summary,
    impact_level,
    category,
    created_at
FROM ai_insights;
```

## 🚨 Troubleshooting

### Common Issues

#### 1. PostgreSQL Connection Failed
```bash
# Check if PostgreSQL is running
sudo systemctl status postgresql

# Check connection
psql -h localhost -U postgres -c "SELECT 1;"

# Reset password if needed
sudo -u postgres psql -c "ALTER USER postgres PASSWORD 'new_password';"
```

#### 2. Extension Installation Failed
```bash
# Check available extensions
SELECT name FROM pg_available_extensions WHERE name LIKE '%vector%';

# Install manually
CREATE EXTENSION IF NOT EXISTS vector;
```

#### 3. Permission Denied
```bash
# Grant necessary permissions
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE ai_valido_online TO postgres;"

# Create user if needed
sudo -u postgres createuser --interactive
```

#### 4. Out of Memory
```bash
# Increase shared memory (Linux)
sudo sh -c 'echo "kernel.shmmax=268435456" >> /etc/sysctl.conf'
sudo sh -c 'echo "kernel.shmall=65536" >> /etc/sysctl.conf'
sudo sysctl -p

# Increase PostgreSQL memory settings
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET work_mem = '64MB';
```

### Performance Tuning

```sql
-- Optimize for AI workloads
ALTER SYSTEM SET shared_preload_libraries = 'pg_stat_statements, vector';
ALTER SYSTEM SET max_parallel_workers_per_gather = 4;
ALTER SYSTEM SET effective_cache_size = '2GB';

-- Reload configuration
SELECT pg_reload_conf();
```

## 📈 Performance Optimization

### Indexing Strategy

```sql
-- Vector similarity search index
CREATE INDEX ON ai_insights USING ivfflat (embedding_vector vector_cosine_ops) WITH (lists = 100);

-- Full-text search indexes
CREATE INDEX ON ai_insights USING gin (to_tsvector('english', title || ' ' || summary));

-- Partial indexes for active records
CREATE INDEX ON users (username) WHERE is_active = true;
```

### Partitioning

The setup uses table partitioning for:
- `general_ledger` - Partitioned by transaction date (yearly)
- `ai_insights` - Partitioned by creation date (yearly)

### Maintenance

```bash
# Regular maintenance
./maintenance_database.sh

# Vacuum and analyze
psql -d ai_valido_online -c "VACUUM ANALYZE;"

# Update statistics
psql -d ai_valido_online -c "ANALYZE;"
```

## 🔒 Security

### Best Practices

1. **Use strong passwords**
2. **Enable SSL connections**
3. **Restrict network access**
4. **Regular security updates**
5. **Monitor logs**

### Row Level Security

```sql
-- Enable RLS on sensitive tables
ALTER TABLE companies ENABLE ROW LEVEL SECURITY;
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

-- Create policies
CREATE POLICY company_isolation ON companies
    FOR ALL USING (companies_id = current_setting('app.current_company_id')::uuid);
```

## 📚 Contributing

### Development Setup

1. Fork the repository
2. Create feature branch
3. Make changes
4. Test thoroughly
5. Submit pull request

### Testing

```bash
# Run validation
./validoai_master_setup.sh --skip-sample-data

# Test AI functions
psql -d ai_valido_online -c "SELECT * FROM validate_database_integrity();"
```

## 📞 Support

### Getting Help

1. Check the troubleshooting section
2. Review the FAQ
3. Check GitHub issues
4. Contact support

### Community

- **GitHub Repository**: [ValidoAI/PostgreSQL-Setup](https://github.com/validoai/postgresql-setup)
- **Documentation**: [ValidoAI Docs](https://docs.validoai.com)
- **Discord**: [ValidoAI Community](https://discord.gg/validoai)

## 📋 Changelog

### Version 1.0.0
- ✅ Complete cross-platform setup script
- ✅ Full AI/ML integration
- ✅ Comprehensive sample data
- ✅ Automated validation and testing
- ✅ Production-ready configuration

### Version 0.9.0
- ✅ Initial PostgreSQL structure
- ✅ Basic AI integration
- ✅ Sample data loading
- ✅ Extension management

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🎯 Quick Commands Reference

```bash
# Complete setup
./validoai_master_setup.sh

# Database backup
./backup_database.sh

# Maintenance
./maintenance_database.sh

# Cleanup old files
./validoai_cleanup.ps1 -Force

# Validation
psql -d ai_valido_online -c "SELECT * FROM validate_database_integrity();"
```

---

**🎉 Your ValidoAI PostgreSQL database is ready for AI-powered applications!**

For more information, visit [ValidoAI Documentation](https://docs.validoai.com) or join our [Discord Community](https://discord.gg/validoai).
