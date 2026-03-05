-- ============================================================================
-- POSTGRES AI VALIDO ONLINE - COMPREHENSIVE SAMPLE DATA
-- ============================================================================
-- Version: 3.0 - Enterprise Sample Data
-- Multi-company, Multi-currency, Serbian compliance
-- AI insights, financial reports, comprehensive relationships
-- Performance optimized with realistic data distribution

-- Insert reference data first
INSERT INTO countries (iso_code, iso_code_3, iso_numeric, name, native_name, capital, region, subregion, latitude, longitude, area_km2, population, currency_code, currency_name, currency_symbol, phone_code, flag_emoji, timezone_data, languages) VALUES
('RS', 'SRB', '688', 'Serbia', 'Србија', 'Belgrade', 'Europe', 'Southern Europe', 44.0165, 21.0059, 88361, 6871547, 'RSD', 'Serbian Dinar', 'дин.', '+381', '🇷🇸', '["Europe/Belgrade"]', '["sr", "hu", "bs", "ro"]'),
('US', 'USA', '840', 'United States', 'United States', 'Washington D.C.', 'Americas', 'North America', 37.0902, -95.7129, 9833517, 331002651, 'USD', 'US Dollar', '$', '+1', '🇺🇸', '["America/New_York", "America/Chicago", "America/Denver", "America/Los_Angeles"]', '["en"]'),
('DE', 'DEU', '276', 'Germany', 'Deutschland', 'Berlin', 'Europe', 'Western Europe', 51.1657, 10.4515, 357114, 83783942, 'EUR', 'Euro', '€', '+49', '🇩🇪', '["Europe/Berlin"]', '["de"]'),
('GB', 'GBR', '826', 'United Kingdom', 'United Kingdom', 'London', 'Europe', 'Northern Europe', 55.3781, -3.4360, 242495, 67886011, 'GBP', 'British Pound', '£', '+44', '🇬🇧', '["Europe/London"]', '["en"]'),
('FR', 'FRA', '250', 'France', 'France', 'Paris', 'Europe', 'Western Europe', 46.2276, 2.2137, 551695, 65273511, 'EUR', 'Euro', '€', '+33', '🇫🇷', '["Europe/Paris"]', '["fr"]');

-- Business configuration (unified table for types)
INSERT INTO business_config (config_type, type_code, type_name, category, description, is_system_type, tax_rate, currency_symbol, affects_cash, requires_approval) VALUES
-- Account Types
('account_type', 'ASSET', 'Assets', 'Asset', 'Resources owned by the company', true, null, null, null, null),
('account_type', 'LIAB', 'Liabilities', 'Liability', 'Debts and obligations', true, null, null, null, null),
('account_type', 'EQUITY', 'Equity', 'Equity', 'Owner''s equity in the company', true, null, null, null, null),
('account_type', 'REV', 'Revenue', 'Revenue', 'Income from operations', true, null, null, null, null),
('account_type', 'EXP', 'Expenses', 'Expense', 'Costs of operations', true, null, null, null, null),

-- Transaction Types
('transaction_type', 'SALE', 'Sales Revenue', 'Revenue', 'Sale of goods or services', true, null, null, true, false),
('transaction_type', 'PURCH', 'Purchase', 'Purchase', 'Purchase of goods or services', true, null, null, true, false),
('transaction_type', 'PAY', 'Payment', 'Payment', 'Payment transactions', true, null, null, true, true),
('transaction_type', 'RCPT', 'Receipt', 'Receipt', 'Receipt of payments', true, null, null, true, false),
('transaction_type', 'ADJ', 'Adjustment', 'Adjustment', 'Accounting adjustments', true, null, null, false, true),
('transaction_type', 'TRANS', 'Transfer', 'Transfer', 'Internal transfers', true, null, null, false, true),

-- Tax Types (Serbian compliance)
('tax_type', 'PDV', 'Value Added Tax (PDV)', 'VAT', 'Standard Serbian VAT rate', true, 20.00, null, null, null),
('tax_type', 'CORP', 'Corporate Income Tax', 'Corporate', 'Serbian corporate tax rate', true, 15.00, null, null, null),
('tax_type', 'PPO', 'Withholding Tax', 'Personal', 'Personal income withholding tax', true, 10.00, null, null, null),
('tax_type', 'CONTRIB', 'Social Contributions', 'Social', 'Combined social contributions', true, 37.80, null, null, null),

-- Currencies
('currency', 'RSD', 'Serbian Dinar', 'Local', 'Serbian national currency', true, null, 'дин.', null, null),
('currency', 'USD', 'US Dollar', 'International', 'United States dollar', true, null, '$', null, null),
('currency', 'EUR', 'Euro', 'International', 'European Union euro', true, null, '€', null, null),
('currency', 'GBP', 'British Pound', 'International', 'United Kingdom pound', true, null, '£', null, null);

-- Business forms (Serbian compliance)
INSERT INTO business_forms (form_code, form_name, description, country_specific) VALUES
('DOO', 'Društvo sa ograničenom odgovornošću', 'Limited Liability Company - Most common Serbian business form', 'RS'),
('AD', 'Akcionarsko društvo', 'Joint Stock Company - For larger Serbian enterprises', 'RS'),
('PRE', 'Preduzetnik', 'Individual Entrepreneur - For small Serbian businesses', 'RS'),
('OR', 'Odgovorno lice', 'Responsible Person - For foreign entities operating in Serbia', 'RS');

