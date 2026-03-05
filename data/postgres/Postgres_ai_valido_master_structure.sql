-- ============================================================================
-- VALIDOAI MASTER DATABASE STRUCTURE
-- ============================================================================
-- Comprehensive Serbian Business Management System
-- Optimized for 100PB+ data with AI/LLM integration
-- Serbian financial compliance and bookkeeping standards
-- Multi-company management with role-based access
-- Audit trail for all data changes
-- AI embeddings and similarity search
-- FULL UNICODE AND CYRILLIC TEXT SUPPORT
-- ============================================================================

-- ============================================================================
-- CONNECTION INFORMATION
-- ============================================================================
-- PostgreSQL Connection Details:
-- Host: localhost (or your PostgreSQL server IP)
-- Port: 5432 (default PostgreSQL port)
-- Database: ai_valido_online
-- Username: postgres
-- Password: postgres
--
-- Connection Command:
-- psql -h localhost -p 5432 -U postgres p:postgres -d ai_valido_online
-- When prompted for password, enter: postgres
--
-- Alternative connection string:
-- postgresql://postgres:postgres@localhost:5432/ai_valido_online
--
-- IMPORTANT: Ensure PostgreSQL service is running before executing this script
-- ============================================================================

-- ============================================================================
-- DATABASE MANAGEMENT - DROP AND CREATE
-- ============================================================================

-- IMPORTANT: Run this section as postgres superuser to completely reset the database
-- This will DROP the existing database and create a fresh one with proper settings

-- Drop existing database (CAUTION: This will delete all data!)
-- DROP DATABASE IF EXISTS ai_valido_online;

-- Create fresh database with full UTF-8 Unicode support
-- CREATE DATABASE ai_valido_online
--     WITH
--     OWNER = postgres
--     ENCODING = 'UTF8'
--     LC_COLLATE = 'C.UTF-8'
--     LC_CTYPE = 'C.UTF-8'
--     TABLESPACE = pg_default
--     CONNECTION LIMIT = -1
--     TEMPLATE = template0;

-- Alternative with ICU support (recommended for better Unicode handling)
-- CREATE DATABASE ai_valido_online
--     WITH
--     OWNER = postgres
--     ENCODING = 'UTF8'
--     LC_COLLATE = 'und-x-icu'
--     LC_CTYPE = 'und-x-icu'
--     TABLESPACE = pg_default
--     CONNECTION LIMIT = -1
--     TEMPLATE = template0;

-- Connect to the database after creation
-- \c ai_valido_online postgres;

-- ============================================================================
-- DATABASE CREATION WITH FULL UTF-8 UNICODE SUPPORT
-- ============================================================================

-- Create database with full UTF-8 Unicode support for all languages
-- Note: Run this section as postgres superuser before connecting to the database
DROP DATABASE IF EXISTS ai_valido_online;
CREATE DATABASE IF NOT EXISTS ai_valido_online
    WITH
    OWNER = postgres
    ENCODING = 'UTF8'
    LC_COLLATE = 'C.UTF-8'
    LC_CTYPE = 'C.UTF-8'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1
    TEMPLATE = template0;

-- Alternative for systems with ICU support (recommended for better Unicode handling)
-- CREATE DATABASE IF NOT EXISTS ai_valido_online
--     WITH
--     OWNER = postgres
--     ENCODING = 'UTF8'
--     LC_COLLATE = 'und-x-icu'
--     LC_CTYPE = 'und-x-icu'
--     TABLESPACE = pg_default
--     CONNECTION LIMIT = -1
--     TEMPLATE = template0;

-- Connect to the database (run this after database creation)
-- \c ai_valido_online postgres;

-- Set proper encoding and Unicode support for all languages
SET client_encoding = 'UTF8';
SET standard_conforming_strings = ON;
SET default_text_search_config = 'pg_catalog.simple';

-- Enable Unicode normalization for consistent text processing
SET unicode_normalization = 'NFC';

-- Create ICU collations for better Unicode support if available
-- CREATE COLLATION IF NOT EXISTS unicode_ci (
--     PROVIDER = icu,
--     LOCALE = 'und-u-ks-level2',
--     DETERMINISTIC = false
-- );

-- CREATE COLLATION IF NOT EXISTS unicode_general_ci (
--     PROVIDER = icu,
--     LOCALE = 'und-u-ks-level1',
--     DETERMINISTIC = false
-- );

-- ============================================================================
-- EXTENSIONS AND COLLATIONS
-- ============================================================================

-- Enable all necessary extensions for scale and AI
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";
CREATE EXTENSION IF NOT EXISTS "pg_buffercache";
CREATE EXTENSION IF NOT EXISTS "pg_prewarm";
CREATE EXTENSION IF NOT EXISTS "pg_similarity";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "btree_gist";
CREATE EXTENSION IF NOT EXISTS "btree_gin";
CREATE EXTENSION IF NOT EXISTS "unaccent";

-- Unicode and text processing extensions
CREATE EXTENSION IF NOT EXISTS "fuzzystrmatch";
CREATE EXTENSION IF NOT EXISTS "pg_trgm"; -- For text similarity (if not already created)

-- Create universal Unicode text search configuration
-- CREATE TEXT SEARCH CONFIGURATION unicode_search (COPY = simple);
-- ALTER TEXT SEARCH CONFIGURATION unicode_search
--     ADD MAPPING FOR word, hword, hword_part, hword_asciipart
--     WITH unaccent, simple;

-- Set default text search to handle all Unicode characters
-- SET default_text_search_config = 'unicode_search';
CREATE EXTENSION IF NOT EXISTS "pg_freespacemap";
CREATE EXTENSION IF NOT EXISTS "pgvector";
CREATE EXTENSION IF NOT EXISTS "timescaledb";
CREATE EXTENSION IF NOT EXISTS "postgis";
CREATE EXTENSION IF NOT EXISTS "pg_cron";
CREATE EXTENSION IF NOT EXISTS "pg_repack";

-- AI and ML Extensions (install separately if needed)
-- CREATE EXTENSION IF NOT EXISTS "pgai";
-- CREATE EXTENSION IF NOT EXISTS "postgresml";

-- ============================================================================
-- SECURITY AND ROLES
-- ============================================================================

-- Create roles for different access levels
CREATE ROLE ai_valido_superadmin WITH LOGIN PASSWORD 'enterprise_secure_admin_2025';
CREATE ROLE ai_valido_admin WITH LOGIN PASSWORD 'secure_admin_pass_2025';
CREATE ROLE ai_valido_developer WITH LOGIN PASSWORD 'secure_dev_pass_2025';
CREATE ROLE ai_valido_accountant WITH LOGIN PASSWORD 'secure_acc_pass_2025';
CREATE ROLE ai_valido_manager WITH LOGIN PASSWORD 'secure_mgr_pass_2025';
CREATE ROLE ai_valido_hr WITH LOGIN PASSWORD 'secure_hr_pass_2025';
CREATE ROLE ai_valido_user WITH LOGIN PASSWORD 'secure_user_pass_2025';
CREATE ROLE ai_valido_readonly WITH LOGIN PASSWORD 'secure_readonly_pass_2025';
CREATE ROLE ai_valido_demo WITH LOGIN PASSWORD 'demo_pass_2025';
CREATE ROLE ai_valido_api WITH LOGIN PASSWORD 'api_secure_pass_2025';

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE ai_valido_online TO ai_valido_superadmin;
GRANT CREATE, CONNECT ON DATABASE ai_valido_online TO ai_valido_admin;
GRANT CONNECT ON DATABASE ai_valido_online TO ai_valido_readonly;

-- ============================================================================
-- CORE REFERENCE TABLES
-- ============================================================================

