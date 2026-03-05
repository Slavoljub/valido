-- AI Valido Online Database Structure Implementation
-- Merged from ai_valido_online_structure.sql and 14.08.2025valido_online_ai.sql
-- Optimized for PostgreSQL with RBAC, RLS, and AI integration
-- Date: January 2025

-- Enable Extensions for 10PB+ Data Support
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS plpython3u;
CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS citus;
CREATE EXTENSION IF NOT EXISTS timescaledb;
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;
CREATE EXTENSION IF NOT EXISTS pg_buffercache;
CREATE EXTENSION IF NOT EXISTS pg_prewarm;
CREATE EXTENSION IF NOT EXISTS pg_similarity;
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE EXTENSION IF NOT EXISTS btree_gist;
CREATE EXTENSION IF NOT EXISTS btree_gin;
CREATE EXTENSION IF NOT EXISTS unaccent;
CREATE EXTENSION IF NOT EXISTS pg_freespacemap;
CREATE EXTENSION IF NOT EXISTS pg_stat_monitor;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS pg_cron;

-- PostgreSQL Roles for RBAC
CREATE ROLE ai_valido_developer WITH LOGIN PASSWORD 'secure_password';
CREATE ROLE ai_valido_admin WITH LOGIN PASSWORD 'secure_password';
CREATE ROLE ai_valido_accountant WITH LOGIN PASSWORD 'secure_password';
CREATE ROLE ai_valido_manager WITH LOGIN PASSWORD 'secure_password';
CREATE ROLE ai_valido_hr WITH LOGIN PASSWORD 'secure_password';
CREATE ROLE ai_valido_support WITH LOGIN PASSWORD 'secure_password';
CREATE ROLE ai_valido_demo WITH LOGIN PASSWORD 'secure_password';