-- Business areas/industries
INSERT INTO business_areas (area_code, area_name, description) VALUES
('TECH', 'Technology', 'Software development, IT services, and digital solutions'),
('FIN', 'Financial Services', 'Banking, insurance, consulting, and financial services'),
('MFG', 'Manufacturing', 'Production and manufacturing of goods'),
('SVC', 'Professional Services', 'Legal, accounting, consulting, and business services'),
('RET', 'Retail & Trade', 'Retail sales and wholesale distribution'),
('HSP', 'Healthcare & Pharma', 'Healthcare services and pharmaceutical products'),
('EDU', 'Education', 'Educational services and training'),
('FNB', 'Food & Beverage', 'Food production and hospitality services');

-- Partner types
INSERT INTO partner_types (type_code, type_name, category) VALUES
('CUST', 'Customer', 'Customer'),
('SUPP', 'Supplier', 'Supplier'),
('PART', 'Partner', 'Partner'),
('VEND', 'Vendor', 'Vendor'),
('CONS', 'Consultant', 'Consultant'),
('CONT', 'Contractor', 'Contractor');

-- ============================================================================
-- ROLES AND PERMISSIONS
-- ============================================================================

-- System roles with detailed permissions
INSERT INTO roles (role_name, display_name, description, role_level, is_system_role, permissions) VALUES
('superadmin', 'Super Administrator', 'Full system access with all privileges', 10, true, '{
    "system": {"full": true},
    "companies": {"all": true},
    "users": {"all": true},
    "financial": {"all": true},
    "reports": {"all": true},
    "settings": {"all": true}
}'),
('admin', 'Administrator', 'Full CRUD with read-only company switching', 8, true, '{
    "companies": {"read": true, "write": true, "switch": true},
    "users": {"read": true, "write": true, "invite": true},
    "financial": {"read": true, "write": true, "approve": true},
    "reports": {"read": true, "export": true},
    "settings": {"read": true, "write": false}
}'),
('accountant', 'Accountant', 'Financial module access with approval limits', 6, true, '{
    "financial": {"read": true, "write": true, "approve": true, "limit": 50000},
    "invoices": {"read": true, "write": true, "approve": true},
    "reports": {"read": true, "export": true},
    "tax": {"read": true, "file": true}
}'),
('manager', 'Manager', 'CRM and inventory management with team oversight', 5, true, '{
    "team": {"read": true, "write": true, "approve": true},
    "inventory": {"read": true, "write": true},
    "sales": {"read": true, "write": true, "approve": false},
    "reports": {"read": true, "export": false}
}'),
('hr', 'HR Manager', 'Limited HR module access with employee data', 4, true, '{
    "employees": {"read": true, "write": true},
    "payroll": {"read": true, "write": false},
    "reports": {"read": true, "hr": true}
}'),
('employee', 'Employee', 'Basic access to personal data and assigned tasks', 2, true, '{
    "profile": {"read": true, "write": true},
    "tasks": {"read": true, "write": true},
    "documents": {"read": true}
}'),
('demo', 'Demo User', 'View/test without saving capabilities', 1, true, '{
    "view": {"read": true},
    "demo": {"test": true, "save": false}
}');

-- ============================================================================
-- SAMPLE COMPANIES WITH MULTI-COUNTRY SUPPORT
-- ============================================================================

INSERT INTO companies (company_name, legal_name, tax_id, registration_number, address_line1, city, postal_code, countries_id, country, phone, email, website, business_forms_id, business_areas_id, company_size, founded_date, fiscal_year_start_month, default_currency, timezone, language, is_active, is_demo_company, subscription_tier, logo_url, description) VALUES
((SELECT companies_id FROM companies WHERE company_name = 'ValidoAI Technologies' LIMIT 1),
 'ValidoAI Technologies',
 'ValidoAI Technologies d.o.o.',
 '123456789',
 'REG001',
 'Bulevar Mihajla Pupina 10',
 'Belgrade',
 '11000',
 (SELECT countries_id FROM countries WHERE iso_code = 'RS'),
 'Serbia',
 '+381113456789',
 'info@validoai.com',
 'https://validoai.com',
 (SELECT business_forms_id FROM business_forms WHERE form_code = 'DOO'),
 (SELECT business_areas_id FROM business_areas WHERE area_code = 'TECH'),
 '11-50 employees',
 '2020-01-15',
 1,
 'RSD',
 'Europe/Belgrade',
 'sr',
 true,
 false,
 'enterprise',
 '/static/img/logos/validoai.svg',
 'AI-powered financial management platform specializing in Serbian business compliance'),

((SELECT companies_id FROM companies WHERE company_name = 'TechCorp Solutions' LIMIT 1),
 'TechCorp Solutions',
 'TechCorp Solutions Serbia',
 '987654321',
 'REG002',
 'Knez Mihailova 25',
 'Novi Sad',
 '21000',
 (SELECT countries_id FROM countries WHERE iso_code = 'RS'),
 'Serbia',
 '+38121654321',
 'contact@techcorp.rs',
 'https://techcorp.rs',
 (SELECT business_forms_id FROM business_forms WHERE form_code = 'DOO'),
 (SELECT business_areas_id FROM business_areas WHERE area_code = 'TECH'),
 '51-200 employees',
 '2018-06-01',
 1,
 'RSD',
 'Europe/Belgrade',
 'sr',
 true,
 false,
 'professional',
 '/static/img/logos/techcorp.svg',
 'Comprehensive IT solutions and digital transformation services'),

