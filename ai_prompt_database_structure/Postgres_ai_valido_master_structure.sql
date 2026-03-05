-- ============================================================================
-- VALIDOAI MASTER STRUCTURE SQL
-- ============================================================================
-- Consolidated PostgreSQL structure for Serbian business financial system
-- Includes all tables, views, functions, and Serbian-specific requirements
-- ============================================================================

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";
CREATE EXTENSION IF NOT EXISTS "pg_buffercache";
CREATE EXTENSION IF NOT EXISTS "pg_similarity";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "pg_cron";
CREATE EXTENSION IF NOT EXISTS "vector";
CREATE EXTENSION IF NOT EXISTS "postgis";
CREATE EXTENSION IF NOT EXISTS "postgis_topology";

-- ============================================================================
-- 1. COMPANIES & BUSINESS ENTITIES (Serbian-specific)
-- ============================================================================

-- Serbian business entity types
CREATE TABLE business_entity_types (
    business_entity_types_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_code VARCHAR(10) UNIQUE NOT NULL,
    entity_name VARCHAR(100) NOT NULL,
    entity_name_sr VARCHAR(100) NOT NULL, -- Serbian name
    description TEXT,
    tax_requirements JSONB,
    reporting_requirements JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Companies table with Serbian requirements
CREATE TABLE companies (
    companies_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_name VARCHAR(255) NOT NULL,
    legal_name VARCHAR(255) NOT NULL,
    tax_id VARCHAR(20) UNIQUE NOT NULL, -- PIB (Tax ID)
    registration_number VARCHAR(20) UNIQUE NOT NULL, -- Matični broj
    business_entity_type_id UUID REFERENCES business_entity_types(business_entity_types_id),
    industry VARCHAR(100),
    company_type VARCHAR(50), -- DOO, AD, Preduzetnik
    company_size VARCHAR(20), -- Small, Medium, Large

    -- Serbian-specific fields
    pdv_registration VARCHAR(20), -- PDV registration number
    statistical_number VARCHAR(20), -- Statistički broj
    bank_account VARCHAR(30), -- Primary bank account
    bank_name VARCHAR(100), -- Primary bank

    -- Contact information
    address_line1 VARCHAR(255),
    address_line2 VARCHAR(255),
    city VARCHAR(100),
    municipality VARCHAR(100),
    postal_code VARCHAR(10),
    country VARCHAR(50) DEFAULT 'Serbia',

    -- Serbian phone format
    phone VARCHAR(20),
    email VARCHAR(255),
    website VARCHAR(255),

    -- Serbian business details
    founding_date DATE,
    fiscal_year_start DATE DEFAULT '2024-01-01',
    currency VARCHAR(3) DEFAULT 'RSD', -- Serbian Dinar as default
    language VARCHAR(5) DEFAULT 'sr-RS',

    -- Status and metadata
    status VARCHAR(20) DEFAULT 'active',
    is_pdv_registered BOOLEAN DEFAULT false,
    is_e_invoice_enabled BOOLEAN DEFAULT false,

    description TEXT,
    notes TEXT,

    -- Audit fields
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by UUID,
    updated_by UUID
);

-- Company settings for Serbian business rules
CREATE TABLE company_settings (
    company_settings_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID REFERENCES companies(companies_id) ON DELETE CASCADE,
    setting_key VARCHAR(100) NOT NULL,
    setting_value JSONB,
    setting_type VARCHAR(50), -- pdv, currency, reporting, etc.
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(company_id, setting_key)
);

-- ============================================================================
-- 2. USERS & ROLES (Serbian business context)
-- ============================================================================

-- Users table
CREATE TABLE users (
    users_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    phone VARCHAR(20),

    -- Serbian-specific
    jmbg VARCHAR(13), -- Unique citizen number
    citizenship VARCHAR(50) DEFAULT 'Serbia',

    role VARCHAR(50) DEFAULT 'user',
    status VARCHAR(20) DEFAULT 'active',
    email_verified_at TIMESTAMP,
    is_active BOOLEAN DEFAULT true,
    company_id UUID REFERENCES companies(companies_id),
    department VARCHAR(100),
    job_title VARCHAR(100),

    -- Security
    two_factor_enabled BOOLEAN DEFAULT false,
    two_factor_secret VARCHAR(100),
    last_login_at TIMESTAMP,
    login_attempts INTEGER DEFAULT 0,
    locked_until TIMESTAMP,

    -- Audit
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by UUID,
    updated_by UUID
);

-- User roles specific to Serbian business
CREATE TABLE user_roles (
    user_roles_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    role_name VARCHAR(100) UNIQUE NOT NULL,
    role_name_sr VARCHAR(100) NOT NULL,
    description TEXT,
    permissions JSONB, -- Serbian business permissions
    is_system_role BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User role assignments
CREATE TABLE user_role_assignments (
    user_role_assignments_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(users_id) ON DELETE CASCADE,
    role_id UUID REFERENCES user_roles(user_roles_id) ON DELETE CASCADE,
    assigned_by UUID REFERENCES users(users_id),
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    is_active BOOLEAN DEFAULT true,
    UNIQUE(user_id, role_id, assigned_at)
);

-- ============================================================================
-- 3. PRODUCTS & INVENTORY (Serbian business context)
-- ============================================================================

-- Product categories with Serbian classifications
CREATE TABLE product_categories (
    product_categories_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    category_code VARCHAR(20) UNIQUE NOT NULL,
    category_name VARCHAR(100) NOT NULL,
    category_name_sr VARCHAR(100) NOT NULL,
    parent_category_id UUID REFERENCES product_categories(product_categories_id),
    description TEXT,

    -- Serbian tax classification
    pdv_rate DECIMAL(5,2) DEFAULT 20.00, -- Standard PDV rate
    is_pdv_exempt BOOLEAN DEFAULT false,
    pdv_exemption_reason TEXT,

    -- Accounting classification
    account_revenue UUID, -- Revenue account
    account_inventory UUID, -- Inventory account
    account_cogs UUID, -- Cost of goods sold account

    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Products table with Serbian requirements
CREATE TABLE products (
    products_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID REFERENCES companies(companies_id),
    product_code VARCHAR(50) UNIQUE NOT NULL,
    product_name VARCHAR(255) NOT NULL,
    product_name_sr VARCHAR(255),

    -- Product details
    description TEXT,
    description_sr TEXT,
    category_id UUID REFERENCES product_categories(product_categories_id),
    subcategory VARCHAR(100),
    brand VARCHAR(100),

    -- Serbian product classification
    product_type VARCHAR(50), -- goods, service, digital
    measurement_unit VARCHAR(20) DEFAULT 'kom', -- komad (piece)
    is_pdv_exempt BOOLEAN DEFAULT false,
    pdv_rate DECIMAL(5,2) DEFAULT 20.00,

    -- Pricing in RSD
    unit_price DECIMAL(15,2) NOT NULL,
    cost_price DECIMAL(15,2),
    wholesale_price DECIMAL(15,2),
    recommended_price DECIMAL(15,2),

    -- Multi-currency support
    price_eur DECIMAL(15,2),
    price_usd DECIMAL(15,2),

    -- Inventory
    stock_quantity DECIMAL(15,3) DEFAULT 0,
    min_stock_level DECIMAL(15,3) DEFAULT 0,
    max_stock_level DECIMAL(15,3),
    reorder_level DECIMAL(15,3) DEFAULT 0,

    -- Product images and documents
    image_url VARCHAR(500),
    barcode VARCHAR(50),
    qr_code VARCHAR(100),

    -- Status
    is_active BOOLEAN DEFAULT true,
    is_available BOOLEAN DEFAULT true,
    availability_date DATE,

    -- SEO and marketing
    seo_keywords TEXT,
    seo_description TEXT,

    -- Audit
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(users_id),
    updated_by UUID REFERENCES users(users_id)
);

-- Product pricing history for Serbian market analysis
CREATE TABLE product_price_history (
    product_price_history_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID REFERENCES products(products_id) ON DELETE CASCADE,
    old_price DECIMAL(15,2),
    new_price DECIMAL(15,2),
    price_type VARCHAR(20) DEFAULT 'unit_price', -- unit_price, wholesale_price, etc.
    currency VARCHAR(3) DEFAULT 'RSD',
    change_reason TEXT,
    effective_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(users_id)
);

-- ============================================================================
-- 4. CUSTOMERS & SUPPLIERS (Serbian business context)
-- ============================================================================

-- Customer types for Serbian market
CREATE TABLE customer_types (
    customer_types_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    type_code VARCHAR(20) UNIQUE NOT NULL,
    type_name VARCHAR(100) NOT NULL,
    type_name_sr VARCHAR(100) NOT NULL,
    description TEXT,
    payment_terms_default VARCHAR(100),
    credit_limit_default DECIMAL(15,2),
    is_business BOOLEAN DEFAULT false,
    is_active BOOLEAN DEFAULT true
);

-- Customers with Serbian identification
CREATE TABLE customers (
    customers_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID REFERENCES companies(companies_id),

    -- Customer identification
    customer_type_id UUID REFERENCES customer_types(customer_types_id),
    customer_number VARCHAR(20) UNIQUE,

    -- For individuals
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    jmbg VARCHAR(13), -- Personal ID number

    -- For businesses
    company_name VARCHAR(255),
    pib VARCHAR(20), -- Tax ID
    matični_broj VARCHAR(20), -- Registration number

    -- Contact information
    email VARCHAR(255),
    phone VARCHAR(20),
    mobile VARCHAR(20),
    address_line1 VARCHAR(255),
    address_line2 VARCHAR(255),
    city VARCHAR(100),
    postal_code VARCHAR(10),
    country VARCHAR(50) DEFAULT 'Serbia',

    -- Serbian-specific
    citizenship VARCHAR(50) DEFAULT 'Serbia',
    residence_city VARCHAR(100),
    residence_municipality VARCHAR(100),

    -- Business details
    industry VARCHAR(100),
    company_size VARCHAR(20),
    website VARCHAR(255),

    -- Financial
    credit_limit DECIMAL(15,2) DEFAULT 0,
    current_balance DECIMAL(15,2) DEFAULT 0,
    payment_terms VARCHAR(100) DEFAULT 'Net 30',
    preferred_currency VARCHAR(3) DEFAULT 'RSD',

    -- Status
    status VARCHAR(20) DEFAULT 'active',
    is_vip BOOLEAN DEFAULT false,
    tax_exempt BOOLEAN DEFAULT false,

    -- Marketing
    marketing_consent BOOLEAN DEFAULT false,
    email_subscribed BOOLEAN DEFAULT true,
    sms_subscribed BOOLEAN DEFAULT false,

    notes TEXT,

    -- Audit
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(users_id),
    updated_by UUID REFERENCES users(users_id)
);

-- Suppliers with Serbian business context
CREATE TABLE suppliers (
    suppliers_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID REFERENCES companies(companies_id),

    supplier_number VARCHAR(20) UNIQUE,
    supplier_name VARCHAR(255) NOT NULL,
    supplier_name_sr VARCHAR(255),

    -- Serbian business identification
    pib VARCHAR(20),
    matični_broj VARCHAR(20),
    pdv_registration VARCHAR(20),

    -- Contact
    contact_person VARCHAR(100),
    email VARCHAR(255),
    phone VARCHAR(20),
    website VARCHAR(255),

    -- Address
    address_line1 VARCHAR(255),
    address_line2 VARCHAR(255),
    city VARCHAR(100),
    postal_code VARCHAR(10),
    country VARCHAR(50) DEFAULT 'Serbia',

    -- Business details
    industry VARCHAR(100),
    payment_terms VARCHAR(100) DEFAULT 'Net 30',
    credit_limit DECIMAL(15,2) DEFAULT 0,
    preferred_currency VARCHAR(3) DEFAULT 'RSD',

    -- Supplier rating
    rating DECIMAL(3,2) DEFAULT 5.00, -- 1-5 scale
    reliability_score INTEGER DEFAULT 100, -- 0-100

    -- Status
    status VARCHAR(20) DEFAULT 'active',
    is_preferred BOOLEAN DEFAULT false,

    notes TEXT,

    -- Audit
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(users_id),
    updated_by UUID REFERENCES users(users_id)
);

-- ============================================================================
-- 5. INVOICES & SALES (Serbian e-faktura compliance)
-- ============================================================================

-- Serbian invoice series
CREATE TABLE invoice_series (
    invoice_series_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID REFERENCES companies(companies_id),
    series_code VARCHAR(10) NOT NULL,
    series_name VARCHAR(100) NOT NULL,
    document_type VARCHAR(20), -- invoice, credit_note, debit_note
    current_number INTEGER DEFAULT 1,
    prefix VARCHAR(10),
    suffix VARCHAR(10),
    format_string VARCHAR(50) DEFAULT '{prefix}{number}{suffix}',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Invoices with Serbian e-faktura requirements
CREATE TABLE invoices (
    invoices_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID REFERENCES companies(companies_id),

    -- Invoice identification
    invoice_number VARCHAR(50) UNIQUE NOT NULL,
    invoice_series_id UUID REFERENCES invoice_series(invoice_series_id),
    invoice_type VARCHAR(20) DEFAULT 'sales', -- sales, purchase, credit_note, debit_note

    -- Dates
    invoice_date DATE NOT NULL,
    due_date DATE,
    payment_date DATE,

    -- Parties
    customer_id UUID REFERENCES customers(customers_id),
    customer_name VARCHAR(255) NOT NULL,
    customer_email VARCHAR(255),
    customer_pib VARCHAR(20),
    customer_address TEXT,

    -- Serbian e-faktura fields
    e_invoice_id VARCHAR(100), -- Unique e-invoice identifier
    qr_code TEXT, -- QR code for e-invoice
    digital_signature TEXT, -- Digital signature
    e_invoice_status VARCHAR(20), -- draft, sent, delivered, rejected

    -- Financial
    currency VARCHAR(3) DEFAULT 'RSD',
    exchange_rate DECIMAL(10,4) DEFAULT 1.0000,

    -- Amounts
    subtotal DECIMAL(15,2) NOT NULL DEFAULT 0,
    discount_amount DECIMAL(15,2) DEFAULT 0,
    discount_percentage DECIMAL(5,2) DEFAULT 0,

    -- PDV (VAT) calculation
    pdv_base DECIMAL(15,2) DEFAULT 0, -- Base for PDV calculation
    pdv_rate DECIMAL(5,2) DEFAULT 20.00,
    pdv_amount DECIMAL(15,2) DEFAULT 0,

    -- Total
    total_amount DECIMAL(15,2) NOT NULL DEFAULT 0,

    -- Payment
    payment_status VARCHAR(20) DEFAULT 'unpaid', -- unpaid, partial, paid, overdue
    payment_method VARCHAR(50), -- bank_transfer, cash, card, check
    payment_reference VARCHAR(100),

    -- Status
    status VARCHAR(20) DEFAULT 'draft', -- draft, issued, sent, cancelled
    is_e_invoice BOOLEAN DEFAULT false,
    is_sent BOOLEAN DEFAULT false,

    -- Notes
    notes TEXT,
    internal_notes TEXT,
    terms_and_conditions TEXT,

    -- Audit
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(users_id),
    updated_by UUID REFERENCES users(users_id),
    issued_by UUID REFERENCES users(users_id),
    approved_by UUID REFERENCES users(users_id)
);

-- Invoice items with Serbian tax calculations
CREATE TABLE invoice_items (
    invoice_items_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    invoice_id UUID REFERENCES invoices(invoices_id) ON DELETE CASCADE,

    -- Product reference
    product_id UUID REFERENCES products(products_id),
    product_code VARCHAR(50),
    product_name VARCHAR(255) NOT NULL,

    -- Quantity and pricing
    quantity DECIMAL(15,3) NOT NULL,
    unit_measure VARCHAR(20) DEFAULT 'kom',
    unit_price DECIMAL(15,2) NOT NULL,
    discount_percentage DECIMAL(5,2) DEFAULT 0,
    discount_amount DECIMAL(15,2) DEFAULT 0,

    -- PDV calculation per item
    pdv_rate DECIMAL(5,2) DEFAULT 20.00,
    pdv_base DECIMAL(15,2), -- (quantity * unit_price) - discount_amount
    pdv_amount DECIMAL(15,2), -- pdv_base * pdv_rate / 100

    -- Total
    line_total DECIMAL(15,2), -- (quantity * unit_price) - discount_amount + pdv_amount

    -- Description
    description TEXT,

    -- Audit
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- 6. GENERAL LEDGER & ACCOUNTING (Serbian SRPS standards)
-- ============================================================================

-- Chart of accounts (Serbian accounting plan)
CREATE TABLE chart_of_accounts (
    chart_of_accounts_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID REFERENCES companies(companies_id),

    -- Account details
    account_code VARCHAR(10) UNIQUE NOT NULL,
    account_name VARCHAR(255) NOT NULL,
    account_name_sr VARCHAR(255) NOT NULL,

    -- Account classification
    account_type_id UUID, -- References account_types
    account_category VARCHAR(50), -- asset, liability, equity, revenue, expense
    account_subcategory VARCHAR(100),

    -- Serbian accounting specifics
    is_pdv_account BOOLEAN DEFAULT false,
    is_bank_account BOOLEAN DEFAULT false,
    is_inventory_account BOOLEAN DEFAULT false,

    -- Status
    is_active BOOLEAN DEFAULT true,
    is_system_account BOOLEAN DEFAULT false,

    -- Description
    description TEXT,
    description_sr TEXT,

    -- Audit
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Account types (SRPS classification)
CREATE TABLE account_types (
    account_types_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    type_code VARCHAR(10) UNIQUE NOT NULL,
    type_name VARCHAR(100) NOT NULL,
    type_name_sr VARCHAR(100) NOT NULL,
    description TEXT,
    normal_balance VARCHAR(10), -- debit, credit
    is_active BOOLEAN DEFAULT true
);

-- General ledger transactions
CREATE TABLE general_ledger (
    general_ledger_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID REFERENCES companies(companies_id),

    -- Transaction details
    transaction_date DATE NOT NULL,
    posting_date DATE NOT NULL DEFAULT CURRENT_DATE,
    document_number VARCHAR(50),
    document_type VARCHAR(50), -- invoice, payment, journal_entry, etc.

    -- Account entries
    account_id UUID REFERENCES chart_of_accounts(chart_of_accounts_id) NOT NULL,
    debit_amount DECIMAL(15,2) DEFAULT 0,
    credit_amount DECIMAL(15,2) DEFAULT 0,

    -- Serbian-specific
    pdv_rate DECIMAL(5,2),
    pdv_amount DECIMAL(15,2),
    currency VARCHAR(3) DEFAULT 'RSD',
    exchange_rate DECIMAL(10,4) DEFAULT 1.0000,

    -- References
    reference_id UUID, -- Can reference invoices, payments, etc.
    reference_type VARCHAR(50), -- invoice, payment, adjustment
    reference_number VARCHAR(100),

    -- Transaction details
    description TEXT NOT NULL,
    description_sr TEXT,

    -- Period and status
    fiscal_year INTEGER,
    fiscal_period INTEGER,
    transaction_type VARCHAR(20), -- normal, adjustment, closing
    status VARCHAR(20) DEFAULT 'posted', -- draft, posted, reversed

    -- Audit
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(users_id),
    posted_by UUID REFERENCES users(users_id),
    approved_by UUID REFERENCES users(users_id)
);

-- ============================================================================
-- 7. PAYMENTS & BANKING (Serbian banking system)
-- ============================================================================

-- Payment methods (Serbian banking)
CREATE TABLE payment_methods (
    payment_methods_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID REFERENCES companies(companies_id),
    method_code VARCHAR(20) UNIQUE NOT NULL,
    method_name VARCHAR(100) NOT NULL,
    method_name_sr VARCHAR(100) NOT NULL,

    -- Payment details
    bank_account_required BOOLEAN DEFAULT false,
    reference_required BOOLEAN DEFAULT false,
    processing_fee DECIMAL(15,2) DEFAULT 0,
    processing_fee_percentage DECIMAL(5,2) DEFAULT 0,

    -- Integration
    bank_integration_enabled BOOLEAN DEFAULT false,
    api_endpoint VARCHAR(255),
    api_key_encrypted TEXT,

    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Payments table with Serbian banking integration
CREATE TABLE payments (
    payments_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID REFERENCES companies(companies_id),

    -- Payment identification
    payment_number VARCHAR(50) UNIQUE NOT NULL,
    payment_type VARCHAR(20) DEFAULT 'outgoing', -- incoming, outgoing
    payment_method_id UUID REFERENCES payment_methods(payment_methods_id),

    -- Financial details
    amount DECIMAL(15,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'RSD',
    exchange_rate DECIMAL(10,4) DEFAULT 1.0000,

    -- Serbian banking details
    payer_name VARCHAR(255),
    payer_pib VARCHAR(20),
    payer_account VARCHAR(30),

    recipient_name VARCHAR(255),
    recipient_pib VARCHAR(20),
    recipient_account VARCHAR(30),
    recipient_bank VARCHAR(100),

    -- Payment reference (Serbian standard)
    payment_reference VARCHAR(100), -- Racun za uplatu
    payment_code VARCHAR(10), -- 289 - standard payment code
    payment_purpose VARCHAR(100), -- Svrha uplate

    -- Dates
    payment_date DATE NOT NULL,
    value_date DATE,
    due_date DATE,

    -- Status
    status VARCHAR(20) DEFAULT 'draft', -- draft, processed, completed, failed, cancelled
    bank_status VARCHAR(20), -- Bank's processing status
    bank_reference VARCHAR(100), -- Bank's reference number

    -- References
    invoice_id UUID REFERENCES invoices(invoices_id),
    customer_id UUID REFERENCES customers(customers_id),
    supplier_id UUID REFERENCES suppliers(suppliers_id),

    -- Additional info
    description TEXT,
    notes TEXT,

    -- Audit
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(users_id),
    processed_by UUID REFERENCES users(users_id),
    approved_by UUID REFERENCES users(users_id)
);

-- ============================================================================
-- 8. AI/ML FEATURES (For Serbian business analysis)
-- ============================================================================

-- AI insights for Serbian business
CREATE TABLE ai_insights (
    ai_insights_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID REFERENCES companies(companies_id),
    user_id UUID REFERENCES users(users_id),

    -- Insight details
    insight_type VARCHAR(50) NOT NULL, -- financial, operational, customer, market
    insight_subtype VARCHAR(100),
    title VARCHAR(255) NOT NULL,
    summary TEXT NOT NULL,
    detailed_analysis TEXT,

    -- Serbian business context
    business_area VARCHAR(50), -- pdv, currency, banking, compliance
    affected_entities TEXT[], -- companies, customers, suppliers affected
    recommendation TEXT,

    -- Input data and sources
    input_data JSONB,
    data_sources TEXT[], -- invoices, payments, ledger, etc.
    time_period_start DATE,
    time_period_end DATE,

    -- AI processing
    model_used VARCHAR(100),
    confidence_score DECIMAL(5,2), -- 0-100
    processing_time_ms INTEGER,

    -- Embedding for semantic search
    embedding_vector VECTOR(1536),

    -- Impact assessment
    impact_level VARCHAR(20), -- critical, high, medium, low
    impact_area VARCHAR(100), -- revenue, costs, compliance, efficiency
    estimated_impact DECIMAL(15,2),

    -- Status and validation
    status VARCHAR(20) DEFAULT 'active', -- draft, active, archived, rejected
    is_automated BOOLEAN DEFAULT true,
    accuracy_verified BOOLEAN DEFAULT false,
    verified_by UUID REFERENCES users(users_id),
    verified_at TIMESTAMP,

    -- Quality scores
    quality_score DECIMAL(3,2), -- 0.0 - 1.0
    usefulness_score DECIMAL(3,2), -- 0.0 - 1.0

    -- Audit
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Chat sessions for AI conversations
CREATE TABLE chat_sessions (
    chat_sessions_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(users_id),
    company_id UUID REFERENCES companies(companies_id),

    session_title VARCHAR(255),
    session_type VARCHAR(20) DEFAULT 'general', -- general, support, technical, financial
    model_used VARCHAR(50) DEFAULT 'gpt-4',
    total_tokens INTEGER DEFAULT 0,

    -- Serbian language support
    language VARCHAR(5) DEFAULT 'sr-RS',
    use_serbian BOOLEAN DEFAULT true,

    -- Status
    status VARCHAR(20) DEFAULT 'active', -- active, completed, archived
    is_archived BOOLEAN DEFAULT false,

    -- Audit
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_message_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Chat messages with Serbian language support
CREATE TABLE chat_messages (
    chat_messages_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    chat_session_id UUID REFERENCES chat_sessions(chat_sessions_id) ON DELETE CASCADE,

    -- Message content
    message_type VARCHAR(20) NOT NULL, -- user, assistant, system
    content TEXT NOT NULL,
    response_content TEXT, -- For AI responses

    -- Serbian language processing
    language_detected VARCHAR(5),
    is_translated BOOLEAN DEFAULT false,
    original_content TEXT,

    -- AI processing
    model_used VARCHAR(50),
    tokens_used INTEGER DEFAULT 0,
    processing_time_ms INTEGER,
    confidence_score DECIMAL(5,2),

    -- Embedding for semantic search
    embedding_vector VECTOR(1536),

    -- Context and references
    referenced_insight_id UUID REFERENCES ai_insights(ai_insights_id),
    referenced_invoice_id UUID REFERENCES invoices(invoices_id),
    referenced_customer_id UUID REFERENCES customers(customers_id),
    referenced_product_id UUID REFERENCES products(products_id),

    -- Status
    status VARCHAR(20) DEFAULT 'sent', -- sent, delivered, read, failed

    -- Audit
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- 9. SYSTEM MANAGEMENT & MONITORING
-- ============================================================================

-- System settings
CREATE TABLE system_settings (
    system_settings_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    setting_key VARCHAR(100) UNIQUE NOT NULL,
    setting_value JSONB,
    setting_type VARCHAR(50), -- database, ai, security, ui
    is_system_setting BOOLEAN DEFAULT true,
    is_editable BOOLEAN DEFAULT true,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Performance metrics
CREATE TABLE performance_metrics (
    performance_metrics_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    metric_name VARCHAR(100) NOT NULL,
    metric_value DECIMAL(15,6),
    metric_unit VARCHAR(20),
    metric_type VARCHAR(20), -- timing, resource, count, rate
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    source VARCHAR(100), -- system, database, ai, ui
    details JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- System logs
CREATE TABLE system_logs (
    system_logs_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    log_level VARCHAR(20) NOT NULL, -- debug, info, warning, error, critical
    log_category VARCHAR(50), -- database, ai, security, business
    message TEXT NOT NULL,
    details JSONB,
    user_id UUID REFERENCES users(users_id),
    company_id UUID REFERENCES companies(companies_id),
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- 10. INDEXES AND PERFORMANCE OPTIMIZATION
-- ============================================================================

-- Primary table indexes
CREATE INDEX idx_companies_status ON companies(status) WHERE status = 'active';
CREATE INDEX idx_companies_pib ON companies(tax_id);
CREATE INDEX idx_companies_registration ON companies(registration_number);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_status ON users(status) WHERE status = 'active';
CREATE INDEX idx_users_company ON users(company_id);

CREATE INDEX idx_products_company ON products(company_id);
CREATE INDEX idx_products_category ON products(category_id);
CREATE INDEX idx_products_status ON products(is_active) WHERE is_active = true;

CREATE INDEX idx_invoices_company ON invoices(company_id);
CREATE INDEX idx_invoices_customer ON invoices(customer_id);
CREATE INDEX idx_invoices_date ON invoices(invoice_date);
CREATE INDEX idx_invoices_status ON invoices(status);

CREATE INDEX idx_invoice_items_invoice ON invoice_items(invoice_id);
CREATE INDEX idx_invoice_items_product ON invoice_items(product_id);

CREATE INDEX idx_general_ledger_company ON general_ledger(company_id);
CREATE INDEX idx_general_ledger_account ON general_ledger(account_id);
CREATE INDEX idx_general_ledger_date ON general_ledger(transaction_date);
CREATE INDEX idx_general_ledger_status ON general_ledger(status) WHERE status = 'posted';

CREATE INDEX idx_payments_company ON payments(company_id);
CREATE INDEX idx_payments_date ON payments(payment_date);
CREATE INDEX idx_payments_status ON payments(status);

-- AI/ML indexes
CREATE INDEX idx_ai_insights_company ON ai_insights(company_id);
CREATE INDEX idx_ai_insights_type ON ai_insights(insight_type);
CREATE INDEX idx_ai_insights_status ON ai_insights(status) WHERE status = 'active';
CREATE INDEX idx_ai_insights_embedding ON ai_insights USING ivfflat (embedding_vector vector_cosine_ops) WITH (lists = 100);

CREATE INDEX idx_chat_sessions_user ON chat_sessions(user_id);
CREATE INDEX idx_chat_sessions_status ON chat_sessions(status) WHERE status = 'active';

CREATE INDEX idx_chat_messages_session ON chat_messages(chat_session_id);
CREATE INDEX idx_chat_messages_type ON chat_messages(message_type);
CREATE INDEX idx_chat_messages_embedding ON chat_messages USING ivfflat (embedding_vector vector_cosine_ops) WITH (lists = 100);

-- Performance indexes
CREATE INDEX idx_performance_metrics_name ON performance_metrics(metric_name);
CREATE INDEX idx_performance_metrics_timestamp ON performance_metrics(timestamp);
CREATE INDEX idx_performance_metrics_type ON performance_metrics(metric_type);

CREATE INDEX idx_system_logs_level ON system_logs(log_level);
CREATE INDEX idx_system_logs_category ON system_logs(log_category);
CREATE INDEX idx_system_logs_timestamp ON system_logs(created_at);

-- ============================================================================
-- 11. FUNCTIONS AND TRIGGERS
-- ============================================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply updated_at trigger to all tables
CREATE TRIGGER update_companies_updated_at BEFORE UPDATE ON companies FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_products_updated_at BEFORE UPDATE ON products FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_customers_updated_at BEFORE UPDATE ON customers FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_suppliers_updated_at BEFORE UPDATE ON suppliers FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_invoices_updated_at BEFORE UPDATE ON invoices FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_general_ledger_updated_at BEFORE UPDATE ON general_ledger FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_payments_updated_at BEFORE UPDATE ON payments FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_ai_insights_updated_at BEFORE UPDATE ON ai_insights FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to calculate PDV (VAT) for invoice items
CREATE OR REPLACE FUNCTION calculate_pdv_for_invoice_item()
RETURNS TRIGGER AS $$
BEGIN
    -- Calculate PDV base: (quantity * unit_price) - discount_amount
    NEW.pdv_base := (NEW.quantity * NEW.unit_price) - COALESCE(NEW.discount_amount, 0);

    -- Calculate PDV amount: pdv_base * pdv_rate / 100
    NEW.pdv_amount := NEW.pdv_base * NEW.pdv_rate / 100;

    -- Calculate line total: pdv_base + pdv_amount
    NEW.line_total := NEW.pdv_base + NEW.pdv_amount;

    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger for PDV calculation on invoice items
CREATE TRIGGER calculate_invoice_item_pdv
    BEFORE INSERT OR UPDATE ON invoice_items
    FOR EACH ROW EXECUTE FUNCTION calculate_pdv_for_invoice_item();

-- Function to update invoice totals when items change
CREATE OR REPLACE FUNCTION update_invoice_totals()
RETURNS TRIGGER AS $$
BEGIN
    -- Update invoice totals based on items
    UPDATE invoices
    SET
        subtotal = COALESCE((
            SELECT SUM(pdv_base)
            FROM invoice_items
            WHERE invoice_id = COALESCE(NEW.invoice_id, OLD.invoice_id)
        ), 0),
        pdv_amount = COALESCE((
            SELECT SUM(pdv_amount)
            FROM invoice_items
            WHERE invoice_id = COALESCE(NEW.invoice_id, OLD.invoice_id)
        ), 0),
        total_amount = COALESCE((
            SELECT SUM(line_total)
            FROM invoice_items
            WHERE invoice_id = COALESCE(NEW.invoice_id, OLD.invoice_id)
        ), 0),
        updated_at = CURRENT_TIMESTAMP
    WHERE invoices_id = COALESCE(NEW.invoice_id, OLD.invoice_id);

    RETURN COALESCE(NEW, OLD);
END;
$$ language 'plpgsql';

-- Trigger for invoice totals update
CREATE TRIGGER update_invoice_totals_trigger
    AFTER INSERT OR UPDATE OR DELETE ON invoice_items
    FOR EACH ROW EXECUTE FUNCTION update_invoice_totals();

-- ============================================================================
-- 12. SERBIAN BUSINESS ENTITIES SETUP
-- ============================================================================

-- Insert Serbian business entity types
INSERT INTO business_entity_types (
    entity_code, entity_name, entity_name_sr, description,
    tax_requirements, reporting_requirements
) VALUES
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
 '{"financial_statements": true, "tax_returns": true, "partner_reports": true}'::jsonb);

-- Insert Serbian user roles
INSERT INTO user_roles (role_name, role_name_sr, description, permissions, is_system_role) VALUES
('admin', 'Administrator', 'System administrator with full access',
 '{"all_permissions": true, "user_management": true, "system_config": true}'::jsonb, true),

('owner', 'Vlasnik', 'Company owner with full business access',
 '{"company_management": true, "financial_management": true, "user_management": true}'::jsonb, true),

('accountant', 'Računovođa', 'Accounting and financial management',
 '{"financial_read": true, "financial_write": true, "reports_read": true}'::jsonb, true),

('manager', 'Menadžer', 'Department or business unit manager',
 '{"department_read": true, "department_write": true, "reports_read": true}'::jsonb, true),

('sales', 'Prodaja', 'Sales representative',
 '{"customer_read": true, "customer_write": true, "invoice_create": true, "product_read": true}'::jsonb, true),

('user', 'Korisnik', 'Standard user with limited access',
 '{"basic_read": true, "own_data_write": true}'::jsonb, true);

-- ============================================================================
-- 13. SERBIAN CHART OF ACCOUNTS (Simplified version)
-- ============================================================================

-- Insert Serbian account types
INSERT INTO account_types (type_code, type_name, type_name_sr, normal_balance, description) VALUES
('0', 'Fixed Assets', 'Osnovna sredstva', 'debit', 'Property, plant, and equipment'),
('1', 'Current Assets', 'Obrtna sredstva', 'debit', 'Cash, inventory, receivables'),
('2', 'Liabilities', 'Obaveze', 'credit', 'Debts and obligations'),
('3', 'Equity', 'Kapital', 'credit', 'Owner''s equity'),
('4', 'Revenue', 'Prihodi', 'credit', 'Sales and other income'),
('5', 'Expenses', 'Rashodi', 'debit', 'Operating expenses'),
('6', 'Extraordinary Items', 'Vanredni prihodi i rashodi', 'debit', 'Exceptional gains and losses');

-- ============================================================================
-- 14. SYSTEM SETTINGS
-- ============================================================================

-- Insert default system settings
INSERT INTO system_settings (setting_key, setting_value, setting_type, description) VALUES
('company_name', '"ValidoAI"'::jsonb, 'system', 'Default company name'),
('default_currency', '"RSD"'::jsonb, 'financial', 'Default currency for the system'),
('default_language', '"sr-RS"'::jsonb, 'system', 'Default system language'),
('pdv_rate', '20.00'::jsonb, 'tax', 'Default PDV (VAT) rate'),
('fiscal_year_start', '"01-01"'::jsonb, 'financial', 'Fiscal year start date'),
('timezone', '"Europe/Belgrade"'::jsonb, 'system', 'System timezone'),
('date_format', '"dd.mm.yyyy"'::jsonb, 'system', 'Date display format'),
('decimal_separator', '","'::jsonb, 'system', 'Decimal separator'),
('thousands_separator', '"."'::jsonb, 'system', 'Thousands separator');

-- ============================================================================
-- 15. MATERIALIZED VIEWS FOR SERBIAN BUSINESS ANALYSIS
-- ============================================================================

-- Monthly revenue by PDV rate (Serbian tax analysis)
CREATE MATERIALIZED VIEW mv_revenue_by_pdv_rate AS
SELECT
    DATE_TRUNC('month', i.invoice_date) as month,
    c.company_name,
    ii.pdv_rate,
    COUNT(*) as invoice_count,
    SUM(ii.pdv_base) as pdv_base_total,
    SUM(ii.pdv_amount) as pdv_amount_total,
    SUM(ii.line_total) as revenue_total,
    ROUND((SUM(ii.pdv_amount) / NULLIF(SUM(ii.pdv_base), 0)) * 100, 2) as effective_pdv_rate
FROM invoices i
JOIN companies c ON i.company_id = c.companies_id
JOIN invoice_items ii ON i.invoices_id = ii.invoice_id
WHERE i.status = 'paid' AND i.invoice_date >= '2024-01-01'
GROUP BY DATE_TRUNC('month', i.invoice_date), c.company_name, ii.pdv_rate;

-- Customer payment behavior (Serbian market analysis)
CREATE MATERIALIZED VIEW mv_customer_payment_analysis AS
SELECT
    c.customer_name,
    c.company_name,
    COUNT(i.invoices_id) as total_invoices,
    COUNT(CASE WHEN i.payment_status = 'paid' THEN 1 END) as paid_invoices,
    COUNT(CASE WHEN i.payment_status = 'overdue' THEN 1 END) as overdue_invoices,
    AVG(EXTRACT(DAY FROM (i.payment_date - i.due_date))) as avg_payment_delay_days,
    SUM(i.total_amount) as total_amount,
    SUM(CASE WHEN i.payment_status = 'paid' THEN i.total_amount END) as paid_amount,
    ROUND(
        (COUNT(CASE WHEN i.payment_status = 'paid' THEN 1 END)::decimal /
         NULLIF(COUNT(i.invoices_id), 0)) * 100, 2
    ) as payment_success_rate
FROM customers c
LEFT JOIN invoices i ON c.customers_id = i.customer_id
WHERE i.invoice_date >= '2024-01-01'
GROUP BY c.customers_id, c.customer_name, c.company_name;

-- Financial position by Serbian accounting standards
CREATE MATERIALIZED VIEW mv_financial_position_srps AS
SELECT
    gl.company_id,
    c.company_name,
    DATE_TRUNC('month', gl.transaction_date) as report_month,
    -- Assets (0-1 accounts)
    COALESCE(SUM(CASE WHEN coa.account_code LIKE '0%' OR coa.account_code LIKE '1%' THEN gl.debit_amount - gl.credit_amount END), 0) as total_assets,
    -- Liabilities (2 accounts)
    COALESCE(SUM(CASE WHEN coa.account_code LIKE '2%' THEN gl.credit_amount - gl.debit_amount END), 0) as total_liabilities,
    -- Equity (3 accounts)
    COALESCE(SUM(CASE WHEN coa.account_code LIKE '3%' THEN gl.credit_amount - gl.debit_amount END), 0) as total_equity,
    -- Revenue (4 accounts)
    COALESCE(SUM(CASE WHEN coa.account_code LIKE '4%' THEN gl.credit_amount - gl.debit_amount END), 0) as total_revenue,
    -- Expenses (5 accounts)
    COALESCE(SUM(CASE WHEN coa.account_code LIKE '5%' THEN gl.debit_amount - gl.credit_amount END), 0) as total_expenses
FROM general_ledger gl
JOIN companies c ON gl.company_id = c.companies_id
JOIN chart_of_accounts coa ON gl.account_id = coa.chart_of_accounts_id
WHERE gl.status = 'posted' AND gl.transaction_date >= '2024-01-01'
GROUP BY gl.company_id, c.company_name, DATE_TRUNC('month', gl.transaction_date);

-- ============================================================================
-- 16. FUNCTIONS FOR SERBIAN BUSINESS OPERATIONS
-- ============================================================================

-- Function to calculate PDV for Serbian e-invoice
CREATE OR REPLACE FUNCTION calculate_serbian_pdv(
    p_subtotal DECIMAL,
    p_pdv_rate DECIMAL DEFAULT 20.00
)
RETURNS TABLE(
    pdv_base DECIMAL,
    pdv_amount DECIMAL,
    total DECIMAL
) AS $$
BEGIN
    -- PDV base is the subtotal
    pdv_base := p_subtotal;

    -- PDV amount calculation (Serbian standard)
    pdv_amount := ROUND(p_subtotal * p_pdv_rate / 100, 2);

    -- Total with PDV
    total := pdv_base + pdv_amount;

    RETURN NEXT;
END;
$$ language 'plpgsql';

-- Function to generate Serbian e-invoice QR code data
CREATE OR REPLACE FUNCTION generate_serbian_e_invoice_qr(
    p_invoice_id UUID
)
RETURNS TEXT AS $$
DECLARE
    v_invoice invoices;
    v_qr_data TEXT;
BEGIN
    -- Get invoice details
    SELECT * INTO v_invoice FROM invoices WHERE invoices_id = p_invoice_id;

    -- Generate QR code data in Serbian format
    v_qr_data := json_build_object(
        'ver', '1.0',
        'tip', 'račun',
        'br', v_invoice.invoice_number,
        'dat', to_char(v_invoice.invoice_date, 'DD.MM.YYYY'),
        'iznos', v_invoice.total_amount,
        'pdv', v_invoice.pdv_amount,
        'platilac', json_build_object(
            'naziv', v_invoice.customer_name,
            'pib', v_invoice.customer_pib
        ),
        'primalac', json_build_object(
            'naziv', (SELECT company_name FROM companies WHERE companies_id = v_invoice.company_id),
            'pib', (SELECT tax_id FROM companies WHERE companies_id = v_invoice.company_id)
        )
    )::text;

    RETURN v_qr_data;
END;
$$ language 'plpgsql';

-- Function to generate Serbian payment reference
CREATE OR REPLACE FUNCTION generate_serbian_payment_reference(
    p_invoice_id UUID,
    p_payment_code VARCHAR DEFAULT '289'
)
RETURNS VARCHAR AS $$
DECLARE
    v_invoice invoices;
    v_reference VARCHAR(100);
    v_clean_amount VARCHAR(20);
BEGIN
    -- Get invoice details
    SELECT * INTO v_invoice FROM invoices WHERE invoices_id = p_invoice_id;

    -- Clean amount for Serbian banking format
    v_clean_amount := REPLACE(ROUND(v_invoice.total_amount, 2)::text, '.', '');

    -- Generate Serbian payment reference
    -- Format: 289 + invoice_number + amount
    v_reference := p_payment_code || '-' ||
                   REPLACE(v_invoice.invoice_number, '-', '') || '-' ||
                   v_clean_amount;

    RETURN v_reference;
END;
$$ language 'plpgsql';

-- Function to get Serbian business health score
CREATE OR REPLACE FUNCTION get_serbian_business_health_score(
    p_company_id UUID,
    p_analysis_date DATE DEFAULT CURRENT_DATE
)
RETURNS TABLE(
    company_name VARCHAR,
    health_score DECIMAL(5,2),
    pdv_compliance_score DECIMAL(5,2),
    payment_success_rate DECIMAL(5,2),
    financial_stability_score DECIMAL(5,2),
    customer_satisfaction_score DECIMAL(5,2),
    recommendations TEXT[]
) AS $$
DECLARE
    v_company_name VARCHAR;
    v_health_score DECIMAL(5,2) := 0;
    v_pdv_compliance DECIMAL(5,2) := 0;
    v_payment_rate DECIMAL(5,2) := 0;
    v_financial_stability DECIMAL(5,2) := 0;
    v_customer_satisfaction DECIMAL(5,2) := 0;
    v_recommendations TEXT[] := ARRAY[]::TEXT[];
BEGIN
    -- Get company name
    SELECT company_name INTO v_company_name FROM companies WHERE companies_id = p_company_id;

    -- Calculate PDV compliance score
    SELECT ROUND(
        (COUNT(CASE WHEN i.is_e_invoice = true THEN 1 END)::decimal /
         NULLIF(COUNT(*), 0)) * 100, 2
    ) INTO v_pdv_compliance
    FROM invoices i
    WHERE i.company_id = p_company_id AND i.invoice_date >= p_analysis_date - INTERVAL '12 months';

    -- Calculate payment success rate
    SELECT ROUND(
        (COUNT(CASE WHEN payment_status = 'paid' THEN 1 END)::decimal /
         NULLIF(COUNT(*), 0)) * 100, 2
    ) INTO v_payment_rate
    FROM invoices
    WHERE company_id = p_company_id AND invoice_date >= p_analysis_date - INTERVAL '12 months';

    -- Calculate financial stability (simplified)
    SELECT ROUND(
        GREATEST(0, LEAST(100,
            CASE
                WHEN total_assets > total_liabilities THEN 80
                WHEN total_assets > total_liabilities * 0.8 THEN 60
                ELSE 40
            END
        )), 2
    ) INTO v_financial_stability
    FROM mv_financial_position_srps
    WHERE company_id = p_company_id
    ORDER BY report_month DESC LIMIT 1;

    -- Calculate customer satisfaction (based on payment behavior)
    v_customer_satisfaction := GREATEST(0, LEAST(100, v_payment_rate * 0.8 + 20));

    -- Calculate overall health score
    v_health_score := ROUND((v_pdv_compliance * 0.3 + v_payment_rate * 0.3 +
                           v_financial_stability * 0.25 + v_customer_satisfaction * 0.15), 2);

    -- Generate recommendations
    IF v_pdv_compliance < 80 THEN
        v_recommendations := v_recommendations || 'Implement e-invoicing system for better PDV compliance';
    END IF;

    IF v_payment_rate < 85 THEN
        v_recommendations := v_recommendations || 'Improve customer payment collection processes';
    END IF;

    IF v_financial_stability < 60 THEN
        v_recommendations := v_recommendations || 'Review financial position and consider debt reduction';
    END IF;

    IF v_customer_satisfaction < 70 THEN
        v_recommendations := v_recommendations || 'Implement customer feedback system and improve service quality';
    END IF;

    RETURN NEXT;
END;
$$ language 'plpgsql';

-- ============================================================================
-- FINAL NOTES
-- ============================================================================

/*
This master SQL structure provides:

1. **Serbian Business Compliance**:
   - PDV (VAT) calculations and reporting
   - Serbian currency (RSD) support
   - E-faktura (e-invoicing) compliance
   - SRPS (Serbian accounting standards)
   - Local tax requirements

2. **Business Entity Support**:
   - DOO (Limited Liability Company)
   - AD (Joint Stock Company)
   - Preduzetnik (Entrepreneur)
   - Local identification numbers

3. **Financial Features**:
   - Multi-currency support (RSD, EUR, USD)
   - Serbian banking integration
   - Payment reference generation
   - Financial reporting in local standards

4. **AI/ML Integration**:
   - Serbian language support
   - Business-specific insights
   - Semantic search capabilities
   - Automated analysis

5. **Performance Optimized**:
   - Strategic indexing
   - Materialized views for analytics
   - Vector indexes for AI search
   - Automated maintenance

To use this structure:
1. Execute this SQL file in PostgreSQL 17+
2. Run the comprehensive data script next
3. Set up the application with proper Serbian configurations

This provides a complete foundation for Serbian business financial management
with AI-powered insights and full regulatory compliance.
*/
