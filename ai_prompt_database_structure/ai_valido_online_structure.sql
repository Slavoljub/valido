-- AI Valido Online Database Schema Structure
-- Date: August 17, 2025, 11:55 PM CEST
-- Optimized for 10PB scalability, Serbian compliance (PDV, SEF, APR), RBAC with PostgreSQL roles, RLS, history logging, and AI integration

-- Create Database (if not exists)
-- CREATE DATABASE ai_valido_online;

-- Enable Extensions
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS plpython3u;
CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS citus;

-- PostgreSQL Roles for RBAC
CREATE ROLE ai_valido_developer WITH LOGIN PASSWORD 'secure_password';
CREATE ROLE ai_valido_admin WITH LOGIN PASSWORD 'secure_password';
CREATE ROLE ai_valido_accountant WITH LOGIN PASSWORD 'secure_password';
CREATE ROLE ai_valido_manager WITH LOGIN PASSWORD 'secure_password';
CREATE ROLE ai_valido_hr WITH LOGIN PASSWORD 'secure_password';
CREATE ROLE ai_valido_support WITH LOGIN PASSWORD 'secure_password';
CREATE ROLE ai_valido_demo WITH LOGIN PASSWORD 'secure_password';

-- Reference Tables
CREATE TABLE accounts_types (
    accounts_types_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    type_name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE businesses_forms (
    businesses_forms_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    form_name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE businesses_areas (
    businesses_areas_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    area_name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE partners_types (
    partners_types_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    type_name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE transactions_types (
    transactions_types_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    type_name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE taxes_types (
    taxes_types_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    type_name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE modules_names (
    modules_names_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE leads_sources (
    leads_sources_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE leads_stages (
    leads_stages_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    stage_name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE opportunities_stages (
    opportunities_stages_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    stage_name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE invoices_statuses (
    invoices_statuses_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    status_name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE roles (
    roles_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    role_name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE tickets_statuses (
    tickets_statuses_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    status_name VARCHAR(50) UNIQUE NOT NULL, -- open, pending_l1, pending_l2, pending_l3, pending_l4, approved, closed
    description TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Main Tables
CREATE TABLE companies (
    companies_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_name VARCHAR(255) NOT NULL,
    businesses_forms_id UUID REFERENCES businesses_forms(businesses_forms_id),
    businesses_areas_id UUID REFERENCES businesses_areas(businesses_areas_id),
    tax_id VARCHAR(20) UNIQUE NOT NULL,
    registration_number VARCHAR(20) UNIQUE NOT NULL,
    address VARCHAR(255),
    city VARCHAR(100),
    postal_code VARCHAR(20),
    country VARCHAR(100) DEFAULT 'Serbia',
    phone VARCHAR(20),
    email VARCHAR(100),
    website VARCHAR(100),
    description TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP
);

CREATE TABLE partners (
    partners_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    companies_id UUID REFERENCES companies(companies_id),
    partners_types_id UUID REFERENCES partners_types(partners_types_id),
    partner_name VARCHAR(255) NOT NULL,
    tax_id VARCHAR(20),
    address VARCHAR(255),
    city VARCHAR(100),
    postal_code VARCHAR(20),
    country VARCHAR(100) DEFAULT 'Serbia',
    phone VARCHAR(20),
    email VARCHAR(100),
    description TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP
);

CREATE TABLE users (
    users_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    companies_id UUID REFERENCES companies(companies_id),
    roles_id UUID REFERENCES roles(roles_id),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP
);

CREATE TABLE fiscal_years (
    fiscal_years_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    companies_id UUID REFERENCES companies(companies_id),
    year INT NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    status VARCHAR(20) DEFAULT 'open', -- open, closed
    description TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE charts_of_accounts (
    charts_of_accounts_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    companies_id UUID REFERENCES companies(companies_id),
    account_number VARCHAR(20) NOT NULL,
    accounts_types_id UUID REFERENCES accounts_types(accounts_types_id),
    account_name VARCHAR(255) NOT NULL,
    pdv_rate DECIMAL(5,2),
    description TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP
);

CREATE TABLE general_ledgers_transactions (
    general_ledgers_transactions_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    companies_id UUID REFERENCES companies(companies_id),
    fiscal_years_id UUID REFERENCES fiscal_years(fiscal_years_id),
    transaction_date DATE NOT NULL,
    charts_of_accounts_id UUID REFERENCES charts_of_accounts(charts_of_accounts_id),
    transactions_types_id UUID REFERENCES transactions_types(transactions_types_id),
    debit_amount DECIMAL(15,2),
    credit_amount DECIMAL(15,2),
    currency_code CHAR(3) DEFAULT 'RSD',
    description TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP
) PARTITION BY RANGE (transaction_date);

CREATE TABLE invoices_receivable (
    invoices_receivable_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    companies_id UUID REFERENCES companies(companies_id),
    fiscal_years_id UUID REFERENCES fiscal_years(fiscal_years_id),
    invoice_number VARCHAR(50) UNIQUE NOT NULL,
    partners_id UUID REFERENCES partners(partners_id),
    invoice_date DATE NOT NULL,
    due_date DATE NOT NULL,
    total_amount DECIMAL(15,2) NOT NULL,
    currency_code CHAR(3) DEFAULT 'RSD',
    sef_xml TEXT,
    invoices_statuses_id UUID REFERENCES invoices_statuses(invoices_statuses_id),
    description TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP
);

CREATE TABLE invoices_payable (
    invoices_payable_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    companies_id UUID REFERENCES companies(companies_id),
    fiscal_years_id UUID REFERENCES fiscal_years(fiscal_years_id),
    invoice_number VARCHAR(50) UNIQUE NOT NULL,
    partners_id UUID REFERENCES partners(partners_id),
    invoice_date DATE NOT NULL,
    due_date DATE NOT NULL,
    total_amount DECIMAL(15,2) NOT NULL,
    currency_code CHAR(3) DEFAULT 'RSD',
    sef_xml TEXT,
    invoices_statuses_id UUID REFERENCES invoices_statuses(invoices_statuses_id),
    description TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP
);

CREATE TABLE banks_accounts (
    banks_accounts_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    companies_id UUID REFERENCES companies(companies_id),
    bank_name VARCHAR(100) NOT NULL,
    account_number VARCHAR(50) UNIQUE NOT NULL,
    currency_code CHAR(3) DEFAULT 'RSD',
    description TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP
);

CREATE TABLE banks_statements (
    banks_statements_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    companies_id UUID REFERENCES companies(companies_id),
    banks_accounts_id UUID REFERENCES banks_accounts(banks_accounts_id),
    fiscal_years_id UUID REFERENCES fiscal_years(fiscal_years_id),
    statement_date DATE NOT NULL,
    transaction_date DATE NOT NULL,
    amount DECIMAL(15,2) NOT NULL,
    currency_code CHAR(3) DEFAULT 'RSD',
    description TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP
) PARTITION BY RANGE (transaction_date);

CREATE TABLE fixed_assets (
    fixed_assets_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    companies_id UUID REFERENCES companies(companies_id),
    fiscal_years_id UUID REFERENCES fiscal_years(fiscal_years_id),
    asset_name VARCHAR(255) NOT NULL,
    acquisition_date DATE NOT NULL,
    acquisition_value DECIMAL(15,2) NOT NULL,
    depreciation_rate DECIMAL(5,2),
    current_value DECIMAL(15,2),
    description TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP
);

CREATE TABLE budgets (
    budgets_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    companies_id UUID REFERENCES companies(companies_id),
    fiscal_years_id UUID REFERENCES fiscal_years(fiscal_years_id),
    budget_name VARCHAR(255) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    amount DECIMAL(15,2) NOT NULL,
    currency_code CHAR(3) DEFAULT 'RSD',
    description TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP
);

CREATE TABLE taxes_registers (
    taxes_registers_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    companies_id UUID REFERENCES companies(companies_id),
    fiscal_years_id UUID REFERENCES fiscal_years(fiscal_years_id),
    taxes_types_id UUID REFERENCES taxes_types(taxes_types_id),
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    taxable_amount DECIMAL(15,2) NOT NULL,
    tax_amount DECIMAL(15,2) NOT NULL,
    xml_content TEXT,
    description TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP
);

CREATE TABLE inventories_items (
    inventories_items_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    companies_id UUID REFERENCES companies(companies_id),
    fiscal_years_id UUID REFERENCES fiscal_years(fiscal_years_id),
    item_name VARCHAR(255) NOT NULL,
    sku VARCHAR(50) UNIQUE NOT NULL,
    unit_price DECIMAL(15,2) NOT NULL,
    currency_code CHAR(3) DEFAULT 'RSD',
    valuation_method VARCHAR(20) DEFAULT 'fifo',
    description TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP
);

CREATE TABLE warehouses (
    warehouses_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    companies_id UUID REFERENCES companies(companies_id),
    warehouse_name VARCHAR(255) NOT NULL,
    location VARCHAR(255),
    capacity DECIMAL(15,2),
    description TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP
);

CREATE TABLE inventories_transactions (
    inventories_transactions_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    companies_id UUID REFERENCES companies(companies_id),
    inventories_items_id UUID REFERENCES inventories_items(inventories_items_id),
    warehouses_id UUID REFERENCES warehouses(warehouses_id),
    fiscal_years_id UUID REFERENCES fiscal_years(fiscal_years_id),
    transaction_date DATE NOT NULL,
    quantity DECIMAL(15,2) NOT NULL,
    unit_price DECIMAL(15,2) NOT NULL,
    transactions_types_id UUID REFERENCES transactions_types(transactions_types_id),
    description TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP
) PARTITION BY RANGE (transaction_date);

CREATE TABLE crm_contacts (
    crm_contacts_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    companies_id UUID REFERENCES companies(companies_id),
    partners_id UUID REFERENCES partners(partners_id),
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    email VARCHAR(100),
    phone VARCHAR(20),
    description TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP
);

CREATE TABLE crm_leads (
    crm_leads_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    companies_id UUID REFERENCES companies(companies_id),
    leads_sources_id UUID REFERENCES leads_sources(leads_sources_id),
    leads_stages_id UUID REFERENCES leads_stages(leads_stages_id),
    lead_name VARCHAR(255) NOT NULL,
    expected_revenue DECIMAL(15,2),
    currency_code CHAR(3) DEFAULT 'RSD',
    description TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP
);

CREATE TABLE crm_opportunities (
    crm_opportunities_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    companies_id UUID REFERENCES companies(companies_id),
    crm_leads_id UUID REFERENCES crm_leads(crm_leads_id),
    opportunities_stages_id UUID REFERENCES opportunities_stages(opportunities_stages_id),
    opportunity_name VARCHAR(255) NOT NULL,
    expected_revenue DECIMAL(15,2),
    currency_code CHAR(3) DEFAULT 'RSD',
    description TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP
);

CREATE TABLE employees_data (
    employees_data_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    companies_id UUID REFERENCES companies(companies_id),
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    employee_number VARCHAR(50) UNIQUE NOT NULL,
    hire_date DATE NOT NULL,
    position VARCHAR(100),
    department VARCHAR(100),
    salary DECIMAL(15,2),
    currency_code CHAR(3) DEFAULT 'RSD',
    description TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP
);

CREATE TABLE payrolls (
    payrolls_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    companies_id UUID REFERENCES companies(companies_id),
    employees_data_id UUID REFERENCES employees_data(employees_data_id),
    fiscal_years_id UUID REFERENCES fiscal_years(fiscal_years_id),
    payroll_date DATE NOT NULL,
    gross_amount DECIMAL(15,2) NOT NULL,
    net_amount DECIMAL(15,2) NOT NULL,
    tax_amount DECIMAL(15,2) NOT NULL,
    currency_code CHAR(3) DEFAULT 'RSD',
    description TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP
);

CREATE TABLE emails_queues (
    emails_queues_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    companies_id UUID REFERENCES companies(companies_id),
    recipient_email VARCHAR(100) NOT NULL,
    subject VARCHAR(255) NOT NULL,
    body TEXT NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    scheduled_send_time TIMESTAMP,
    recurrence_pattern VARCHAR(50),
    description TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP
);

CREATE TABLE emails_templates (
    emails_templates_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    companies_id UUID REFERENCES companies(companies_id),
    template_name VARCHAR(100) NOT NULL,
    subject VARCHAR(255) NOT NULL,
    body TEXT NOT NULL,
    placeholders JSONB,
    description TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP
);

CREATE TABLE emails_logs (
    emails_logs_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    companies_id UUID REFERENCES companies(companies_id),
    emails_queues_id UUID REFERENCES emails_queues(emails_queues_id),
    sent_at TIMESTAMP,
    status VARCHAR(20) NOT NULL,
    error_message TEXT,
    description TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE erp_modules_configs (
    erp_modules_configs_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    companies_id UUID REFERENCES companies(companies_id),
    modules_names_id UUID REFERENCES modules_names(modules_names_id),
    enabled BOOLEAN DEFAULT TRUE,
    config_settings JSONB,
    description TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP
);

CREATE TABLE routes_permissions (
    routes_permissions_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    roles_id UUID REFERENCES roles(roles_id),
    route_path VARCHAR(255) NOT NULL,
    methods VARCHAR(50) NOT NULL, -- e.g., 'GET,POST,PUT,DELETE'
    allowed_columns TEXT[], -- e.g., '{"column1", "column2"}'
    allow_access BOOLEAN DEFAULT FALSE,
    description TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE table_history_logs (
    history_log_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    companies_id UUID REFERENCES companies(companies_id),
    users_id UUID REFERENCES users(users_id),
    table_name VARCHAR(100) NOT NULL,
    operation VARCHAR(20) NOT NULL,
    old_values JSONB,
    new_values JSONB,
    action_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    description TEXT,
    notes TEXT
);

CREATE TABLE audit_logs (
    audit_logs_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    companies_id UUID REFERENCES companies(companies_id),
    users_id UUID REFERENCES users(users_id),
    table_name VARCHAR(100) NOT NULL,
    operation VARCHAR(20) NOT NULL,
    old_values JSONB,
    new_values JSONB,
    action_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    description TEXT,
    notes TEXT
);

CREATE TABLE demo_logs (
    demo_logs_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    users_id UUID REFERENCES users(users_id),
    action VARCHAR(100),
    action_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    companies_id UUID REFERENCES companies(companies_id)
);

CREATE TABLE tickets (
    tickets_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    tickets_statuses_id UUID REFERENCES tickets_statuses(tickets_statuses_id),
    requester_id UUID REFERENCES users(users_id),
    approver_id UUID REFERENCES users(users_id),
    modules_names_id UUID REFERENCES modules_names(modules_names_id),
    companies_id UUID REFERENCES companies(companies_id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE llm_embeddings (
    llm_embeddings_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_type VARCHAR(50) NOT NULL,
    entity_id UUID NOT NULL,
    embedding_vector VECTOR(1536),
    context_text TEXT NOT NULL,
    companies_id UUID REFERENCES companies(companies_id) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP
);

-- Indexes for Scalability
CREATE INDEX idx_general_ledgers_transactions_date ON general_ledgers_transactions USING BRIN (transaction_date);
CREATE INDEX idx_banks_statements_date ON banks_statements USING BRIN (transaction_date);
CREATE INDEX idx_inventories_transactions_date ON inventories_transactions USING BRIN (transaction_date);
CREATE INDEX idx_companies_id ON companies (companies_id);
CREATE INDEX idx_users_companies_id ON users (companies_id);
CREATE INDEX idx_llm_embeddings ON llm_embeddings USING hnsw (embedding_vector vector_cosine_ops);

-- RLS Policies
ALTER TABLE companies ENABLE ROW LEVEL SECURITY;
CREATE POLICY developer_access ON companies USING (true) WITH CHECK (true);
CREATE POLICY admin_access ON companies USING (companies_id = (SELECT companies_id FROM users WHERE users_id = current_setting('app.current_user_id')::UUID));
CREATE POLICY accountant_access ON companies USING (companies_id = (SELECT companies_id FROM users WHERE users_id = current_setting('app.current_user_id')::UUID));
CREATE POLICY manager_access ON companies USING (companies_id = (SELECT companies_id FROM users WHERE users_id = current_setting('app.current_user_id')::UUID));
CREATE POLICY hr_access ON companies USING (companies_id = (SELECT companies_id FROM users WHERE users_id = current_setting('app.current_user_id')::UUID));
CREATE POLICY support_access ON companies USING (true);
CREATE POLICY demo_access ON companies USING (companies_id = (SELECT companies_id FROM users WHERE users_id = current_setting('app.current_user_id')::UUID));

-- Apply similar RLS policies to other tables
DO $$
DECLARE
    table_name TEXT;
BEGIN
    FOREACH table_name IN ARRAY ARRAY[
        'users', 'fiscal_years', 'charts_of_accounts', 'general_ledgers_transactions',
        'invoices_receivable', 'invoices_payable', 'partners', 'banks_accounts',
        'banks_statements', 'fixed_assets', 'budgets', 'taxes_registers',
        'inventories_items', 'warehouses', 'inventories_transactions', 'crm_contacts',
        'crm_leads', 'crm_opportunities', 'employees_data', 'payrolls', 'emails_queues',
        'emails_templates', 'emails_logs', 'erp_modules_configs', 'audit_logs',
        'demo_logs', 'tickets', 'llm_embeddings'
    ]
    LOOP
        EXECUTE format('ALTER TABLE %I ENABLE ROW LEVEL SECURITY', table_name);
        EXECUTE format('CREATE POLICY developer_access ON %I USING (true) WITH CHECK (true)', table_name);
        EXECUTE format('CREATE POLICY admin_access ON %I USING (companies_id = (SELECT companies_id FROM users WHERE users_id = current_setting(''app.current_user_id'')::UUID))', table_name);
        EXECUTE format('CREATE POLICY accountant_access ON %I USING (companies_id = (SELECT companies_id FROM users WHERE users_id = current_setting(''app.current_user_id'')::UUID))', table_name);
        EXECUTE format('CREATE POLICY manager_access ON %I USING (companies_id = (SELECT companies_id FROM users WHERE users_id = current_setting(''app.current_user_id'')::UUID))', table_name);
        EXECUTE format('CREATE POLICY hr_access ON %I USING (companies_id = (SELECT companies_id FROM users WHERE users_id = current_setting(''app.current_user_id'')::UUID))', table_name);
        EXECUTE format('CREATE POLICY support_access ON %I USING (true)', table_name);
        EXECUTE format('CREATE POLICY demo_access ON %I USING (companies_id = (SELECT companies_id FROM users WHERE users_id = current_setting(''app.current_user_id'')::UUID))', table_name);
    END LOOP;
END $$;

-- Table Permissions
GRANT ALL ON ALL TABLES IN SCHEMA public TO ai_valido_developer;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO ai_valido_admin;
GRANT SELECT, INSERT, UPDATE ON general_ledgers_transactions, invoices_receivable, invoices_payable, taxes_registers, banks_accounts, fixed_assets, budgets TO ai_valido_accountant;
GRANT SELECT, INSERT, UPDATE, DELETE ON crm_contacts, crm_leads, crm_opportunities, inventories_items, inventories_transactions, warehouses TO ai_valido_manager;
GRANT SELECT ON payrolls, employees_data TO ai_valido_hr;
GRANT SELECT ON audit_logs, demo_logs, erp_modules_configs, tickets TO ai_valido_support;
GRANT INSERT, UPDATE ON tickets TO ai_valido_support;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO ai_valido_demo;

-- Fiscal Year Procedures
CREATE OR REPLACE PROCEDURE open_fiscal_year(comp_id UUID, yr INT)
LANGUAGE plpgsql AS $$
BEGIN
    INSERT INTO fiscal_years (companies_id, year, start_date, end_date, status)
    VALUES (comp_id, yr, make_date(yr, 1, 1), make_date(yr, 12, 31), 'open');
END $$;

CREATE OR REPLACE PROCEDURE close_fiscal_year(comp_id UUID, yr INT)
LANGUAGE plpgsql AS $$
BEGIN
    UPDATE fiscal_years
    SET status = 'closed'
    WHERE companies_id = comp_id AND year = yr;
    -- Archive transactions
    INSERT INTO general_ledgers_transactions_archive
    SELECT * FROM general_ledgers_transactions
    WHERE companies_id = comp_id AND EXTRACT(YEAR FROM transaction_date) = yr;
END $$;

-- History Logging Trigger
CREATE OR REPLACE FUNCTION log_table_history()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO table_history_logs (
        companies_id, users_id, table_name, operation, old_values, new_values
    )
    VALUES (
        NEW.companies_id,
        current_setting('app.current_user_id')::UUID,
        TG_TABLE_NAME,
        TG_OP,
        CASE WHEN TG_OP = 'UPDATE' OR TG_OP = 'DELETE' THEN row_to_json(OLD)::JSONB ELSE NULL END,
        CASE WHEN TG_OP = 'INSERT' OR TG_OP = 'UPDATE' THEN row_to_json(NEW)::JSONB ELSE NULL END
    );
    RETURN NEW;
END $$ LANGUAGE plpgsql;

DO $$
DECLARE
    table_name TEXT;
BEGIN
    FOREACH table_name IN ARRAY ARRAY[
        'companies', 'users', 'fiscal_years', 'charts_of_accounts', 'general_ledgers_transactions',
        'invoices_receivable', 'invoices_payable', 'partners', 'banks_accounts',
        'banks_statements', 'fixed_assets', 'budgets', 'taxes_registers',
        'inventories_items', 'warehouses', 'inventories_transactions', 'crm_contacts',
        'crm_leads', 'crm_opportunities', 'employees_data', 'payrolls', 'emails_queues',
        'emails_templates', 'emails_logs', 'erp_modules_configs', 'tickets'
    ]
    LOOP
        EXECUTE format('
            CREATE TRIGGER history_trigger_%I
            AFTER INSERT OR UPDATE OR DELETE ON %I
            FOR EACH ROW EXECUTE FUNCTION log_table_history()',
            table_name, table_name
        );
    END LOOP;
END $$;