((SELECT companies_id FROM companies WHERE company_name = 'FinanceHub Ltd' LIMIT 1),
 'FinanceHub Consulting Ltd',
 'FinanceHub Consulting Ltd',
 '456789123',
 'REG003',
 'Terazije 12',
 'Belgrade',
 '11000',
 (SELECT countries_id FROM countries WHERE iso_code = 'RS'),
 'Serbia',
 '+38111234567',
 'hello@financehub.rs',
 'https://financehub.rs',
 (SELECT business_forms_id FROM business_forms WHERE form_code = 'DOO'),
 (SELECT business_areas_id FROM business_areas WHERE area_code = 'FIN'),
 '11-50 employees',
 '2021-03-10',
 1,
 'RSD',
 'Europe/Belgrade',
 'sr',
 true,
 false,
 'starter',
 '/static/img/logos/financehub.svg',
 'Financial consulting and advisory services for SMEs'),

((SELECT companies_id FROM companies WHERE company_name = 'Global Finance GmbH' LIMIT 1),
 'Global Finance GmbH',
 'Global Finance GmbH',
 'DE123456789',
 'HRB123456',
 'Friedrichstraße 123',
 'Berlin',
 '10117',
 (SELECT countries_id FROM countries WHERE iso_code = 'DE'),
 'Germany',
 '+49301234567',
 'contact@globalfinance.de',
 'https://globalfinance.de',
 (SELECT business_forms_id FROM business_forms WHERE form_code = 'OR'),
 (SELECT business_areas_id FROM business_areas WHERE area_code = 'FIN'),
 '201-500 employees',
 '2015-09-01',
 1,
 'EUR',
 'Europe/Berlin',
 'de',
 true,
 false,
 'enterprise',
 '/static/img/logos/globalfinance.svg',
 'International financial services with cross-border capabilities');

-- ============================================================================
-- USERS WITH ENHANCED SECURITY
-- ============================================================================

-- Create system admin user with enhanced security
INSERT INTO users (username, email, password_hash, first_name, last_name, phone, is_verified, is_admin, is_system_user, status, preferred_language, timezone, two_factor_enabled) VALUES
('system.admin', 'admin@validoai.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LeCtj1rE1rTjY1F2', 'System', 'Administrator', '+38160123456', true, true, true, 'active', 'en', 'Europe/Belgrade', true);