-- Countries Table with Comprehensive Information
CREATE TABLE countries (
    countries_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    iso_code CHAR(2) UNIQUE NOT NULL,
    iso_code_3 CHAR(3) UNIQUE,
    iso_numeric CHAR(3),
    name VARCHAR(100) NOT NULL,
    native_name VARCHAR(100),
    capital VARCHAR(100),
    region VARCHAR(50),
    subregion VARCHAR(50),
    latitude DECIMAL(10,8),
    longitude DECIMAL(11,8),
    area_km2 BIGINT,
    population BIGINT,
    currency_code CHAR(3),
    currency_name VARCHAR(50),
    currency_symbol VARCHAR(5),
    phone_code VARCHAR(10),
    languages JSONB,
    timezones TEXT[],
    flag_emoji VARCHAR(10),
    flag_svg_url TEXT,
    flag_png_url TEXT,
    coat_of_arms_url TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Core Tables
CREATE TABLE companies (
    companies_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_name VARCHAR(255) NOT NULL,
    legal_name VARCHAR(255),
    tax_id VARCHAR(20) UNIQUE NOT NULL,
    registration_number VARCHAR(20) UNIQUE NOT NULL,
    vat_number VARCHAR(20),
    address_line1 VARCHAR(255),
    address_line2 VARCHAR(255),
    city VARCHAR(100),
    state_province VARCHAR(100),
    postal_code VARCHAR(20),
    countries_id UUID REFERENCES countries(countries_id),
    country VARCHAR(100) DEFAULT 'Serbia',
    phone VARCHAR(20),
    mobile VARCHAR(20),
    email VARCHAR(100),
    website VARCHAR(100),
    industry VARCHAR(100),
    company_size VARCHAR(50),
    founded_date DATE,
    parent_company_id UUID REFERENCES companies(companies_id),
    company_logo_url TEXT,
    company_description TEXT,
    business_hours JSONB,
    time_zone VARCHAR(50) DEFAULT 'Europe/Belgrade',
    default_currency CHAR(3) DEFAULT 'RSD',
    fiscal_year_start_month INTEGER DEFAULT 1,
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    verification_date TIMESTAMP,
    notes TEXT,
    metadata JSONB,
    embedding_vector VECTOR(1536),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP
);

-- Enhanced Users Table with Comprehensive Authentication Support
CREATE TABLE users (
    users_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    companies_id UUID REFERENCES companies(companies_id),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(20),
    password_hash VARCHAR(255),
    password_salt VARCHAR(255),
    password_changed_at TIMESTAMP,
    password_expires_at TIMESTAMP,
    password_strength_score INTEGER DEFAULT 0,

    -- Personal Information
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    middle_name VARCHAR(50),
    display_name VARCHAR(100),
    date_of_birth DATE,
    gender VARCHAR(20),
    nationality VARCHAR(50),
    profile_picture_url TEXT,
    avatar_url TEXT,
    bio TEXT,
    timezone VARCHAR(50) DEFAULT 'Europe/Belgrade',
    language VARCHAR(10) DEFAULT 'sr',

    -- Contact Information
    secondary_email VARCHAR(100),
    emergency_contact_name VARCHAR(100),
    emergency_contact_phone VARCHAR(20),
    emergency_contact_relationship VARCHAR(50),

    -- Authentication & Security
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    is_locked BOOLEAN DEFAULT FALSE,
    lockout_until TIMESTAMP,
    failed_login_attempts INTEGER DEFAULT 0,
    last_login_at TIMESTAMP,
    last_login_ip INET,
    last_failed_login_at TIMESTAMP,
    account_expires_at TIMESTAMP,

    -- Two-Factor Authentication
    two_factor_enabled BOOLEAN DEFAULT FALSE,
    two_factor_secret VARCHAR(32),
    two_factor_backup_codes TEXT[], -- Array of backup codes
    two_factor_method VARCHAR(20) DEFAULT 'totp', -- totp, sms, email, push
    two_factor_phone VARCHAR(20),
    two_factor_email VARCHAR(100),

    -- Email Verification
    email_verified BOOLEAN DEFAULT FALSE,
    email_verification_token VARCHAR(255),
    email_verification_token_expires_at TIMESTAMP,
    email_verification_sent_at TIMESTAMP,

    -- Phone/SMS Verification
    phone_verified BOOLEAN DEFAULT FALSE,
    phone_verification_code VARCHAR(10),
    phone_verification_code_expires_at TIMESTAMP,
    phone_verification_sent_at TIMESTAMP,
    sms_otp_enabled BOOLEAN DEFAULT FALSE,

    -- External Authentication Providers
    keycloak_id VARCHAR(255),
    keycloak_username VARCHAR(255),
    openid_issuer VARCHAR(255),
    openid_subject VARCHAR(255),
    ad_username VARCHAR(255),
    ad_domain VARCHAR(255),
    ad_sid VARCHAR(255),
    ad_guid UUID,
    saml_id VARCHAR(255),
    oauth_google_id VARCHAR(255),
    oauth_github_id VARCHAR(255),
    oauth_microsoft_id VARCHAR(255),
    oauth_linkedin_id VARCHAR(255),

    -- Session Management
    session_max_lifetime INTEGER DEFAULT 3600, -- seconds
    session_idle_timeout INTEGER DEFAULT 1800, -- seconds
    max_concurrent_sessions INTEGER DEFAULT 5,
    force_password_change BOOLEAN DEFAULT FALSE,

    -- Security Settings
    password_policy_id UUID,
    security_questions_enabled BOOLEAN DEFAULT FALSE,
    security_questions JSONB, -- Array of security questions and answers
    trusted_devices JSONB, -- Array of trusted device information
    login_history JSONB, -- Recent login attempts
    risk_score DECIMAL(5,2) DEFAULT 0.00,

    -- Preferences
    theme_preference VARCHAR(20) DEFAULT 'system',
    dashboard_layout JSONB,
    notification_preferences JSONB,
    privacy_settings JSONB,

    -- Audit & Compliance
    created_by UUID REFERENCES users(users_id),
    approved_by UUID REFERENCES users(users_id),
    approved_at TIMESTAMP,
    last_password_reset_at TIMESTAMP,
    password_reset_token VARCHAR(255),
    password_reset_token_expires_at TIMESTAMP,

    -- System Integration
    integration_data JSONB, -- For external system integrations
    custom_fields JSONB, -- For extensible user attributes
    tags TEXT[], -- Array of user tags
    groups TEXT[], -- Array of user groups
    roles TEXT[], -- Array of user roles

    -- AI & Analytics
    embedding_vector VECTOR(1536),
    behavior_patterns JSONB,
    risk_profile JSONB,

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP,

    -- Soft Delete Support
    is_deleted BOOLEAN DEFAULT FALSE
);

-- User-Company Access Management
CREATE TABLE user_company_access (
    user_company_access_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(users_id) ON DELETE CASCADE,
    company_id UUID NOT NULL REFERENCES companies(companies_id) ON DELETE CASCADE,
    access_level VARCHAR(20) DEFAULT 'user', -- owner, admin, manager, employee, contractor, external
    role_type VARCHAR(30) DEFAULT 'employee', -- employee, contractor, consultant, partner, customer
    department VARCHAR(100),
    job_title VARCHAR(100),
    manager_id UUID REFERENCES users(users_id),

    -- Access Permissions
    can_switch_to_company BOOLEAN DEFAULT TRUE,
    can_manage_company BOOLEAN DEFAULT FALSE,
    can_invite_users BOOLEAN DEFAULT FALSE,
    can_manage_billing BOOLEAN DEFAULT FALSE,
    can_access_financial_data BOOLEAN DEFAULT FALSE,
    can_access_hr_data BOOLEAN DEFAULT FALSE,
    can_access_customer_data BOOLEAN DEFAULT FALSE,

    -- Status and Dates
    status VARCHAR(20) DEFAULT 'active', -- active, inactive, suspended, pending, invited
    invited_at TIMESTAMP,
    activated_at TIMESTAMP,
    last_accessed_at TIMESTAMP,
    expires_at TIMESTAMP,

    -- Invitation and Onboarding
    invitation_token VARCHAR(255),
    invitation_sent_at TIMESTAMP,
    invitation_accepted_at TIMESTAMP,
    invited_by UUID REFERENCES users(users_id),
    onboarding_completed BOOLEAN DEFAULT FALSE,
    onboarding_steps_completed JSONB,

    -- Security and Audit
    ip_whitelist TEXT[], -- Array of allowed IP addresses
    session_timeout INTEGER DEFAULT 3600, -- seconds
    mfa_required BOOLEAN DEFAULT FALSE,
    risk_score DECIMAL(5,2) DEFAULT 0.00,

    -- Preferences
    default_dashboard VARCHAR(50) DEFAULT 'overview',
    notification_preferences JSONB,
    company_specific_settings JSONB,

    -- Integration
    external_user_id VARCHAR(100), -- ID from external systems
    integration_data JSONB,

    -- Audit
    created_by UUID REFERENCES users(users_id),
    approved_by UUID REFERENCES users(users_id),
    approved_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Constraints
    UNIQUE(user_id, company_id),

    -- Indexes for performance
    CONSTRAINT valid_access_level CHECK (access_level IN ('owner', 'admin', 'manager', 'employee', 'contractor', 'external')),
    CONSTRAINT valid_status CHECK (status IN ('active', 'inactive', 'suspended', 'pending', 'invited'))
);

CREATE TABLE user_roles (
    user_roles_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    role_name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    permissions JSONB, -- Detailed permissions object
    role_level INTEGER DEFAULT 1, -- 1=Basic, 2=Standard, 3=Advanced, 4=Admin, 5=Owner
    is_system_role BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE user_permissions (
    user_permissions_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_roles_id UUID REFERENCES user_roles(user_roles_id),
    permission_name VARCHAR(100) NOT NULL,
    description TEXT,
    resource_type VARCHAR(50), -- company, user, financial, hr, etc.
    resource_id UUID, -- Specific resource if needed
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Company Switching and Session Management
CREATE TABLE user_company_sessions (
    user_company_session_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(users_id) ON DELETE CASCADE,
    company_id UUID NOT NULL REFERENCES companies(companies_id) ON DELETE CASCADE,
    session_id VARCHAR(255) NOT NULL, -- Web session ID
    ip_address INET,
    user_agent TEXT,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_activity_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    device_info JSONB,
    location_info JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Company Switching Audit Log
CREATE TABLE company_switch_audit (
    company_switch_audit_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(users_id) ON DELETE CASCADE,
    from_company_id UUID REFERENCES companies(companies_id) ON DELETE SET NULL,
    to_company_id UUID NOT NULL REFERENCES companies(companies_id) ON DELETE CASCADE,
    switch_reason VARCHAR(100), -- manual, automatic, forced, session_timeout
    switch_method VARCHAR(50), -- ui, api, cli, system
    session_id VARCHAR(255),
    ip_address INET,
    user_agent TEXT,
    success BOOLEAN DEFAULT TRUE,
    error_message TEXT,
    switched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Company Invitation System
CREATE TABLE company_invitations (
    company_invitation_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID NOT NULL REFERENCES companies(companies_id) ON DELETE CASCADE,
    invited_email VARCHAR(255) NOT NULL,
    invited_name VARCHAR(100),
    invited_by UUID NOT NULL REFERENCES users(users_id),
    invitation_token VARCHAR(255) UNIQUE NOT NULL,
    access_level VARCHAR(20) DEFAULT 'employee',
    role_type VARCHAR(30) DEFAULT 'employee',
    department VARCHAR(100),
    job_title VARCHAR(100),
    custom_message TEXT,
    expires_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP + INTERVAL '7 days',
    status VARCHAR(20) DEFAULT 'pending', -- pending, accepted, expired, cancelled
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    accepted_at TIMESTAMP,
    accepted_by UUID REFERENCES users(users_id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User Company Preferences
CREATE TABLE user_company_preferences (
    user_company_preference_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(users_id) ON DELETE CASCADE,
    company_id UUID NOT NULL REFERENCES companies(companies_id) ON DELETE CASCADE,
    preference_key VARCHAR(100) NOT NULL,
    preference_value TEXT,
    preference_type VARCHAR(20) DEFAULT 'string', -- string, number, boolean, json
    is_system_preference BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(user_id, company_id, preference_key)
);

-- Company Teams and Departments
CREATE TABLE company_departments (
    company_department_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID NOT NULL REFERENCES companies(companies_id) ON DELETE CASCADE,
    department_name VARCHAR(100) NOT NULL,
    department_code VARCHAR(20),
    parent_department_id UUID REFERENCES company_departments(company_department_id),
    manager_id UUID REFERENCES users(users_id),
    description TEXT,
    budget_allocated DECIMAL(15,2),
    budget_used DECIMAL(15,2),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(company_id, department_name)
);

-- User Department Assignments
CREATE TABLE user_department_assignments (
    user_department_assignment_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(users_id) ON DELETE CASCADE,
    company_id UUID NOT NULL REFERENCES companies(companies_id) ON DELETE CASCADE,
    department_id UUID NOT NULL REFERENCES company_departments(company_department_id) ON DELETE CASCADE,
    assignment_type VARCHAR(20) DEFAULT 'primary', -- primary, secondary, temporary
    start_date DATE NOT NULL,
    end_date DATE,
    is_active BOOLEAN DEFAULT TRUE,
    created_by UUID REFERENCES users(users_id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(user_id, company_id, department_id, assignment_type)
);

-- Financial Tables
CREATE TABLE fiscal_years (
    fiscal_years_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    companies_id UUID REFERENCES companies(companies_id),
    year INT NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    status VARCHAR(20) DEFAULT 'open',
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE chart_of_accounts (
    chart_of_accounts_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    companies_id UUID REFERENCES companies(companies_id),
    account_number VARCHAR(20) NOT NULL,
    account_name VARCHAR(255) NOT NULL,
    account_type VARCHAR(50),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE general_ledger (
    general_ledger_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    companies_id UUID REFERENCES companies(companies_id),
    fiscal_years_id UUID REFERENCES fiscal_years(fiscal_years_id),
    transaction_date DATE NOT NULL,
    chart_of_accounts_id UUID REFERENCES chart_of_accounts(chart_of_accounts_id),
    debit_amount DECIMAL(15,2),
    credit_amount DECIMAL(15,2),
    currency_code CHAR(3) DEFAULT 'RSD',
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) PARTITION BY RANGE (transaction_date);

-- Invoice Tables
CREATE TABLE invoices (
    invoices_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    companies_id UUID REFERENCES companies(companies_id),
    invoice_number VARCHAR(50) UNIQUE NOT NULL,
    invoice_date DATE NOT NULL,
    due_date DATE NOT NULL,
    total_amount DECIMAL(15,2) NOT NULL,
    currency_code CHAR(3) DEFAULT 'RSD',
    status VARCHAR(20) DEFAULT 'draft',
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE invoice_items (
    invoice_items_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    invoices_id UUID REFERENCES invoices(invoices_id),
    item_name VARCHAR(255) NOT NULL,
    quantity DECIMAL(10,2) NOT NULL,
    unit_price DECIMAL(15,2) NOT NULL,
    total_price DECIMAL(15,2) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Bank Tables
CREATE TABLE bank_accounts (
    bank_accounts_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    companies_id UUID REFERENCES companies(companies_id),
    bank_name VARCHAR(100) NOT NULL,
    account_number VARCHAR(50) UNIQUE NOT NULL,
    currency_code CHAR(3) DEFAULT 'RSD',
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE bank_statements (
    bank_statements_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    companies_id UUID REFERENCES companies(companies_id),
    bank_accounts_id UUID REFERENCES bank_accounts(bank_accounts_id),
    statement_date DATE NOT NULL,
    transaction_date DATE NOT NULL,
    amount DECIMAL(15,2) NOT NULL,
    currency_code CHAR(3) DEFAULT 'RSD',
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) PARTITION BY RANGE (transaction_date);

-- CRM Tables
CREATE TABLE crm_contacts (
    crm_contacts_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    companies_id UUID REFERENCES companies(companies_id),
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    email VARCHAR(100),
    phone VARCHAR(20),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE crm_leads (
    crm_leads_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    companies_id UUID REFERENCES companies(companies_id),
    lead_name VARCHAR(255) NOT NULL,
    expected_revenue DECIMAL(15,2),
    currency_code CHAR(3) DEFAULT 'RSD',
    status VARCHAR(20) DEFAULT 'new',
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE crm_opportunities (
    crm_opportunities_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    companies_id UUID REFERENCES companies(companies_id),
    opportunity_name VARCHAR(255) NOT NULL,
    expected_revenue DECIMAL(15,2),
    currency_code CHAR(3) DEFAULT 'RSD',
    status VARCHAR(20) DEFAULT 'open',
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- HR Tables with Enhanced Salary and Reporting Support
CREATE TABLE employees (
    employees_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    companies_id UUID REFERENCES companies(companies_id),
    user_id UUID REFERENCES users(users_id), -- Link to users table
    employee_number VARCHAR(50) UNIQUE NOT NULL,
    national_id VARCHAR(20),
    tax_id VARCHAR(20),
    social_security_number VARCHAR(20),

    -- Personal Information
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    middle_name VARCHAR(50),
    preferred_name VARCHAR(50),
    date_of_birth DATE,
    gender VARCHAR(20),
    marital_status VARCHAR(20),
    nationality VARCHAR(50),

    -- Employment Information
    hire_date DATE NOT NULL,
    termination_date DATE,
    employment_status VARCHAR(20) DEFAULT 'active', -- active, terminated, on_leave, suspended
    employment_type VARCHAR(20) DEFAULT 'full_time', -- full_time, part_time, contract, intern
    job_title VARCHAR(100),
    department VARCHAR(100),
    division VARCHAR(100),
    manager_id UUID REFERENCES employees(employees_id),
    work_location VARCHAR(100),
    office_location VARCHAR(100),

    -- Salary Information
    base_salary DECIMAL(15,2),
    hourly_rate DECIMAL(10,2),
    currency_code CHAR(3) DEFAULT 'RSD',
    salary_frequency VARCHAR(20) DEFAULT 'monthly', -- monthly, biweekly, weekly, hourly
    overtime_eligible BOOLEAN DEFAULT FALSE,
    overtime_rate DECIMAL(5,2) DEFAULT 1.5,

    -- Compensation Components
    allowances JSONB, -- housing, transport, meal, phone allowances
    bonuses JSONB, -- performance, annual, project bonuses
    deductions JSONB, -- tax, insurance, loan deductions
    benefits JSONB, -- health insurance, retirement, vacation days

    -- Work Schedule
    work_schedule JSONB, -- weekly schedule with hours
    standard_hours_per_week DECIMAL(5,2) DEFAULT 40.0,
    vacation_days_per_year INTEGER DEFAULT 25,
    sick_days_per_year INTEGER DEFAULT 10,

    -- Contact Information
    work_email VARCHAR(100),
    personal_email VARCHAR(100),
    work_phone VARCHAR(20),
    personal_phone VARCHAR(20),
    emergency_contact_name VARCHAR(100),
    emergency_contact_phone VARCHAR(20),
    emergency_contact_relationship VARCHAR(50),
    address_line1 VARCHAR(255),
    address_line2 VARCHAR(255),
    city VARCHAR(100),
    state_province VARCHAR(100),
    postal_code VARCHAR(20),
    countries_id UUID REFERENCES countries(countries_id),

    -- Bank Information
    bank_name VARCHAR(100),
    bank_account_number VARCHAR(50),
    bank_routing_number VARCHAR(20),
    payment_method VARCHAR(20) DEFAULT 'bank_transfer', -- bank_transfer, check, cash, direct_deposit

    -- Tax Information
    tax_residence_country VARCHAR(50),
    tax_withholding_rate DECIMAL(5,2),
    tax_bracket VARCHAR(20),

    -- Performance & Development
    performance_rating DECIMAL(3,2),
    last_performance_review DATE,
    next_performance_review DATE,
    training_completed JSONB,
    skills JSONB,
    certifications JSONB,

    -- System Integration
    hr_system_id VARCHAR(100), -- External HR system ID
    payroll_system_id VARCHAR(100), -- External payroll system ID
    ad_username VARCHAR(255), -- Active Directory username
    integration_data JSONB,

    -- AI & Analytics
    embedding_vector VECTOR(1536),
    risk_profile JSONB,
    behavioral_analytics JSONB,

    -- Audit & Compliance
    created_by UUID REFERENCES users(users_id),
    approved_by UUID REFERENCES users(users_id),
    approved_at TIMESTAMP,

    -- Status & Timestamps
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP
);

CREATE TABLE payroll (
    payroll_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    companies_id UUID REFERENCES companies(companies_id),
    employees_id UUID REFERENCES employees(employees_id),
    payroll_period_start DATE NOT NULL,
    payroll_period_end DATE NOT NULL,
    payroll_date DATE NOT NULL,
    pay_schedule VARCHAR(20) DEFAULT 'monthly', -- monthly, biweekly, weekly, semimonthly

    -- Salary Components
    base_salary DECIMAL(15,2) NOT NULL,
    overtime_hours DECIMAL(6,2) DEFAULT 0,
    overtime_amount DECIMAL(15,2) DEFAULT 0,
    bonus_amount DECIMAL(15,2) DEFAULT 0,
    commission_amount DECIMAL(15,2) DEFAULT 0,
    allowances_total DECIMAL(15,2) DEFAULT 0,

    -- Gross Pay
    gross_amount DECIMAL(15,2) NOT NULL,

    -- Deductions
    tax_amount DECIMAL(15,2) DEFAULT 0,
    social_security_amount DECIMAL(15,2) DEFAULT 0,
    health_insurance_amount DECIMAL(15,2) DEFAULT 0,
    retirement_amount DECIMAL(15,2) DEFAULT 0,
    loan_deductions DECIMAL(15,2) DEFAULT 0,
    other_deductions DECIMAL(15,2) DEFAULT 0,
    total_deductions DECIMAL(15,2) DEFAULT 0,

    -- Net Pay
    net_amount DECIMAL(15,2) NOT NULL,
    currency_code CHAR(3) DEFAULT 'RSD',

    -- Payment Information
    payment_method VARCHAR(20) DEFAULT 'bank_transfer',
    payment_reference VARCHAR(100),
    payment_date DATE,
    payment_status VARCHAR(20) DEFAULT 'pending', -- pending, processed, paid, failed, cancelled
    bank_transfer_id VARCHAR(100),
    check_number VARCHAR(20),

    -- Detailed Breakdowns
    earnings_breakdown JSONB, -- Detailed earnings by type
    deductions_breakdown JSONB, -- Detailed deductions by type
    tax_breakdown JSONB, -- Detailed tax calculations
    benefits_breakdown JSONB, -- Benefits and allowances

    -- Hours and Time Tracking
    regular_hours DECIMAL(6,2) DEFAULT 0,
    overtime_hours_paid DECIMAL(6,2) DEFAULT 0,
    vacation_hours_used DECIMAL(6,2) DEFAULT 0,
    sick_hours_used DECIMAL(6,2) DEFAULT 0,
    holiday_hours DECIMAL(6,2) DEFAULT 0,

    -- Compliance and Reporting
    tax_year INTEGER,
    tax_period VARCHAR(20),
    w2_form_data JSONB, -- For US compliance
    payslip_data JSONB, -- Payslip generation data
    compliance_flags JSONB, -- Any compliance issues or flags

    -- System Integration
    payroll_system_id VARCHAR(100),
    external_reference_id VARCHAR(100),
    integration_status VARCHAR(20) DEFAULT 'synced',
    integration_errors JSONB,

    -- AI & Analytics
    risk_indicators JSONB,
    anomaly_score DECIMAL(5,2),

    -- Audit & Approval
    processed_by UUID REFERENCES users(users_id),
    approved_by UUID REFERENCES users(users_id),
    approved_at TIMESTAMP,
    approval_notes TEXT,

    -- Status & Timestamps
    is_void BOOLEAN DEFAULT FALSE,
    void_reason TEXT,
    voided_by UUID REFERENCES users(users_id),
    voided_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) PARTITION BY RANGE (payroll_date);

-- Inventory Tables
CREATE TABLE inventory (
    inventory_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    companies_id UUID REFERENCES companies(companies_id),
    item_name VARCHAR(255) NOT NULL,
    sku VARCHAR(50) UNIQUE NOT NULL,
    unit_price DECIMAL(15,2) NOT NULL,
    currency_code CHAR(3) DEFAULT 'RSD',
    quantity_on_hand DECIMAL(15,2) DEFAULT 0,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE warehouses (
    warehouses_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    companies_id UUID REFERENCES companies(companies_id),
    warehouse_name VARCHAR(255) NOT NULL,
    location VARCHAR(255),
    capacity DECIMAL(15,2),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- AI and ML Tables
-- Enhanced AI Insights Table
CREATE TABLE ai_insights (
    ai_insights_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    companies_id UUID REFERENCES companies(companies_id),
    user_id UUID REFERENCES users(users_id), -- User who requested the insight

    -- Insight Information
    insight_type VARCHAR(100) NOT NULL, -- financial_analysis, risk_assessment, trend_analysis, anomaly_detection, prediction
    insight_subtype VARCHAR(100),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    summary TEXT, -- AI-generated summary

    -- Data and Context
    insight_data JSONB, -- Detailed insight data
    input_data JSONB, -- Original data that generated this insight
    parameters JSONB, -- Parameters used for generation
    context_data JSONB, -- Additional context

    -- AI Model Information
    model_used VARCHAR(100), -- qwen-3, gpt-4, claude-3, etc.
    model_version VARCHAR(20),
    prompt_used TEXT,
    generation_method VARCHAR(30), -- automatic, on_demand, scheduled

    -- Quality and Confidence
    confidence_score DECIMAL(5,4),
    quality_score DECIMAL(3,2), -- Human-rated quality
    usefulness_score DECIMAL(3,2), -- User-rated usefulness
    accuracy_verified BOOLEAN DEFAULT FALSE,
    verified_by UUID REFERENCES users(users_id),
    verification_notes TEXT,

    -- Impact and Actions
    impact_level VARCHAR(20), -- low, medium, high, critical
    recommended_actions JSONB, -- Suggested actions based on insight
    business_value DECIMAL(15,2), -- Estimated business value
    implementation_cost DECIMAL(15,2),
    roi_estimate DECIMAL(5,2),

    -- Categories and Tags
    category VARCHAR(50), -- finance, operations, hr, sales, marketing
    subcategory VARCHAR(100),
    tags TEXT[], -- Array of tags for better searchability
    keywords TEXT[], -- AI-extracted keywords

    -- Time and Period
    analysis_period_start DATE,
    analysis_period_end DATE,
    data_freshness TIMESTAMP, -- When the source data was last updated
    insight_validity_period INTERVAL DEFAULT '30 days',

    -- Sharing and Collaboration
    is_public BOOLEAN DEFAULT FALSE,
    shared_with_users UUID[],
    shared_with_roles TEXT[],
    collaboration_enabled BOOLEAN DEFAULT FALSE,
    comments_enabled BOOLEAN DEFAULT TRUE,

    -- Visualization
    chart_type VARCHAR(30), -- bar, line, pie, scatter, heatmap, etc.
    chart_data JSONB,
    visualization_config JSONB,

    -- Integration
    external_system VARCHAR(50),
    external_id VARCHAR(100),
    webhook_url TEXT,
    notification_sent BOOLEAN DEFAULT FALSE,

    -- AI and Analytics
    embedding_vector VECTOR(1536),
    similar_insights JSONB, -- AI-suggested similar insights
    sentiment_score DECIMAL(3,2),
    urgency_score DECIMAL(3,2),
    complexity_score DECIMAL(3,2),

    -- Audit and Tracking
    generated_by_system BOOLEAN DEFAULT FALSE,
    generation_time_seconds DECIMAL(6,2),
    token_usage INTEGER,
    cost_estimate DECIMAL(8,4),
    created_by UUID REFERENCES users(users_id),
    approved_by UUID REFERENCES users(users_id),
    approved_at TIMESTAMP,

    -- Status
    status VARCHAR(20) DEFAULT 'active', -- draft, active, archived, deleted
    is_archived BOOLEAN DEFAULT FALSE,
    archived_at TIMESTAMP,
    archive_reason TEXT,

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP -- When insight becomes outdated
) PARTITION BY RANGE (created_at);

-- Enhanced AI Training Data Table (Can be merged with insights for some use cases)
CREATE TABLE ai_training_data (
    ai_training_data_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    companies_id UUID REFERENCES companies(companies_id),
    user_id UUID REFERENCES users(users_id),

    -- Data Information
    data_type VARCHAR(100) NOT NULL, -- financial, behavioral, operational, market, custom
    data_subtype VARCHAR(100),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    source VARCHAR(100), -- system_generated, user_uploaded, api_import, manual_entry

    -- Content
    training_data JSONB, -- The actual training data
    raw_content TEXT, -- Original raw content if applicable
    processed_content TEXT, -- Preprocessed content
    metadata JSONB, -- Additional metadata

    -- Quality and Validation
    quality_score DECIMAL(3,2) DEFAULT 1.0,
    validation_status VARCHAR(20) DEFAULT 'pending', -- pending, validated, rejected, needs_review
    validation_notes TEXT,
    validated_by UUID REFERENCES users(users_id),
    validation_date TIMESTAMP,
    rejection_reason TEXT,

    -- Usage and Performance
    usage_count INTEGER DEFAULT 0,
    last_used_at TIMESTAMP,
    success_rate DECIMAL(5,4),
    performance_metrics JSONB,

    -- AI Model Information
    model_version VARCHAR(20),
    training_parameters JSONB,
    feature_extraction_method VARCHAR(50),

    -- Categories and Organization
    category VARCHAR(50),
    subcategory VARCHAR(100),
    tags TEXT[],
    keywords TEXT[],

    -- Data Characteristics
    data_size_bytes BIGINT,
    record_count INTEGER,
    feature_count INTEGER,
    data_format VARCHAR(20), -- json, csv, xml, text, binary
    encoding VARCHAR(20) DEFAULT 'utf-8',

    -- Privacy and Security
    contains_pii BOOLEAN DEFAULT FALSE,
    anonymization_method VARCHAR(50),
    data_retention_period INTERVAL DEFAULT '7 years',
    compliance_flags JSONB,

    -- Integration
    external_system_id VARCHAR(100),
    external_source_url TEXT,
    import_batch_id VARCHAR(100),
    sync_status VARCHAR(20) DEFAULT 'synced',

    -- AI and Analytics
    embedding_vector VECTOR(1536),
    similarity_score DECIMAL(5,4),
    cluster_id INTEGER,
    outlier_score DECIMAL(5,4),

    -- Audit and Tracking
    created_by UUID REFERENCES users(users_id),
    approved_by UUID REFERENCES users(users_id),
    approved_at TIMESTAMP,
    last_modified_by UUID REFERENCES users(users_id),

    -- Status
    status VARCHAR(20) DEFAULT 'active', -- active, archived, deleted, quarantined
    is_archived BOOLEAN DEFAULT FALSE,
    archived_at TIMESTAMP,
    quarantine_reason TEXT,

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP
);

CREATE TABLE llm_embeddings (
    llm_embeddings_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_type VARCHAR(50) NOT NULL,
    entity_id UUID NOT NULL,
    embedding_vector VECTOR(1536),
    context_text TEXT NOT NULL,
    companies_id UUID REFERENCES companies(companies_id) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- System Tables
CREATE TABLE notifications (
    notifications_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    companies_id UUID REFERENCES companies(companies_id),
    users_id UUID REFERENCES users(users_id),
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    type VARCHAR(20) DEFAULT 'info',
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Enhanced Tickets Table with SLA Support for Finance and Customer Service
CREATE TABLE tickets (
    tickets_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    companies_id UUID REFERENCES companies(companies_id),
    created_by UUID REFERENCES users(users_id),
    assigned_to UUID REFERENCES users(users_id),
    customer_id UUID REFERENCES users(users_id), -- If ticket is for a customer
    contact_id UUID REFERENCES crm_contacts(crm_contacts_id),

    -- Ticket Information
    ticket_number VARCHAR(50) UNIQUE NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(50), -- finance, technical, billing, support, general
    subcategory VARCHAR(100),
    tags TEXT[], -- Array of tags for better categorization

    -- Status and Priority
    status VARCHAR(30) DEFAULT 'open', -- open, in_progress, waiting, resolved, closed, cancelled
    priority VARCHAR(20) DEFAULT 'medium', -- low, medium, high, urgent, critical
    severity VARCHAR(20) DEFAULT 'minor', -- minor, major, critical, blocker

    -- SLA Information
    sla_id UUID,
    sla_breach_time TIMESTAMP,
    sla_response_time TIMESTAMP, -- When first response should be made
    sla_resolution_time TIMESTAMP, -- When ticket should be resolved
    first_response_at TIMESTAMP,
    first_response_duration INTERVAL,
    resolution_at TIMESTAMP,
    resolution_duration INTERVAL,
    is_sla_breached BOOLEAN DEFAULT FALSE,
    sla_breach_reason TEXT,
    business_hours_only BOOLEAN DEFAULT TRUE,

    -- Financial Information (for billing/support tickets)
    estimated_cost DECIMAL(15,2),
    actual_cost DECIMAL(15,2),
    currency_code CHAR(3) DEFAULT 'RSD',
    billing_category VARCHAR(50), -- billable, non_billable, warranty, support_contract
    invoice_id UUID,
    contract_id UUID,

    -- Customer Service Information
    customer_satisfaction_rating INTEGER CHECK (customer_satisfaction_rating >= 1 AND customer_satisfaction_rating <= 5),
    customer_feedback TEXT,
    customer_contact_method VARCHAR(20), -- email, phone, chat, portal
    customer_language VARCHAR(10) DEFAULT 'sr',

    -- Assignment and Workflow
    department VARCHAR(50),
    team VARCHAR(50),
    current_queue VARCHAR(50),
    previous_assignees UUID[],
    reassignment_count INTEGER DEFAULT 0,
    escalation_level INTEGER DEFAULT 0,
    escalation_reason TEXT,
    escalated_at TIMESTAMP,
    escalation_resolved_at TIMESTAMP,

    -- Communication
    channel VARCHAR(30) DEFAULT 'portal', -- email, phone, chat, portal, api, social
    source VARCHAR(30), -- web_form, email, phone_call, chat, api, social_media
    last_customer_update TIMESTAMP,
    last_agent_update TIMESTAMP,
    public_comments_count INTEGER DEFAULT 0,
    private_comments_count INTEGER DEFAULT 0,

    -- Resolution Information
    resolution_category VARCHAR(50),
    resolution_subcategory VARCHAR(100),
    resolution_method VARCHAR(30), -- email, phone, chat, knowledge_base, manual
    resolution_confidence DECIMAL(3,2), -- AI confidence in resolution
    knowledge_base_article_id UUID,

    -- Attachments and Media
    attachment_count INTEGER DEFAULT 0,
    attachment_urls TEXT[],
    attachment_metadata JSONB,

    -- Integration
    external_system_id VARCHAR(100),
    external_ticket_id VARCHAR(100),
    integration_data JSONB,

    -- AI and Analytics
    sentiment_score DECIMAL(3,2),
    urgency_score DECIMAL(3,2), -- AI calculated urgency
    complexity_score DECIMAL(3,2), -- AI calculated complexity
    embedding_vector VECTOR(1536),
    similar_tickets JSONB, -- AI suggested similar tickets

    -- Audit and Compliance
    created_by_system BOOLEAN DEFAULT FALSE,
    approved_for_closure BOOLEAN DEFAULT TRUE,
    closure_approved_by UUID REFERENCES users(users_id),
    closure_approved_at TIMESTAMP,
    data_retention_date DATE,
    compliance_flags JSONB,

    -- Status and Timestamps
    is_archived BOOLEAN DEFAULT FALSE,
    archived_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP
) PARTITION BY RANGE (created_at);

CREATE TABLE audit_logs (
    audit_logs_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    companies_id UUID REFERENCES companies(companies_id),
    users_id UUID REFERENCES users(users_id),
    table_name VARCHAR(100) NOT NULL,
    operation VARCHAR(20) NOT NULL,
    old_values JSONB,
    new_values JSONB,
    action_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Enhanced Settings Table with Comprehensive Configuration Support
CREATE TABLE settings (
    settings_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    companies_id UUID REFERENCES companies(companies_id), -- NULL for global settings
    user_id UUID REFERENCES users(users_id), -- NULL for company/global settings

    -- Setting Information
    setting_key VARCHAR(150) NOT NULL,
    setting_value TEXT,
    setting_type VARCHAR(30) DEFAULT 'string', -- string, number, boolean, json, file, color, date, time, datetime
    setting_category VARCHAR(50), -- system, security, finance, hr, crm, email, api, ui, notifications, etc.

    -- Metadata
    display_name VARCHAR(100),
    description TEXT,
    help_text TEXT,
    placeholder_text VARCHAR(100),

    -- Configuration
    is_system_setting BOOLEAN DEFAULT FALSE, -- Cannot be changed by users
    is_user_setting BOOLEAN DEFAULT FALSE, -- Can be customized per user
    is_company_setting BOOLEAN DEFAULT TRUE, -- Can be customized per company
    is_required BOOLEAN DEFAULT FALSE,
    is_encrypted BOOLEAN DEFAULT FALSE, -- For sensitive settings like API keys

    -- Validation
    validation_rules JSONB, -- min, max, pattern, options, etc.
    default_value TEXT,
    allowed_values TEXT[], -- For dropdown/select settings

    -- Dependencies and Conditions
    depends_on_setting VARCHAR(150), -- Key of setting this depends on
    condition_expression TEXT, -- JavaScript-like expression for conditional visibility
    parent_setting_id UUID REFERENCES settings(settings_id),

    -- UI Configuration
    ui_component VARCHAR(30) DEFAULT 'text', -- text, number, email, password, textarea, select, checkbox, radio, color, file, date, time
    ui_group VARCHAR(50), -- Group settings for better organization
    ui_order INTEGER DEFAULT 0,
    ui_icon VARCHAR(30),
    ui_readonly BOOLEAN DEFAULT FALSE,

    -- Permissions
    required_permissions TEXT[], -- Array of permissions needed to view/modify
    role_restrictions TEXT[], -- Array of roles that can access this setting

    -- Audit and Tracking
    created_by UUID REFERENCES users(users_id),
    approved_by UUID REFERENCES users(users_id),
    approved_at TIMESTAMP,
    last_modified_by UUID REFERENCES users(users_id),
    last_modified_at TIMESTAMP,
    change_log JSONB, -- Track changes to this setting

    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    effective_from TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    effective_until TIMESTAMP,
    maintenance_mode BOOLEAN DEFAULT FALSE,

    -- Integration
    external_system VARCHAR(50), -- Source system if synced
    external_id VARCHAR(100),
    sync_status VARCHAR(20) DEFAULT 'synced', -- synced, pending, error, disabled
    sync_errors JSONB,

    -- AI and Analytics
    embedding_vector VECTOR(1536),
    usage_analytics JSONB,

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Settings Categories and Example Configurations
-- This will be populated with INSERT statements in the data file

-- Comprehensive Indexes for 10PB+ Data Support and Performance

-- Core Table Indexes
CREATE INDEX CONCURRENTLY idx_companies_id ON companies (companies_id);
CREATE INDEX CONCURRENTLY idx_companies_name ON companies (company_name);
CREATE INDEX CONCURRENTLY idx_companies_tax_id ON companies (tax_id);
CREATE INDEX CONCURRENTLY idx_companies_country ON companies (countries_id);
CREATE INDEX CONCURRENTLY idx_companies_active ON companies (is_active) WHERE is_active = TRUE;
CREATE INDEX CONCURRENTLY idx_companies_embedding ON companies USING hnsw (embedding_vector vector_cosine_ops);

CREATE INDEX CONCURRENTLY idx_countries_iso_code ON countries (iso_code);
CREATE INDEX CONCURRENTLY idx_countries_name ON countries (name);
CREATE INDEX CONCURRENTLY idx_countries_region ON countries (region);

-- User Indexes with Multi-tenant Support
CREATE INDEX CONCURRENTLY idx_users_companies_id ON users (companies_id);
CREATE INDEX CONCURRENTLY idx_users_email ON users (email);
CREATE INDEX CONCURRENTLY idx_users_username ON users (username);
CREATE INDEX CONCURRENTLY idx_users_active ON users (is_active) WHERE is_active = TRUE;
CREATE INDEX CONCURRENTLY idx_users_verified ON users (is_verified) WHERE is_verified = TRUE;
CREATE INDEX CONCURRENTLY idx_users_phone ON users (phone);
CREATE INDEX CONCURRENTLY idx_users_embedding ON users USING hnsw (embedding_vector vector_cosine_ops);

-- Authentication Indexes
CREATE INDEX CONCURRENTLY idx_users_keycloak ON users (keycloak_id) WHERE keycloak_id IS NOT NULL;
CREATE INDEX CONCURRENTLY idx_users_openid ON users (openid_subject) WHERE openid_subject IS NOT NULL;
CREATE INDEX CONCURRENTLY idx_users_ad ON users (ad_username) WHERE ad_username IS NOT NULL;
CREATE INDEX CONCURRENTLY idx_users_oauth_google ON users (oauth_google_id) WHERE oauth_google_id IS NOT NULL;
CREATE INDEX CONCURRENTLY idx_users_2fa_enabled ON users (two_factor_enabled) WHERE two_factor_enabled = TRUE;

-- Financial Indexes
CREATE INDEX CONCURRENTLY idx_general_ledger_company_date ON general_ledger (companies_id, transaction_date);
CREATE INDEX CONCURRENTLY idx_general_ledger_date ON general_ledger USING BRIN (transaction_date) WITH (pages_per_range = 128);
CREATE INDEX CONCURRENTLY idx_general_ledger_account ON general_ledger (chart_of_accounts_id);
CREATE INDEX CONCURRENTLY idx_general_ledger_posted ON general_ledger (is_posted) WHERE is_posted = FALSE;

CREATE INDEX CONCURRENTLY idx_chart_of_accounts_company ON chart_of_accounts (companies_id, account_code);
CREATE INDEX CONCURRENTLY idx_chart_of_accounts_type ON chart_of_accounts (account_type);

CREATE INDEX CONCURRENTLY idx_invoices_company_date ON invoices (companies_id, invoice_date);
CREATE INDEX CONCURRENTLY idx_invoices_status ON invoices (status);
CREATE INDEX CONCURRENTLY idx_invoices_due_date ON invoices (due_date) WHERE due_date > CURRENT_DATE;

CREATE INDEX CONCURRENTLY idx_bank_accounts_company ON bank_accounts (companies_id);
CREATE INDEX CONCURRENTLY idx_bank_statements_company_date ON bank_statements (companies_id, transaction_date);
CREATE INDEX CONCURRENTLY idx_bank_statements_date ON bank_statements USING BRIN (transaction_date) WITH (pages_per_range = 128);

-- HR and Payroll Indexes
CREATE INDEX CONCURRENTLY idx_employees_company ON employees (companies_id);
CREATE INDEX CONCURRENTLY idx_employees_user ON employees (user_id);
CREATE INDEX CONCURRENTLY idx_employees_number ON employees (employee_number);
CREATE INDEX CONCURRENTLY idx_employees_department ON employees (department);
CREATE INDEX CONCURRENTLY idx_employees_active ON employees (is_active) WHERE is_active = TRUE;
CREATE INDEX CONCURRENTLY idx_employees_embedding ON employees USING hnsw (embedding_vector vector_cosine_ops);

CREATE INDEX CONCURRENTLY idx_payroll_company_date ON payroll (companies_id, payroll_date);
CREATE INDEX CONCURRENTLY idx_payroll_employee ON payroll (employees_id);
CREATE INDEX CONCURRENTLY idx_payroll_date ON payroll USING BRIN (payroll_date) WITH (pages_per_range = 128);
CREATE INDEX CONCURRENTLY idx_payroll_status ON payroll (payment_status);

-- CRM Indexes
CREATE INDEX CONCURRENTLY idx_crm_contacts_company ON crm_contacts (companies_id);
CREATE INDEX CONCURRENTLY idx_crm_leads_company ON crm_leads (companies_id);
CREATE INDEX CONCURRENTLY idx_crm_leads_status ON crm_leads (status);
CREATE INDEX CONCURRENTLY idx_crm_opportunities_company ON crm_opportunities (companies_id);
CREATE INDEX CONCURRENTLY idx_crm_opportunities_status ON crm_opportunities (status);

-- Inventory Indexes
CREATE INDEX CONCURRENTLY idx_inventory_company ON inventory (companies_id);
CREATE INDEX CONCURRENTLY idx_inventory_sku ON inventory (sku);
CREATE INDEX CONCURRENTLY idx_inventory_category ON inventory (category);

-- AI and ML Indexes
CREATE INDEX CONCURRENTLY idx_ai_insights_company_type ON ai_insights (companies_id, insight_type);
CREATE INDEX CONCURRENTLY idx_ai_insights_date ON ai_insights (created_at);
CREATE INDEX CONCURRENTLY idx_ai_insights_confidence ON ai_insights (confidence_score);
CREATE INDEX CONCURRENTLY idx_ai_insights_embedding ON ai_insights USING hnsw (embedding_vector vector_cosine_ops) WITH (ef_construction = 200, m = 16);

CREATE INDEX CONCURRENTLY idx_ai_training_data_company_type ON ai_training_data (companies_id, data_type);
CREATE INDEX CONCURRENTLY idx_ai_training_data_quality ON ai_training_data (quality_score);
CREATE INDEX CONCURRENTLY idx_ai_training_data_embedding ON ai_training_data USING hnsw (embedding_vector vector_cosine_ops) WITH (ef_construction = 200, m = 16);

CREATE INDEX CONCURRENTLY idx_llm_embeddings_entity ON llm_embeddings (entity_type, entity_id);
CREATE INDEX CONCURRENTLY idx_llm_embeddings_embedding ON llm_embeddings USING hnsw (embedding_vector vector_cosine_ops) WITH (ef_construction = 200, m = 16);

-- Ticket System Indexes (Enhanced for SLA)
CREATE INDEX CONCURRENTLY idx_tickets_company_status ON tickets (companies_id, status);
CREATE INDEX CONCURRENTLY idx_tickets_priority ON tickets (priority);
CREATE INDEX CONCURRENTLY idx_tickets_category ON tickets (category);
CREATE INDEX CONCURRENTLY idx_tickets_assigned_to ON tickets (assigned_to);
CREATE INDEX CONCURRENTLY idx_tickets_created_by ON tickets (created_by);
CREATE INDEX CONCURRENTLY idx_tickets_sla_breach ON tickets (is_sla_breached) WHERE is_sla_breached = TRUE;
CREATE INDEX CONCURRENTLY idx_tickets_due_dates ON tickets (sla_resolution_time) WHERE sla_resolution_time > CURRENT_TIMESTAMP;
CREATE INDEX CONCURRENTLY idx_tickets_date ON tickets USING BRIN (created_at) WITH (pages_per_range = 128);
CREATE INDEX CONCURRENTLY idx_tickets_embedding ON tickets USING hnsw (embedding_vector vector_cosine_ops);

-- Settings Indexes
CREATE INDEX CONCURRENTLY idx_settings_company_key ON settings (companies_id, setting_key);
CREATE INDEX CONCURRENTLY idx_settings_user_key ON settings (user_id, setting_key);
CREATE INDEX CONCURRENTLY idx_settings_category ON settings (setting_category);
CREATE INDEX CONCURRENTLY idx_settings_system ON settings (is_system_setting) WHERE is_system_setting = TRUE;
CREATE INDEX CONCURRENTLY idx_settings_active ON settings (is_active) WHERE is_active = TRUE;

-- Notification Indexes
CREATE INDEX CONCURRENTLY idx_notifications_user_read ON notifications (users_id, is_read);
CREATE INDEX CONCURRENTLY idx_notifications_type ON notifications (type);
CREATE INDEX CONCURRENTLY idx_notifications_date ON notifications (created_at);

-- Audit and Security Indexes
CREATE INDEX CONCURRENTLY idx_audit_logs_company_table ON audit_logs (companies_id, table_name);
CREATE INDEX CONCURRENTLY idx_audit_logs_user ON audit_logs (users_id);
CREATE INDEX CONCURRENTLY idx_audit_logs_date ON audit_logs (action_timestamp);
CREATE INDEX CONCURRENTLY idx_audit_logs_operation ON audit_logs (operation);

-- Full-text Search Indexes
CREATE INDEX CONCURRENTLY idx_companies_fts ON companies USING GIN (to_tsvector('english', company_name || ' ' || COALESCE(description, '')));
CREATE INDEX CONCURRENTLY idx_users_fts ON users USING GIN (to_tsvector('english', first_name || ' ' || last_name || ' ' || COALESCE(bio, '')));
CREATE INDEX CONCURRENTLY idx_tickets_fts ON tickets USING GIN (to_tsvector('english', title || ' ' || COALESCE(description, '')));
CREATE INDEX CONCURRENTLY idx_ai_insights_fts ON ai_insights USING GIN (to_tsvector('english', title || ' ' || COALESCE(description, '')));

-- JSONB Indexes for Performance
CREATE INDEX CONCURRENTLY idx_users_preferences ON users USING GIN (notification_preferences);
CREATE INDEX CONCURRENTLY idx_users_security ON users USING GIN (trusted_devices);
CREATE INDEX CONCURRENTLY idx_employees_benefits ON employees USING GIN (benefits);
CREATE INDEX CONCURRENTLY idx_ai_insights_data ON ai_insights USING GIN (insight_data);
CREATE INDEX CONCURRENTLY idx_settings_validation ON settings USING GIN (validation_rules);

-- Partition Management Indexes
CREATE INDEX CONCURRENTLY idx_general_ledger_partition ON general_ledger (transaction_date) WHERE transaction_date >= CURRENT_DATE - INTERVAL '1 year';
CREATE INDEX CONCURRENTLY idx_payroll_partition ON payroll (payroll_date) WHERE payroll_date >= CURRENT_DATE - INTERVAL '2 years';
CREATE INDEX CONCURRENTLY idx_tickets_partition ON tickets (created_at) WHERE created_at >= CURRENT_DATE - INTERVAL '1 year';

-- Multi-Company Access Indexes
CREATE INDEX CONCURRENTLY idx_user_company_access_user ON user_company_access (user_id);
CREATE INDEX CONCURRENTLY idx_user_company_access_company ON user_company_access (company_id);
CREATE INDEX CONCURRENTLY idx_user_company_access_active ON user_company_access (user_id, company_id, status) WHERE status = 'active';
CREATE INDEX CONCURRENTLY idx_user_company_access_level ON user_company_access (access_level);
CREATE INDEX CONCURRENTLY idx_user_company_access_permissions ON user_company_access USING GIN (
    (ARRAY[can_manage_company, can_invite_users, can_manage_billing, can_access_financial_data, can_access_hr_data, can_access_customer_data])
);

-- Company Sessions and Switching Indexes
CREATE INDEX CONCURRENTLY idx_user_company_sessions_user ON user_company_sessions (user_id);
CREATE INDEX CONCURRENTLY idx_user_company_sessions_company ON user_company_sessions (company_id);
CREATE INDEX CONCURRENTLY idx_user_company_sessions_active ON user_company_sessions (user_id, is_active) WHERE is_active = TRUE;
CREATE INDEX CONCURRENTLY idx_user_company_sessions_session ON user_company_sessions (session_id);

-- Company Switching Audit Indexes
CREATE INDEX CONCURRENTLY idx_company_switch_audit_user ON company_switch_audit (user_id);
CREATE INDEX CONCURRENTLY idx_company_switch_audit_company ON company_switch_audit (to_company_id);
CREATE INDEX CONCURRENTLY idx_company_switch_audit_date ON company_switch_audit (switched_at);

-- Company Invitations Indexes
CREATE INDEX CONCURRENTLY idx_company_invitations_company ON company_invitations (company_id);
CREATE INDEX CONCURRENTLY idx_company_invitations_email ON company_invitations (invited_email);
CREATE INDEX CONCURRENTLY idx_company_invitations_token ON company_invitations (invitation_token);
CREATE INDEX CONCURRENTLY idx_company_invitations_status ON company_invitations (status);
CREATE INDEX CONCURRENTLY idx_company_invitations_expires ON company_invitations (expires_at) WHERE status = 'pending';

-- User Company Preferences Indexes
CREATE INDEX CONCURRENTLY idx_user_company_preferences_user ON user_company_preferences (user_id);
CREATE INDEX CONCURRENTLY idx_user_company_preferences_company ON user_company_preferences (company_id);
CREATE INDEX CONCURRENTLY idx_user_company_preferences_key ON user_company_preferences (preference_key);

-- Company Departments Indexes
CREATE INDEX CONCURRENTLY idx_company_departments_company ON company_departments (company_id);
CREATE INDEX CONCURRENTLY idx_company_departments_manager ON company_departments (manager_id);
CREATE INDEX CONCURRENTLY idx_company_departments_parent ON company_departments (parent_department_id);

-- User Department Assignments Indexes
CREATE INDEX CONCURRENTLY idx_user_dept_assignments_user ON user_department_assignments (user_id);
CREATE INDEX CONCURRENTLY idx_user_dept_assignments_company ON user_department_assignments (company_id);
CREATE INDEX CONCURRENTLY idx_user_dept_assignments_dept ON user_department_assignments (department_id);
CREATE INDEX CONCURRENTLY idx_user_dept_assignments_active ON user_department_assignments (user_id, company_id, is_active) WHERE is_active = TRUE;

-- Composite Indexes for Common Queries
CREATE INDEX CONCURRENTLY idx_users_company_active ON users (companies_id, is_active) WHERE is_active = TRUE;
CREATE INDEX CONCURRENTLY idx_employees_company_dept ON employees (companies_id, department) WHERE is_active = TRUE;
CREATE INDEX CONCURRENTLY idx_invoices_company_status_due ON invoices (companies_id, status, due_date) WHERE status = 'sent';
CREATE INDEX CONCURRENTLY idx_tickets_company_status_priority ON tickets (companies_id, status, priority) WHERE status NOT IN ('closed', 'resolved');

-- RLS Policies
ALTER TABLE companies ENABLE ROW LEVEL SECURITY;
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE general_ledger ENABLE ROW LEVEL SECURITY;
ALTER TABLE invoices ENABLE ROW LEVEL SECURITY;
ALTER TABLE bank_accounts ENABLE ROW LEVEL SECURITY;
ALTER TABLE crm_contacts ENABLE ROW LEVEL SECURITY;
ALTER TABLE employees ENABLE ROW LEVEL SECURITY;
ALTER TABLE inventory ENABLE ROW LEVEL SECURITY;
ALTER TABLE notifications ENABLE ROW LEVEL SECURITY;
ALTER TABLE tickets ENABLE ROW LEVEL SECURITY;

-- Sample RLS Policies
CREATE POLICY company_access ON companies USING (true);
CREATE POLICY user_company_access ON users USING (companies_id = (SELECT companies_id FROM users WHERE users_id = current_setting('app.current_user_id')::UUID));

-- Permissions
GRANT ALL ON ALL TABLES IN SCHEMA public TO ai_valido_developer;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO ai_valido_admin;
GRANT SELECT, INSERT, UPDATE ON general_ledger, invoices, bank_accounts TO ai_valido_accountant;
GRANT SELECT, INSERT, UPDATE, DELETE ON crm_contacts, crm_leads, crm_opportunities, inventory TO ai_valido_manager;
GRANT SELECT ON payroll, employees TO ai_valido_hr;
GRANT SELECT ON audit_logs, tickets TO ai_valido_support;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO ai_valido_demo;

-- Sample Data
INSERT INTO companies (company_name, tax_id, registration_number, city, country) VALUES
('ValidoAI', '123456789', 'REG001', 'Belgrade', 'Serbia'),
('TechCorp', '987654321', 'REG002', 'Novi Sad', 'Serbia'),
('FinanceHub', '456789123', 'REG003', 'Niš', 'Serbia');

INSERT INTO user_roles (role_name, description) VALUES
('admin', 'Administrator with full access'),
('accountant', 'Accountant with financial access'),
('manager', 'Manager with CRM and inventory access'),
('hr', 'HR with employee access'),
('support', 'Support with limited access'),
('demo', 'Demo user with read-only access');