-- Countries with Serbian focus
CREATE TABLE countries (
    countries_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    iso_code VARCHAR(3) NOT NULL UNIQUE,
    iso_code3 VARCHAR(3),
    name VARCHAR(100) NOT NULL,
    name_sr VARCHAR(100),
    region VARCHAR(50),
    subregion VARCHAR(50),
    currency_code VARCHAR(3) DEFAULT 'RSD',
    phone_code VARCHAR(10),
    flag_emoji VARCHAR(10),
    is_eu_member BOOLEAN DEFAULT false,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Currencies with Serbian Dinar focus
CREATE TABLE currencies (
    currencies_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    code VARCHAR(3) NOT NULL UNIQUE,
    name VARCHAR(50) NOT NULL,
    name_sr VARCHAR(50),
    symbol VARCHAR(5),
    decimal_places INTEGER DEFAULT 2,
    exchange_rate_to_rsd DECIMAL(15,6),
    is_crypto BOOLEAN DEFAULT false,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Serbian business entity types
CREATE TABLE business_entity_types (
    business_entity_types_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    entity_code VARCHAR(10) NOT NULL UNIQUE,
    entity_name VARCHAR(100) NOT NULL,
    entity_name_sr VARCHAR(100),
    description TEXT,
    tax_requirements JSONB,
    reporting_requirements JSONB,
    pdv_obligations JSONB,
    e_invoice_requirements JSONB,
    legal_requirements JSONB,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Business areas/industries
CREATE TABLE business_areas (
    business_areas_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    area_code VARCHAR(20) NOT NULL UNIQUE,
    area_name VARCHAR(100) NOT NULL,
    area_name_sr VARCHAR(100),
    description TEXT,
    nace_codes JSONB,
    tax_rates JSONB,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- USER MANAGEMENT SYSTEM
-- ============================================================================

-- ============================================================================
-- CORE TABLES - START WITH DROP/CREATE SUPPORT
-- ============================================================================

-- ============================================================================
-- CORE TABLES WITH DROP/CREATE SUPPORT
-- ============================================================================

-- Companies (multi-tenant architecture) - MAIN TABLE
DROP TABLE IF EXISTS companies CASCADE; CREATE TABLE companies (
    companies_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_name VARCHAR(255) NOT NULL,
    legal_name VARCHAR(255),
    tax_id VARCHAR(20) UNIQUE NOT NULL, -- PIB (Tax ID)
    registration_number VARCHAR(20) UNIQUE, -- Matični broj
    business_entity_type_id UUID REFERENCES business_entity_types(business_entity_types_id),
    business_area_id UUID REFERENCES business_areas(business_areas_id),
    country_id UUID REFERENCES countries(countries_id),

    -- Serbian business details
    pdv_registration VARCHAR(20),
    statistical_number VARCHAR(20),
    activity_code VARCHAR(10), -- Šifra delatnosti
    founding_date DATE,
    fiscal_year_start DATE DEFAULT '2024-01-01',
    currency_id UUID REFERENCES currencies(currencies_id),

    -- Contact information
    address_line1 VARCHAR(255),
    address_line2 VARCHAR(255),
    city VARCHAR(100),
    municipality VARCHAR(100),
    postal_code VARCHAR(10),
    country VARCHAR(50) DEFAULT 'Serbia',
    phone VARCHAR(20),
    email VARCHAR(255),
    website VARCHAR(255),

    -- Bank information
    bank_account VARCHAR(30),
    bank_name VARCHAR(100),
    bank_bic VARCHAR(20),

    -- Status and compliance
    status VARCHAR(20) DEFAULT 'active',
    is_pdv_registered BOOLEAN DEFAULT false,
    is_e_invoice_enabled BOOLEAN DEFAULT false,
    is_active BOOLEAN DEFAULT true,
    compliance_status VARCHAR(20) DEFAULT 'compliant',
    last_audit_date DATE,

    -- Business metrics for AI comparison
    employee_count INTEGER DEFAULT 0,
    annual_revenue DECIMAL(15,2) DEFAULT 0,
    market_share DECIMAL(5,2) DEFAULT 0,
    customer_count INTEGER DEFAULT 0,
    product_count INTEGER DEFAULT 0,

    -- AI and similarity search
    business_description TEXT,
    strengths JSONB,
    weaknesses JSONB,
    opportunities JSONB,
    threats JSONB,
    embedding_vector VECTOR(1536), -- For AI similarity search

    -- Metadata
    description TEXT,
    notes TEXT,
    company_logo_url VARCHAR(500),
    tags JSONB,
    custom_fields JSONB,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by UUID,
    updated_by UUID,

    -- Partitioning key for 100PB scale
    PARTITION BY RANGE (created_at)
);

-- Create partitions for time-based data distribution
CREATE TABLE companies_y2024 PARTITION OF companies
    FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');
CREATE TABLE companies_y2025 PARTITION OF companies
    FOR VALUES FROM ('2025-01-01') TO ('2026-01-01');
CREATE TABLE companies_future PARTITION OF companies
    FOR VALUES FROM ('2026-01-01') TO (MAXVALUE);

-- ============================================================================
-- MULTI-COMPANY USER MANAGEMENT
-- ============================================================================

-- User company access - allows users to manage multiple companies
DROP TABLE IF EXISTS user_company_access CASCADE;
CREATE TABLE user_company_access (
    user_company_access_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(users_id) ON DELETE CASCADE,
    companies_id UUID NOT NULL REFERENCES companies(companies_id) ON DELETE CASCADE,
    access_level VARCHAR(20) DEFAULT 'user', -- owner, admin, accountant, manager, user, readonly
    role_description TEXT,
    permissions JSONB, -- Specific permissions for this company access

    -- Access settings
    is_primary_company BOOLEAN DEFAULT false,
    can_create_invoices BOOLEAN DEFAULT true,
    can_manage_users BOOLEAN DEFAULT false,
    can_view_reports BOOLEAN DEFAULT true,
    can_manage_settings BOOLEAN DEFAULT false,
    can_access_all_data BOOLEAN DEFAULT false,

    -- Status
    status VARCHAR(20) DEFAULT 'active', -- active, suspended, pending, invited
    invited_by UUID REFERENCES users(users_id),
    invited_at TIMESTAMP,
    invitation_token VARCHAR(100),
    invitation_expires_at TIMESTAMP,

    -- Audit
    last_accessed_at TIMESTAMP,
    access_count INTEGER DEFAULT 0,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(users_id),
    updated_by UUID REFERENCES users(users_id),

    UNIQUE(user_id, companies_id)
);

-- User company sessions - track which company user is currently working with
DROP TABLE IF EXISTS user_company_sessions CASCADE;
CREATE TABLE user_company_sessions (
    user_company_sessions_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(users_id) ON DELETE CASCADE,
    companies_id UUID NOT NULL REFERENCES companies(companies_id) ON DELETE CASCADE,
    session_id VARCHAR(100) NOT NULL,
    session_token VARCHAR(255),
    ip_address INET,
    user_agent TEXT,

    -- Session settings
    is_active BOOLEAN DEFAULT true,
    expires_at TIMESTAMP,
    last_activity_at TIMESTAMP,

    -- Context
    current_module VARCHAR(50),
    current_page VARCHAR(100),
    context_data JSONB,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Company invitations - for inviting users to manage companies
DROP TABLE IF EXISTS company_invitations CASCADE;
CREATE TABLE company_invitations (
    company_invitations_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    companies_id UUID NOT NULL REFERENCES companies(companies_id) ON DELETE CASCADE,
    invited_email VARCHAR(255) NOT NULL,
    invited_by UUID NOT NULL REFERENCES users(users_id),
    invitation_token VARCHAR(100) UNIQUE NOT NULL,
    access_level VARCHAR(20) DEFAULT 'user',
    permissions JSONB,

    -- Status
    status VARCHAR(20) DEFAULT 'pending', -- pending, accepted, expired, cancelled
    expires_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP + INTERVAL '7 days',

    -- Tracking
    sent_count INTEGER DEFAULT 1,
    last_sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    accepted_at TIMESTAMP,
    accepted_by UUID REFERENCES users(users_id),

    -- Message
    personal_message TEXT,
    invitation_message TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- AUDIT TRAIL SYSTEM
-- ============================================================================

-- Master audit log for all table changes
DROP TABLE IF EXISTS audit_logs CASCADE;
CREATE TABLE audit_logs (
    audit_logs_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    table_name VARCHAR(100) NOT NULL,
    record_id UUID NOT NULL,
    companies_id UUID REFERENCES companies(companies_id),
    user_id UUID REFERENCES users(users_id),

    -- Action details
    action VARCHAR(20) NOT NULL, -- INSERT, UPDATE, DELETE
    action_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    session_id VARCHAR(100),

    -- Changes
    old_values JSONB,
    new_values JSONB,
    changed_fields JSONB,
    change_description TEXT,

    -- Context
    ip_address INET,
    user_agent TEXT,
    source_system VARCHAR(50) DEFAULT 'application',

    -- Metadata
    transaction_id VARCHAR(100),
    correlation_id VARCHAR(100),
    tags JSONB,

    -- Partitioning for performance
    PARTITION BY RANGE (action_timestamp)
);

-- Create partitions for audit logs
CREATE TABLE audit_logs_2024 PARTITION OF audit_logs
    FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');
CREATE TABLE audit_logs_2025 PARTITION OF audit_logs
    FOR VALUES FROM ('2025-01-01') TO ('2026-01-01');
CREATE TABLE audit_logs_future PARTITION OF audit_logs
    FOR VALUES FROM ('2026-01-01') TO (MAXVALUE);

-- Audit log for specific sensitive tables
DROP TABLE IF EXISTS sensitive_data_audit CASCADE;
CREATE TABLE sensitive_data_audit (
    sensitive_data_audit_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    table_name VARCHAR(100) NOT NULL,
    record_id UUID NOT NULL,
    companies_id UUID REFERENCES companies(companies_id),
    user_id UUID REFERENCES users(users_id),

    -- Action details
    action VARCHAR(20) NOT NULL,
    action_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    session_id VARCHAR(100),

    -- Sensitive data tracking
    sensitive_fields JSONB, -- Which fields contained sensitive data
    data_classification VARCHAR(20), -- public, internal, confidential, restricted
    encryption_status VARCHAR(20), -- encrypted, decrypted, masked

    -- Compliance
    gdpr_purpose VARCHAR(100),
    retention_period_days INTEGER,
    data_subject_id UUID, -- If related to a specific person

    -- Security
    risk_level VARCHAR(20) DEFAULT 'low',
    security_flags JSONB,

    -- Audit
    ip_address INET,
    user_agent TEXT,
    access_pattern VARCHAR(50), -- read, write, export, etc.

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Users table with advanced features
DROP TABLE IF EXISTS users CASCADE; CREATE TABLE users (
    users_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    companies_id UUID REFERENCES companies(companies_id), -- Consistent FK naming
    username VARCHAR(100) UNIQUE,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(20),
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    middle_name VARCHAR(100),

    -- Authentication
    password_hash VARCHAR(255),
    password_salt VARCHAR(100),
    password_changed_at TIMESTAMP,
    two_factor_enabled BOOLEAN DEFAULT false,
    two_factor_secret VARCHAR(100),

    -- OAuth and external auth
    keycloak_id VARCHAR(100),
    openid_subject VARCHAR(255),
    ad_username VARCHAR(100),
    oauth_google_id VARCHAR(255),
    oauth_microsoft_id VARCHAR(255),

    -- Serbian-specific fields
    jmbg VARCHAR(13), -- Unique citizen number
    citizenship VARCHAR(50) DEFAULT 'Serbia',
    birth_date DATE,
    birth_place VARCHAR(100),

    -- Employment details
    employee_number VARCHAR(20),
    department VARCHAR(100),
    job_title VARCHAR(100),
    job_title_sr VARCHAR(100),
    manager_id UUID REFERENCES users(users_id),
    employment_date DATE,
    contract_type VARCHAR(50),

    -- Security and compliance
    security_clearance_level VARCHAR(20),
    data_access_level VARCHAR(20),
    gdpr_consent BOOLEAN DEFAULT false,
    terms_accepted BOOLEAN DEFAULT false,
    terms_accepted_at TIMESTAMP,

    -- Preferences
    language VARCHAR(5) DEFAULT 'sr-RS',
    timezone VARCHAR(50) DEFAULT 'Europe/Belgrade',
    theme VARCHAR(20) DEFAULT 'light',
    notification_preferences JSONB,
    trusted_devices JSONB,

    -- Status
    status VARCHAR(20) DEFAULT 'active',
    email_verified BOOLEAN DEFAULT false,
    phone_verified BOOLEAN DEFAULT false,
    is_admin BOOLEAN DEFAULT false,
    is_active BOOLEAN DEFAULT true,
    last_login_at TIMESTAMP,
    last_active_at TIMESTAMP,

    -- AI and analytics
    embedding_vector VECTOR(1536),
    behavior_profile JSONB,
    risk_score DECIMAL(3,2),

    -- Multi-company support
    default_companies_id UUID REFERENCES companies(companies_id),

    -- Audit
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(users_id),
    updated_by UUID REFERENCES users(users_id),
    deactivated_at TIMESTAMP,
    deactivated_by UUID REFERENCES users(users_id),

    PARTITION BY RANGE (created_at)
);

-- User role assignments
DROP TABLE IF EXISTS user_role_assignments CASCADE; CREATE TABLE user_role_assignments (
    user_role_assignments_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    users_id UUID NOT NULL REFERENCES users(users_id) ON DELETE CASCADE,
    role_name VARCHAR(50) NOT NULL,
    assigned_by UUID REFERENCES users(users_id),
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    is_active BOOLEAN DEFAULT true,
    permissions JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(users_id, role_name, is_active)
);

-- ============================================================================
-- FINANCIAL AND ACCOUNTING SYSTEM (SRPS COMPLIANT)
-- ============================================================================

-- Account types (Serbian chart of accounts)
DROP TABLE IF EXISTS account_types CASCADE;
CREATE TABLE account_types (
    account_types_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    type_code VARCHAR(10) NOT NULL UNIQUE,
    type_name VARCHAR(100) NOT NULL,
    type_name_sr VARCHAR(100),
    description TEXT,
    category VARCHAR(30), -- asset, liability, equity, income, expense
    srps_category VARCHAR(50), -- SRPS standard category
    is_system_account BOOLEAN DEFAULT false,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Chart of accounts
DROP TABLE IF EXISTS chart_of_accounts CASCADE;
CREATE TABLE chart_of_accounts (
    chart_of_accounts_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    companies_id UUID NOT NULL REFERENCES companies(companies_id), -- Consistent FK naming
    account_code VARCHAR(20) NOT NULL,
    account_name VARCHAR(255) NOT NULL,
    account_name_sr VARCHAR(255),
    account_types_id UUID REFERENCES account_types(account_types_id), -- Consistent FK naming
    parent_account_id UUID REFERENCES chart_of_accounts(chart_of_accounts_id),
    currencies_id UUID REFERENCES currencies(currencies_id), -- Consistent FK naming

    -- SRPS compliance
    srps_code VARCHAR(20),
    account_level INTEGER DEFAULT 1,
    is_analytical BOOLEAN DEFAULT false,
    is_synthetic BOOLEAN DEFAULT true,

    -- Financial properties
    opening_balance DECIMAL(15,2) DEFAULT 0,
    current_balance DECIMAL(15,2) DEFAULT 0,
    debit_balance DECIMAL(15,2) DEFAULT 0,
    credit_balance DECIMAL(15,2) DEFAULT 0,
    last_movement_date DATE,

    -- Control
    is_active BOOLEAN DEFAULT true,
    is_system_account BOOLEAN DEFAULT false,
    requires_approval BOOLEAN DEFAULT false,
    approval_level INTEGER DEFAULT 1,

    -- Metadata
    description TEXT,
    notes TEXT,
    tags JSONB,
    embedding_vector VECTOR(1536),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(users_id),
    updated_by UUID REFERENCES users(users_id),

    UNIQUE(companies_id, account_code),
    PARTITION BY HASH (companies_id)
);

-- Fiscal years
DROP TABLE IF EXISTS fiscal_years CASCADE;
CREATE TABLE fiscal_years (
    fiscal_years_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    companies_id UUID NOT NULL REFERENCES companies(companies_id), -- Consistent FK naming
    year INTEGER NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    status VARCHAR(20) DEFAULT 'open', -- open, closed, locked
    is_current BOOLEAN DEFAULT false,

    -- Serbian compliance
    tax_return_filed BOOLEAN DEFAULT false,
    statutory_audit_required BOOLEAN DEFAULT false,
    audit_completed BOOLEAN DEFAULT false,

    -- Financial summary
    opening_assets DECIMAL(15,2) DEFAULT 0,
    closing_assets DECIMAL(15,2) DEFAULT 0,
    net_profit DECIMAL(15,2) DEFAULT 0,
    tax_liability DECIMAL(15,2) DEFAULT 0,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(users_id),
    updated_by UUID REFERENCES users(users_id),

    UNIQUE(companies_id, year),
    CHECK (end_date > start_date)
);

-- General Ledger with time-series optimization
DROP TABLE IF EXISTS general_ledger CASCADE;
CREATE TABLE general_ledger (
    general_ledger_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    companies_id UUID NOT NULL REFERENCES companies(companies_id), -- Consistent FK naming
    fiscal_years_id UUID REFERENCES fiscal_years(fiscal_years_id), -- Consistent FK naming
    transaction_date DATE NOT NULL,
    document_date DATE,
    posting_date DATE DEFAULT CURRENT_DATE,

    -- Account information
    chart_of_accounts_id UUID NOT NULL REFERENCES chart_of_accounts(chart_of_accounts_id), -- Consistent FK naming
    contra_account_id UUID REFERENCES chart_of_accounts(chart_of_accounts_id),

    -- Transaction details
    document_type VARCHAR(50) NOT NULL, -- invoice, payment, journal, adjustment
    document_id UUID NOT NULL,
    document_number VARCHAR(50),
    description TEXT,
    reference_number VARCHAR(100),

    -- Amounts (double-entry bookkeeping)
    debit_amount DECIMAL(15,2) DEFAULT 0,
    credit_amount DECIMAL(15,2) DEFAULT 0,
    amount DECIMAL(15,2) NOT NULL, -- Absolute amount
    currencies_id UUID REFERENCES currencies(currencies_id), -- Consistent FK naming
    exchange_rate DECIMAL(10,4) DEFAULT 1.0000,

    -- Serbian PDV
    is_pdv_applicable BOOLEAN DEFAULT false,
    pdv_rate DECIMAL(5,2),
    pdv_amount DECIMAL(15,2) DEFAULT 0,
    pdv_account_id UUID REFERENCES chart_of_accounts(chart_of_accounts_id),

    -- Status and workflow
    status VARCHAR(20) DEFAULT 'draft', -- draft, posted, reversed
    is_posted BOOLEAN DEFAULT false,
    posted_at TIMESTAMP,
    posted_by UUID REFERENCES users(users_id),
    is_reversed BOOLEAN DEFAULT false,
    reversed_at TIMESTAMP,
    reversed_by UUID REFERENCES users(users_id),
    reversal_reason TEXT,

    -- Audit and compliance
    source_system VARCHAR(50),
    cost_center VARCHAR(50),
    profit_center VARCHAR(50),
    segment VARCHAR(50),
    project_id VARCHAR(50),

    -- Approval workflow
    requires_approval BOOLEAN DEFAULT false,
    approval_status VARCHAR(20) DEFAULT 'approved', -- pending, approved, rejected
    approved_by UUID REFERENCES users(users_id),
    approved_at TIMESTAMP,
    rejection_reason TEXT,

    -- AI and analytics
    confidence_score DECIMAL(3,2),
    anomaly_score DECIMAL(3,2),
    risk_category VARCHAR(20),
    embedding_vector VECTOR(1536),
    tags JSONB,
    metadata JSONB,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(users_id),
    updated_by UUID REFERENCES users(users_id),

    PARTITION BY RANGE (transaction_date)
);

-- Create monthly partitions for the last 10 years
CREATE TABLE general_ledger_2024 PARTITION OF general_ledger
    FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');
CREATE TABLE general_ledger_2025 PARTITION OF general_ledger
    FOR VALUES FROM ('2025-01-01') TO ('2026-01-01');
CREATE TABLE general_ledger_future PARTITION OF general_ledger
    FOR VALUES FROM ('2026-01-01') TO (MAXVALUE);

-- ============================================================================
-- ACCOUNTS RECEIVABLE & PAYABLE
-- ============================================================================

-- Customers
DROP TABLE IF EXISTS customers CASCADE;
CREATE TABLE customers (
    customers_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    companies_id UUID NOT NULL REFERENCES companies(companies_id), -- Consistent FK naming
    company_name VARCHAR(255) NOT NULL,
    legal_name VARCHAR(255),
    tax_id VARCHAR(20), -- PIB
    registration_number VARCHAR(20), -- Matični broj

    -- Contact information
    contact_person VARCHAR(100),
    email VARCHAR(255),
    phone VARCHAR(20),
    address_line1 VARCHAR(255),
    address_line2 VARCHAR(255),
    city VARCHAR(100),
    postal_code VARCHAR(10),
    country VARCHAR(50) DEFAULT 'Serbia',

    -- Financial details
    credit_limit DECIMAL(15,2) DEFAULT 0,
    payment_terms VARCHAR(100) DEFAULT 'Net 30',
    payment_terms_days INTEGER DEFAULT 30,
    currencies_id UUID REFERENCES currencies(currencies_id), -- Consistent FK naming
    preferred_payment_method VARCHAR(50),

    -- Serbian business details
    business_entity_types_id UUID REFERENCES business_entity_types(business_entity_types_id), -- Consistent FK naming
    business_areas_id UUID REFERENCES business_areas(business_areas_id), -- Consistent FK naming
    is_pdv_registered BOOLEAN DEFAULT false,
    pdv_number VARCHAR(20),

    -- Relationship management
    customer_type VARCHAR(50) DEFAULT 'business', -- individual, business, government
    customer_segment VARCHAR(50),
    customer_status VARCHAR(20) DEFAULT 'active', -- active, inactive, suspended
    customer_rating INTEGER DEFAULT 5, -- 1-10 rating

    -- Financial summary
    total_invoiced DECIMAL(15,2) DEFAULT 0,
    total_paid DECIMAL(15,2) DEFAULT 0,
    total_outstanding DECIMAL(15,2) DEFAULT 0,
    last_invoice_date DATE,
    last_payment_date DATE,
    average_payment_days INTEGER,

    -- Risk assessment
    risk_rating VARCHAR(20) DEFAULT 'low',
    credit_score INTEGER,
    payment_reliability_score DECIMAL(3,2),

    -- AI and similarity search
    business_description TEXT,
    market_position VARCHAR(50),
    competitor_analysis JSONB,
    embedding_vector VECTOR(1536),

    -- Metadata
    notes TEXT,
    tags JSONB,
    custom_fields JSONB,

    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(users_id),
    updated_by UUID REFERENCES users(users_id),

    UNIQUE(companies_id, tax_id),
    PARTITION BY HASH (companies_id)
);

-- Suppliers/Vendors
DROP TABLE IF EXISTS suppliers CASCADE;
CREATE TABLE suppliers (
    suppliers_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    companies_id UUID NOT NULL REFERENCES companies(companies_id), -- Consistent FK naming
    supplier_name VARCHAR(255) NOT NULL,
    legal_name VARCHAR(255),
    tax_id VARCHAR(20),
    registration_number VARCHAR(20),

    -- Contact information
    contact_person VARCHAR(100),
    email VARCHAR(255),
    phone VARCHAR(20),
    address_line1 VARCHAR(255),
    address_line2 VARCHAR(255),
    city VARCHAR(100),
    postal_code VARCHAR(10),
    country VARCHAR(50) DEFAULT 'Serbia',

    -- Financial details
    credit_limit DECIMAL(15,2) DEFAULT 0,
    payment_terms VARCHAR(100) DEFAULT 'Net 30',
    payment_terms_days INTEGER DEFAULT 30,
    currencies_id UUID REFERENCES currencies(currencies_id), -- Consistent FK naming
    bank_account VARCHAR(30),
    bank_name VARCHAR(100),

    -- Serbian business details
    business_entity_types_id UUID REFERENCES business_entity_types(business_entity_types_id), -- Consistent FK naming
    business_areas_id UUID REFERENCES business_areas(business_areas_id), -- Consistent FK naming
    is_pdv_registered BOOLEAN DEFAULT false,
    pdv_number VARCHAR(20),

    -- Relationship management
    supplier_type VARCHAR(50) DEFAULT 'vendor',
    supplier_status VARCHAR(20) DEFAULT 'active',
    supplier_rating INTEGER DEFAULT 5,
    preferred_supplier BOOLEAN DEFAULT false,

    -- Financial summary
    total_purchased DECIMAL(15,2) DEFAULT 0,
    total_paid DECIMAL(15,2) DEFAULT 0,
    total_outstanding DECIMAL(15,2) DEFAULT 0,
    last_invoice_date DATE,
    last_payment_date DATE,

    -- Risk assessment
    risk_rating VARCHAR(20) DEFAULT 'low',
    quality_rating INTEGER,
    delivery_reliability_score DECIMAL(3,2),

    -- AI and similarity search
    business_description TEXT,
    supplier_category VARCHAR(50),
    product_categories JSONB,
    embedding_vector VECTOR(1536),

    -- Metadata
    notes TEXT,
    tags JSONB,
    custom_fields JSONB,

    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(users_id),
    updated_by UUID REFERENCES users(users_id),

    UNIQUE(companies_id, tax_id),
    PARTITION BY HASH (companies_id)
);

-- Invoice series for Serbian compliance
DROP TABLE IF EXISTS invoice_series CASCADE;
CREATE TABLE invoice_series (
    invoice_series_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    companies_id UUID NOT NULL REFERENCES companies(companies_id), -- Consistent FK naming
    series_name VARCHAR(20) NOT NULL,
    series_description TEXT,
    series_type VARCHAR(20) DEFAULT 'sales', -- sales, purchase, credit_note, debit_note

    -- Numbering
    prefix VARCHAR(10) DEFAULT 'INV',
    suffix VARCHAR(10),
    current_number INTEGER DEFAULT 1,
    number_format VARCHAR(50) DEFAULT '{prefix}-{number}-{year}',

    -- PDV settings
    is_pdv_applicable BOOLEAN DEFAULT true,
    pdv_rate DECIMAL(5,2) DEFAULT 20.00,
    chart_of_accounts_id UUID REFERENCES chart_of_accounts(chart_of_accounts_id), -- Consistent FK naming

    -- E-invoice settings
    is_e_invoice_enabled BOOLEAN DEFAULT false,
    e_invoice_format VARCHAR(20), -- peppol, cxml, etc.

    -- Control
    is_active BOOLEAN DEFAULT true,
    requires_approval BOOLEAN DEFAULT false,
    approval_level INTEGER DEFAULT 1,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(users_id),
    updated_by UUID REFERENCES users(users_id),

    UNIQUE(companies_id, series_name)
);

-- Invoices with comprehensive Serbian compliance
DROP TABLE IF EXISTS invoices CASCADE;
CREATE TABLE invoices (
    invoices_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    companies_id UUID NOT NULL REFERENCES companies(companies_id), -- Consistent FK naming
    invoice_series_id UUID REFERENCES invoice_series(invoice_series_id),
    invoice_number VARCHAR(50) NOT NULL,
    invoice_type VARCHAR(20) DEFAULT 'sales', -- sales, purchase, credit_note, debit_note

    -- Dates
    invoice_date DATE NOT NULL,
    due_date DATE,
    payment_date DATE,
    document_date DATE,

    -- Parties
    customers_id UUID REFERENCES customers(customers_id), -- Consistent FK naming
    suppliers_id UUID REFERENCES suppliers(suppliers_id), -- Consistent FK naming
    customer_name VARCHAR(255),
    customer_tax_id VARCHAR(20),
    customer_address TEXT,
    customer_email VARCHAR(255),

    -- Financial details
    currencies_id UUID REFERENCES currencies(currencies_id), -- Consistent FK naming
    exchange_rate DECIMAL(10,4) DEFAULT 1.0000,

    -- Serbian PDV calculation
    subtotal DECIMAL(15,2) NOT NULL DEFAULT 0,
    discount_amount DECIMAL(15,2) DEFAULT 0,
    discount_percentage DECIMAL(5,2) DEFAULT 0,
    pdv_base DECIMAL(15,2) DEFAULT 0,
    pdv_rate DECIMAL(5,2) DEFAULT 20.00,
    pdv_amount DECIMAL(15,2) DEFAULT 0,
    total_amount DECIMAL(15,2) NOT NULL,

    -- Status and workflow
    status VARCHAR(20) DEFAULT 'draft', -- draft, issued, sent, paid, overdue, cancelled
    payment_status VARCHAR(20) DEFAULT 'unpaid', -- unpaid, partial, paid, overdue
    payment_terms VARCHAR(100),
    payment_method VARCHAR(50),

    -- E-invoice compliance
    is_e_invoice BOOLEAN DEFAULT false,
    e_invoice_id VARCHAR(100),
    e_invoice_status VARCHAR(20),
    e_invoice_qr_code TEXT,
    peppol_id VARCHAR(100),

    -- References
    order_number VARCHAR(50),
    delivery_note VARCHAR(50),
    contract_number VARCHAR(50),
    project_id VARCHAR(50),

    -- Accounting integration
    revenue_account_id UUID REFERENCES chart_of_accounts(chart_of_accounts_id),
    pdv_account_id UUID REFERENCES chart_of_accounts(chart_of_accounts_id),
    customer_account_id UUID REFERENCES chart_of_accounts(chart_of_accounts_id),

    -- Notes and attachments
    notes TEXT,
    internal_notes TEXT,
    terms_and_conditions TEXT,
    footer_text TEXT,

    -- AI and analytics
    confidence_score DECIMAL(3,2),
    risk_score DECIMAL(3,2),
    embedding_vector VECTOR(1536),
    tags JSONB,
    custom_fields JSONB,

    -- Audit
    is_posted BOOLEAN DEFAULT false,
    posted_at TIMESTAMP,
    posted_by UUID REFERENCES users(users_id),
    is_cancelled BOOLEAN DEFAULT false,
    cancelled_at TIMESTAMP,
    cancelled_by UUID REFERENCES users(users_id),
    cancellation_reason TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(users_id),
    updated_by UUID REFERENCES users(users_id),

    UNIQUE(companies_id, invoice_number),
    PARTITION BY RANGE (invoice_date)
);

-- Invoice line items
DROP TABLE IF EXISTS invoice_items CASCADE;
CREATE TABLE invoice_items (
    invoice_items_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    invoices_id UUID NOT NULL REFERENCES invoices(invoices_id) ON DELETE CASCADE, -- Consistent FK naming
    line_number INTEGER NOT NULL,

    -- Product/Service details
    products_id UUID, -- Consistent FK naming
    product_name VARCHAR(255) NOT NULL,
    product_code VARCHAR(50),
    description TEXT,
    product_type VARCHAR(20) DEFAULT 'product', -- product, service

    -- Quantity and pricing
    quantity DECIMAL(12,4) NOT NULL,
    unit VARCHAR(20) DEFAULT 'kom',
    unit_price DECIMAL(12,4) NOT NULL,
    discount_percentage DECIMAL(5,2) DEFAULT 0,
    discount_amount DECIMAL(12,4) DEFAULT 0,

    -- Serbian PDV
    pdv_rate DECIMAL(5,2) DEFAULT 20.00,
    pdv_amount DECIMAL(12,4) DEFAULT 0,
    line_total DECIMAL(12,4) NOT NULL,

    -- Accounting
    revenue_account_id UUID REFERENCES chart_of_accounts(chart_of_accounts_id),
    cost_account_id UUID REFERENCES chart_of_accounts(chart_of_accounts_id),

    -- Additional data
    notes TEXT,
    custom_fields JSONB,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(invoices_id, line_number)
);

-- Payment methods
DROP TABLE IF EXISTS payment_methods CASCADE;
CREATE TABLE payment_methods (
    payment_methods_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    method_code VARCHAR(20) NOT NULL UNIQUE,
    method_name VARCHAR(100) NOT NULL,
    method_name_sr VARCHAR(100),
    description TEXT,

    -- Configuration
    is_active BOOLEAN DEFAULT true,
    requires_bank_details BOOLEAN DEFAULT false,
    requires_reference_number BOOLEAN DEFAULT false,
    processing_fee_percentage DECIMAL(5,2) DEFAULT 0,
    processing_fee_fixed DECIMAL(8,2) DEFAULT 0,

    -- Serbian compliance
    is_e_payment BOOLEAN DEFAULT false,
    bank_integration_required BOOLEAN DEFAULT false,
    qr_code_supported BOOLEAN DEFAULT false,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Payments
DROP TABLE IF EXISTS payments CASCADE;
CREATE TABLE payments (
    payments_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    companies_id UUID NOT NULL REFERENCES companies(companies_id), -- Consistent FK naming
    payment_number VARCHAR(50) NOT NULL,

    -- Invoice relationship
    invoices_id UUID REFERENCES invoices(invoices_id), -- Consistent FK naming
    invoice_number VARCHAR(50),

    -- Parties
    customers_id UUID REFERENCES customers(customers_id), -- Consistent FK naming
    suppliers_id UUID REFERENCES suppliers(suppliers_id), -- Consistent FK naming

    -- Payment details
    payment_date DATE NOT NULL,
    payment_methods_id UUID REFERENCES payment_methods(payment_methods_id), -- Consistent FK naming
    payment_method VARCHAR(50),
    amount DECIMAL(15,2) NOT NULL,
    currencies_id UUID REFERENCES currencies(currencies_id), -- Consistent FK naming
    exchange_rate DECIMAL(10,4) DEFAULT 1.0000,

    -- Bank details
    bank_account_from VARCHAR(30),
    bank_account_to VARCHAR(30),
    bank_name VARCHAR(100),
    bank_reference VARCHAR(100),
    transaction_id VARCHAR(100),

    -- Status and processing
    status VARCHAR(20) DEFAULT 'completed', -- pending, processing, completed, failed, cancelled
    processing_date TIMESTAMP,
    confirmation_date TIMESTAMP,

    -- Accounting integration
    bank_account_id UUID REFERENCES chart_of_accounts(chart_of_accounts_id),
    cash_account_id UUID REFERENCES chart_of_accounts(chart_of_accounts_id),
    customer_account_id UUID REFERENCES chart_of_accounts(chart_of_accounts_id),

    -- Notes and references
    description TEXT,
    reference_number VARCHAR(100),
    notes TEXT,
    attachment_url VARCHAR(500),

    -- Audit
    is_reconciled BOOLEAN DEFAULT false,
    reconciled_at TIMESTAMP,
    reconciled_by UUID REFERENCES users(users_id),
    reconciliation_reference VARCHAR(100),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(users_id),
    updated_by UUID REFERENCES users(users_id),

    UNIQUE(companies_id, payment_number),
    PARTITION BY RANGE (payment_date)
);

-- ============================================================================
-- INVENTORY MANAGEMENT SYSTEM
-- ============================================================================

-- Product categories
CREATE TABLE product_categories (
    product_categories_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID NOT NULL REFERENCES companies(companies_id),
    category_code VARCHAR(20) NOT NULL,
    category_name VARCHAR(100) NOT NULL,
    category_name_sr VARCHAR(100),
    parent_category_id UUID REFERENCES product_categories(product_categories_id),
    description TEXT,

    -- PDV settings
    pdv_rate DECIMAL(5,2) DEFAULT 20.00,
    is_pdv_exempt BOOLEAN DEFAULT false,

    -- Control
    is_active BOOLEAN DEFAULT true,
    display_order INTEGER DEFAULT 0,

    -- Metadata
    tags JSONB,
    embedding_vector VECTOR(1536),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(users_id),
    updated_by UUID REFERENCES users(users_id),

    UNIQUE(company_id, category_code)
);

-- Products and services
CREATE TABLE products (
    products_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID NOT NULL REFERENCES companies(companies_id),
    product_code VARCHAR(50) NOT NULL,
    product_name VARCHAR(255) NOT NULL,
    product_name_sr VARCHAR(255),
    product_type VARCHAR(20) DEFAULT 'product', -- product, service, bundle

    -- Categorization
    category_id UUID REFERENCES product_categories(product_categories_id),
    subcategory_id UUID REFERENCES product_categories(product_categories_id),

    -- Description and details
    description TEXT,
    description_sr TEXT,
    specifications JSONB,
    unit VARCHAR(20) DEFAULT 'kom',
    barcode VARCHAR(50),
    sku VARCHAR(50),

    -- Pricing
    currency_id UUID REFERENCES currencies(currencies_id),
    unit_price DECIMAL(12,4) NOT NULL,
    cost_price DECIMAL(12,4),
    wholesale_price DECIMAL(12,4),
    retail_price DECIMAL(12,4),

    -- PDV settings
    pdv_rate DECIMAL(5,2) DEFAULT 20.00,
    is_pdv_exempt BOOLEAN DEFAULT false,
    pdv_account_id UUID REFERENCES chart_of_accounts(chart_of_accounts_id),

    -- Inventory management
    is_inventory_tracked BOOLEAN DEFAULT true,
    current_stock DECIMAL(12,4) DEFAULT 0,
    reserved_stock DECIMAL(12,4) DEFAULT 0,
    available_stock DECIMAL(12,4) DEFAULT 0,
    minimum_stock DECIMAL(12,4) DEFAULT 0,
    maximum_stock DECIMAL(12,4),
    reorder_point DECIMAL(12,4),

    -- Sales settings
    is_active BOOLEAN DEFAULT true,
    is_for_sale BOOLEAN DEFAULT true,
    is_for_purchase BOOLEAN DEFAULT true,
    can_be_sold BOOLEAN DEFAULT true,
    can_be_purchased BOOLEAN DEFAULT true,

    -- Accounting integration
    revenue_account_id UUID REFERENCES chart_of_accounts(chart_of_accounts_id),
    cost_account_id UUID REFERENCES chart_of_accounts(chart_of_accounts_id),
    inventory_account_id UUID REFERENCES chart_of_accounts(chart_of_accounts_id),

    -- Images and attachments
    main_image_url VARCHAR(500),
    additional_images JSONB,
    attachments JSONB,

    -- AI and analytics
    embedding_vector VECTOR(1536),
    popularity_score DECIMAL(5,2),
    tags JSONB,
    custom_fields JSONB,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(users_id),
    updated_by UUID REFERENCES users(users_id),

    UNIQUE(company_id, product_code),
    PARTITION BY HASH (company_id)
);

-- Warehouses/Locations
CREATE TABLE warehouses (
    warehouses_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID NOT NULL REFERENCES companies(companies_id),
    warehouse_code VARCHAR(20) NOT NULL,
    warehouse_name VARCHAR(100) NOT NULL,
    warehouse_type VARCHAR(20) DEFAULT 'warehouse', -- warehouse, store, showroom

    -- Location details
    address_line1 VARCHAR(255),
    address_line2 VARCHAR(255),
    city VARCHAR(100),
    postal_code VARCHAR(10),
    country VARCHAR(50) DEFAULT 'Serbia',
    latitude DECIMAL(10,8),
    longitude DECIMAL(11,8),

    -- Contact
    contact_person VARCHAR(100),
    phone VARCHAR(20),
    email VARCHAR(255),

    -- Settings
    is_active BOOLEAN DEFAULT true,
    is_default BOOLEAN DEFAULT false,
    allows_negative_stock BOOLEAN DEFAULT false,

    -- Metadata
    description TEXT,
    operating_hours JSONB,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(users_id),
    updated_by UUID REFERENCES users(users_id),

    UNIQUE(company_id, warehouse_code)
);

-- Inventory transactions
CREATE TABLE inventory_transactions (
    inventory_transactions_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID NOT NULL REFERENCES companies(companies_id),
    warehouse_id UUID NOT NULL REFERENCES warehouses(warehouses_id),
    product_id UUID NOT NULL REFERENCES products(products_id),

    -- Transaction details
    transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    transaction_type VARCHAR(30) NOT NULL, -- purchase, sale, adjustment, transfer, return
    document_type VARCHAR(30), -- invoice, delivery_note, adjustment, transfer
    document_id UUID,
    document_number VARCHAR(50),

    -- Quantities
    quantity DECIMAL(12,4) NOT NULL,
    unit_cost DECIMAL(12,4),
    total_cost DECIMAL(12,4),

    -- Stock levels
    stock_before DECIMAL(12,4) NOT NULL,
    stock_after DECIMAL(12,4) NOT NULL,

    -- Additional data
    reference_number VARCHAR(50),
    notes TEXT,
    custom_fields JSONB,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(users_id),

    PARTITION BY RANGE (transaction_date)
);

-- ============================================================================
-- AI AND LLM INTEGRATION SYSTEM
-- ============================================================================

-- AI Models Registry
CREATE TABLE ai_models (
    ai_models_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID REFERENCES companies(companies_id),
    model_name VARCHAR(100) NOT NULL,
    model_type VARCHAR(50) NOT NULL, -- llm, embedding, classification, generation
    provider VARCHAR(50) NOT NULL, -- openai, huggingface, local, custom

    -- Model details
    model_version VARCHAR(20),
    model_size VARCHAR(20), -- 7b, 13b, 70b, etc.
    model_format VARCHAR(20), -- gguf, safetensors, pytorch
    quantization VARCHAR(20), -- f16, q4, q8, etc.

    -- Configuration
    api_endpoint VARCHAR(500),
    api_key_required BOOLEAN DEFAULT true,
    max_tokens INTEGER,
    temperature DECIMAL(3,2) DEFAULT 0.7,
    top_p DECIMAL(3,2) DEFAULT 0.9,
    context_window INTEGER DEFAULT 4096,

    -- Status and performance
    is_downloaded BOOLEAN DEFAULT false,
    is_loaded BOOLEAN DEFAULT false,
    download_url VARCHAR(500),
    local_path VARCHAR(500),
    memory_required_gb DECIMAL(6,2),
    download_size_gb DECIMAL(6,2),

    -- Performance metrics
    average_response_time_ms INTEGER,
    tokens_per_second INTEGER,
    last_used_at TIMESTAMP,
    usage_count INTEGER DEFAULT 0,

    -- Cost management
    cost_per_token DECIMAL(8,6),
    monthly_cost_limit DECIMAL(10,2),
    current_monthly_cost DECIMAL(10,2) DEFAULT 0,

    -- Security and access
    access_level VARCHAR(20) DEFAULT 'company', -- public, company, private
    allowed_users JSONB,
    security_requirements JSONB,

    -- Metadata
    description TEXT,
    capabilities JSONB,
    limitations JSONB,
    tags JSONB,
    embedding_vector VECTOR(1536),

    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(users_id),
    updated_by UUID REFERENCES users(users_id),

    UNIQUE(company_id, model_name, model_version)
);

-- AI Insights and Analytics
CREATE TABLE ai_insights (
    ai_insights_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID REFERENCES companies(companies_id),
    insight_type VARCHAR(50) NOT NULL, -- prediction, anomaly, recommendation, summary
    insight_category VARCHAR(50), -- financial, operational, customer, inventory

    -- Content
    title VARCHAR(255) NOT NULL,
    description TEXT,
    insight_data JSONB,
    confidence_score DECIMAL(3,2), -- 0.0 to 1.0

    -- Related entities
    related_user_id UUID REFERENCES users(users_id),
    related_customer_id UUID REFERENCES customers(customers_id),
    related_supplier_id UUID REFERENCES suppliers(suppliers_id),
    related_product_id UUID REFERENCES products(products_id),
    related_invoice_id UUID REFERENCES invoices(invoices_id),
    related_transaction_id UUID REFERENCES general_ledger(general_ledger_id),

    -- AI model information
    ai_model_id UUID REFERENCES ai_models(ai_models_id),
    model_version VARCHAR(20),
    prompt_used TEXT,
    tokens_used INTEGER,

    -- Impact and priority
    impact_level VARCHAR(20), -- low, medium, high, critical
    priority_score DECIMAL(3,2),
    action_required BOOLEAN DEFAULT false,
    recommended_action TEXT,

    -- Status and lifecycle
    status VARCHAR(20) DEFAULT 'active', -- draft, active, reviewed, archived, dismissed
    is_archived BOOLEAN DEFAULT false,
    archived_at TIMESTAMP,
    archived_by UUID REFERENCES users(users_id),

    -- Review and validation
    reviewed_by UUID REFERENCES users(users_id),
    reviewed_at TIMESTAMP,
    review_notes TEXT,
    is_validated BOOLEAN DEFAULT false,

    -- Analytics
    view_count INTEGER DEFAULT 0,
    last_viewed_at TIMESTAMP,
    embedding_vector VECTOR(1536),
    tags JSONB,
    metadata JSONB,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(users_id),
    updated_by UUID REFERENCES users(users_id),

    PARTITION BY RANGE (created_at)
);

-- AI Training Data
CREATE TABLE ai_training_data (
    ai_training_data_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID REFERENCES companies(companies_id),
    data_type VARCHAR(50) NOT NULL, -- text, conversation, document, transaction
    data_category VARCHAR(50), -- financial, customer, operational, general

    -- Content
    content TEXT NOT NULL,
    content_summary TEXT,
    content_metadata JSONB,

    -- Source information
    source_system VARCHAR(50),
    source_table VARCHAR(50),
    source_record_id UUID,
    source_url VARCHAR(500),

    -- Quality and validation
    quality_score DECIMAL(3,2), -- 0.0 to 1.0
    is_labeled BOOLEAN DEFAULT false,
    labels JSONB,
    validation_status VARCHAR(20) DEFAULT 'pending', -- pending, validated, rejected
    validated_by UUID REFERENCES users(users_id),
    validated_at TIMESTAMP,

    -- Usage tracking
    usage_count INTEGER DEFAULT 0,
    last_used_at TIMESTAMP,
    training_sessions JSONB,

    -- Privacy and compliance
    contains_pii BOOLEAN DEFAULT false,
    data_retention_policy VARCHAR(50),
    anonymized_content TEXT,
    compliance_status VARCHAR(20) DEFAULT 'compliant',

    -- Analytics
    embedding_vector VECTOR(1536),
    similarity_hash VARCHAR(64),
    content_hash VARCHAR(64),
    tags JSONB,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(users_id),
    updated_by UUID REFERENCES users(users_id),

    PARTITION BY HASH (company_id)
);

-- Vector Embeddings for AI Search
CREATE TABLE vector_embeddings (
    vector_embeddings_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID REFERENCES companies(companies_id),
    entity_type VARCHAR(50) NOT NULL, -- user, customer, product, invoice, document, etc.
    entity_id UUID NOT NULL,
    embedding_model VARCHAR(50) NOT NULL,
    embedding_vector VECTOR(1536) NOT NULL,

    -- Content information
    content_type VARCHAR(50), -- title, description, content, summary
    content_hash VARCHAR(64),
    content_length INTEGER,

    -- Performance optimization
    similarity_threshold DECIMAL(3,2) DEFAULT 0.8,
    last_similarity_search TIMESTAMP,
    search_count INTEGER DEFAULT 0,

    -- Metadata
    tags JSONB,
    custom_metadata JSONB,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(entity_type, entity_id, embedding_model),
    PARTITION BY HASH (company_id)
);

-- ============================================================================
-- CHAT AND COMMUNICATION SYSTEM
-- ============================================================================

-- Chat Sessions
CREATE TABLE chat_sessions (
    chat_sessions_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID REFERENCES companies(companies_id),
    user_id UUID REFERENCES users(users_id),
    session_name VARCHAR(255),
    session_type VARCHAR(20) DEFAULT 'general', -- general, support, ai_assistant, team

    -- Participants
    participants JSONB,
    is_group_chat BOOLEAN DEFAULT false,
    max_participants INTEGER DEFAULT 2,

    -- Status and settings
    status VARCHAR(20) DEFAULT 'active', -- active, paused, closed, archived
    is_archived BOOLEAN DEFAULT false,
    archived_at TIMESTAMP,
    settings JSONB,

    -- AI integration
    ai_model_id UUID REFERENCES ai_models(ai_models_id),
    ai_enabled BOOLEAN DEFAULT true,
    ai_personality VARCHAR(50),
    ai_temperature DECIMAL(3,2) DEFAULT 0.7,

    -- Analytics
    message_count INTEGER DEFAULT 0,
    last_message_at TIMESTAMP,
    duration_minutes INTEGER,
    embedding_vector VECTOR(1536),

    -- Metadata
    tags JSONB,
    custom_fields JSONB,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(users_id),
    updated_by UUID REFERENCES users(users_id),

    PARTITION BY RANGE (created_at)
);

-- Chat Messages
CREATE TABLE chat_messages (
    chat_messages_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL REFERENCES chat_sessions(chat_sessions_id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(users_id),
    message_type VARCHAR(20) DEFAULT 'text', -- text, file, image, system, ai_response

    -- Content
    content TEXT,
    content_html TEXT,
    content_metadata JSONB,

    -- File attachments
    attachment_url VARCHAR(500),
    attachment_name VARCHAR(255),
    attachment_size INTEGER,
    attachment_type VARCHAR(50),

    -- AI processing
    ai_model_id UUID REFERENCES ai_models(ai_models_id),
    ai_processing_time_ms INTEGER,
    ai_confidence_score DECIMAL(3,2),
    ai_response_metadata JSONB,

    -- Message status
    is_edited BOOLEAN DEFAULT false,
    edited_at TIMESTAMP,
    is_deleted BOOLEAN DEFAULT false,
    deleted_at TIMESTAMP,
    deletion_reason TEXT,

    -- Threading and replies
    parent_message_id UUID REFERENCES chat_messages(chat_messages_id),
    thread_id UUID,
    reply_count INTEGER DEFAULT 0,

    -- Reactions and interactions
    reactions JSONB,
    mentions JSONB,
    links JSONB,

    -- Analytics
    read_by JSONB,
    read_count INTEGER DEFAULT 0,
    embedding_vector VECTOR(1536),

    -- Metadata
    message_order BIGINT DEFAULT EXTRACT(EPOCH FROM CURRENT_TIMESTAMP) * 1000,
    custom_fields JSONB,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    PARTITION BY HASH (session_id)
);

-- ============================================================================
-- SYSTEM AND MONITORING
-- ============================================================================

-- System Settings
CREATE TABLE system_settings (
    system_settings_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID REFERENCES companies(companies_id),
    setting_key VARCHAR(100) NOT NULL,
    setting_value TEXT,
    setting_type VARCHAR(20) DEFAULT 'string', -- string, number, boolean, json
    category VARCHAR(50),

    -- Configuration
    is_system_setting BOOLEAN DEFAULT false,
    is_user_customizable BOOLEAN DEFAULT true,
    requires_restart BOOLEAN DEFAULT false,
    validation_rules JSONB,

    -- Access control
    access_level VARCHAR(20) DEFAULT 'user', -- admin, manager, user
    allowed_roles JSONB,

    -- Description and help
    description TEXT,
    help_text TEXT,
    example_value TEXT,

    -- Audit
    is_encrypted BOOLEAN DEFAULT false,
    last_modified_by UUID REFERENCES users(users_id),
    last_modified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(company_id, setting_key)
);

-- Performance Metrics
CREATE TABLE performance_metrics (
    performance_metrics_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID REFERENCES companies(companies_id),
    metric_name VARCHAR(100) NOT NULL,
    metric_value DECIMAL(15,4) NOT NULL,
    unit VARCHAR(20),
    metric_type VARCHAR(30) DEFAULT 'system', -- system, business, ai, user

    -- Context
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    source_system VARCHAR(50) DEFAULT 'system',
    source_component VARCHAR(50),

    -- Dimensions
    dimensions JSONB, -- key-value pairs for filtering
    tags JSONB,

    -- Aggregation
    aggregation_type VARCHAR(20), -- gauge, counter, histogram, summary
    aggregation_window VARCHAR(20), -- 1m, 5m, 15m, 1h, 1d
    retention_days INTEGER DEFAULT 90,

    -- Metadata
    description TEXT,
    threshold_warning DECIMAL(15,4),
    threshold_critical DECIMAL(15,4),

    PARTITION BY RANGE (recorded_at)
);

-- Audit Log
CREATE TABLE audit_log (
    audit_log_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID REFERENCES companies(companies_id),
    user_id UUID REFERENCES users(users_id),
    action VARCHAR(50) NOT NULL,
    resource_type VARCHAR(50) NOT NULL,
    resource_id UUID,

    -- Action details
    action_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address INET,
    user_agent TEXT,
    session_id VARCHAR(100),

    -- Changes
    old_values JSONB,
    new_values JSONB,
    change_description TEXT,

    -- Context
    related_user_id UUID REFERENCES users(users_id),
    related_customer_id UUID REFERENCES customers(customers_id),
    related_invoice_id UUID REFERENCES invoices(invoices_id),

    -- Security
    risk_level VARCHAR(20) DEFAULT 'low',
    compliance_flags JSONB,

    -- Metadata
    tags JSONB,
    custom_fields JSONB,

    PARTITION BY RANGE (action_timestamp)
);

-- ============================================================================
-- CREATE INDEXES FOR PERFORMANCE
-- ============================================================================

-- User and authentication indexes
CREATE INDEX CONCURRENTLY idx_users_company_active ON users (company_id, is_active) WHERE is_active = true;
CREATE INDEX CONCURRENTLY idx_users_email ON users (email);
CREATE INDEX CONCURRENTLY idx_users_username ON users (username);
CREATE INDEX CONCURRENTLY idx_users_phone ON users (phone);
CREATE INDEX CONCURRENTLY idx_users_embedding ON users USING ivfflat (embedding_vector vector_cosine_ops) WITH (lists = 100);

-- Company indexes
CREATE INDEX CONCURRENTLY idx_companies_active ON companies (is_active) WHERE is_active = true;
CREATE INDEX CONCURRENTLY idx_companies_tax_id ON companies (tax_id);
CREATE INDEX CONCURRENTLY idx_companies_business_entity ON companies (business_entity_type_id);
CREATE INDEX CONCURRENTLY idx_companies_embedding ON companies USING ivfflat (embedding_vector vector_cosine_ops) WITH (lists = 100);

-- Financial indexes
CREATE INDEX CONCURRENTLY idx_chart_of_accounts_company ON chart_of_accounts (company_id, account_code);
CREATE INDEX CONCURRENTLY idx_chart_of_accounts_type ON chart_of_accounts (account_type);
CREATE INDEX CONCURRENTLY idx_general_ledger_company_date ON general_ledger (company_id, transaction_date);
CREATE INDEX CONCURRENTLY idx_general_ledger_account ON general_ledger (account_id);
CREATE INDEX CONCURRENTLY idx_general_ledger_status ON general_ledger (status) WHERE status = 'posted';
CREATE INDEX CONCURRENTLY idx_general_ledger_embedding ON general_ledger USING ivfflat (embedding_vector vector_cosine_ops) WITH (lists = 100);

-- Invoice indexes
CREATE INDEX CONCURRENTLY idx_invoices_company_date ON invoices (company_id, invoice_date);
CREATE INDEX CONCURRENTLY idx_invoices_customer ON invoices (customer_id);
CREATE INDEX CONCURRENTLY idx_invoices_supplier ON invoices (supplier_id);
CREATE INDEX CONCURRENTLY idx_invoices_status ON invoices (status);
CREATE INDEX CONCURRENTLY idx_invoices_due_date ON invoices (due_date) WHERE due_date > CURRENT_DATE;
CREATE INDEX CONCURRENTLY idx_invoices_embedding ON invoices USING ivfflat (embedding_vector vector_cosine_ops) WITH (lists = 100);

-- Product indexes
CREATE INDEX CONCURRENTLY idx_products_company ON products (company_id);
CREATE INDEX CONCURRENTLY idx_products_category ON products (category_id);
CREATE INDEX CONCURRENTLY idx_products_active ON products (is_active) WHERE is_active = true;
CREATE INDEX CONCURRENTLY idx_products_code ON products (product_code);
CREATE INDEX CONCURRENTLY idx_products_embedding ON products USING ivfflat (embedding_vector vector_cosine_ops) WITH (lists = 100);

-- Customer and supplier indexes
CREATE INDEX CONCURRENTLY idx_customers_company ON customers (company_id);
CREATE INDEX CONCURRENTLY idx_customers_tax_id ON customers (tax_id);
CREATE INDEX CONCURRENTLY idx_customers_status ON customers (customer_status) WHERE customer_status = 'active';
CREATE INDEX CONCURRENTLY idx_customers_embedding ON customers USING ivfflat (embedding_vector vector_cosine_ops) WITH (lists = 100);

CREATE INDEX CONCURRENTLY idx_suppliers_company ON suppliers (company_id);
CREATE INDEX CONCURRENTLY idx_suppliers_tax_id ON suppliers (tax_id);
CREATE INDEX CONCURRENTLY idx_suppliers_status ON suppliers (supplier_status) WHERE supplier_status = 'active';
CREATE INDEX CONCURRENTLY idx_suppliers_embedding ON suppliers USING ivfflat (embedding_vector vector_cosine_ops) WITH (lists = 100);

-- AI and LLM indexes
CREATE INDEX CONCURRENTLY idx_ai_models_company ON ai_models (company_id);
CREATE INDEX CONCURRENTLY idx_ai_models_type ON ai_models (model_type);
CREATE INDEX CONCURRENTLY idx_ai_models_active ON ai_models (is_active) WHERE is_active = true;
CREATE INDEX CONCURRENTLY idx_ai_insights_company_type ON ai_insights (company_id, insight_type);
CREATE INDEX CONCURRENTLY idx_ai_insights_date ON ai_insights (created_at);
CREATE INDEX CONCURRENTLY idx_ai_insights_embedding ON ai_insights USING ivfflat (embedding_vector vector_cosine_ops) WITH (lists = 100);
CREATE INDEX CONCURRENTLY idx_ai_training_data_company_type ON ai_training_data (company_id, data_type);
CREATE INDEX CONCURRENTLY idx_ai_training_data_embedding ON ai_training_data USING ivfflat (embedding_vector vector_cosine_ops) WITH (lists = 100);
CREATE INDEX CONCURRENTLY idx_vector_embeddings_entity ON vector_embeddings (entity_type, entity_id);
CREATE INDEX CONCURRENTLY idx_vector_embeddings_embedding ON vector_embeddings USING ivfflat (embedding_vector vector_cosine_ops) WITH (lists = 100);

-- Chat system indexes
CREATE INDEX CONCURRENTLY idx_chat_sessions_user ON chat_sessions (user_id);
CREATE INDEX CONCURRENTLY idx_chat_sessions_company ON chat_sessions (company_id);
CREATE INDEX CONCURRENTLY idx_chat_sessions_active ON chat_sessions (status) WHERE status = 'active';
CREATE INDEX CONCURRENTLY idx_chat_messages_session ON chat_messages (session_id);
CREATE INDEX CONCURRENTLY idx_chat_messages_user ON chat_messages (user_id);
CREATE INDEX CONCURRENTLY idx_chat_messages_embedding ON chat_messages USING ivfflat (embedding_vector vector_cosine_ops) WITH (lists = 100);

-- System indexes
CREATE INDEX CONCURRENTLY idx_performance_metrics_name ON performance_metrics (metric_name);
CREATE INDEX CONCURRENTLY idx_performance_metrics_timestamp ON performance_metrics (recorded_at DESC);
CREATE INDEX CONCURRENTLY idx_performance_metrics_type ON performance_metrics (metric_type);
CREATE INDEX CONCURRENTLY idx_audit_log_company_action ON audit_log (company_id, action);
CREATE INDEX CONCURRENTLY idx_audit_log_timestamp ON audit_log (action_timestamp DESC);
CREATE INDEX CONCURRENTLY idx_system_settings_key ON system_settings (setting_key);

-- Full-text search indexes
CREATE INDEX CONCURRENTLY idx_companies_fts ON companies USING GIN (to_tsvector('serbian', company_name || ' ' || COALESCE(description, '')));
CREATE INDEX CONCURRENTLY idx_companies_unicode_search ON companies USING GIN (create_multilingual_search_text(company_name || ' ' || COALESCE(description, '')));
CREATE INDEX CONCURRENTLY idx_companies_normalized_name ON companies (normalize_unicode_text(company_name));
CREATE INDEX CONCURRENTLY idx_users_fts ON users USING GIN (to_tsvector('serbian', first_name || ' ' || last_name || ' ' || COALESCE(bio, '')));
CREATE INDEX CONCURRENTLY idx_products_fts ON products USING GIN (to_tsvector('serbian', product_name || ' ' || COALESCE(description, '')));
CREATE INDEX CONCURRENTLY idx_invoices_fts ON invoices USING GIN (to_tsvector('serbian', invoice_number || ' ' || COALESCE(notes, '')));
CREATE INDEX CONCURRENTLY idx_customers_fts ON customers USING GIN (to_tsvector('serbian', company_name || ' ' || COALESCE(notes, '')));
CREATE INDEX CONCURRENTLY idx_ai_insights_fts ON ai_insights USING GIN (to_tsvector('english', title || ' ' || COALESCE(description, '')));

-- Time-series indexes for performance metrics
CREATE INDEX CONCURRENTLY idx_performance_metrics_recent ON performance_metrics (recorded_at DESC) WHERE recorded_at > NOW() - INTERVAL '30 days';
CREATE INDEX CONCURRENTLY idx_performance_metrics_hourly ON performance_metrics (date_trunc('hour', recorded_at), metric_name);
CREATE INDEX CONCURRENTLY idx_performance_metrics_daily ON performance_metrics (date_trunc('day', recorded_at), metric_name);

-- ============================================================================
-- AI AND SENTIMENT ANALYSIS SYSTEM
-- ============================================================================

-- Customer feedback and reviews
DROP TABLE IF EXISTS customer_feedback CASCADE; CREATE TABLE customer_feedback (
    customer_feedback_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    companies_id UUID NOT NULL REFERENCES companies(companies_id),
    customers_id UUID REFERENCES customers(customers_id),
    users_id UUID REFERENCES users(users_id), -- Who submitted the feedback
    feedback_type VARCHAR(20) DEFAULT 'review', -- review, complaint, suggestion, survey
    feedback_source VARCHAR(20) DEFAULT 'website', -- website, email, phone, social, survey

    -- Content
    title VARCHAR(255),
    content TEXT NOT NULL,
    content_language VARCHAR(5) DEFAULT 'sr-RS',
    content_hash VARCHAR(64), -- For duplicate detection

    -- Sentiment analysis
    sentiment_score DECIMAL(3,2), -- -1.0 to 1.0 (negative to positive)
    sentiment_label VARCHAR(20), -- positive, negative, neutral
    sentiment_confidence DECIMAL(3,2),
    emotion_detected JSONB, -- joy, anger, sadness, fear, surprise, disgust

    -- AI analysis
    topics_detected JSONB,
    keywords_extracted JSONB,
    urgency_level VARCHAR(20), -- low, medium, high, critical
    intent_detected VARCHAR(50), -- complaint, praise, question, suggestion
    entities_mentioned JSONB, -- products, services, people mentioned

    -- Response tracking
    response_required BOOLEAN DEFAULT false,
    response_status VARCHAR(20) DEFAULT 'pending', -- pending, in_progress, completed, closed
    response_priority VARCHAR(20) DEFAULT 'medium',
    assigned_to UUID REFERENCES users(users_id),
    responded_at TIMESTAMP,
    response_content TEXT,

    -- Customer satisfaction
    rating_given INTEGER CHECK (rating_given >= 1 AND rating_given <= 5),
    nps_score INTEGER CHECK (nps_score >= 0 AND nps_score <= 10),
    would_recommend BOOLEAN,

    -- Metadata
    embedding_vector VECTOR(1536), -- For semantic search and similarity
    tags JSONB,
    custom_fields JSONB,
    is_public BOOLEAN DEFAULT false,
    is_anonymous BOOLEAN DEFAULT false,

    -- AI processing status
    ai_processed BOOLEAN DEFAULT false,
    ai_processed_at TIMESTAMP,
    ai_model_used VARCHAR(100),
    ai_processing_duration_ms INTEGER,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(users_id),
    updated_by UUID REFERENCES users(users_id),

    PARTITION BY RANGE (created_at)
);

-- Create partitions for customer feedback
CREATE TABLE customer_feedback_2024 PARTITION OF customer_feedback
    FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');
CREATE TABLE customer_feedback_2025 PARTITION OF customer_feedback
    FOR VALUES FROM ('2025-01-01') TO ('2026-01-01');
CREATE TABLE customer_feedback_future PARTITION OF customer_feedback
    FOR VALUES FROM ('2026-01-01') TO (MAXVALUE);

-- AI Models registry with enhanced capabilities
DROP TABLE IF EXISTS ai_models CASCADE; CREATE TABLE ai_models (
    ai_models_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    companies_id UUID REFERENCES companies(companies_id),
    model_name VARCHAR(100) NOT NULL,
    model_type VARCHAR(50) NOT NULL, -- llm, embedding, sentiment, classification, generation, summarization
    provider VARCHAR(50) NOT NULL, -- openai, huggingface, local, custom, anthropic, cohere
    model_family VARCHAR(50), -- gpt, bert, llama, mistral, claude, etc.

    -- Model configuration
    model_version VARCHAR(20),
    model_size VARCHAR(20), -- 7b, 13b, 70b, 1.5b, etc.
    model_format VARCHAR(20), -- gguf, safetensors, pytorch, onnx
    quantization VARCHAR(20), -- f16, q4, q8, q4_k_m, etc.

    -- Technical specifications
    context_window INTEGER DEFAULT 4096,
    max_tokens INTEGER,
    temperature DECIMAL(3,2) DEFAULT 0.7,
    top_p DECIMAL(3,2) DEFAULT 0.9,
    top_k INTEGER,
    frequency_penalty DECIMAL(3,2),
    presence_penalty DECIMAL(3,2),

    -- API configuration
    api_endpoint VARCHAR(500),
    api_key_required BOOLEAN DEFAULT true,
    api_key_name VARCHAR(100),
    api_rate_limit INTEGER, -- requests per minute
    api_cost_per_token DECIMAL(8,6),

    -- Model capabilities
    supported_languages JSONB,
    supported_tasks JSONB, -- text-classification, sentiment-analysis, question-answering, etc.
    model_limitations TEXT,
    model_biases TEXT,

    -- Performance metrics
    average_response_time_ms INTEGER,
    tokens_per_second DECIMAL(6,2),
    memory_required_gb DECIMAL(6,2),
    download_size_gb DECIMAL(6,2),

    -- Status and deployment
    is_downloaded BOOLEAN DEFAULT false,
    is_loaded BOOLEAN DEFAULT false,
    is_active BOOLEAN DEFAULT true,
    deployment_status VARCHAR(20) DEFAULT 'available', -- available, training, error, maintenance
    last_used_at TIMESTAMP,
    usage_count INTEGER DEFAULT 0,

    -- Cost management
    cost_per_request DECIMAL(6,4),
    monthly_cost_limit DECIMAL(10,2),
    current_monthly_cost DECIMAL(10,2) DEFAULT 0,

    -- Security and compliance
    data_privacy_level VARCHAR(20) DEFAULT 'standard', -- public, confidential, restricted
    gdpr_compliant BOOLEAN DEFAULT true,
    data_retention_days INTEGER DEFAULT 365,

    -- AI model metadata
    training_data_info JSONB,
    evaluation_metrics JSONB,
    benchmark_scores JSONB,
    embedding_dimensions INTEGER DEFAULT 1536,

    -- Integration
    integration_config JSONB, -- Webhooks, API keys, etc.
    custom_parameters JSONB,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(users_id),
    updated_by UUID REFERENCES users(users_id)
);

-- AI Processing queue for async operations
DROP TABLE IF EXISTS ai_processing_queue CASCADE; CREATE TABLE ai_processing_queue (
    ai_processing_queue_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    companies_id UUID REFERENCES companies(companies_id),

    -- What to process
    entity_type VARCHAR(50) NOT NULL, -- customer_feedback, invoice, user, company, etc.
    entity_id UUID NOT NULL,
    operation_type VARCHAR(50) NOT NULL, -- sentiment_analysis, embedding_generation, summarization, classification

    -- AI configuration
    ai_models_id UUID REFERENCES ai_models(ai_models_id),
    model_config JSONB,
    prompt_template TEXT,
    input_data JSONB,

    -- Processing status
    status VARCHAR(20) DEFAULT 'pending', -- pending, processing, completed, failed, cancelled
    priority INTEGER DEFAULT 5, -- 1=highest, 10=lowest
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,

    -- Results
    output_data JSONB,
    processing_metadata JSONB,
    error_message TEXT,
    processing_duration_ms INTEGER,

    -- Scheduling
    scheduled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    expires_at TIMESTAMP, -- When to remove from queue

    -- Audit
    created_by UUID REFERENCES users(users_id),
    processed_by VARCHAR(100), -- AI service or system component

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Enhanced vector embeddings with metadata
DROP TABLE IF EXISTS vector_embeddings CASCADE; CREATE TABLE vector_embeddings (
    vector_embeddings_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    companies_id UUID REFERENCES companies(companies_id),

    -- Source entity
    entity_type VARCHAR(50) NOT NULL,
    entity_id UUID NOT NULL,
    content_type VARCHAR(50), -- title, description, content, summary, feedback
    content_hash VARCHAR(64),

    -- AI model information
    ai_models_id UUID REFERENCES ai_models(ai_models_id),
    embedding_model VARCHAR(100) NOT NULL,
    embedding_dimensions INTEGER DEFAULT 1536,
    embedding_vector VECTOR(1536) NOT NULL,

    -- Content information
    original_content TEXT,
    processed_content TEXT,
    content_length INTEGER,
    content_language VARCHAR(5) DEFAULT 'sr-RS',

    -- Quality metrics
    embedding_quality_score DECIMAL(3,2), -- 0.0 to 1.0
    similarity_threshold DECIMAL(3,2) DEFAULT 0.8,
    clustering_group INTEGER, -- For grouping similar embeddings

    -- Performance tracking
    generation_time_ms INTEGER,
    last_similarity_search TIMESTAMP,
    search_count INTEGER DEFAULT 0,
    cache_hit_count INTEGER DEFAULT 0,

    -- Metadata
    tags JSONB,
    custom_metadata JSONB,
    is_active BOOLEAN DEFAULT true,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(entity_type, entity_id, embedding_model),
    PARTITION BY HASH (companies_id)
);

-- Sentiment analysis results and tracking
DROP TABLE IF EXISTS sentiment_analysis_results CASCADE; CREATE TABLE sentiment_analysis_results (
    sentiment_analysis_results_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    companies_id UUID REFERENCES companies(companies_id),

    -- Source entity
    entity_type VARCHAR(50) NOT NULL, -- customer_feedback, chat_message, email, review
    entity_id UUID NOT NULL,

    -- AI model used
    ai_models_id UUID REFERENCES ai_models(ai_models_id),
    analysis_type VARCHAR(50) DEFAULT 'sentiment', -- sentiment, emotion, intent, urgency

    -- Sentiment results
    sentiment_score DECIMAL(3,2) CHECK (sentiment_score >= -1.0 AND sentiment_score <= 1.0),
    sentiment_label VARCHAR(20), -- very_positive, positive, neutral, negative, very_negative
    sentiment_confidence DECIMAL(3,2),

    -- Emotional analysis
    emotion_primary VARCHAR(20), -- joy, anger, sadness, fear, surprise, disgust, trust, anticipation
    emotion_secondary VARCHAR(20),
    emotion_confidence DECIMAL(3,2),
    emotion_intensities JSONB, -- Detailed emotion scores

    -- Intent and topic analysis
    intent_primary VARCHAR(50), -- complaint, praise, question, suggestion, feedback
    intent_secondary VARCHAR(50),
    intent_confidence DECIMAL(3,2),
    topics_detected JSONB, -- Array of topics with confidence scores

    -- Language and text analysis
    language_detected VARCHAR(5),
    language_confidence DECIMAL(3,2),
    keywords_extracted JSONB,
    entities_extracted JSONB, -- People, organizations, products mentioned

    -- Quality and validation
    analysis_quality_score DECIMAL(3,2), -- Overall quality of analysis
    human_validated BOOLEAN DEFAULT false,
    human_validation_user UUID REFERENCES users(users_id),
    human_validation_timestamp TIMESTAMP,
    validation_notes TEXT,

    -- Processing metadata
    processing_duration_ms INTEGER,
    tokens_processed INTEGER,
    api_cost DECIMAL(6,4),

    -- Trends and patterns
    sentiment_trend VARCHAR(20), -- improving, declining, stable
    sentiment_change DECIMAL(3,2), -- Change from previous analysis
    comparison_period_days INTEGER DEFAULT 30,

    -- Actions and recommendations
    recommended_action VARCHAR(100),
    action_priority VARCHAR(20), -- low, medium, high, urgent
    action_deadline TIMESTAMP,
    action_assigned_to UUID REFERENCES users(users_id),
    action_status VARCHAR(20) DEFAULT 'pending',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(users_id),
    updated_by UUID REFERENCES users(users_id),

    UNIQUE(entity_type, entity_id, analysis_type),
    PARTITION BY RANGE (created_at)
);

-- AI Training data management
DROP TABLE IF EXISTS ai_training_data CASCADE; CREATE TABLE ai_training_data (
    ai_training_data_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    companies_id UUID REFERENCES companies(companies_id),

    -- Data source
    data_type VARCHAR(50) NOT NULL, -- text, conversation, feedback, labeled_data
    data_category VARCHAR(50), -- sentiment, classification, generation, qa
    source_entity_type VARCHAR(50),
    source_entity_id UUID,

    -- Training content
    input_text TEXT NOT NULL,
    output_text TEXT,
    expected_output JSONB, -- For classification tasks
    labels JSONB, -- Human-assigned labels
    metadata JSONB, -- Additional context

    -- Quality and validation
    quality_score DECIMAL(3,2), -- 0.0 to 1.0
    is_labeled BOOLEAN DEFAULT false,
    validation_status VARCHAR(20) DEFAULT 'pending', -- pending, validated, rejected
    validated_by UUID REFERENCES users(users_id),
    validated_at TIMESTAMP,
    validation_notes TEXT,

    -- AI processing
    ai_processed BOOLEAN DEFAULT false,
    ai_model_used VARCHAR(100),
    processing_result JSONB,
    confidence_score DECIMAL(3,2),

    -- Usage tracking
    usage_count INTEGER DEFAULT 0,
    last_used_at TIMESTAMP,
    training_sessions JSONB, -- Which training sessions used this data

    -- Privacy and compliance
    contains_pii BOOLEAN DEFAULT false,
    data_classification VARCHAR(20) DEFAULT 'internal', -- public, internal, confidential
    anonymized_text TEXT,
    retention_policy VARCHAR(50) DEFAULT '1_year',

    -- Performance metrics
    training_accuracy DECIMAL(3,2),
    training_loss DECIMAL(5,4),
    evaluation_metrics JSONB,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(users_id),
    updated_by UUID REFERENCES users(users_id),

    PARTITION BY HASH (companies_id)
);

-- AI Model performance tracking
DROP TABLE IF EXISTS ai_model_performance CASCADE; CREATE TABLE ai_model_performance (
    ai_model_performance_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    companies_id UUID REFERENCES companies(companies_id),
    ai_models_id UUID REFERENCES ai_models(ai_models_id),

    -- Performance metrics
    metric_date DATE NOT NULL,
    metric_type VARCHAR(50) NOT NULL, -- accuracy, latency, throughput, cost, quality

    -- Numerical metrics
    metric_value DECIMAL(10,4) NOT NULL,
    metric_unit VARCHAR(20), -- percentage, milliseconds, tokens/second, etc.
    baseline_value DECIMAL(10,4), -- For comparison
    target_value DECIMAL(10,4), -- Target performance

    -- Context
    sample_size INTEGER,
    time_period_seconds INTEGER,
    data_processed_mb DECIMAL(8,2),

    -- Quality metrics
    precision_score DECIMAL(4,3), -- For classification tasks
    recall_score DECIMAL(4,3),
    f1_score DECIMAL(4,3),
    accuracy_score DECIMAL(4,3),

    -- Cost metrics
    cost_per_request DECIMAL(6,4),
    cost_per_token DECIMAL(8,6),
    total_cost DECIMAL(8,2),

    -- Performance issues
    performance_issues JSONB,
    recommendations TEXT,
    alerts_triggered JSONB,

    -- Metadata
    tags JSONB,
    custom_metrics JSONB,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(ai_models_id, metric_date, metric_type),
    PARTITION BY RANGE (metric_date)
);

-- Chat messages with AI integration
DROP TABLE IF EXISTS chat_messages CASCADE; CREATE TABLE chat_messages (
    chat_messages_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    chat_sessions_id UUID NOT NULL REFERENCES chat_sessions(chat_sessions_id) ON DELETE CASCADE,
    users_id UUID REFERENCES users(users_id),
    message_type VARCHAR(20) DEFAULT 'text', -- text, file, image, system, ai_response

    -- Message content
    content TEXT,
    content_html TEXT,
    content_language VARCHAR(5) DEFAULT 'sr-RS',

    -- AI processing
    ai_models_id UUID REFERENCES ai_models(ai_models_id),
    ai_processing_time_ms INTEGER,
    ai_confidence_score DECIMAL(3,2),
    ai_response_metadata JSONB,
    sentiment_analysis_id UUID REFERENCES sentiment_analysis_results(sentiment_analysis_results_id),

    -- File attachments
    attachment_url VARCHAR(500),
    attachment_name VARCHAR(255),
    attachment_size INTEGER,
    attachment_type VARCHAR(50),

    -- Message status
    is_edited BOOLEAN DEFAULT false,
    edited_at TIMESTAMP,
    is_deleted BOOLEAN DEFAULT false,
    deleted_at TIMESTAMP,
    deletion_reason TEXT,

    -- Threading and replies
    parent_message_id UUID REFERENCES chat_messages(chat_messages_id),
    thread_id UUID,
    reply_count INTEGER DEFAULT 0,

    -- Reactions and interactions
    reactions JSONB, -- emoji reactions
    mentions JSONB, -- mentioned users
    links JSONB, -- extracted links

    -- Analytics
    read_by JSONB,
    read_count INTEGER DEFAULT 0,
    embedding_vector VECTOR(1536),

    -- Message ordering
    message_order BIGINT DEFAULT EXTRACT(EPOCH FROM CURRENT_TIMESTAMP) * 1000,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    PARTITION BY HASH (chat_sessions_id)
);

-- AI Insights with enhanced capabilities
DROP TABLE IF EXISTS ai_insights CASCADE; CREATE TABLE ai_insights (
    ai_insights_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    companies_id UUID REFERENCES companies(companies_id),
    insight_type VARCHAR(50) NOT NULL, -- prediction, anomaly, recommendation, sentiment_summary

    -- Content and analysis
    title VARCHAR(255) NOT NULL,
    description TEXT,
    insight_data JSONB,
    confidence_score DECIMAL(3,2), -- 0.0 to 1.0

    -- AI model and processing
    ai_models_id UUID REFERENCES ai_models(ai_models_id),
    model_version VARCHAR(20),
    prompt_used TEXT,
    tokens_used INTEGER,
    processing_cost DECIMAL(6,4),

    -- Related entities
    related_entity_type VARCHAR(50),
    related_entity_id UUID,
    affected_entities JSONB, -- Multiple related entities

    -- Business impact
    impact_level VARCHAR(20), -- low, medium, high, critical
    impact_score DECIMAL(3,2),
    business_value DECIMAL(8,2),
    priority_score DECIMAL(3,2),

    -- Actions and recommendations
    recommended_action TEXT,
    action_required BOOLEAN DEFAULT false,
    action_deadline TIMESTAMP,
    action_assigned_to UUID REFERENCES users(users_id),
    action_status VARCHAR(20) DEFAULT 'pending',
    action_completion_notes TEXT,

    -- Validation and feedback
    is_validated BOOLEAN DEFAULT false,
    validated_by UUID REFERENCES users(users_id),
    validated_at TIMESTAMP,
    validation_score DECIMAL(3,2), -- User feedback on insight accuracy
    validation_feedback TEXT,

    -- Lifecycle management
    status VARCHAR(20) DEFAULT 'active', -- draft, active, implemented, archived, dismissed
    is_archived BOOLEAN DEFAULT false,
    archived_at TIMESTAMP,
    archived_by UUID REFERENCES users(users_id),

    -- Performance tracking
    view_count INTEGER DEFAULT 0,
    last_viewed_at TIMESTAMP,
    helpful_votes INTEGER DEFAULT 0,
    total_votes INTEGER DEFAULT 0,
    effectiveness_score DECIMAL(3,2),

    -- AI embeddings and search
    embedding_vector VECTOR(1536),
    tags JSONB,
    custom_fields JSONB,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(users_id),
    updated_by UUID REFERENCES users(users_id),

    PARTITION BY RANGE (created_at)
);

-- ============================================================================
-- AI VIEWS AND MATERIALIZED VIEWS FOR SIMILARITY SEARCH
-- ============================================================================

-- View for company similarity search - answers "which company is doing the same business like me?"
DROP VIEW IF EXISTS v_company_similarity_search;
CREATE VIEW v_company_similarity_search AS
SELECT
    c1.companies_id as source_company_id,
    c1.company_name as source_company_name,
    c1.business_areas_id as source_business_area,
    c2.companies_id as similar_company_id,
    c2.company_name as similar_company_name,
    c2.business_areas_id as similar_business_area,
    ba1.area_name as source_area_name,
    ba2.area_name as similar_area_name,
    c2.employee_count as similar_employee_count,
    c2.annual_revenue as similar_revenue,
    c2.market_share as similar_market_share,
    c2.customer_count as similar_customer_count,
    c2.strengths as similar_strengths,
    c2.weaknesses as similar_weaknesses,
    c2.opportunities as similar_opportunities,
    c2.threats as similar_threats,
    -- Calculate business similarity score based on multiple factors
    (
        CASE WHEN c1.business_areas_id = c2.business_areas_id THEN 0.4 ELSE 0 END +
        CASE WHEN ABS(COALESCE(c1.employee_count, 0) - COALESCE(c2.employee_count, 0)) <= 50 THEN 0.2 ELSE 0 END +
        CASE WHEN ABS(COALESCE(c1.annual_revenue, 0) - COALESCE(c2.annual_revenue, 0)) / GREATEST(COALESCE(c1.annual_revenue, 1), COALESCE(c2.annual_revenue, 1)) <= 0.5 THEN 0.2 ELSE 0 END +
        CASE WHEN c1.market_share IS NOT NULL AND c2.market_share IS NOT NULL AND ABS(c1.market_share - c2.market_share) <= 5 THEN 0.2 ELSE 0 END
    ) as business_similarity_score,
    -- Vector similarity using cosine distance
    CASE WHEN c1.embedding_vector IS NOT NULL AND c2.embedding_vector IS NOT NULL
         THEN 1 - (c1.embedding_vector <=> c2.embedding_vector)
         ELSE 0
    END as embedding_similarity_score
FROM companies c1
CROSS JOIN companies c2
LEFT JOIN business_areas ba1 ON c1.business_areas_id = ba1.business_areas_id
LEFT JOIN business_areas ba2 ON c2.business_areas_id = ba2.business_areas_id
WHERE c1.companies_id != c2.companies_id
  AND c1.is_active = true
  AND c2.is_active = true
  AND c1.business_areas_id IS NOT NULL
  AND c2.business_areas_id IS NOT NULL;

-- Materialized view for customer similarity search
DROP MATERIALIZED VIEW IF EXISTS mv_customer_similarity_analysis;
CREATE MATERIALIZED VIEW mv_customer_similarity_analysis AS
SELECT
    c1.customers_id as source_customer_id,
    c1.company_name as source_customer_name,
    c1.companies_id as source_company_id,
    c2.customers_id as similar_customer_id,
    c2.company_name as similar_customer_name,
    c2.companies_id as similar_company_id,
    -- Business similarity factors
    CASE WHEN c1.business_entity_types_id = c2.business_entity_types_id THEN 0.3 ELSE 0 END +
    CASE WHEN c1.business_areas_id = c2.business_areas_id THEN 0.3 ELSE 0 END +
    CASE WHEN ABS(COALESCE(c1.total_invoiced, 0) - COALESCE(c2.total_invoiced, 0)) / GREATEST(COALESCE(c1.total_invoiced, 1), COALESCE(c2.total_invoiced, 1)) <= 0.5 THEN 0.2 ELSE 0 END +
    CASE WHEN c1.customer_segment = c2.customer_segment THEN 0.2 ELSE 0 END as similarity_score,
    -- Embedding similarity
    CASE WHEN c1.embedding_vector IS NOT NULL AND c2.embedding_vector IS NOT NULL
         THEN 1 - (c1.embedding_vector <=> c2.embedding_vector)
         ELSE 0
    END as embedding_similarity_score,
    -- Comparative analysis
    c1.total_invoiced as source_total_invoiced,
    c2.total_invoiced as similar_total_invoiced,
    c1.customer_rating as source_rating,
    c2.customer_rating as similar_rating,
    c1.risk_rating as source_risk,
    c2.risk_rating as similar_risk
FROM customers c1
CROSS JOIN customers c2
WHERE c1.customers_id != c2.customers_id
  AND c1.is_active = true
  AND c2.is_active = true
  AND c1.business_entity_types_id IS NOT NULL
  AND c2.business_entity_types_id IS NOT NULL
WITH NO DATA;

-- View for product similarity and competitive analysis
DROP VIEW IF EXISTS v_product_similarity_search;
CREATE VIEW v_product_similarity_search AS
SELECT
    p1.products_id as source_product_id,
    p1.product_name as source_product_name,
    p1.companies_id as source_company_id,
    p2.products_id as similar_product_id,
    p2.product_name as similar_product_name,
    p2.companies_id as similar_company_id,
    pc1.category_name as source_category,
    pc2.category_name as similar_category,
    -- Price and margin comparison
    p1.unit_price as source_price,
    p2.unit_price as similar_price,
    p1.cost_price as source_cost,
    p2.cost_price as similar_cost,
    CASE WHEN p1.unit_price > 0 AND p2.unit_price > 0
         THEN ((p1.unit_price - p2.unit_price) / p1.unit_price) * 100
         ELSE 0
    END as price_difference_percent,
    -- Similarity scoring
    CASE WHEN p1.product_categories_id = p2.product_categories_id THEN 0.4 ELSE 0 END +
    CASE WHEN ABS(COALESCE(p1.unit_price, 0) - COALESCE(p2.unit_price, 0)) / GREATEST(COALESCE(p1.unit_price, 1), COALESCE(p2.unit_price, 1)) <= 0.3 THEN 0.3 ELSE 0 END +
    CASE WHEN p1.product_type = p2.product_type THEN 0.3 ELSE 0 END as similarity_score,
    -- Embedding similarity
    CASE WHEN p1.embedding_vector IS NOT NULL AND p2.embedding_vector IS NOT NULL
         THEN 1 - (p1.embedding_vector <=> p2.embedding_vector)
         ELSE 0
    END as embedding_similarity_score
FROM products p1
CROSS JOIN products p2
LEFT JOIN product_categories pc1 ON p1.product_categories_id = pc1.product_categories_id
LEFT JOIN product_categories pc2 ON p2.product_categories_id = pc2.product_categories_id
WHERE p1.products_id != p2.products_id
  AND p1.is_active = true
  AND p2.is_active = true
  AND p1.product_categories_id IS NOT NULL
  AND p2.product_categories_id IS NOT NULL;

-- Materialized view for invoice pattern analysis
DROP MATERIALIZED VIEW IF EXISTS mv_invoice_pattern_analysis;
CREATE MATERIALIZED VIEW mv_invoice_pattern_analysis AS
SELECT
    i.companies_id,
    c.company_name,
    i.customers_id,
    cust.company_name as customer_name,
    DATE_TRUNC('month', i.invoice_date) as invoice_month,
    COUNT(*) as invoice_count,
    SUM(i.total_amount) as total_amount,
    AVG(i.total_amount) as avg_invoice_amount,
    SUM(i.pdv_amount) as total_pdv,
    AVG(i.payment_terms_days) as avg_payment_terms,
    -- Payment performance
    COUNT(CASE WHEN i.payment_status = 'paid' THEN 1 END) as paid_invoices,
    COUNT(CASE WHEN i.payment_status = 'overdue' THEN 1 END) as overdue_invoices,
    COUNT(CASE WHEN i.payment_date <= i.due_date THEN 1 END) as on_time_payments,
    AVG(CASE WHEN i.payment_date IS NOT NULL THEN EXTRACT(DAY FROM (i.payment_date - i.invoice_date)) ELSE NULL END) as avg_payment_days,
    -- Seasonal patterns
    EXTRACT(MONTH FROM i.invoice_date) as month_number,
    EXTRACT(DOW FROM i.invoice_date) as day_of_week
FROM invoices i
JOIN companies c ON i.companies_id = c.companies_id
LEFT JOIN customers cust ON i.customers_id = cust.customers_id
WHERE i.status = 'issued'
  AND i.invoice_date >= CURRENT_DATE - INTERVAL '2 years'
GROUP BY i.companies_id, c.company_name, i.customers_id, cust.company_name, DATE_TRUNC('month', i.invoice_date),
         EXTRACT(MONTH FROM i.invoice_date), EXTRACT(DOW FROM i.invoice_date)
WITH NO DATA;

-- View for business intelligence insights
DROP VIEW IF EXISTS v_business_intelligence_insights;
CREATE VIEW v_business_intelligence_insights AS
SELECT
    c.companies_id,
    c.company_name,
    c.business_areas_id,
    ba.area_name,
    -- Financial metrics
    COUNT(DISTINCT i.invoices_id) as total_invoices,
    COALESCE(SUM(i.total_amount), 0) as total_revenue,
    COALESCE(AVG(i.total_amount), 0) as avg_invoice_value,
    COALESCE(SUM(i.pdv_amount), 0) as total_pdv,
    -- Customer metrics
    COUNT(DISTINCT cust.customers_id) as total_customers,
    COALESCE(AVG(cust.customer_rating), 0) as avg_customer_rating,
    -- Product metrics
    COUNT(DISTINCT p.products_id) as total_products,
    -- Performance metrics
    COUNT(CASE WHEN i.payment_status = 'paid' THEN 1 END) * 100.0 / NULLIF(COUNT(*), 0) as payment_success_rate,
    AVG(CASE WHEN i.payment_date IS NOT NULL THEN EXTRACT(DAY FROM (i.payment_date - i.invoice_date)) ELSE NULL END) as avg_collection_days,
    -- Growth indicators
    COUNT(CASE WHEN i.invoice_date >= CURRENT_DATE - INTERVAL '3 months' THEN 1 END) as recent_invoices,
    COUNT(CASE WHEN i.invoice_date >= CURRENT_DATE - INTERVAL '6 months' THEN 1 END) as six_month_invoices,
    -- Risk indicators
    COUNT(CASE WHEN i.payment_status = 'overdue' THEN 1 END) as overdue_invoices,
    COUNT(CASE WHEN cust.risk_rating = 'high' THEN 1 END) as high_risk_customers
FROM companies c
LEFT JOIN business_areas ba ON c.business_areas_id = ba.business_areas_id
LEFT JOIN invoices i ON c.companies_id = i.companies_id AND i.status = 'issued' AND i.invoice_date >= CURRENT_DATE - INTERVAL '1 year'
LEFT JOIN customers cust ON c.companies_id = cust.companies_id AND cust.is_active = true
LEFT JOIN products p ON c.companies_id = p.companies_id AND p.is_active = true
WHERE c.is_active = true
GROUP BY c.companies_id, c.company_name, c.business_areas_id, ba.area_name;

-- Materialized view for competitive market analysis
DROP MATERIALIZED VIEW IF EXISTS mv_competitive_market_analysis;
CREATE MATERIALIZED VIEW mv_competitive_market_analysis AS
SELECT
    ba.business_areas_id,
    ba.area_name,
    ba.area_name_sr,
    -- Market concentration
    COUNT(DISTINCT c.companies_id) as total_companies,
    COUNT(DISTINCT CASE WHEN c.employee_count <= 10 THEN c.companies_id END) as small_companies,
    COUNT(DISTINCT CASE WHEN c.employee_count BETWEEN 11 AND 50 THEN c.companies_id END) as medium_companies,
    COUNT(DISTINCT CASE WHEN c.employee_count > 50 THEN c.companies_id END) as large_companies,
    -- Market size indicators
    COALESCE(SUM(c.annual_revenue), 0) as total_market_revenue,
    COALESCE(AVG(c.annual_revenue), 0) as avg_company_revenue,
    COALESCE(SUM(c.employee_count), 0) as total_employees,
    -- Market share analysis
    COALESCE(SUM(c.market_share), 0) as total_market_share,
    COALESCE(MAX(c.market_share), 0) as largest_market_share,
    -- Growth indicators
    COUNT(DISTINCT CASE WHEN c.founding_date >= CURRENT_DATE - INTERVAL '2 years' THEN c.companies_id END) as new_companies_2_years,
    COUNT(DISTINCT CASE WHEN c.founding_date >= CURRENT_DATE - INTERVAL '5 years' THEN c.companies_id END) as new_companies_5_years,
    -- Regional distribution
    COUNT(DISTINCT CASE WHEN c.city = 'Beograd' THEN c.companies_id END) as belgrade_companies,
    COUNT(DISTINCT CASE WHEN c.city = 'Novi Sad' THEN c.companies_id END) as novi_sad_companies,
    COUNT(DISTINCT CASE WHEN c.city = 'Niš' THEN c.companies_id END) as nis_companies
FROM business_areas ba
LEFT JOIN companies c ON ba.business_areas_id = c.business_areas_id AND c.is_active = true
GROUP BY ba.business_areas_id, ba.area_name, ba.area_name_sr
WITH NO DATA;

-- ============================================================================
-- FUNCTIONS AND TRIGGERS
-- ============================================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Function to calculate PDV for invoice items
CREATE OR REPLACE FUNCTION calculate_pdv_for_invoice_item()
RETURNS TRIGGER AS $$
BEGIN
    -- Calculate PDV amount based on line total and PDV rate
    NEW.pdv_amount = ROUND((NEW.line_total * NEW.pdv_rate / 100), 2);
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Function to update invoice totals
CREATE OR REPLACE FUNCTION update_invoice_totals()
RETURNS TRIGGER AS $$
BEGIN
    -- Update invoice totals when items are added/modified
    UPDATE invoices
    SET
        subtotal = (
            SELECT COALESCE(SUM(line_total), 0)
            FROM invoice_items
            WHERE invoice_id = COALESCE(NEW.invoice_id, OLD.invoice_id)
        ),
        pdv_amount = (
            SELECT COALESCE(SUM(pdv_amount), 0)
            FROM invoice_items
            WHERE invoice_id = COALESCE(NEW.invoice_id, OLD.invoice_id)
        ),
        total_amount = (
            SELECT COALESCE(SUM(line_total + pdv_amount), 0)
            FROM invoice_items
            WHERE invoice_id = COALESCE(NEW.invoice_id, OLD.invoice_id)
        ),
        pdv_base = (
            SELECT COALESCE(SUM(line_total), 0)
            FROM invoice_items
            WHERE invoice_id = COALESCE(NEW.invoice_id, OLD.invoice_id)
        )
    WHERE invoices_id = COALESCE(NEW.invoice_id, OLD.invoice_id);

    RETURN COALESCE(NEW, OLD);
END;
$$ language 'plpgsql';

-- Function to update account balance
CREATE OR REPLACE FUNCTION update_account_balance()
RETURNS TRIGGER AS $$
BEGIN
    -- Update account balance in chart of accounts
    UPDATE chart_of_accounts
    SET
        current_balance = (
            SELECT COALESCE(SUM(
                CASE
                    WHEN gl.debit_amount > 0 THEN gl.debit_amount
                    ELSE -gl.credit_amount
                END
            ), 0)
            FROM general_ledger gl
            WHERE gl.account_id = COALESCE(NEW.account_id, OLD.account_id)
            AND gl.status = 'posted'
        ),
        updated_at = CURRENT_TIMESTAMP
    WHERE chart_of_accounts_id = COALESCE(NEW.account_id, OLD.account_id);

    RETURN COALESCE(NEW, OLD);
END;
$$ language 'plpgsql';

-- Function for Serbian PDV calculation
CREATE OR REPLACE FUNCTION calculate_serbian_pdv(
    p_subtotal DECIMAL,
    p_pdv_rate DECIMAL DEFAULT 20.0
)
RETURNS DECIMAL AS $$
BEGIN
    -- Calculate PDV according to Serbian regulations
    RETURN ROUND(p_subtotal * p_pdv_rate / 100, 2);
END;
$$ language 'plpgsql';

-- Function for AI embedding generation
CREATE OR REPLACE FUNCTION generate_embedding_vector(input_text TEXT)
RETURNS VECTOR(1536) AS $$
BEGIN
    -- Placeholder function - would integrate with actual AI service
    -- For now, return a zero vector
    RETURN ('[' || repeat('0,', 1535) || '0]')::vector;
END;
$$ language 'plpgsql';

-- Function for vector similarity search
CREATE OR REPLACE FUNCTION vector_search(
    query_vector VECTOR(1536),
    company_id UUID,
    limit_count INTEGER DEFAULT 10
)
RETURNS TABLE(
    entity_type VARCHAR(50),
    entity_id UUID,
    similarity_score DECIMAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        ve.entity_type,
        ve.entity_id,
        1 - (ve.embedding_vector <=> query_vector) as similarity_score
    FROM vector_embeddings ve
    WHERE ve.company_id = company_id
    ORDER BY ve.embedding_vector <=> query_vector
    LIMIT limit_count;
END;
$$ language 'plpgsql';

-- ============================================================================
-- TRIGGERS
-- ============================================================================

-- Updated at triggers
CREATE TRIGGER update_companies_updated_at BEFORE UPDATE ON companies FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_products_updated_at BEFORE UPDATE ON products FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_customers_updated_at BEFORE UPDATE ON customers FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_suppliers_updated_at BEFORE UPDATE ON suppliers FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_invoices_updated_at BEFORE UPDATE ON invoices FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_general_ledger_updated_at BEFORE UPDATE ON general_ledger FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_payments_updated_at BEFORE UPDATE ON payments FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_ai_insights_updated_at BEFORE UPDATE ON ai_insights FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_chat_sessions_updated_at BEFORE UPDATE ON chat_sessions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_system_settings_updated_at BEFORE UPDATE ON system_settings FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Business logic triggers
CREATE TRIGGER calculate_invoice_item_pdv
    BEFORE INSERT OR UPDATE ON invoice_items
    FOR EACH ROW EXECUTE FUNCTION calculate_pdv_for_invoice_item();

CREATE TRIGGER update_invoice_totals_trigger
    AFTER INSERT OR UPDATE OR DELETE ON invoice_items
    FOR EACH ROW EXECUTE FUNCTION update_invoice_totals();

CREATE TRIGGER update_account_balance_trigger
    AFTER INSERT OR UPDATE OR DELETE ON general_ledger
    FOR EACH ROW EXECUTE FUNCTION update_account_balance();

-- Audit triggers
CREATE OR REPLACE FUNCTION audit_trigger_function()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO audit_log (
        company_id,
        user_id,
        action,
        resource_type,
        resource_id,
        old_values,
        new_values,
        change_description
    ) VALUES (
        COALESCE(NEW.company_id, OLD.company_id),
        COALESCE(NEW.updated_by, NEW.created_by),
        TG_OP,
        TG_TABLE_NAME,
        COALESCE(NEW.id, OLD.id),
        CASE WHEN TG_OP = 'DELETE' THEN row_to_json(OLD) ELSE NULL END,
        CASE WHEN TG_OP = 'INSERT' THEN row_to_json(NEW) ELSE row_to_json(NEW) END,
        TG_OP || ' operation on ' || TG_TABLE_NAME
    );
    RETURN COALESCE(NEW, OLD);
END;
$$ language 'plpgsql';

-- Audit triggers for key tables
CREATE TRIGGER audit_companies AFTER INSERT OR UPDATE OR DELETE ON companies FOR EACH ROW EXECUTE FUNCTION audit_trigger_function();
CREATE TRIGGER audit_users AFTER INSERT OR UPDATE OR DELETE ON users FOR EACH ROW EXECUTE FUNCTION audit_trigger_function();
CREATE TRIGGER audit_invoices AFTER INSERT OR UPDATE OR DELETE ON invoices FOR EACH ROW EXECUTE FUNCTION audit_trigger_function();
CREATE TRIGGER audit_general_ledger AFTER INSERT OR UPDATE OR DELETE ON general_ledger FOR EACH ROW EXECUTE FUNCTION audit_trigger_function();

-- ============================================================================
-- MATERIALIZED VIEWS FOR ANALYTICS
-- ============================================================================

-- Monthly revenue analysis
CREATE MATERIALIZED VIEW mv_monthly_revenue AS
SELECT
    date_trunc('month', i.invoice_date) as month,
    i.company_id,
    c.company_name,
    COUNT(i.invoices_id) as invoice_count,
    SUM(i.subtotal) as total_subtotal,
    SUM(i.pdv_amount) as total_pdv,
    SUM(i.total_amount) as total_revenue,
    AVG(i.total_amount) as avg_invoice_value,
    COUNT(CASE WHEN i.payment_status = 'paid' THEN 1 END) as paid_invoices,
    COUNT(CASE WHEN i.payment_status = 'pending' THEN 1 END) as pending_invoices
FROM invoices i
JOIN companies c ON i.company_id = c.companies_id
WHERE i.status = 'issued' AND i.invoice_date >= CURRENT_DATE - INTERVAL '2 years'
GROUP BY date_trunc('month', i.invoice_date), i.company_id, c.company_name
WITH NO DATA;

-- Customer analytics
CREATE MATERIALIZED VIEW mv_customer_analytics AS
SELECT
    cu.customers_id,
    cu.company_name as customer_name,
    cu.company_id,
    COUNT(i.invoices_id) as total_invoices,
    SUM(i.total_amount) as total_revenue,
    AVG(i.total_amount) as avg_invoice_value,
    MAX(i.invoice_date) as last_invoice_date,
    COUNT(CASE WHEN i.payment_status = 'paid' THEN 1 END) as paid_invoices,
    COUNT(CASE WHEN i.payment_status = 'pending' THEN 1 END) as pending_invoices,
    COUNT(CASE WHEN i.payment_status = 'overdue' THEN 1 END) as overdue_invoices,
    SUM(CASE WHEN i.due_date < CURRENT_DATE AND i.payment_status != 'paid' THEN i.total_amount ELSE 0 END) as overdue_amount,
    cu.customer_rating,
    cu.risk_rating
FROM customers cu
LEFT JOIN invoices i ON cu.customers_id = i.customer_id AND i.status = 'issued'
WHERE cu.is_active = true
GROUP BY cu.customers_id, cu.company_name, cu.company_id, cu.customer_rating, cu.risk_rating
WITH NO DATA;

-- AI insights performance
CREATE MATERIALIZED VIEW mv_ai_insights_performance AS
SELECT
    date_trunc('day', ai.created_at) as analysis_date,
    ai.company_id,
    ai.insight_type,
    ai.insight_category,
    COUNT(*) as insight_count,
    AVG(ai.confidence_score) as avg_confidence,
    COUNT(CASE WHEN ai.status = 'reviewed' THEN 1 END) as reviewed_count,
    COUNT(CASE WHEN ai.action_required = true THEN 1 END) as action_required_count
FROM ai_insights ai
WHERE ai.created_at >= CURRENT_DATE - INTERVAL '90 days'
GROUP BY date_trunc('day', ai.created_at), ai.company_id, ai.insight_type, ai.insight_category
WITH NO DATA;

-- Financial position summary
CREATE MATERIALIZED VIEW mv_financial_position AS
SELECT
    gl.company_id,
    c.company_name,
    date_trunc('month', gl.transaction_date) as month,
    coa.account_type,
    SUM(gl.debit_amount) as total_debit,
    SUM(gl.credit_amount) as total_credit,
    SUM(gl.debit_amount - gl.credit_amount) as balance
FROM general_ledger gl
JOIN chart_of_accounts coa ON gl.account_id = coa.chart_of_accounts_id
JOIN companies c ON gl.company_id = c.companies_id
WHERE gl.status = 'posted' AND gl.transaction_date >= CURRENT_DATE - INTERVAL '1 year'
GROUP BY gl.company_id, c.company_name, date_trunc('month', gl.transaction_date), coa.account_type
WITH NO DATA;

-- ============================================================================
-- DEFAULT DATA INSERTION
-- ============================================================================

-- Insert default countries
INSERT INTO countries (iso_code, iso_code3, name, name_sr, region, phone_code, currency_code) VALUES
('RS', 'SRB', 'Serbia', 'Srbija', 'Europe', '+381', 'RSD'),
('US', 'USA', 'United States', 'Sjedinjene Američke Države', 'North America', '+1', 'USD'),
('DE', 'DEU', 'Germany', 'Nemačka', 'Europe', '+49', 'EUR'),
('GB', 'GBR', 'United Kingdom', 'Ujedinjeno Kraljevstvo', 'Europe', '+44', 'GBP'),
('FR', 'FRA', 'France', 'Francuska', 'Europe', '+33', 'EUR')
ON CONFLICT (iso_code) DO NOTHING;

-- Insert currencies
INSERT INTO currencies (code, name, name_sr, symbol, decimal_places) VALUES
('RSD', 'Serbian Dinar', 'Srpski Dinar', 'RSD', 2),
('EUR', 'Euro', 'Euro', '€', 2),
('USD', 'US Dollar', 'Američki Dolar', '$', 2),
('GBP', 'British Pound', 'Britanska Funta', '£', 2),
('CHF', 'Swiss Franc', 'Švajcarski Franak', 'CHF', 2)
ON CONFLICT (code) DO NOTHING;

-- Insert Serbian business entity types
INSERT INTO business_entity_types (entity_code, entity_name, entity_name_sr, description, tax_requirements, reporting_requirements) VALUES
('DOO', 'Limited Liability Company', 'Društvo sa ograničenom odgovornošću',
 'Most common Serbian business entity for small and medium businesses',
 '{"pdv_required": true, "annual_reports": true, "statistical_reports": true}'::jsonb,
 '{"financial_statements": true, "tax_returns": true, "employee_reports": true}'::jsonb),

('AD', 'Joint Stock Company', 'Akcionarsko društvo',
 'For larger businesses with multiple shareholders',
 '{"pdv_required": true, "annual_reports": true, "statistical_reports": true, "shareholder_reports": true}'::jsonb,
 '{"financial_statements": true, "tax_returns": true, "shareholder_reports": true, "public_disclosure": true}'::jsonb),

('Preduzetnik', 'Entrepreneur', 'Preduzetnik',
 'Individual entrepreneur without limited liability',
 '{"pdv_optional": true, "simplified_reports": true}'::jsonb,
 '{"simplified_tax_return": true, "income_reports": true}'::jsonb),

('OD', 'General Partnership', 'Ortačko društvo',
 'Partnership with unlimited liability',
 '{"pdv_required": true, "annual_reports": true, "statistical_reports": true}'::jsonb,
 '{"financial_statements": true, "tax_returns": true, "partner_reports": true}'::jsonb)
ON CONFLICT (entity_code) DO NOTHING;

-- Insert business areas
INSERT INTO business_areas (area_code, area_name, area_name_sr, description, nace_codes) VALUES
('TECH', 'Technology', 'Tehnologija', 'Software, IT services, digital solutions',
 '{"6201": "Software development", "6202": "IT consulting", "6209": "Other IT services"}'::jsonb),

('MANU', 'Manufacturing', 'Proizvodnja', 'Industrial production and manufacturing',
 '{"10": "Food products", "11": "Beverages", "13": "Textiles"}'::jsonb),

('CONS', 'Construction', 'Građevinarstvo', 'Building and construction services',
 '{"41": "Construction", "42": "Civil engineering", "43": "Specialized construction"}'::jsonb),

('TRADE', 'Trade', 'Trgovina', 'Wholesale and retail trade',
 '{"45": "Motor vehicles", "46": "Wholesale trade", "47": "Retail trade"}'::jsonb),

('SERV', 'Services', 'Usluge', 'Professional and business services',
 '{"69": "Legal services", "70": "Management consulting", "71": "Architecture"}'::jsonb)
ON CONFLICT (area_code) DO NOTHING;

-- Insert payment methods
INSERT INTO payment_methods (method_code, method_name, method_name_sr, description) VALUES
('BANK', 'Bank Transfer', 'Bankovni Transfer', 'Wire transfer via bank'),
('CARD', 'Credit/Debit Card', 'Kartica', 'Credit or debit card payment'),
('CASH', 'Cash', 'Gotovina', 'Cash payment'),
('CHECK', 'Check', 'Ček', 'Payment by check'),
('ONLINE', 'Online Payment', 'Online Plaćanje', 'Online payment gateway')
ON CONFLICT (method_code) DO NOTHING;

-- Insert default system settings
INSERT INTO system_settings (setting_key, setting_value, category, description, is_system_setting) VALUES
('company_name', 'ValidoAI Solutions DOO', 'company', 'Default company name', true),
('company_pib', '123456789', 'company', 'Default company PIB', true),
('default_currency', 'RSD', 'finance', 'Default currency for transactions', true),
('default_language', 'sr-RS', 'system', 'Default system language', true),
('pdv_rate', '20.0', 'tax', 'Default PDV rate', true),
('invoice_number_format', 'INV-{prefix}-{number}-{year}', 'invoicing', 'Invoice number format', true),
('email_notifications', 'true', 'notifications', 'Enable email notifications', true),
('timezone', 'Europe/Belgrade', 'system', 'System timezone', true),
('max_file_size', '10MB', 'uploads', 'Maximum file upload size', true),
('auto_backup', 'true', 'system', 'Enable automatic backups', true)
ON CONFLICT (setting_key) DO NOTHING;

-- ============================================================================
-- GRANT PERMISSIONS
-- ============================================================================

-- Grant necessary permissions to roles
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO ai_valido_admin;
GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO ai_valido_accountant;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO ai_valido_readonly;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO ai_valido_admin, ai_valido_accountant;

-- Grant specific permissions for AI features
GRANT SELECT, INSERT, UPDATE ON ai_models, ai_insights, ai_training_data, vector_embeddings TO ai_valido_admin;
GRANT SELECT ON ai_models, ai_insights, ai_training_data, vector_embeddings TO ai_valido_accountant;

-- ============================================================================
-- FINAL SETUP
-- ============================================================================

-- ============================================================================
-- ADVANCED AI FUNCTIONS AND AUTOMATION
-- ============================================================================

-- Function to automatically analyze sentiment for new feedback
CREATE OR REPLACE FUNCTION analyze_customer_feedback_sentiment()
RETURNS TRIGGER AS $$
DECLARE
    sentiment_result RECORD;
    feedback_text TEXT;
BEGIN
    -- Skip if already processed
    IF NEW.ai_processed = true THEN
        RETURN NEW;
    END IF;

    -- Prepare text for analysis
    feedback_text := COALESCE(NEW.title || ' ', '') || NEW.content;

    -- Queue for AI processing (simplified - would integrate with actual AI service)
    INSERT INTO ai_processing_queue (
        companies_id, entity_type, entity_id, operation_type,
        priority, input_data, created_by
    ) VALUES (
        NEW.companies_id, 'customer_feedback', NEW.customer_feedback_id, 'sentiment_analysis',
        CASE WHEN NEW.urgency_level = 'high' THEN 1 ELSE 5 END,
        jsonb_build_object(
            'text', feedback_text,
            'language', NEW.content_language,
            'feedback_type', NEW.feedback_type,
            'source', NEW.feedback_source
        ),
        NEW.created_by
    );

    -- Mark as queued for processing
    NEW.ai_processed := false; -- Will be set to true when processing completes

    RETURN NEW;
END;
$$ language 'plpgsql';

-- Function to generate embeddings for entities
CREATE OR REPLACE FUNCTION generate_entity_embedding(
    p_entity_type VARCHAR,
    p_entity_id UUID,
    p_content TEXT,
    p_content_type VARCHAR DEFAULT 'content'
)
RETURNS VOID AS $$
DECLARE
    content_hash VARCHAR(64);
    embedding_vector VECTOR(1536);
BEGIN
    -- Generate content hash
    content_hash := encode(sha256(p_content::bytea), 'hex');

    -- Skip if embedding already exists
    IF EXISTS (
        SELECT 1 FROM vector_embeddings
        WHERE entity_type = p_entity_type
        AND entity_id = p_entity_id
        AND content_hash = content_hash
    ) THEN
        RETURN;
    END IF;

    -- Queue for embedding generation
    INSERT INTO ai_processing_queue (
        companies_id,
        entity_type,
        entity_id,
        operation_type,
        priority,
        input_data
    )
    SELECT
        CASE
            WHEN p_entity_type = 'companies' THEN (SELECT companies_id FROM companies WHERE companies_id = p_entity_id)
            WHEN p_entity_type = 'customers' THEN (SELECT companies_id FROM customers WHERE customers_id = p_entity_id)
            WHEN p_entity_type = 'products' THEN (SELECT companies_id FROM products WHERE products_id = p_entity_id)
            WHEN p_entity_type = 'customer_feedback' THEN (SELECT companies_id FROM customer_feedback WHERE customer_feedback_id = p_entity_id)
            ELSE NULL
        END,
        p_entity_type,
        p_entity_id,
        'embedding_generation',
        3, -- Medium priority
        jsonb_build_object(
            'content', p_content,
            'content_type', p_content_type,
            'content_hash', content_hash
        );

    -- Log the operation
    INSERT INTO audit_logs (
        table_name, record_id, companies_id,
        action, change_description
    ) VALUES (
        p_entity_type || '_embeddings',
        p_entity_id,
        (SELECT companies_id FROM companies WHERE companies_id = p_entity_id),
        'EMBEDDING_QUEUED',
        'Embedding generation queued for ' || p_entity_type
    );
END;
$$ language 'plpgsql';

-- Function to perform semantic search
CREATE OR REPLACE FUNCTION semantic_search(
    p_query_embedding VECTOR(1536),
    p_entity_type VARCHAR DEFAULT NULL,
    p_companies_id UUID DEFAULT NULL,
    p_limit INTEGER DEFAULT 10,
    p_similarity_threshold DECIMAL DEFAULT 0.7
)
RETURNS TABLE(
    entity_type VARCHAR(50),
    entity_id UUID,
    similarity_score DECIMAL,
    content_preview TEXT,
    metadata JSONB
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        ve.entity_type,
        ve.entity_id,
        (1 - (ve.embedding_vector <=> p_query_embedding))::DECIMAL(5,3) as similarity_score,
        LEFT(COALESCE(ve.processed_content, ve.original_content), 200) as content_preview,
        ve.custom_metadata as metadata
    FROM vector_embeddings ve
    WHERE (1 - (ve.embedding_vector <=> p_query_embedding)) >= p_similarity_threshold
    AND (p_entity_type IS NULL OR ve.entity_type = p_entity_type)
    AND (p_companies_id IS NULL OR ve.companies_id = p_companies_id)
    AND ve.is_active = true
    ORDER BY ve.embedding_vector <=> p_query_embedding
    LIMIT p_limit;
END;
$$ language 'plpgsql';

-- Function to get customer sentiment summary
CREATE OR REPLACE FUNCTION get_customer_sentiment_summary(
    p_companies_id UUID,
    p_days INTEGER DEFAULT 30
)
RETURNS JSONB AS $$
DECLARE
    result JSONB;
BEGIN
    SELECT jsonb_build_object(
        'total_feedbacks', COUNT(*),
        'sentiment_distribution', jsonb_object_agg(
            COALESCE(sentiment_label, 'unanalyzed'),
            COUNT(*)
        ),
        'average_sentiment_score', AVG(sentiment_score),
        'urgency_distribution', jsonb_object_agg(
            COALESCE(urgency_level, 'unknown'),
            COUNT(*)
        ),
        'response_rate', (
            COUNT(CASE WHEN response_status = 'completed' THEN 1 END)::DECIMAL /
            NULLIF(COUNT(*), 0) * 100
        ),
        'average_response_time_hours', AVG(
            EXTRACT(EPOCH FROM (responded_at - created_at)) / 3600
        ),
        'top_issues', (
            SELECT jsonb_agg(jsonb_build_object(
                'topic', topic,
                'count', topic_count
            ))
            FROM (
                SELECT
                    jsonb_array_elements_text(topics_detected->'topics') as topic,
                    COUNT(*) as topic_count
                FROM customer_feedback
                WHERE companies_id = p_companies_id
                AND created_at >= CURRENT_DATE - INTERVAL '30 days'
                AND topics_detected IS NOT NULL
                GROUP BY jsonb_array_elements_text(topics_detected->'topics')
                ORDER BY topic_count DESC
                LIMIT 5
            ) topics
        ),
        'nps_score', AVG(nps_score),
        'recommendation_rate', (
            COUNT(CASE WHEN would_recommend = true THEN 1 END)::DECIMAL /
            NULLIF(COUNT(*), 0) * 100
        )
    ) INTO result
    FROM customer_feedback
    WHERE companies_id = p_companies_id
    AND created_at >= CURRENT_DATE - (p_days || ' days')::INTERVAL;

    RETURN COALESCE(result, '{}'::jsonb);
END;
$$ language 'plpgsql';

-- Function to generate AI insights from patterns
CREATE OR REPLACE FUNCTION generate_business_insights(
    p_companies_id UUID,
    p_insight_type VARCHAR DEFAULT 'general'
)
RETURNS INTEGER AS $$
DECLARE
    insight_count INTEGER := 0;
    sentiment_summary JSONB;
    customer_trends JSONB;
    business_metrics JSONB;
BEGIN
    -- Get sentiment summary
    sentiment_summary := get_customer_sentiment_summary(p_companies_id, 30);

    -- Generate sentiment-based insights
    IF (sentiment_summary->>'total_feedbacks')::INTEGER > 0 THEN
        -- Negative sentiment insight
        IF (sentiment_summary->>'average_sentiment_score')::DECIMAL < -0.3 THEN
            INSERT INTO ai_insights (
                companies_id, insight_type, title, description,
                confidence_score, impact_level, action_required,
                insight_data, created_by
            ) VALUES (
                p_companies_id, 'sentiment_alert',
                'Customer Sentiment Decline Detected',
                'Recent customer feedback shows declining sentiment. Immediate attention required.',
                0.85, 'high', true,
                sentiment_summary,
                (SELECT users_id FROM users WHERE companies_id = p_companies_id LIMIT 1)
            );
            insight_count := insight_count + 1;
        END IF;

        -- Low response rate insight
        IF (sentiment_summary->>'response_rate')::DECIMAL < 70 THEN
            INSERT INTO ai_insights (
                companies_id, insight_type, title, description,
                confidence_score, impact_level, action_required,
                insight_data, created_by
            ) VALUES (
                p_companies_id, 'operational_efficiency',
                'Low Customer Response Rate',
                'Customer feedback response rate is below 70%. Consider improving response times.',
                0.75, 'medium', true,
                sentiment_summary,
                (SELECT users_id FROM users WHERE companies_id = p_companies_id LIMIT 1)
            );
            insight_count := insight_count + 1;
        END IF;

        -- High urgency feedback insight
        IF (sentiment_summary->'urgency_distribution'->>'high')::INTEGER > 0 THEN
            INSERT INTO ai_insights (
                companies_id, insight_type, title, description,
                confidence_score, impact_level, action_required,
                insight_data, created_by
            ) VALUES (
                p_companies_id, 'urgent_issues',
                'High Priority Customer Issues',
                'Multiple high-priority customer issues require immediate attention.',
                0.90, 'critical', true,
                sentiment_summary,
                (SELECT users_id FROM users WHERE companies_id = p_companies_id LIMIT 1)
            );
            insight_count := insight_count + 1;
        END IF;
    END IF;

    -- Generate business performance insights
    INSERT INTO ai_insights (
        companies_id, insight_type, title, description,
        confidence_score, impact_level, insight_data, created_by
    )
    SELECT
        c.companies_id,
        'business_performance',
        'Business Performance Overview',
        'Monthly business performance summary with key metrics and trends.',
        0.80,
        'low',
        jsonb_build_object(
            'total_revenue', COALESCE(SUM(i.total_amount), 0),
            'invoice_count', COUNT(i.invoices_id),
            'customer_count', COUNT(DISTINCT i.customers_id),
            'avg_invoice_value', AVG(i.total_amount),
            'payment_rate', (
                COUNT(CASE WHEN i.payment_status = 'paid' THEN 1 END)::DECIMAL /
                NULLIF(COUNT(*), 0) * 100
            )
        ),
        (SELECT users_id FROM users WHERE companies_id = c.companies_id LIMIT 1)
    FROM companies c
    LEFT JOIN invoices i ON c.companies_id = i.companies_id
        AND i.invoice_date >= CURRENT_DATE - INTERVAL '30 days'
        AND i.status = 'issued'
    WHERE c.companies_id = p_companies_id
    GROUP BY c.companies_id;

    insight_count := insight_count + 1;

    RETURN insight_count;
END;
$$ language 'plpgsql';

-- Function to refresh AI analytics views
CREATE OR REPLACE FUNCTION refresh_ai_analytics_views()
RETURNS VOID AS $$
BEGIN
    -- Refresh materialized views
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_customer_similarity_analysis;
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_invoice_pattern_analysis;
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_competitive_market_analysis;

    -- Generate new insights for all active companies
    PERFORM generate_business_insights(companies_id)
    FROM companies
    WHERE is_active = true;
END;
$$ language 'plpgsql';

-- Create refresh function for materialized views
CREATE OR REPLACE FUNCTION refresh_analytics_views()
RETURNS VOID AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_monthly_revenue;
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_customer_analytics;
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_ai_insights_performance;
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_financial_position;

    -- Also refresh AI views
    PERFORM refresh_ai_analytics_views();
END;
$$ language 'plpgsql';

-- Create maintenance function
CREATE OR REPLACE FUNCTION perform_system_maintenance()
RETURNS VOID AS $$
BEGIN
    -- Update performance metrics
    INSERT INTO performance_metrics (metric_name, metric_value, metric_type, source_system)
    SELECT
        'database_size_gb',
        pg_database_size(current_database()) / 1024.0 / 1024.0 / 1024.0,
        'system',
        'maintenance'
    WHERE NOT EXISTS (
        SELECT 1 FROM performance_metrics
        WHERE metric_name = 'database_size_gb'
        AND date_trunc('day', recorded_at) = CURRENT_DATE
    );

    -- Clean up old AI processing queue items
    DELETE FROM ai_processing_queue
    WHERE status IN ('completed', 'failed')
    AND completed_at < CURRENT_DATE - INTERVAL '7 days';

    -- Clean up old sentiment analysis results
    DELETE FROM sentiment_analysis_results
    WHERE created_at < CURRENT_DATE - INTERVAL '1 year';

    -- Refresh materialized views
    PERFORM refresh_analytics_views();

    -- Clean up old data (older than 7 years for compliance)
    DELETE FROM audit_log WHERE action_timestamp < CURRENT_DATE - INTERVAL '7 years';
    DELETE FROM performance_metrics WHERE recorded_at < CURRENT_DATE - INTERVAL '2 years';
END;
$$ language 'plpgsql';

-- ============================================================================
-- AI TRIGGERS AND AUTOMATION
-- ============================================================================

-- Trigger for automatic sentiment analysis on customer feedback
DROP TRIGGER IF EXISTS trigger_customer_feedback_sentiment ON customer_feedback;
CREATE TRIGGER trigger_customer_feedback_sentiment
    AFTER INSERT ON customer_feedback
    FOR EACH ROW
    WHEN (NEW.ai_processed = false)
    EXECUTE FUNCTION analyze_customer_feedback_sentiment();

-- Trigger for automatic embedding generation on companies
DROP TRIGGER IF EXISTS trigger_company_embedding ON companies;
CREATE TRIGGER trigger_company_embedding
    AFTER INSERT OR UPDATE ON companies
    FOR EACH ROW
    WHEN (NEW.business_description IS NOT NULL AND (OLD.business_description IS NULL OR OLD.business_description != NEW.business_description))
    EXECUTE FUNCTION generate_entity_embedding('companies', NEW.companies_id, NEW.business_description, 'business_description');

-- Trigger for automatic embedding generation on customers
DROP TRIGGER IF EXISTS trigger_customer_embedding ON customers;
CREATE TRIGGER trigger_customer_embedding
    AFTER INSERT OR UPDATE ON customers
    FOR EACH ROW
    WHEN (NEW.business_description IS NOT NULL AND (OLD.business_description IS NULL OR OLD.business_description != NEW.business_description))
    EXECUTE FUNCTION generate_entity_embedding('customers', NEW.customers_id, NEW.business_description, 'business_description');

-- Trigger for automatic embedding generation on products
DROP TRIGGER IF EXISTS trigger_product_embedding ON products;
CREATE TRIGGER trigger_product_embedding
    AFTER INSERT OR UPDATE ON products
    FOR EACH ROW
    WHEN (NEW.description IS NOT NULL AND (OLD.description IS NULL OR OLD.description != NEW.description))
    EXECUTE FUNCTION generate_entity_embedding('products', NEW.products_id, NEW.description, 'product_description');

-- Trigger for audit logging on all major tables
CREATE OR REPLACE FUNCTION audit_all_changes()
RETURNS TRIGGER AS $$
DECLARE
    companies_id_val UUID;
    users_id_val UUID;
BEGIN
    -- Get company and user context
    BEGIN
        companies_id_val := COALESCE(NEW.companies_id, OLD.companies_id);
        users_id_val := COALESCE(NEW.updated_by, NEW.created_by);
    EXCEPTION WHEN OTHERS THEN
        companies_id_val := NULL;
        users_id_val := NULL;
    END;

    -- Insert audit record
    INSERT INTO audit_logs (
        table_name, record_id, companies_id, user_id,
        action, action_timestamp, old_values, new_values,
        change_description
    ) VALUES (
        TG_TABLE_NAME,
        COALESCE(NEW.id, OLD.id),
        companies_id_val,
        users_id_val,
        TG_OP,
        CURRENT_TIMESTAMP,
        CASE WHEN TG_OP = 'DELETE' THEN row_to_json(OLD) ELSE NULL END,
        CASE WHEN TG_OP = 'INSERT' THEN row_to_json(NEW) ELSE row_to_json(NEW) END,
        TG_OP || ' operation on ' || TG_TABLE_NAME
    );

    RETURN COALESCE(NEW, OLD);
END;
$$ language 'plpgsql';

-- Apply audit triggers to major tables (sample - can be expanded)
DROP TRIGGER IF EXISTS audit_companies ON companies;
CREATE TRIGGER audit_companies AFTER INSERT OR UPDATE OR DELETE ON companies
    FOR EACH ROW EXECUTE FUNCTION audit_all_changes();

DROP TRIGGER IF EXISTS audit_customers ON customers;
CREATE TRIGGER audit_customers AFTER INSERT OR UPDATE OR DELETE ON customers
    FOR EACH ROW EXECUTE FUNCTION audit_all_changes();

DROP TRIGGER IF EXISTS audit_invoices ON invoices;
CREATE TRIGGER audit_invoices AFTER INSERT OR UPDATE OR DELETE ON invoices
    FOR EACH ROW EXECUTE FUNCTION audit_all_changes();

-- Create automated maintenance schedule
SELECT cron.schedule('system-maintenance', '0 2 * * *', 'SELECT perform_system_maintenance();');
SELECT cron.schedule('refresh-analytics', '0 */6 * * *', 'SELECT refresh_analytics_views();');
SELECT cron.schedule('refresh-ai-views', '0 */12 * * *', 'SELECT refresh_ai_similarity_views();');

-- Function to refresh AI similarity views
CREATE OR REPLACE FUNCTION refresh_ai_similarity_views()
RETURNS VOID AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_customer_similarity_analysis;
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_invoice_pattern_analysis;
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_competitive_market_analysis;
END;
$$ language 'plpgsql';

-- ============================================================================
-- FULL UNICODE TEXT SUPPORT FUNCTIONS
-- ============================================================================

-- Function to normalize Unicode text for better search (supports all languages)
CREATE OR REPLACE FUNCTION normalize_unicode_text(input_text TEXT)
RETURNS TEXT AS $$
BEGIN
    -- Convert to lowercase
    input_text := LOWER(input_text);

    -- Remove accents and diacritics using unaccent
    input_text := unaccent(input_text);

    -- Remove special characters but keep Unicode letters, numbers, and spaces
    input_text := REGEXP_REPLACE(input_text, '[^\w\s]', ' ', 'g');
    input_text := REGEXP_REPLACE(input_text, '\s+', ' ', 'g');
    input_text := TRIM(input_text);

    RETURN input_text;
END;
$$ language 'plpgsql' IMMUTABLE;

-- Function for universal Unicode similarity search
CREATE OR REPLACE FUNCTION unicode_similarity(text1 TEXT, text2 TEXT)
RETURNS REAL AS $$
DECLARE
    norm_text1 TEXT;
    norm_text2 TEXT;
BEGIN
    -- Normalize both texts using Unicode normalization
    norm_text1 := normalize_unicode_text(text1);
    norm_text2 := normalize_unicode_text(text2);

    -- Return trigram similarity
    RETURN SIMILARITY(norm_text1, norm_text2);
END;
$$ language 'plpgsql' IMMUTABLE;

-- Function to detect script type (Latin, Cyrillic, Arabic, Chinese, etc.)
CREATE OR REPLACE FUNCTION detect_script_type(input_text TEXT)
RETURNS TEXT AS $$
BEGIN
    -- Check for Cyrillic script
    IF input_text ~ '[\u0400-\u04FF\u0500-\u052F]' THEN
        RETURN 'cyrillic';
    -- Check for Arabic script
    ELSIF input_text ~ '[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]' THEN
        RETURN 'arabic';
    -- Check for Chinese/Japanese/Korean (CJK)
    ELSIF input_text ~ '[\u4E00-\u9FFF\u3400-\u4DBF\u20000-\u2A6DF\u2A700-\u2B73F\u2B740-\u2B81F\u2B820-\u2CEAF]' THEN
        RETURN 'cjk';
    -- Check for Devanagari (Hindi, Sanskrit)
    ELSIF input_text ~ '[\u0900-\u097F\uA8E0-\uA8FF]' THEN
        RETURN 'devanagari';
    -- Check for Latin with diacritics
    ELSIF input_text ~ '[àáâãäåæçèéêëìíîïðñòóôõö÷øùúûüýþÿ]' THEN
        RETURN 'latin_diacritics';
    ELSE
        RETURN 'latin_basic';
    END IF;
END;
$$ language 'plpgsql' IMMUTABLE;

-- Function to create multilingual searchable text
CREATE OR REPLACE FUNCTION create_multilingual_search_text(input_text TEXT)
RETURNS TEXT AS $$
DECLARE
    result TEXT;
    script_type TEXT;
BEGIN
    -- Start with original text
    result := input_text;

    -- Get script type
    script_type := detect_script_type(input_text);

    -- Add normalized version
    result := result || ' ' || normalize_unicode_text(input_text);

    -- Add unaccented version for better matching
    result := result || ' ' || unaccent(input_text);

    -- Add language-specific variations based on script type
    CASE script_type
        WHEN 'cyrillic' THEN
            -- Add Serbian-specific transliterations
            result := result || ' ' || REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(input_text,
                    'č', 'c'), 'ć', 'c'), 'đ', 'dj'), 'š', 's'), 'ž', 'z');
        WHEN 'latin_diacritics' THEN
            -- Keep diacritic variations for European languages
            result := result || ' ' || unaccent(input_text);
        ELSE
            -- For other scripts, rely on Unicode normalization
            result := result || ' ' || normalize_unicode_text(input_text);
    END CASE;

    RETURN TRIM(result);
END;
$$ language 'plpgsql' IMMUTABLE;

-- Function to get Unicode normalization (enhanced)
CREATE OR REPLACE FUNCTION unicode_normalize_text(input_text TEXT, form TEXT DEFAULT 'NFC')
RETURNS TEXT AS $$
BEGIN
    -- Use PostgreSQL's built-in normalize function for Unicode normalization
    -- Forms: NFC, NFD, NFKC, NFKD (canonical composition/decomposition)
    RETURN normalize(input_text, form);
EXCEPTION
    WHEN undefined_function THEN
        -- Fallback for older PostgreSQL versions
        RETURN input_text;
    WHEN invalid_parameter_value THEN
        -- Fallback for invalid normalization forms
        RETURN input_text;
END;
$$ language 'plpgsql' IMMUTABLE;

-- Function to get text encoding information
CREATE OR REPLACE FUNCTION get_text_encoding_info(input_text TEXT)
RETURNS JSONB AS $$
DECLARE
    result JSONB;
BEGIN
    SELECT jsonb_build_object(
        'script_type', detect_script_type(input_text),
        'length_bytes', LENGTH(input_text::bytea),
        'length_chars', CHAR_LENGTH(input_text),
        'contains_unicode', input_text ~ '[^\x00-\x7F]',
        'is_normalized_nfc', input_text = normalize(input_text, 'NFC'),
        'is_normalized_nfd', input_text = normalize(input_text, 'NFD'),
        'encoding', 'UTF8'
    ) INTO result;

    RETURN result;
END;
$$ language 'plpgsql' IMMUTABLE;

-- ============================================================================
-- COMPLETE DATABASE RESET SCRIPT
-- ============================================================================

-- Use this section to completely reset the database when needed
-- Run as postgres superuser

-- 1. Disconnect all users from the database
-- SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = 'ai_valido_online';

-- 2. Drop the database
-- DROP DATABASE IF EXISTS ai_valido_online;

-- 3. Create fresh database with Unicode support
-- CREATE DATABASE ai_valido_online
--     WITH
--     OWNER = postgres
--     ENCODING = 'UTF8'
--     LC_COLLATE = 'C.UTF-8'
--     LC_CTYPE = 'C.UTF-8'
--     TABLESPACE = pg_default
--     CONNECTION LIMIT = -1
--     TEMPLATE = template0;

-- 4. Connect to the new database
-- \c ai_valido_online postgres;

-- 5. Run this entire structure file to recreate all tables, functions, and indexes
-- (This file contains all the CREATE statements)

-- 6. Finally, run the data file to populate with sample data
-- \i Postgres_ai_valido_master_data.sql;

-- ============================================================================
-- TROUBLESHOOTING AND MAINTENANCE
-- ============================================================================

-- Quick database health check
-- SELECT
--     current_database() as database_name,
--     current_user as current_user,
--     encoding as database_encoding,
--     datcollate as collation,
--     datctype as character_type
-- FROM pg_database WHERE datname = current_database();

-- Check table sizes
-- SELECT
--     schemaname,
--     tablename,
--     pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
-- FROM pg_tables
-- WHERE schemaname = 'public'
-- ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Check for Unicode issues
-- SELECT
--     table_name,
--     column_name,
--     data_type
-- FROM information_schema.columns
-- WHERE table_schema = 'public'
-- AND data_type IN ('character varying', 'text')
-- ORDER BY table_name, column_name;

-- ============================================================================
-- DOCUMENTATION AND COMMENTS
-- ============================================================================

COMMENT ON DATABASE ai_valido_online IS 'ValidoAI - Comprehensive Serbian Business Management System with AI/LLM integration';
COMMENT ON SCHEMA public IS 'Main schema containing all business data and AI features';

-- Add helpful comments to key tables
COMMENT ON TABLE companies IS 'Multi-tenant company management with Serbian business compliance';
COMMENT ON TABLE users IS 'User management with advanced authentication and Serbian citizen data';
COMMENT ON TABLE general_ledger IS 'Double-entry bookkeeping system with SRPS compliance';
COMMENT ON TABLE invoices IS 'Comprehensive invoicing with PDV and e-invoice support';
COMMENT ON TABLE ai_insights IS 'AI-generated business insights and recommendations';
COMMENT ON TABLE vector_embeddings IS 'AI embeddings for semantic search across all entities';
COMMENT ON TABLE chat_sessions IS 'AI-powered chat system for business communication';

-- ============================================================================
-- END OF MASTER STRUCTURE FILE
-- ============================================================================