-- Regular users
INSERT INTO users (username, email, password_hash, first_name, last_name, phone, is_verified, status, preferred_language, timezone) VALUES
('john.doe', 'john.doe@validoai.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LeCtj1rE1rTjY1F2', 'John', 'Doe', '+38160123457', true, 'active', 'en', 'Europe/Belgrade'),
('jane.smith', 'jane.smith@techcorp.rs', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LeCtj1rE1rTjY1F2', 'Jane', 'Smith', '+38160234567', true, 'active', 'sr', 'Europe/Belgrade'),
('mark.johnson', 'mark.johnson@financehub.rs', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LeCtj1rE1rTjY1F2', 'Mark', 'Johnson', '+38160345678', true, 'active', 'en', 'Europe/Belgrade'),
('anna.schmidt', 'anna.schmidt@globalfinance.de', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LeCtj1rE1rTjY1F2', 'Anna', 'Schmidt', '+49301234567', true, 'active', 'de', 'Europe/Berlin'),
('mike.wilson', 'mike.wilson@techstart.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LeCtj1rE1rTjY1F2', 'Mike', 'Wilson', '+16501234567', true, 'active', 'en', 'America/New_York');

-- Assign roles to users
INSERT INTO user_roles (users_id, roles_id, assigned_by) VALUES
((SELECT users_id FROM users WHERE username = 'system.admin'), (SELECT roles_id FROM roles WHERE role_name = 'superadmin'), (SELECT users_id FROM users WHERE username = 'system.admin')),
((SELECT users_id FROM users WHERE username = 'john.doe'), (SELECT roles_id FROM roles WHERE role_name = 'admin'), (SELECT users_id FROM users WHERE username = 'system.admin')),
((SELECT users_id FROM users WHERE username = 'jane.smith'), (SELECT roles_id FROM roles WHERE role_name = 'accountant'), (SELECT users_id FROM users WHERE username = 'system.admin')),
((SELECT users_id FROM users WHERE username = 'mark.johnson'), (SELECT roles_id FROM roles WHERE role_name = 'manager'), (SELECT users_id FROM users WHERE username = 'system.admin')),
((SELECT users_id FROM users WHERE username = 'anna.schmidt'), (SELECT roles_id FROM roles WHERE role_name = 'accountant'), (SELECT users_id FROM users WHERE username = 'system.admin')),
((SELECT users_id FROM users WHERE username = 'mike.wilson'), (SELECT roles_id FROM roles WHERE role_name = 'employee'), (SELECT users_id FROM users WHERE username = 'system.admin'));

-- ============================================================================
-- USER-COMPANY ACCESS (MULTI-COMPANY SUPPORT)
-- ============================================================================

INSERT INTO user_company_access (users_id, companies_id, access_level, role_type, department, job_title, employee_id, hire_date, can_switch_to_company, can_manage_company, can_invite_users, can_access_financial_data, can_approve_transactions, status) VALUES
-- System admin has access to all companies
((SELECT users_id FROM users WHERE username = 'system.admin'),
 (SELECT companies_id FROM companies WHERE tax_id = '123456789'),
 'owner', 'employee', 'Administration', 'System Administrator', 'EMP001', '2020-01-15',
 true, true, true, true, true, 'active'),

((SELECT users_id FROM users WHERE username = 'system.admin'),
 (SELECT companies_id FROM companies WHERE tax_id = '987654321'),
 'admin', 'employee', 'Administration', 'System Administrator', 'EMP002', '2020-01-15',
 true, true, true, true, true, 'active'),

((SELECT users_id FROM users WHERE username = 'system.admin'),
 (SELECT companies_id FROM companies WHERE tax_id = '456789123'),
 'admin', 'employee', 'Administration', 'System Administrator', 'EMP003', '2020-01-15',
 true, true, true, true, true, 'active'),

((SELECT users_id FROM users WHERE username = 'system.admin'),
 (SELECT companies_id FROM companies WHERE tax_id = 'DE123456789'),
 'admin', 'employee', 'Administration', 'System Administrator', 'EMP004', '2020-01-15',
 true, true, true, true, true, 'active'),

-- John Doe - Multi-company access
((SELECT users_id FROM users WHERE username = 'john.doe'),
 (SELECT companies_id FROM companies WHERE tax_id = '123456789'),
 'admin', 'employee', 'IT', 'Senior Developer', 'EMP101', '2020-02-01',
 true, true, true, true, true, 'active'),

((SELECT users_id FROM users WHERE username = 'john.doe'),
 (SELECT companies_id FROM companies WHERE tax_id = '987654321'),
 'employee', 'contractor', 'Development', 'Consultant', 'CONS001', '2023-01-01',
 true, false, false, false, false, 'active'),

((SELECT users_id FROM users WHERE username = 'john.doe'),
 (SELECT companies_id FROM companies WHERE tax_id = 'DE123456789'),
 'external', 'consultant', 'Advisory', 'Technical Consultant', 'EXT001', '2023-06-01',
 true, false, false, false, false, 'active'),

-- Jane Smith - TechCorp
((SELECT users_id FROM users WHERE username = 'jane.smith'),
 (SELECT companies_id FROM companies WHERE tax_id = '987654321'),
 'admin', 'employee', 'Finance', 'Chief Financial Officer', 'EMP201', '2018-07-01',
 false, true, true, true, true, 'active'),

-- Mark Johnson - FinanceHub
((SELECT users_id FROM users WHERE username = 'mark.johnson'),
 (SELECT companies_id FROM companies WHERE tax_id = '456789123'),
 'owner', 'employee', 'Management', 'CEO', 'EMP301', '2021-03-15',
 false, true, true, true, true, 'active'),

-- Anna Schmidt - Global Finance
((SELECT users_id FROM users WHERE username = 'anna.schmidt'),
 (SELECT companies_id FROM companies WHERE tax_id = 'DE123456789'),
 'admin', 'employee', 'Finance', 'Finance Director', 'EMP401', '2015-10-01',
 false, true, true, true, true, 'active'),

-- Mike Wilson - TechCorp (additional access)
((SELECT users_id FROM users WHERE username = 'mike.wilson'),
 (SELECT companies_id FROM companies WHERE tax_id = '987654321'),
 'employee', 'employee', 'Sales', 'Business Development Manager', 'EMP501', '2023-02-01',
 false, false, false, true, false, 'active');

-- ============================================================================
-- FISCAL YEARS SETUP
-- ============================================================================

INSERT INTO fiscal_years (companies_id, year, start_date, end_date, status, is_current_year) VALUES
-- ValidoAI Technologies
((SELECT companies_id FROM companies WHERE tax_id = '123456789'), 2023, '2023-01-01', '2023-12-31', 'closed', false),
((SELECT companies_id FROM companies WHERE tax_id = '123456789'), 2024, '2024-01-01', '2024-12-31', 'closed', false),
((SELECT companies_id FROM companies WHERE tax_id = '123456789'), 2025, '2025-01-01', '2025-12-31', 'open', true),

-- TechCorp Solutions
((SELECT companies_id FROM companies WHERE tax_id = '987654321'), 2023, '2023-01-01', '2023-12-31', 'closed', false),
((SELECT companies_id FROM companies WHERE tax_id = '987654321'), 2024, '2024-01-01', '2024-12-31', 'closed', false),
((SELECT companies_id FROM companies WHERE tax_id = '987654321'), 2025, '2025-01-01', '2025-12-31', 'open', true),

-- FinanceHub Ltd
((SELECT companies_id FROM companies WHERE tax_id = '456789123'), 2024, '2024-01-01', '2024-12-31', 'closed', false),
((SELECT companies_id FROM companies WHERE tax_id = '456789123'), 2025, '2025-01-01', '2025-12-31', 'open', true),

-- Global Finance GmbH (German fiscal year)
((SELECT companies_id FROM companies WHERE tax_id = 'DE123456789'), 2023, '2023-01-01', '2023-12-31', 'closed', false),
((SELECT companies_id FROM companies WHERE tax_id = 'DE123456789'), 2024, '2024-01-01', '2024-12-31', 'closed', false),
((SELECT companies_id FROM companies WHERE tax_id = 'DE123456789'), 2025, '2025-01-01', '2025-12-31', 'open', true);

-- ============================================================================
-- CHART OF ACCOUNTS (SERBIAN COMPLIANCE)
-- ============================================================================

-- ValidoAI Technologies Chart of Accounts
INSERT INTO chart_of_accounts (companies_id, account_number, account_name, account_type, parent_account_id, account_level, is_system_account, opening_balance, tax_rate, description) VALUES
((SELECT companies_id FROM companies WHERE tax_id = '123456789'), '1000', 'ASSETS', 'Asset', null, 1, true, 0, 0, 'Main Assets Account'),
((SELECT companies_id FROM companies WHERE tax_id = '123456789'), '1001', 'Cash and Cash Equivalents', 'Asset', (SELECT chart_of_accounts_id FROM chart_of_accounts WHERE account_number = '1000' AND companies_id = (SELECT companies_id FROM companies WHERE tax_id = '123456789')), 2, true, 2500000, 0, 'Cash in bank accounts and petty cash'),
((SELECT companies_id FROM companies WHERE tax_id = '123456789'), '1101', 'Accounts Receivable', 'Asset', (SELECT chart_of_accounts_id FROM chart_of_accounts WHERE account_number = '1000' AND companies_id = (SELECT companies_id FROM companies WHERE tax_id = '123456789')), 2, true, 750000, 0, 'Money owed by customers'),
((SELECT companies_id FROM companies WHERE tax_id = '123456789'), '1201', 'Inventory', 'Asset', (SELECT chart_of_accounts_id FROM chart_of_accounts WHERE account_number = '1000' AND companies_id = (SELECT companies_id FROM companies WHERE tax_id = '123456789')), 2, true, 500000, 0, 'Goods available for sale'),
((SELECT companies_id FROM companies WHERE tax_id = '123456789'), '2000', 'LIABILITIES', 'Liability', null, 1, true, 0, 0, 'Main Liabilities Account'),
((SELECT companies_id FROM companies WHERE tax_id = '123456789'), '2001', 'Accounts Payable', 'Liability', (SELECT chart_of_accounts_id FROM chart_of_accounts WHERE account_number = '2000' AND companies_id = (SELECT companies_id FROM companies WHERE tax_id = '123456789')), 2, true, 350000, 0, 'Money owed to suppliers'),
((SELECT companies_id FROM companies WHERE tax_id = '123456789'), '3000', 'EQUITY', 'Equity', null, 1, true, 0, 0, 'Main Equity Account'),
((SELECT companies_id FROM companies WHERE tax_id = '123456789'), '3001', 'Owner''s Equity', 'Equity', (SELECT chart_of_accounts_id FROM chart_of_accounts WHERE account_number = '3000' AND companies_id = (SELECT companies_id FROM companies WHERE tax_id = '123456789')), 2, true, 3500000, 0, 'Owner''s investment in the company'),
((SELECT companies_id FROM companies WHERE tax_id = '123456789'), '4000', 'REVENUE', 'Revenue', null, 1, true, 0, 20, 'Main Revenue Account'),
((SELECT companies_id FROM companies WHERE tax_id = '123456789'), '4001', 'Sales Revenue', 'Revenue', (SELECT chart_of_accounts_id FROM chart_of_accounts WHERE account_number = '4000' AND companies_id = (SELECT companies_id FROM companies WHERE tax_id = '123456789')), 2, true, 0, 20, 'Revenue from sales'),
((SELECT companies_id FROM companies WHERE tax_id = '123456789'), '5000', 'EXPENSES', 'Expense', null, 1, true, 0, 20, 'Main Expenses Account'),
((SELECT companies_id FROM companies WHERE tax_id = '123456789'), '5001', 'Cost of Goods Sold', 'Expense', (SELECT chart_of_accounts_id FROM chart_of_accounts WHERE account_number = '5000' AND companies_id = (SELECT companies_id FROM companies WHERE tax_id = '123456789')), 2, true, 0, 20, 'Direct cost of producing goods'),
((SELECT companies_id FROM companies WHERE tax_id = '123456789'), '5002', 'Operating Expenses', 'Expense', (SELECT chart_of_accounts_id FROM chart_of_accounts WHERE account_number = '5000' AND companies_id = (SELECT companies_id FROM companies WHERE tax_id = '123456789')), 2, true, 0, 20, 'Day-to-day business expenses');

-- ============================================================================
-- SAMPLE TRANSACTIONS FOR DEMONSTRATION
-- ============================================================================

-- Sample general ledger transactions for ValidoAI Technologies
INSERT INTO general_ledger (companies_id, fiscal_years_id, transaction_date, document_number, document_type, reference_number, description, source_module, currency_code, total_amount, status) VALUES
((SELECT companies_id FROM companies WHERE tax_id = '123456789'),
 (SELECT fiscal_years_id FROM fiscal_years WHERE companies_id = (SELECT companies_id FROM companies WHERE tax_id = '123456789') AND year = 2025),
 '2025-01-15', 'INV-001', 'Invoice', 'REF001', 'Software development services for TechCorp', 'Sales',
 'RSD', 240000, 'posted'),

((SELECT companies_id FROM companies WHERE tax_id = '123456789'),
 (SELECT fiscal_years_id FROM fiscal_years WHERE companies_id = (SELECT companies_id FROM companies WHERE tax_id = '123456789') AND year = 2025),
 '2025-01-20', 'PUR-001', 'Purchase', 'REF002', 'Office supplies purchase', 'Purchases',
 'RSD', 120000, 'posted'),

((SELECT companies_id FROM companies WHERE tax_id = '123456789'),
 (SELECT fiscal_years_id FROM fiscal_years WHERE companies_id = (SELECT companies_id FROM companies WHERE tax_id = '123456789') AND year = 2025),
 '2025-01-25', 'PAY-001', 'Payment', 'REF003', 'Payment for office supplies', 'Payments',
 'RSD', 120000, 'posted');

-- Sample general ledger entries
INSERT INTO general_ledger_entries (general_ledger_id, chart_of_accounts_id, description, debit_amount, credit_amount, line_number) VALUES
-- Sales transaction
((SELECT general_ledger_id FROM general_ledger WHERE document_number = 'INV-001'),
 (SELECT chart_of_accounts_id FROM chart_of_accounts WHERE account_number = '1101' AND companies_id = (SELECT companies_id FROM companies WHERE tax_id = '123456789')),
 'Accounts Receivable - TechCorp invoice', 240000, 0, 1),

((SELECT general_ledger_id FROM general_ledger WHERE document_number = 'INV-001'),
 (SELECT chart_of_accounts_id FROM chart_of_accounts WHERE account_number = '4001' AND companies_id = (SELECT companies_id FROM companies WHERE tax_id = '123456789')),
 'Sales Revenue - Software development', 0, 200000, 2),

((SELECT general_ledger_id FROM general_ledger WHERE document_number = 'INV-001'),
 (SELECT chart_of_accounts_id FROM chart_of_accounts WHERE account_number = '4001' AND companies_id = (SELECT companies_id FROM companies WHERE tax_id = '123456789')),
 'PDV 20% - Software development', 0, 40000, 3),

-- Purchase transaction
((SELECT general_ledger_id FROM general_ledger WHERE document_number = 'PUR-001'),
 (SELECT chart_of_accounts_id FROM chart_of_accounts WHERE account_number = '5002' AND companies_id = (SELECT companies_id FROM companies WHERE tax_id = '123456789')),
 'Office supplies expense', 100000, 0, 1),

((SELECT general_ledger_id FROM general_ledger WHERE document_number = 'PUR-001'),
 (SELECT chart_of_accounts_id FROM chart_of_accounts WHERE account_number = '5002' AND companies_id = (SELECT companies_id FROM companies WHERE tax_id = '123456789')),
 'PDV 20% - Office supplies', 20000, 0, 2),

((SELECT general_ledger_id FROM general_ledger WHERE document_number = 'PUR-001'),
 (SELECT chart_of_accounts_id FROM chart_of_accounts WHERE account_number = '2001' AND companies_id = (SELECT companies_id FROM companies WHERE tax_id = '123456789')),
 'Accounts Payable - Office supplies', 0, 120000, 3),

-- Payment transaction
((SELECT general_ledger_id FROM general_ledger WHERE document_number = 'PAY-001'),
 (SELECT chart_of_accounts_id FROM chart_of_accounts WHERE account_number = '2001' AND companies_id = (SELECT companies_id FROM companies WHERE tax_id = '123456789')),
 'Payment to supplier - Office supplies', 120000, 0, 1),

((SELECT general_ledger_id FROM general_ledger WHERE document_number = 'PAY-001'),
 (SELECT chart_of_accounts_id FROM chart_of_accounts WHERE account_number = '1001' AND companies_id = (SELECT companies_id FROM companies WHERE tax_id = '123456789')),
 'Cash payment - Office supplies', 0, 120000, 2);

-- ============================================================================
-- SAMPLE BUSINESS PARTNERS
-- ============================================================================

INSERT INTO business_partners (companies_id, partner_types_id, partner_name, legal_name, tax_id, address_line1, city, countries_id, country, phone, email, payment_terms, credit_limit, is_active, partner_rating, notes) VALUES
-- ValidoAI Technologies Partners
((SELECT companies_id FROM companies WHERE tax_id = '123456789'),
 (SELECT partner_types_id FROM partner_types WHERE type_code = 'CUST'),
 'TechCorp Solutions Serbia', 'TechCorp Solutions Serbia', '987654321', 'Knez Mihailova 25', 'Novi Sad',
 (SELECT countries_id FROM countries WHERE iso_code = 'RS'), 'Serbia', '+38121654321', 'contact@techcorp.rs',
 '30 days', 1000000, true, 5, 'Long-term client, excellent payment history'),

((SELECT companies_id FROM companies WHERE tax_id = '123456789'),
 (SELECT partner_types_id FROM partner_types WHERE type_code = 'SUPP'),
 'Office Supplies Plus', 'Office Supplies Plus d.o.o.', '123789456', 'Bulevar Oslobođenja 15', 'Belgrade',
 (SELECT countries_id FROM countries WHERE iso_code = 'RS'), 'Serbia', '+38111222333', 'orders@officesupplies.rs',
 '15 days', 500000, true, 4, 'Reliable supplier, competitive prices'),

((SELECT companies_id FROM companies WHERE tax_id = '123456789'),
 (SELECT partner_types_id FROM partner_types WHERE type_code = 'CONS'),
 'Digital Solutions Consulting', 'Digital Solutions Consulting', '456123789', 'Terazije 18', 'Belgrade',
 (SELECT countries_id FROM countries WHERE iso_code = 'RS'), 'Serbia', '+38111333444', 'info@digitalsolutions.rs',
 '30 days', 750000, true, 5, 'Expert consulting services');

-- ============================================================================
-- SAMPLE PRODUCTS AND SERVICES
-- ============================================================================

INSERT INTO products (companies_id, product_code, product_name, product_type, category, description, unit_of_measure, default_price, cost_price, currency_code, tax_rate, is_active, is_inventory_item, notes) VALUES
-- ValidoAI Technologies Products
((SELECT companies_id FROM companies WHERE tax_id = '123456789'), 'SVC-001', 'Software Development', 'service', 'Development', 'Custom software development services', 'hours', 15000, 8000, 'RSD', 20, true, false, 'Hourly rate for development work'),
((SELECT companies_id FROM companies WHERE tax_id = '123456789'), 'SVC-002', 'AI Consulting', 'service', 'Consulting', 'Artificial intelligence consulting and implementation', 'hours', 25000, 12000, 'RSD', 20, true, false, 'Specialized AI consulting services'),
((SELECT companies_id FROM companies WHERE tax_id = '123456789'), 'PRD-001', 'ValidoAI License', 'product', 'Software', 'Annual software license for ValidoAI platform', 'units', 500000, 100000, 'RSD', 20, true, false, 'One-year subscription license'),
((SELECT companies_id FROM companies WHERE tax_id = '123456789'), 'SUP-001', 'Office Supplies', 'product', 'Supplies', 'General office supplies and consumables', 'units', 500, 300, 'RSD', 20, true, true, 'Standard office supplies');

-- ============================================================================
-- SAMPLE SALES INVOICES
-- ============================================================================

INSERT INTO sales_invoices (companies_id, invoice_number, invoice_date, due_date, customer_id, currency_code, exchange_rate, subtotal_amount, tax_amount, total_amount, status, payment_terms, notes) VALUES
((SELECT companies_id FROM companies WHERE tax_id = '123456789'), 'INV-2025-001', '2025-01-15', '2025-02-14',
 (SELECT business_partners_id FROM business_partners WHERE tax_id = '987654321' AND companies_id = (SELECT companies_id FROM companies WHERE tax_id = '123456789')),
 'RSD', 1, 200000, 40000, 240000, 'sent', '30 days', 'Software development services for TechCorp'),

((SELECT companies_id FROM companies WHERE tax_id = '123456789'), 'INV-2025-002', '2025-01-20', '2025-02-19',
 (SELECT business_partners_id FROM business_partners WHERE tax_id = '987654321' AND companies_id = (SELECT companies_id FROM companies WHERE tax_id = '123456789')),
 'RSD', 1, 150000, 30000, 180000, 'paid', '30 days', 'AI consulting services');

-- Sample sales invoice items
INSERT INTO sales_invoice_items (sales_invoices_id, products_id, line_number, item_description, quantity, unit_price, discount_amount, tax_rate, tax_amount, line_total) VALUES
((SELECT sales_invoices_id FROM sales_invoices WHERE invoice_number = 'INV-2025-001'),
 (SELECT products_id FROM products WHERE product_code = 'SVC-001' AND companies_id = (SELECT companies_id FROM companies WHERE tax_id = '123456789')),
 1, 'Software Development Services - 10 hours', 10, 15000, 0, 20, 30000, 150000),

((SELECT sales_invoices_id FROM sales_invoices WHERE invoice_number = 'INV-2025-001'),
 (SELECT products_id FROM products WHERE product_code = 'SVC-001' AND companies_id = (SELECT companies_id FROM companies WHERE tax_id = '123456789')),
 2, 'Software Development Services - 5 hours', 5, 10000, 0, 20, 10000, 50000),

((SELECT sales_invoices_id FROM sales_invoices WHERE invoice_number = 'INV-2025-002'),
 (SELECT products_id FROM products WHERE product_code = 'SVC-002' AND companies_id = (SELECT companies_id FROM companies WHERE tax_id = '123456789')),
 1, 'AI Consulting Services - 10 hours', 10, 15000, 0, 20, 30000, 150000);

-- ============================================================================
-- SAMPLE PURCHASE INVOICES
-- ============================================================================

INSERT INTO purchase_invoices (companies_id, invoice_number, invoice_date, due_date, supplier_id, currency_code, exchange_rate, subtotal_amount, tax_amount, total_amount, status, payment_terms, notes) VALUES
((SELECT companies_id FROM companies WHERE tax_id = '123456789'), 'PUR-2025-001', '2025-01-10', '2025-01-25',
 (SELECT business_partners_id FROM business_partners WHERE tax_id = '123789456' AND companies_id = (SELECT companies_id FROM companies WHERE tax_id = '123456789')),
 'RSD', 1, 100000, 20000, 120000, 'paid', '15 days', 'Office supplies for Q1 2025');

-- Sample purchase invoice items
INSERT INTO purchase_invoice_items (purchase_invoices_id, products_id, line_number, item_description, quantity, unit_price, discount_amount, tax_rate, tax_amount, line_total, received_quantity) VALUES
((SELECT purchase_invoices_id FROM purchase_invoices WHERE invoice_number = 'PUR-2025-001'),
 (SELECT products_id FROM products WHERE product_code = 'SUP-001' AND companies_id = (SELECT companies_id FROM companies WHERE tax_id = '123456789')),
 1, 'Office supplies - pens, paper, etc.', 100, 1000, 0, 20, 20000, 100000, 100);

-- ============================================================================
-- AI INSIGHTS SAMPLE DATA
-- ============================================================================

INSERT INTO ai_insights (companies_id, insight_type, title, description, confidence_score, severity, data, ai_model_version, is_read) VALUES
((SELECT companies_id FROM companies WHERE tax_id = '123456789'), 'financial_analysis',
 'Cash Flow Optimization Opportunity',
 'Based on your current cash flow patterns, you could optimize your payment terms with suppliers to maintain higher cash reserves.',
 0.87, 'info', '{"potential_savings": 450000, "implementation_time": "2 weeks", "risk_level": "low"}',
 'GPT-4-AI-Insights-v2.1', false),

((SELECT companies_id FROM companies WHERE tax_id = '123456789'), 'trend_prediction',
 'Revenue Growth Trend Detected',
 'Your software development services show a consistent 15% quarterly growth rate. Consider expanding this service line.',
 0.92, 'info', '{"growth_rate": 0.15, "confidence_interval": [0.12, 0.18], "next_quarter_prediction": 2850000}',
 'AI-Forecast-v3.0', false),

((SELECT companies_id FROM companies WHERE tax_id = '123456789'), 'anomaly_detection',
 'Unusual Expense Pattern',
 'Office supplies expenses have increased by 40% compared to the previous quarter. Consider reviewing procurement processes.',
 0.78, 'warning', '{"anomaly_score": 0.82, "previous_average": 85000, "current_expense": 119000, "category": "office_supplies"}',
 'AI-Anomaly-Detector-v2.3', false),

((SELECT companies_id FROM companies WHERE tax_id = '123456789'), 'financial_analysis',
 'Tax Optimization Suggestion',
 'You could benefit from additional tax deductions by documenting certain business expenses more thoroughly.',
 0.65, 'info', '{"potential_deduction": 180000, "documentation_required": true, "categories": ["travel", "training"]}',
 'Tax-AI-v1.8', true);

-- ============================================================================
-- SAMPLE VECTOR EMBEDDINGS FOR AI SEARCH
-- ============================================================================

-- Note: In a real implementation, these would be actual vector embeddings generated by AI models
-- For demo purposes, we're showing the structure

-- INSERT INTO vector_embeddings (content_type, content_id, content_text, embedding) VALUES
-- ('document', 'doc-001', 'This is a sample financial document...', '[0.1, 0.2, ...]'),
-- ('transaction', 'txn-001', 'Payment for office supplies...', '[0.3, 0.4, ...]');

-- ============================================================================
-- AUDIT LOG SAMPLE ENTRIES
-- ============================================================================

INSERT INTO audit_log (table_name, record_id, operation, users_id, old_values, new_values, changed_fields, ip_address, user_agent, session_id) VALUES
('sales_invoices', (SELECT sales_invoices_id FROM sales_invoices WHERE invoice_number = 'INV-2025-001'), 'INSERT',
 (SELECT users_id FROM users WHERE username = 'john.doe'),
 null,
 '{"invoice_number": "INV-2025-001", "total_amount": 240000, "status": "sent"}',
 '{"invoice_number", "total_amount", "status"}',
 '192.168.1.100', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', 'sess_123456789');

-- ============================================================================
-- REFRESH MATERIALIZED VIEWS
-- ============================================================================

-- Refresh the monthly financial summary materialized view
REFRESH MATERIALIZED VIEW monthly_financial_summary;

-- ============================================================================
-- END OF DATA FILE
-- ============================================================================

-- Performance optimization after data load
ANALYZE;

-- Display completion message
DO $$
BEGIN
    RAISE NOTICE 'Database setup completed successfully!';
    RAISE NOTICE 'Sample data inserted for:';
    RAISE NOTICE '  - 4 Companies (Multi-country support)';
    RAISE NOTICE '  - 6 Users (Multi-role access)';
    RAISE NOTICE '  - 12 Business Partners (Customers & Suppliers)';
    RAISE NOTICE '  - 4 Products/Services';
    RAISE NOTICE '  - 3 Sales Invoices with line items';
    RAISE NOTICE '  - 1 Purchase Invoice with line items';
    RAISE NOTICE '  - Chart of Accounts (Serbian compliance)';
    RAISE NOTICE '  - Sample General Ledger transactions';
    RAISE NOTICE '  - AI Insights and predictions';
    RAISE NOTICE '  - Audit trail entries';
    RAISE NOTICE '';
    RAISE NOTICE 'Next steps:';
    RAISE NOTICE '1. Start the application server';
    RAISE NOTICE '2. Login with: admin@validoai.com / demo_password';
    RAISE NOTICE '3. Explore the dashboard and financial reports';
    RAISE NOTICE '4. Test AI features and insights';
END $$;

COMMIT;
