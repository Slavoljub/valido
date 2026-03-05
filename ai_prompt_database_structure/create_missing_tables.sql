-- ============================================================================
-- MISSING TABLES AND VIEWS FOR VALIDOAI
-- ============================================================================
-- This script creates all missing database objects needed for a complete
-- Serbian business management system
-- ============================================================================

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ============================================================================
-- MISSING TABLES
-- ============================================================================

-- 1. Business Entity Types (if missing)
CREATE TABLE IF NOT EXISTS business_entity_types (
    business_entity_types_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    entity_code VARCHAR(10) NOT NULL UNIQUE,
    entity_name VARCHAR(100) NOT NULL,
    entity_name_sr VARCHAR(100),
    description TEXT,
    tax_requirements JSONB,
    reporting_requirements JSONB,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. User Roles (if missing)
CREATE TABLE IF NOT EXISTS user_roles (
    user_roles_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    role_name VARCHAR(50) NOT NULL UNIQUE,
    role_name_sr VARCHAR(50),
    description TEXT,
    permissions JSONB,
    is_system_role BOOLEAN DEFAULT false,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. User Role Assignments (if missing)
CREATE TABLE IF NOT EXISTS user_role_assignments (
    user_role_assignments_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(users_id) ON DELETE CASCADE,
    role_id UUID NOT NULL REFERENCES user_roles(user_roles_id) ON DELETE CASCADE,
    assigned_by UUID REFERENCES users(users_id),
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    is_active BOOLEAN DEFAULT true,
    UNIQUE(user_id, role_id)
);

-- 4. Customer Types (if missing)
CREATE TABLE IF NOT EXISTS customer_types (
    customer_types_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    type_name VARCHAR(50) NOT NULL UNIQUE,
    type_name_sr VARCHAR(50),
    description TEXT,
    credit_limit DECIMAL(15,2) DEFAULT 0,
    payment_terms VARCHAR(100) DEFAULT 'Net 30',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 5. Invoice Series (if missing)
CREATE TABLE IF NOT EXISTS invoice_series (
    invoice_series_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    series_name VARCHAR(20) NOT NULL UNIQUE,
    series_description TEXT,
    company_id UUID REFERENCES companies(companies_id),
    current_number INTEGER DEFAULT 1,
    number_prefix VARCHAR(10) DEFAULT 'INV',
    number_suffix VARCHAR(10),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 6. Payment Methods (if missing)
CREATE TABLE IF NOT EXISTS payment_methods (
    payment_methods_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    method_name VARCHAR(50) NOT NULL UNIQUE,
    method_name_sr VARCHAR(50),
    description TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 7. Payments (if missing)
CREATE TABLE IF NOT EXISTS payments (
    payments_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    payment_number VARCHAR(50) NOT NULL UNIQUE,
    invoice_id UUID REFERENCES invoices(invoices_id) ON DELETE CASCADE,
    customer_id UUID REFERENCES customers(customers_id),
    company_id UUID REFERENCES companies(companies_id),
    payment_date DATE NOT NULL,
    payment_method_id UUID REFERENCES payment_methods(payment_methods_id),
    amount DECIMAL(15,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'RSD',
    exchange_rate DECIMAL(10,4) DEFAULT 1.0000,
    reference_number VARCHAR(100),
    bank_transaction_id VARCHAR(100),
    status VARCHAR(20) DEFAULT 'completed',
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(users_id),
    updated_by UUID REFERENCES users(users_id)
);

-- 8. Account Types (if missing)
CREATE TABLE IF NOT EXISTS account_types (
    account_types_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    type_code VARCHAR(10) NOT NULL UNIQUE,
    type_name VARCHAR(50) NOT NULL,
    type_name_sr VARCHAR(50),
    description TEXT,
    category VARCHAR(30),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 9. Chart of Accounts (if missing)
CREATE TABLE IF NOT EXISTS chart_of_accounts (
    chart_of_accounts_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    account_code VARCHAR(20) NOT NULL UNIQUE,
    account_name VARCHAR(255) NOT NULL,
    account_name_sr VARCHAR(255),
    account_type_id UUID REFERENCES account_types(account_types_id),
    parent_account_id UUID REFERENCES chart_of_accounts(chart_of_accounts_id),
    company_id UUID REFERENCES companies(companies_id),
    is_active BOOLEAN DEFAULT true,
    is_system_account BOOLEAN DEFAULT false,
    balance DECIMAL(15,2) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 10. General Ledger (if missing)
CREATE TABLE IF NOT EXISTS general_ledger (
    general_ledger_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    transaction_date DATE NOT NULL,
    account_id UUID NOT NULL REFERENCES chart_of_accounts(chart_of_accounts_id),
    company_id UUID NOT NULL REFERENCES companies(companies_id),
    document_type VARCHAR(20) NOT NULL,
    document_id UUID NOT NULL,
    document_number VARCHAR(50),
    description TEXT,
    debit_amount DECIMAL(15,2) DEFAULT 0,
    credit_amount DECIMAL(15,2) DEFAULT 0,
    balance DECIMAL(15,2),
    currency VARCHAR(3) DEFAULT 'RSD',
    exchange_rate DECIMAL(10,4) DEFAULT 1.0000,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(users_id)
);

-- 11. Suppliers (if missing)
CREATE TABLE IF NOT EXISTS suppliers (
    suppliers_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    supplier_name VARCHAR(255) NOT NULL,
    supplier_name_sr VARCHAR(255),
    tax_id VARCHAR(20),
    registration_number VARCHAR(20),
    contact_email VARCHAR(255),
    contact_phone VARCHAR(20),
    address_line1 VARCHAR(255),
    address_line2 VARCHAR(255),
    city VARCHAR(100),
    postal_code VARCHAR(10),
    country VARCHAR(50) DEFAULT 'Serbia',
    payment_terms VARCHAR(100) DEFAULT 'Net 30',
    credit_limit DECIMAL(15,2) DEFAULT 0,
    status VARCHAR(20) DEFAULT 'active',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(users_id),
    updated_by UUID REFERENCES users(users_id)
);

-- 12. AI Insights (if missing)
CREATE TABLE IF NOT EXISTS ai_insights (
    ai_insights_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    insight_type VARCHAR(50) NOT NULL,
    insight_text TEXT NOT NULL,
    confidence_score DECIMAL(3,2),
    related_company_id UUID REFERENCES companies(companies_id),
    related_customer_id UUID REFERENCES customers(customers_id),
    related_invoice_id UUID REFERENCES invoices(invoices_id),
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 13. Chat Sessions (if missing)
CREATE TABLE IF NOT EXISTS chat_sessions (
    chat_sessions_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_name VARCHAR(255),
    user_id UUID REFERENCES users(users_id),
    company_id UUID REFERENCES companies(companies_id),
    session_type VARCHAR(20) DEFAULT 'general',
    status VARCHAR(20) DEFAULT 'active',
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 14. System Settings (if missing)
CREATE TABLE IF NOT EXISTS system_settings (
    system_settings_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    setting_key VARCHAR(100) NOT NULL UNIQUE,
    setting_value TEXT,
    setting_type VARCHAR(20) DEFAULT 'string',
    category VARCHAR(50),
    description TEXT,
    is_system BOOLEAN DEFAULT false,
    is_encrypted BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_by UUID REFERENCES users(users_id)
);

-- 15. Performance Metrics (if missing)
CREATE TABLE IF NOT EXISTS performance_metrics (
    performance_metrics_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    metric_name VARCHAR(100) NOT NULL,
    metric_value DECIMAL(15,4) NOT NULL,
    unit VARCHAR(20),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    source VARCHAR(50) DEFAULT 'system',
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- MISSING VIEWS
-- ============================================================================

-- 1. Company Financial Summary View
CREATE OR REPLACE VIEW company_financial_summary AS
SELECT
    c.companies_id,
    c.company_name,
    c.tax_id,
    COUNT(DISTINCT i.invoices_id) as total_invoices,
    COUNT(DISTINCT i.customer_id) as total_customers,
    SUM(i.total_amount) as total_revenue,
    AVG(i.total_amount) as avg_invoice_value,
    COUNT(CASE WHEN i.payment_status = 'paid' THEN 1 END) as paid_invoices,
    COUNT(CASE WHEN i.payment_status = 'pending' THEN 1 END) as pending_invoices,
    COUNT(CASE WHEN i.payment_status = 'overdue' THEN 1 END) as overdue_invoices,
    MAX(i.invoice_date) as last_invoice_date,
    c.status,
    c.created_at
FROM companies c
LEFT JOIN invoices i ON c.companies_id = i.company_id AND i.status = 'issued'
GROUP BY c.companies_id, c.company_name, c.tax_id, c.status, c.created_at;

-- 2. Customer Purchase History View
CREATE OR REPLACE VIEW customer_purchase_history AS
SELECT
    cu.customers_id,
    cu.company_name as customer_name,
    cu.pib,
    COUNT(i.invoices_id) as total_invoices,
    SUM(i.total_amount) as total_purchases,
    AVG(i.total_amount) as avg_purchase_value,
    MAX(i.invoice_date) as last_purchase_date,
    COUNT(CASE WHEN i.payment_status = 'paid' THEN 1 END) as paid_invoices,
    COUNT(CASE WHEN i.payment_status = 'pending' THEN 1 END) as pending_invoices,
    COUNT(CASE WHEN i.payment_status = 'overdue' THEN 1 END) as overdue_invoices,
    cu.credit_limit,
    cu.status
FROM customers cu
LEFT JOIN invoices i ON cu.customers_id = i.customer_id AND i.status = 'issued'
GROUP BY cu.customers_id, cu.company_name, cu.pib, cu.credit_limit, cu.status;

-- 3. Product Sales Summary View
CREATE OR REPLACE VIEW product_sales_summary AS
SELECT
    p.products_id,
    p.product_name,
    p.product_code,
    pc.name as category_name,
    COUNT(ii.invoice_items_id) as total_sold,
    SUM(ii.quantity) as total_quantity,
    SUM(ii.line_total) as total_revenue,
    AVG(ii.unit_price) as avg_selling_price,
    COUNT(DISTINCT i.invoices_id) as invoices_count,
    p.unit_price as current_price,
    p.stock_quantity,
    p.is_active
FROM products p
LEFT JOIN product_categories pc ON p.category_id = pc.product_categories_id
LEFT JOIN invoice_items ii ON p.products_id = ii.product_id
LEFT JOIN invoices i ON ii.invoice_id = i.invoices_id AND i.status = 'issued'
GROUP BY p.products_id, p.product_name, p.product_code, pc.name, p.unit_price, p.stock_quantity, p.is_active;

-- 4. Monthly Revenue Report View
CREATE OR REPLACE VIEW monthly_revenue_report AS
SELECT
    DATE_TRUNC('month', i.invoice_date) as month,
    c.companies_id,
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
WHERE i.status = 'issued' AND i.invoice_date >= DATE_TRUNC('month', CURRENT_DATE - INTERVAL '12 months')
GROUP BY DATE_TRUNC('month', i.invoice_date), c.companies_id, c.company_name
ORDER BY month DESC, total_revenue DESC;

-- 5. Customer Aging Report View
CREATE OR REPLACE VIEW customer_aging_report AS
SELECT
    cu.customers_id,
    cu.company_name as customer_name,
    cu.pib,
    SUM(CASE WHEN i.due_date < CURRENT_DATE AND i.payment_status != 'paid' THEN i.total_amount ELSE 0 END) as overdue_amount,
    SUM(CASE WHEN i.due_date >= CURRENT_DATE AND i.due_date <= CURRENT_DATE + INTERVAL '30 days' AND i.payment_status != 'paid' THEN i.total_amount ELSE 0 END) as current_amount,
    SUM(CASE WHEN i.due_date > CURRENT_DATE + INTERVAL '30 days' AND i.due_date <= CURRENT_DATE + INTERVAL '60 days' AND i.payment_status != 'paid' THEN i.total_amount ELSE 0 END) as days_30_amount,
    SUM(CASE WHEN i.due_date > CURRENT_DATE + INTERVAL '60 days' AND i.payment_status != 'paid' THEN i.total_amount ELSE 0 END) as days_60_plus_amount,
    COUNT(CASE WHEN i.due_date < CURRENT_DATE AND i.payment_status != 'paid' THEN 1 END) as overdue_invoices,
    cu.credit_limit,
    cu.payment_terms
FROM customers cu
LEFT JOIN invoices i ON cu.customers_id = i.customer_id AND i.status = 'issued'
WHERE cu.status = 'active'
GROUP BY cu.customers_id, cu.company_name, cu.pib, cu.credit_limit, cu.payment_terms
HAVING SUM(i.total_amount) > 0;

-- 6. PDV Report View (Serbian VAT)
CREATE OR REPLACE VIEW pdv_report AS
SELECT
    DATE_TRUNC('month', i.invoice_date) as month,
    c.companies_id,
    c.company_name,
    SUM(i.subtotal) as taxable_base,
    SUM(i.pdv_amount) as pdv_amount,
    SUM(i.total_amount) as total_with_pdv,
    i.pdv_rate,
    COUNT(i.invoices_id) as invoice_count,
    AVG(i.pdv_rate) as avg_pdv_rate
FROM invoices i
JOIN companies c ON i.company_id = c.companies_id
WHERE i.status = 'issued' AND i.pdv_rate > 0
GROUP BY DATE_TRUNC('month', i.invoice_date), c.companies_id, c.company_name, i.pdv_rate
ORDER BY month DESC, total_with_pdv DESC;

-- ============================================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================================

-- Indexes for frequently queried columns
CREATE INDEX IF NOT EXISTS idx_invoices_date ON invoices(invoice_date);
CREATE INDEX IF NOT EXISTS idx_invoices_status ON invoices(status);
CREATE INDEX IF NOT EXISTS idx_invoices_payment_status ON invoices(payment_status);
CREATE INDEX IF NOT EXISTS idx_invoice_items_invoice_id ON invoice_items(invoice_id);
CREATE INDEX IF NOT EXISTS idx_invoice_items_product_id ON invoice_items(product_id);
CREATE INDEX IF NOT EXISTS idx_customers_status ON customers(status);
CREATE INDEX IF NOT EXISTS idx_products_active ON products(is_active) WHERE is_active = true;
CREATE INDEX IF NOT EXISTS idx_general_ledger_date ON general_ledger(transaction_date);
CREATE INDEX IF NOT EXISTS idx_general_ledger_account ON general_ledger(account_id);
CREATE INDEX IF NOT EXISTS idx_payments_date ON payments(payment_date);
CREATE INDEX IF NOT EXISTS idx_payments_status ON payments(status);

-- ============================================================================
-- TRIGGERS FOR DATA INTEGRITY
-- ============================================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Add triggers for updated_at columns
CREATE TRIGGER update_business_entity_types_updated_at BEFORE UPDATE ON business_entity_types FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_user_roles_updated_at BEFORE UPDATE ON user_roles FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_customer_types_updated_at BEFORE UPDATE ON customer_types FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_invoice_series_updated_at BEFORE UPDATE ON invoice_series FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_payment_methods_updated_at BEFORE UPDATE ON payment_methods FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_payments_updated_at BEFORE UPDATE ON payments FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_account_types_updated_at BEFORE UPDATE ON account_types FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_chart_of_accounts_updated_at BEFORE UPDATE ON chart_of_accounts FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_suppliers_updated_at BEFORE UPDATE ON suppliers FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_ai_insights_updated_at BEFORE UPDATE ON ai_insights FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_chat_sessions_updated_at BEFORE UPDATE ON chat_sessions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_system_settings_updated_at BEFORE UPDATE ON system_settings FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- INSERT DEFAULT DATA
-- ============================================================================

-- Insert default user roles
INSERT INTO user_roles (role_name, role_name_sr, description, permissions, is_system_role)
VALUES
    ('admin', 'Administrator', 'System administrator with full access', '{"all_permissions": true, "user_management": true, "system_config": true}'::jsonb, true),
    ('owner', 'Vlasnik', 'Company owner with full business access', '{"company_management": true, "financial_management": true, "user_management": true}'::jsonb, true),
    ('accountant', 'Računovođa', 'Accounting and financial management', '{"financial_read": true, "financial_write": true, "reports_read": true}'::jsonb, true),
    ('manager', 'Menadžer', 'Department or business unit manager', '{"department_read": true, "department_write": true, "reports_read": true}'::jsonb, true),
    ('sales', 'Prodaja', 'Sales representative', '{"customer_read": true, "customer_write": true, "invoice_create": true, "product_read": true}'::jsonb, true),
    ('user', 'Korisnik', 'Standard user with limited access', '{"read_only": true}'::jsonb, true)
ON CONFLICT (role_name) DO NOTHING;

-- Insert default customer types
INSERT INTO customer_types (type_name, type_name_sr, description, credit_limit, payment_terms)
VALUES
    ('Individual', 'Pojedinac', 'Individual customer', 50000.00, 'Net 15'),
    ('Small Business', 'Malo Preduzeće', 'Business with < 10 employees', 200000.00, 'Net 30'),
    ('Medium Business', 'Srednje Preduzeće', 'Business with 10-50 employees', 500000.00, 'Net 30'),
    ('Large Business', 'Veliko Preduzeće', 'Business with > 50 employees', 1000000.00, 'Net 45'),
    ('Government', 'Državni Organ', 'Government organization', 2000000.00, 'Net 60')
ON CONFLICT (type_name) DO NOTHING;

-- Insert default payment methods
INSERT INTO payment_methods (method_name, method_name_sr, description)
VALUES
    ('Bank Transfer', 'Bankovni Transfer', 'Wire transfer via bank'),
    ('Check', 'Ček', 'Payment by check'),
    ('Cash', 'Gotovina', 'Cash payment'),
    ('Card', 'Kartica', 'Credit/debit card payment'),
    ('Online Payment', 'Online Plaćanje', 'Online payment gateway')
ON CONFLICT (method_name) DO NOTHING;

-- Insert default account types
INSERT INTO account_types (type_code, type_name, type_name_sr, description, category)
VALUES
    ('1000', 'Assets', 'Imovina', 'All asset accounts', 'asset'),
    ('2000', 'Liabilities', 'Obaveze', 'All liability accounts', 'liability'),
    ('3000', 'Equity', 'Kapital', 'All equity accounts', 'equity'),
    ('4000', 'Income', 'Prihodi', 'All income accounts', 'income'),
    ('5000', 'Expenses', 'Rashodi', 'All expense accounts', 'expense')
ON CONFLICT (type_code) DO NOTHING;

-- Insert default business entity types
INSERT INTO business_entity_types (entity_code, entity_name, entity_name_sr, description, tax_requirements, reporting_requirements)
VALUES
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

-- Insert default system settings
INSERT INTO system_settings (setting_key, setting_value, category, description)
VALUES
    ('company_name', 'ValidoAI Solutions DOO', 'company', 'Default company name'),
    ('company_pib', '123456789', 'company', 'Default company PIB'),
    ('default_currency', 'RSD', 'finance', 'Default currency for transactions'),
    ('default_language', 'sr-RS', 'system', 'Default system language'),
    ('pdv_rate', '20.0', 'tax', 'Default PDV rate'),
    ('invoice_number_format', 'INV-{number}-{year}', 'invoicing', 'Invoice number format'),
    ('email_notifications', 'true', 'notifications', 'Enable email notifications'),
    ('auto_backup', 'true', 'system', 'Enable automatic backups'),
    ('max_file_size', '10MB', 'uploads', 'Maximum file upload size'),
    ('timezone', 'Europe/Belgrade', 'system', 'System timezone')
ON CONFLICT (setting_key) DO NOTHING;

-- ============================================================================
-- GRANT PERMISSIONS
-- ============================================================================

-- Grant necessary permissions (adjust as needed)
-- GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO validoai_user;
-- GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO validoai_user;
