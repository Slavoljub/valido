-- AI Valido Online - Comprehensive Data Structure
-- Separate data file for all INSERT statements
-- This file contains all sample data, default configurations, and embeddings

-- Countries Data with Comprehensive Information
INSERT INTO countries (iso_code, iso_code_3, iso_numeric, name, native_name, capital, region, subregion, latitude, longitude, area_km2, population, currency_code, currency_name, currency_symbol, phone_code, flag_emoji, flag_svg_url, flag_png_url) VALUES
('RS', 'SRB', '688', 'Serbia', 'Србија', 'Belgrade', 'Europe', 'Southern Europe', 44.0165, 21.0059, 88361, 6871547, 'RSD', 'Serbian Dinar', 'дин.', '+381', '🇷🇸', 'https://flagcdn.com/rs.svg', 'https://flagcdn.com/w320/rs.png'),
('US', 'USA', '840', 'United States', 'United States', 'Washington D.C.', 'Americas', 'North America', 37.0902, -95.7129, 9833517, 331002651, 'USD', 'US Dollar', '$', '+1', '🇺🇸', 'https://flagcdn.com/us.svg', 'https://flagcdn.com/w320/us.png'),
('DE', 'DEU', '276', 'Germany', 'Deutschland', 'Berlin', 'Europe', 'Western Europe', 51.1657, 10.4515, 357114, 83783942, 'EUR', 'Euro', '€', '+49', '🇩🇪', 'https://flagcdn.com/de.svg', 'https://flagcdn.com/w320/de.png'),
('GB', 'GBR', '826', 'United Kingdom', 'United Kingdom', 'London', 'Europe', 'Northern Europe', 55.3781, -3.4360, 242495, 67886011, 'GBP', 'British Pound', '£', '+44', '🇬🇧', 'https://flagcdn.com/gb.svg', 'https://flagcdn.com/w320/gb.png'),
('FR', 'FRA', '250', 'France', 'France', 'Paris', 'Europe', 'Western Europe', 46.2276, 2.2137, 551695, 65273511, 'EUR', 'Euro', '€', '+33', '🇫🇷', 'https://flagcdn.com/fr.svg', 'https://flagcdn.com/w320/fr.png'),
('IT', 'ITA', '380', 'Italy', 'Italia', 'Rome', 'Europe', 'Southern Europe', 41.8719, 12.5674, 301336, 60461826, 'EUR', 'Euro', '€', '+39', '🇮🇹', 'https://flagcdn.com/it.svg', 'https://flagcdn.com/w320/it.png'),
('HR', 'HRV', '191', 'Croatia', 'Hrvatska', 'Zagreb', 'Europe', 'Southern Europe', 45.1000, 15.2000, 56594, 4105267, 'EUR', 'Euro', '€', '+385', '🇭🇷', 'https://flagcdn.com/hr.svg', 'https://flagcdn.com/w320/hr.png'),
('BA', 'BIH', '070', 'Bosnia and Herzegovina', 'Bosna i Hercegovina', 'Sarajevo', 'Europe', 'Southern Europe', 43.9159, 17.6791, 51209, 3280819, 'BAM', 'Bosnia and Herzegovina Mark', 'KM', '+387', '🇧🇦', 'https://flagcdn.com/ba.svg', 'https://flagcdn.com/w320/ba.png'),
('ME', 'MNE', '499', 'Montenegro', 'Crna Gora', 'Podgorica', 'Europe', 'Southern Europe', 42.7087, 19.3744, 13812, 621873, 'EUR', 'Euro', '€', '+382', '🇲🇪', 'https://flagcdn.com/me.svg', 'https://flagcdn.com/w320/me.png'),
('MK', 'MKD', '807', 'North Macedonia', 'Северна Македонија', 'Skopje', 'Europe', 'Southern Europe', 41.6086, 21.7453, 25713, 2077132, 'MKD', 'Macedonian Denar', 'ден', '+389', '🇲🇰', 'https://flagcdn.com/mk.svg', 'https://flagcdn.com/w320/mk.png'),
('AL', 'ALB', '008', 'Albania', 'Shqipëria', 'Tirana', 'Europe', 'Southern Europe', 41.1533, 20.1683, 28748, 2837743, 'ALL', 'Albanian Lek', 'L', '+355', '🇦🇱', 'https://flagcdn.com/al.svg', 'https://flagcdn.com/w320/al.png'),
('GR', 'GRC', '300', 'Greece', 'Ελλάδα', 'Athens', 'Europe', 'Southern Europe', 39.0742, 21.8243, 131957, 10423054, 'EUR', 'Euro', '€', '+30', '🇬🇷', 'https://flagcdn.com/gr.svg', 'https://flagcdn.com/w320/gr.png');

-- Sample Companies
INSERT INTO companies (company_name, legal_name, tax_id, registration_number, address_line1, city, postal_code, countries_id, country, phone, email, website, industry, company_size, description, embedding_vector) VALUES
('ValidoAI Technologies', 'ValidoAI Technologies d.o.o.', '123456789', 'REG001', 'Bulevar Mihajla Pupina 10', 'Belgrade', '11000', (SELECT countries_id FROM countries WHERE iso_code = 'RS'), 'Serbia', '+381113456789', 'info@validoai.com', 'https://validoai.com', 'Technology', '11-50 employees', 'AI-powered financial analysis and automation platform', '[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 0.11, 0.12, 0.13, 0.14, 0.15, 0.16]'),
('TechCorp Solutions', 'TechCorp Solutions Serbia', '987654321', 'REG002', 'Knez Mihailova 25', 'Novi Sad', '21000', (SELECT countries_id FROM countries WHERE iso_code = 'RS'), 'Serbia', '+38121654321', 'contact@techcorp.rs', 'https://techcorp.rs', 'Information Technology', '51-200 employees', 'Comprehensive IT solutions and digital transformation services', '[0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 0.1, 0.21, 0.22, 0.23, 0.24, 0.25, 0.26]'),
('FinanceHub Ltd', 'FinanceHub Consulting Ltd', '456789123', 'REG003', 'Terazije 12', 'Belgrade', '11000', (SELECT countries_id FROM countries WHERE iso_code = 'RS'), 'Serbia', '+38111234567', 'hello@financehub.rs', 'https://financehub.rs', 'Financial Services', '11-50 employees', 'Financial consulting and advisory services for SMEs', '[0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 0.1, 0.2, 0.31, 0.32, 0.33, 0.34, 0.35, 0.36]');

-- Sample Users with Comprehensive Authentication Support
INSERT INTO users (username, email, password_hash, first_name, last_name, companies_id, is_admin, is_verified, two_factor_enabled, two_factor_method, embedding_vector) VALUES
('admin', 'admin@validoai.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LeCtj1rE1rTjY1F2', 'System', 'Administrator', (SELECT companies_id FROM companies WHERE tax_id = '123456789'), TRUE, TRUE, TRUE, 'totp', '[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 0.11, 0.12, 0.13, 0.14, 0.15, 0.16]'),
('manager', 'manager@validoai.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LeCtj1rE1rTjY1F2', 'John', 'Manager', (SELECT companies_id FROM companies WHERE tax_id = '123456789'), FALSE, TRUE, FALSE, 'sms', '[0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 0.1, 0.21, 0.22, 0.23, 0.24, 0.25, 0.26]'),
('accountant', 'accountant@validoai.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LeCtj1rE1rTjY1F2', 'Jane', 'Accountant', (SELECT companies_id FROM companies WHERE tax_id = '123456789'), FALSE, TRUE, TRUE, 'email', '[0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 0.1, 0.2, 0.31, 0.32, 0.33, 0.34, 0.35, 0.36]');

-- User Roles
INSERT INTO user_roles (role_name, description) VALUES
('Administrator', 'Full system access with all permissions'),
('Manager', 'Management access to company resources'),
('Accountant', 'Financial and accounting access'),
('Employee', 'Basic employee access'),
('HR', 'Human resources management access'),
('Support', 'Customer support access'),
('Developer', 'System development and maintenance access');

-- User Role Assignments
INSERT INTO user_role_assignments (user_id, role_id, assigned_by) VALUES
((SELECT users_id FROM users WHERE username = 'admin'), (SELECT user_roles_id FROM user_roles WHERE role_name = 'Administrator'), (SELECT users_id FROM users WHERE username = 'admin')),
((SELECT users_id FROM users WHERE username = 'manager'), (SELECT user_roles_id FROM user_roles WHERE role_name = 'Manager'), (SELECT users_id FROM users WHERE username = 'admin')),
((SELECT users_id FROM users WHERE username = 'accountant'), (SELECT user_roles_id FROM user_roles WHERE role_name = 'Accountant'), (SELECT users_id FROM users WHERE username = 'admin'));

-- Chart of Accounts
INSERT INTO chart_of_accounts (companies_id, account_code, account_name, account_type, account_category) VALUES
((SELECT companies_id FROM companies WHERE tax_id = '123456789'), '1000', 'Cash and Cash Equivalents', 'Asset', 'Current Assets'),
((SELECT companies_id FROM companies WHERE tax_id = '123456789'), '1100', 'Accounts Receivable', 'Asset', 'Current Assets'),
((SELECT companies_id FROM companies WHERE tax_id = '123456789'), '1200', 'Inventory', 'Asset', 'Current Assets'),
((SELECT companies_id FROM companies WHERE tax_id = '123456789'), '1300', 'Prepaid Expenses', 'Asset', 'Current Assets'),
((SELECT companies_id FROM companies WHERE tax_id = '123456789'), '2000', 'Accounts Payable', 'Liability', 'Current Liabilities'),
((SELECT companies_id FROM companies WHERE tax_id = '123456789'), '3000', 'Common Stock', 'Equity', 'Equity'),
((SELECT companies_id FROM companies WHERE tax_id = '123456789'), '4000', 'Sales Revenue', 'Income', 'Revenue'),
((SELECT companies_id FROM companies WHERE tax_id = '123456789'), '5000', 'Cost of Goods Sold', 'Expense', 'Cost of Sales'),
((SELECT companies_id FROM companies WHERE tax_id = '123456789'), '6000', 'Operating Expenses', 'Expense', 'Operating Expenses'),
((SELECT companies_id FROM companies WHERE tax_id = '123456789'), '7000', 'Interest Expense', 'Expense', 'Financial Expenses');

-- Sample Employees with Comprehensive Information
INSERT INTO employees (companies_id, user_id, employee_number, first_name, last_name, hire_date, job_title, department, base_salary, currency_code, payment_method, work_email, embedding_vector) VALUES
((SELECT companies_id FROM companies WHERE tax_id = '123456789'), (SELECT users_id FROM users WHERE username = 'manager'), 'EMP001', 'John', 'Manager', '2023-01-15', 'Operations Manager', 'Management', 85000.00, 'RSD', 'bank_transfer', 'john.manager@validoai.com', '[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 0.11, 0.12, 0.13, 0.14, 0.15, 0.16]'),
((SELECT companies_id FROM companies WHERE tax_id = '123456789'), (SELECT users_id FROM users WHERE username = 'accountant'), 'EMP002', 'Jane', 'Accountant', '2023-02-01', 'Senior Accountant', 'Finance', 65000.00, 'RSD', 'bank_transfer', 'jane.accountant@validoai.com', '[0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 0.1, 0.21, 0.22, 0.23, 0.24, 0.25, 0.26]'),
((SELECT companies_id FROM companies WHERE tax_id = '123456789'), NULL, 'EMP003', 'Michael', 'Developer', '2023-03-01', 'Senior Developer', 'IT', 75000.00, 'RSD', 'bank_transfer', 'michael.developer@validoai.com', '[0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 0.1, 0.2, 0.31, 0.32, 0.33, 0.34, 0.35, 0.36]');

-- Sample Payroll Data
INSERT INTO payroll (companies_id, employees_id, payroll_period_start, payroll_period_end, payroll_date, pay_schedule, base_salary, gross_amount, tax_amount, net_amount, payment_status, embedding_vector) VALUES
((SELECT companies_id FROM companies WHERE tax_id = '123456789'), (SELECT employees_id FROM employees WHERE employee_number = 'EMP001'), '2024-01-01', '2024-01-31', '2024-02-05', 'monthly', 85000.00, 85000.00, 17850.00, 67150.00, 'paid', '[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 0.11, 0.12, 0.13, 0.14, 0.15, 0.16]'),
((SELECT companies_id FROM companies WHERE tax_id = '123456789'), (SELECT employees_id FROM employees WHERE employee_number = 'EMP002'), '2024-01-01', '2024-01-31', '2024-02-05', 'monthly', 65000.00, 65000.00, 13650.00, 51350.00, 'paid', '[0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 0.1, 0.21, 0.22, 0.23, 0.24, 0.25, 0.26]'),
((SELECT companies_id FROM companies WHERE tax_id = '123456789'), (SELECT employees_id FROM employees WHERE employee_number = 'EMP003'), '2024-01-01', '2024-01-31', '2024-02-05', 'monthly', 75000.00, 75000.00, 15750.00, 59250.00, 'paid', '[0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 0.1, 0.2, 0.31, 0.32, 0.33, 0.34, 0.35, 0.36]');

-- Sample Tickets with SLA Support
INSERT INTO tickets (companies_id, created_by, title, description, category, priority, status, sla_response_time, sla_resolution_time, embedding_vector) VALUES
((SELECT companies_id FROM companies WHERE tax_id = '123456789'), (SELECT users_id FROM users WHERE username = 'admin'), 'Invoice Processing Issue', 'Unable to process invoice #12345 due to system error', 'finance', 'high', 'open', CURRENT_TIMESTAMP + INTERVAL '2 hours', CURRENT_TIMESTAMP + INTERVAL '8 hours', '[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 0.11, 0.12, 0.13, 0.14, 0.15, 0.16]'),
((SELECT companies_id FROM companies WHERE tax_id = '123456789'), (SELECT users_id FROM users WHERE username = 'manager'), 'Payroll Calculation Error', 'Payroll calculations showing incorrect tax amounts for Q1 2024', 'hr', 'urgent', 'in_progress', CURRENT_TIMESTAMP + INTERVAL '1 hour', CURRENT_TIMESTAMP + INTERVAL '4 hours', '[0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 0.1, 0.21, 0.22, 0.23, 0.24, 0.25, 0.26]'),
((SELECT companies_id FROM companies WHERE tax_id = '123456789'), (SELECT users_id FROM users WHERE username = 'accountant'), 'Bank Reconciliation Issue', 'Bank statement does not match our records for December 2023', 'finance', 'medium', 'waiting', CURRENT_TIMESTAMP + INTERVAL '4 hours', CURRENT_TIMESTAMP + INTERVAL '24 hours', '[0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 0.1, 0.2, 0.31, 0.32, 0.33, 0.34, 0.35, 0.36]');

-- Sample AI Insights
INSERT INTO ai_insights (companies_id, insight_type, title, description, confidence_score, impact_level, embedding_vector) VALUES
((SELECT companies_id FROM companies WHERE tax_id = '123456789'), 'financial_analysis', 'Revenue Growth Trend', 'Revenue has shown consistent 15% quarterly growth over the past 6 months', 0.89, 'high', '[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 0.11, 0.12, 0.13, 0.14, 0.15, 0.16]'),
((SELECT companies_id FROM companies WHERE tax_id = '123456789'), 'risk_assessment', 'Cash Flow Risk', 'Potential cash flow issues detected for Q2 2024 due to delayed receivables', 0.76, 'medium', '[0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 0.1, 0.21, 0.22, 0.23, 0.24, 0.25, 0.26]'),
((SELECT companies_id FROM companies WHERE tax_id = '123456789'), 'operational_efficiency', 'Process Optimization', 'Invoice processing time can be reduced by 35% through automation', 0.92, 'high', '[0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 0.1, 0.2, 0.31, 0.32, 0.33, 0.34, 0.35, 0.36]');

-- Sample AI Training Data
INSERT INTO ai_training_data (companies_id, data_type, title, description, quality_score, embedding_vector) VALUES
((SELECT companies_id FROM companies WHERE tax_id = '123456789'), 'financial', 'Monthly Revenue Analysis', 'Analysis of monthly revenue patterns from 2022-2024', 0.95, '[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 0.11, 0.12, 0.13, 0.14, 0.15, 0.16]'),
((SELECT companies_id FROM companies WHERE tax_id = '123456789'), 'behavioral', 'Customer Payment Patterns', 'Historical data on customer payment behaviors and trends', 0.88, '[0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 0.1, 0.21, 0.22, 0.23, 0.24, 0.25, 0.26]'),
((SELECT companies_id FROM companies WHERE tax_id = '123456789'), 'operational', 'Process Efficiency Metrics', 'Operational metrics and efficiency indicators for business processes', 0.91, '[0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 0.1, 0.2, 0.31, 0.32, 0.33, 0.34, 0.35, 0.36]');

-- Comprehensive Settings Configuration
INSERT INTO settings (setting_key, setting_value, setting_type, setting_category, display_name, description, is_system_setting, is_required, is_encrypted) VALUES
-- System Settings
('app_name', 'ValidoAI', 'string', 'system', 'Application Name', 'The name of the application', TRUE, TRUE, FALSE),
('app_version', '1.0.0', 'string', 'system', 'Application Version', 'Current version of the application', TRUE, TRUE, FALSE),
('maintenance_mode', 'false', 'boolean', 'system', 'Maintenance Mode', 'Enable maintenance mode for system updates', TRUE, FALSE, FALSE),
('debug_mode', 'false', 'boolean', 'system', 'Debug Mode', 'Enable debug logging and features', TRUE, FALSE, FALSE),
('timezone', 'Europe/Belgrade', 'string', 'system', 'Default Timezone', 'Default timezone for the application', TRUE, TRUE, FALSE),

-- Security Settings
('password_min_length', '8', 'number', 'security', 'Minimum Password Length', 'Minimum length for user passwords', FALSE, TRUE, FALSE),
('password_require_uppercase', 'true', 'boolean', 'security', 'Require Uppercase', 'Require uppercase letters in passwords', FALSE, FALSE, FALSE),
('password_require_numbers', 'true', 'boolean', 'security', 'Require Numbers', 'Require numbers in passwords', FALSE, FALSE, FALSE),
('password_require_symbols', 'false', 'boolean', 'security', 'Require Symbols', 'Require symbols in passwords', FALSE, FALSE, FALSE),
('session_timeout', '3600', 'number', 'security', 'Session Timeout', 'Session timeout in seconds', FALSE, TRUE, FALSE),
('max_login_attempts', '5', 'number', 'security', 'Max Login Attempts', 'Maximum failed login attempts before lockout', FALSE, TRUE, FALSE),
('lockout_duration', '900', 'number', 'security', 'Lockout Duration', 'Account lockout duration in seconds', FALSE, TRUE, FALSE),

-- Financial Settings
('default_currency', 'RSD', 'string', 'finance', 'Default Currency', 'Default currency for financial operations', FALSE, TRUE, FALSE),
('fiscal_year_start', '1', 'number', 'finance', 'Fiscal Year Start Month', 'Month when fiscal year starts (1-12)', FALSE, TRUE, FALSE),
('tax_rate', '20.0', 'number', 'finance', 'Default Tax Rate', 'Default tax rate percentage', FALSE, TRUE, FALSE),
('invoice_due_days', '30', 'number', 'finance', 'Invoice Due Days', 'Default due days for invoices', FALSE, FALSE, FALSE),
('payment_terms', 'Net 30', 'string', 'finance', 'Default Payment Terms', 'Default payment terms for invoices', FALSE, FALSE, FALSE),

-- AI/ML Settings
('ai_enabled', 'true', 'boolean', 'ai', 'AI Features Enabled', 'Enable AI-powered features', FALSE, FALSE, FALSE),
('default_ai_model', 'qwen-3', 'string', 'ai', 'Default AI Model', 'Default AI model for processing', FALSE, FALSE, FALSE),
('ai_confidence_threshold', '0.7', 'number', 'ai', 'AI Confidence Threshold', 'Minimum confidence score for AI insights', FALSE, FALSE, FALSE),
('ai_max_tokens', '4096', 'number', 'ai', 'Max AI Tokens', 'Maximum tokens for AI model responses', FALSE, FALSE, FALSE),

-- Email Settings
('smtp_server', 'smtp.gmail.com', 'string', 'email', 'SMTP Server', 'SMTP server for sending emails', FALSE, FALSE, TRUE),
('smtp_port', '587', 'number', 'email', 'SMTP Port', 'SMTP server port', FALSE, FALSE, TRUE),
('smtp_username', '', 'string', 'email', 'SMTP Username', 'SMTP authentication username', FALSE, FALSE, TRUE),
('smtp_password', '', 'string', 'email', 'SMTP Password', 'SMTP authentication password', FALSE, FALSE, TRUE),
('email_from_address', 'noreply@validoai.com', 'string', 'email', 'From Address', 'Default from address for emails', FALSE, TRUE, FALSE),

-- Notification Settings
('email_notifications', 'true', 'boolean', 'notifications', 'Email Notifications', 'Enable email notifications', FALSE, FALSE, FALSE),
('sms_notifications', 'false', 'boolean', 'notifications', 'SMS Notifications', 'Enable SMS notifications', FALSE, FALSE, FALSE),
('push_notifications', 'true', 'boolean', 'notifications', 'Push Notifications', 'Enable push notifications', FALSE, FALSE, FALSE),
('notification_frequency', 'daily', 'string', 'notifications', 'Notification Frequency', 'How often to send notifications', FALSE, FALSE, FALSE),

-- File Upload Settings
('max_file_size', '50MB', 'string', 'files', 'Max File Size', 'Maximum file upload size', FALSE, TRUE, FALSE),
('allowed_file_types', '["pdf", "doc", "docx", "xlsx", "csv", "jpg", "png"]', 'json', 'files', 'Allowed File Types', 'List of allowed file types for upload', FALSE, TRUE, FALSE),
('upload_path', 'uploads/', 'string', 'files', 'Upload Path', 'Path for file uploads', FALSE, TRUE, FALSE),

-- UI/UX Settings
('theme', 'light', 'string', 'ui', 'Default Theme', 'Default application theme', FALSE, FALSE, FALSE),
('language', 'en', 'string', 'ui', 'Default Language', 'Default application language', FALSE, FALSE, FALSE),
('items_per_page', '25', 'number', 'ui', 'Items Per Page', 'Default number of items per page', FALSE, FALSE, FALSE),
('date_format', 'DD/MM/YYYY', 'string', 'ui', 'Date Format', 'Default date display format', FALSE, FALSE, FALSE);

-- Sample Notifications
INSERT INTO notifications (companies_id, users_id, title, message, type) VALUES
((SELECT companies_id FROM companies WHERE tax_id = '123456789'), (SELECT users_id FROM users WHERE username = 'admin'), 'System Update', 'System has been updated to version 1.0.0', 'info'),
((SELECT companies_id FROM companies WHERE tax_id = '123456789'), (SELECT users_id FROM users WHERE username = 'manager'), 'Monthly Report Ready', 'Your monthly financial report is ready for review', 'success'),
((SELECT companies_id FROM companies WHERE tax_id = '123456789'), (SELECT users_id FROM users WHERE username = 'accountant'), 'Invoice Due', 'Invoice #12345 is due in 3 days', 'warning');

-- Sample Audit Logs
INSERT INTO audit_logs (companies_id, users_id, table_name, operation, old_values, new_values) VALUES
((SELECT companies_id FROM companies WHERE tax_id = '123456789'), (SELECT users_id FROM users WHERE username = 'admin'), 'users', 'INSERT', '{}', '{"username": "admin", "email": "admin@validoai.com"}'),
((SELECT companies_id FROM companies WHERE tax_id = '123456789'), (SELECT users_id FROM users WHERE username = 'admin'), 'companies', 'INSERT', '{}', '{"company_name": "ValidoAI Technologies"}'),
((SELECT companies_id FROM companies WHERE tax_id = '123456789'), (SELECT users_id FROM users WHERE username = 'manager'), 'employees', 'UPDATE', '{"department": "Management"}', '{"department": "Operations"}');

-- Sample CRM Data
INSERT INTO crm_contacts (companies_id, first_name, last_name, email, phone) VALUES
((SELECT companies_id FROM companies WHERE tax_id = '123456789'), 'Marko', 'Petrovic', 'marko.petrovic@company.rs', '+38160123456'),
((SELECT companies_id FROM companies WHERE tax_id = '123456789'), 'Ana', 'Jovanovic', 'ana.jovanovic@client.rs', '+38160234567'),
((SELECT companies_id FROM companies WHERE tax_id = '123456789'), 'Nikola', 'Nikolic', 'nikola.nikolic@partner.rs', '+38160345678');

-- Sample CRM Leads
INSERT INTO crm_leads (companies_id, lead_name, expected_revenue, currency_code, status) VALUES
((SELECT companies_id FROM companies WHERE tax_id = '123456789'), 'Tech Startup Project', 50000.00, 'RSD', 'qualified'),
((SELECT companies_id FROM companies WHERE tax_id = '123456789'), 'Manufacturing Contract', 150000.00, 'RSD', 'proposal'),
((SELECT companies_id FROM companies WHERE tax_id = '123456789'), 'Consulting Services', 75000.00, 'RSD', 'negotiation');

-- Sample CRM Opportunities
INSERT INTO crm_opportunities (companies_id, opportunity_name, expected_revenue, currency_code, status) VALUES
((SELECT companies_id FROM companies WHERE tax_id = '123456789'), 'Digital Transformation Project', 250000.00, 'RSD', 'closed_won'),
((SELECT companies_id FROM companies WHERE tax_id = '123456789'), 'ERP Implementation', 180000.00, 'RSD', 'in_progress'),
((SELECT companies_id FROM companies WHERE tax_id = '123456789'), 'Mobile App Development', 90000.00, 'RSD', 'on_hold');

-- Sample Inventory
INSERT INTO inventory (companies_id, item_name, sku, unit_price, currency_code, quantity_on_hand, description) VALUES
((SELECT companies_id FROM companies WHERE tax_id = '123456789'), 'Office Chair', 'CHR-001', 15000.00, 'RSD', 25, 'Ergonomic office chair with lumbar support'),
((SELECT companies_id FROM companies WHERE tax_id = '123456789'), 'Laptop Dell Inspiron', 'LTP-002', 85000.00, 'RSD', 15, 'Business laptop with 16GB RAM'),
((SELECT companies_id FROM companies WHERE tax_id = '123456789'), 'A4 Paper', 'PPR-003', 500.00, 'RSD', 200, 'Standard office paper, 80gsm'),
((SELECT companies_id FROM companies WHERE tax_id = '123456789'), 'Coffee Machine', 'COF-004', 25000.00, 'RSD', 5, 'Automatic coffee machine for office');

-- Sample Financial Transactions
INSERT INTO general_ledger (companies_id, transaction_date, description, is_posted) VALUES
((SELECT companies_id FROM companies WHERE tax_id = '123456789'), '2024-01-15', 'Initial setup transaction', TRUE),
((SELECT companies_id FROM companies WHERE tax_id = '123456789'), '2024-01-16', 'Office supplies purchase', TRUE),
((SELECT companies_id FROM companies WHERE tax_id = '123456789'), '2024-01-17', 'Service revenue', TRUE);

-- Sample General Ledger Entries
INSERT INTO general_ledger_entries (transaction_id, account_id, description, debit_amount, credit_amount) VALUES
((SELECT general_ledger_id FROM general_ledger WHERE description = 'Initial setup transaction' LIMIT 1), (SELECT chart_of_accounts_id FROM chart_of_accounts WHERE account_code = '1000' LIMIT 1), 'Cash deposit', 100000.00, 0),
((SELECT general_ledger_id FROM general_ledger WHERE description = 'Initial setup transaction' LIMIT 1), (SELECT chart_of_accounts_id FROM chart_of_accounts WHERE account_code = '3000' LIMIT 1), 'Common stock', 0, 100000.00),
((SELECT general_ledger_id FROM general_ledger WHERE description = 'Office supplies purchase' LIMIT 1), (SELECT chart_of_accounts_id FROM chart_of_accounts WHERE account_code = '6000' LIMIT 1), 'Office supplies', 15000.00, 0),
((SELECT general_ledger_id FROM general_ledger WHERE description = 'Office supplies purchase' LIMIT 1), (SELECT chart_of_accounts_id FROM chart_of_accounts WHERE account_code = '2000' LIMIT 1), 'Accounts payable', 0, 15000.00),
((SELECT general_ledger_id FROM general_ledger WHERE description = 'Service revenue' LIMIT 1), (SELECT chart_of_accounts_id FROM chart_of_accounts WHERE account_code = '1100' LIMIT 1), 'Service revenue', 50000.00, 0),
((SELECT general_ledger_id FROM general_ledger WHERE description = 'Service revenue' LIMIT 1), (SELECT chart_of_accounts_id FROM chart_of_accounts WHERE account_code = '4000' LIMIT 1), 'Sales revenue', 0, 50000.00);

-- Sample Invoices
INSERT INTO invoices (companies_id, invoice_number, invoice_date, due_date, total_amount, currency_code, status) VALUES
((SELECT companies_id FROM companies WHERE tax_id = '123456789'), 'INV-2024-001', '2024-01-15', '2024-02-14', 50000.00, 'RSD', 'sent'),
((SELECT companies_id FROM companies WHERE tax_id = '123456789'), 'INV-2024-002', '2024-01-16', '2024-02-15', 15000.00, 'RSD', 'paid'),
((SELECT companies_id FROM companies WHERE tax_id = '123456789'), 'INV-2024-003', '2024-01-17', '2024-02-16', 75000.00, 'RSD', 'draft');

-- Sample Invoice Items
INSERT INTO invoice_items (invoices_id, item_name, quantity, unit_price, total_price, description) VALUES
((SELECT invoices_id FROM invoices WHERE invoice_number = 'INV-2024-001' LIMIT 1), 'Software Development Services', 50.0, 1000.00, 50000.00, 'Custom software development for Q1 2024'),
((SELECT invoices_id FROM invoices WHERE invoice_number = 'INV-2024-002' LIMIT 1), 'Office Supplies', 10.0, 1500.00, 15000.00, 'Monthly office supplies'),
((SELECT invoices_id FROM invoices WHERE invoice_number = 'INV-2024-003' LIMIT 1), 'Consulting Services', 30.0, 2500.00, 75000.00, 'Business consulting for Q1 2024');

-- Sample Bank Accounts
INSERT INTO bank_accounts (companies_id, bank_name, account_number, currency_code, description) VALUES
((SELECT companies_id FROM companies WHERE tax_id = '123456789'), 'Banca Intesa', '1701234567890', 'RSD', 'Primary business account'),
((SELECT companies_id FROM companies WHERE tax_id = '123456789'), 'Raiffeisen Bank', '2659876543210', 'EUR', 'Euro account for international payments');

-- Sample Bank Statements
INSERT INTO bank_statements (companies_id, bank_accounts_id, statement_date, transaction_date, amount, currency_code, description) VALUES
((SELECT companies_id FROM companies WHERE tax_id = '123456789'), (SELECT bank_accounts_id FROM bank_accounts WHERE bank_name = 'Banca Intesa' LIMIT 1), '2024-01-31', '2024-01-15', 100000.00, 'RSD', 'Initial capital deposit'),
((SELECT companies_id FROM companies WHERE tax_id = '123456789'), (SELECT bank_accounts_id FROM bank_accounts WHERE bank_name = 'Banca Intesa' LIMIT 1), '2024-01-31', '2024-01-16', -15000.00, 'RSD', 'Office supplies payment'),
((SELECT companies_id FROM companies WHERE tax_id = '123456789'), (SELECT bank_accounts_id FROM bank_accounts WHERE bank_name = 'Banca Intesa' LIMIT 1), '2024-01-31', '2024-01-17', 50000.00, 'RSD', 'Service revenue payment');

-- Sample LLM Embeddings for AI Features
INSERT INTO llm_embeddings (entity_type, entity_id, embedding_vector, context_text, companies_id) VALUES
('companies', (SELECT companies_id FROM companies WHERE tax_id = '123456789'), '[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 0.11, 0.12, 0.13, 0.14, 0.15, 0.16, 0.17, 0.18, 0.19, 0.20, 0.21, 0.22, 0.23, 0.24, 0.25, 0.26, 0.27, 0.28, 0.29, 0.30, 0.31, 0.32, 0.33, 0.34, 0.35, 0.36, 0.37, 0.38, 0.39, 0.40, 0.41, 0.42, 0.43, 0.44, 0.45, 0.46, 0.47, 0.48, 0.49, 0.50, 0.51, 0.52, 0.53, 0.54, 0.55, 0.56, 0.57, 0.58, 0.59, 0.60, 0.61, 0.62, 0.63, 0.64, 0.65, 0.66, 0.67, 0.68, 0.69, 0.70, 0.71, 0.72, 0.73, 0.74, 0.75, 0.76, 0.77, 0.78, 0.79, 0.80, 0.81, 0.82, 0.83, 0.84, 0.85, 0.86, 0.87, 0.88, 0.89, 0.90, 0.91, 0.92, 0.93, 0.94, 0.95, 0.96, 0.97, 0.98, 0.99, 1.00, 0.101, 0.102, 0.103, 0.104, 0.105, 0.106, 0.107, 0.108, 0.109, 0.110, 0.111, 0.112, 0.113, 0.114, 0.115, 0.116, 0.117, 0.118, 0.119, 0.120, 0.121, 0.122, 0.123, 0.124, 0.125, 0.126, 0.127, 0.128, 0.129, 0.130, 0.131, 0.132, 0.133, 0.134, 0.135, 0.136, 0.137, 0.138, 0.139, 0.140, 0.141, 0.142, 0.143, 0.144, 0.145, 0.146, 0.147, 0.148, 0.149, 0.150, 0.151, 0.152, 0.153, 0.154, 0.155, 0.156, 0.157, 0.158, 0.159, 0.160, 0.161, 0.162, 0.163, 0.164, 0.165, 0.166, 0.167, 0.168, 0.169, 0.170, 0.171, 0.172, 0.173, 0.174, 0.175, 0.176, 0.177, 0.178, 0.179, 0.180, 0.181, 0.182, 0.183, 0.184, 0.185, 0.186, 0.187, 0.188, 0.189, 0.190, 0.191, 0.192, 0.193, 0.194, 0.195, 0.196, 0.197, 0.198, 0.199, 0.200]', 'ValidoAI Technologies - AI-powered financial analysis and automation platform specializing in business intelligence and process optimization', (SELECT companies_id FROM companies WHERE tax_id = '123456789')),
('users', (SELECT users_id FROM users WHERE username = 'admin'), '[0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 0.1, 0.21, 0.22, 0.23, 0.24, 0.25, 0.26, 0.27, 0.28, 0.29, 0.30, 0.31, 0.32, 0.33, 0.34, 0.35, 0.36, 0.37, 0.38, 0.39, 0.40, 0.41, 0.42, 0.43, 0.44, 0.45, 0.46, 0.47, 0.48, 0.49, 0.50, 0.51, 0.52, 0.53, 0.54, 0.55, 0.56, 0.57, 0.58, 0.59, 0.60, 0.61, 0.62, 0.63, 0.64, 0.65, 0.66, 0.67, 0.68, 0.69, 0.70, 0.71, 0.72, 0.73, 0.74, 0.75, 0.76, 0.77, 0.78, 0.79, 0.80, 0.81, 0.82, 0.83, 0.84, 0.85, 0.86, 0.87, 0.88, 0.89, 0.90, 0.91, 0.92, 0.93, 0.94, 0.95, 0.96, 0.97, 0.98, 0.99, 1.00, 0.101, 0.102, 0.103, 0.104, 0.105, 0.106, 0.107, 0.108, 0.109, 0.110, 0.111, 0.112, 0.113, 0.114, 0.115, 0.116, 0.117, 0.118, 0.119, 0.120, 0.121, 0.122, 0.123, 0.124, 0.125, 0.126, 0.127, 0.128, 0.129, 0.130, 0.131, 0.132, 0.133, 0.134, 0.135, 0.136, 0.137, 0.138, 0.139, 0.140, 0.141, 0.142, 0.143, 0.144, 0.145, 0.146, 0.147, 0.148, 0.149, 0.150, 0.151, 0.152, 0.153, 0.154, 0.155, 0.156, 0.157, 0.158, 0.159, 0.160, 0.161, 0.162, 0.163, 0.164, 0.165, 0.166, 0.167, 0.168, 0.169, 0.170, 0.171, 0.172, 0.173, 0.174, 0.175, 0.176, 0.177, 0.178, 0.179, 0.180, 0.181, 0.182, 0.183, 0.184, 0.185, 0.186, 0.187, 0.188, 0.189, 0.190, 0.191, 0.192, 0.193, 0.194, 0.195, 0.196, 0.197, 0.198, 0.199, 0.200]', 'System Administrator - Full system access with all permissions and administrative capabilities', (SELECT companies_id FROM companies WHERE tax_id = '123456789')),
('tickets', (SELECT tickets_id FROM tickets LIMIT 1), '[0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 0.1, 0.2, 0.31, 0.32, 0.33, 0.34, 0.35, 0.36, 0.37, 0.38, 0.39, 0.40, 0.41, 0.42, 0.43, 0.44, 0.45, 0.46, 0.47, 0.48, 0.49, 0.50, 0.51, 0.52, 0.53, 0.54, 0.55, 0.56, 0.57, 0.58, 0.59, 0.60, 0.61, 0.62, 0.63, 0.64, 0.65, 0.66, 0.67, 0.68, 0.69, 0.70, 0.71, 0.72, 0.73, 0.74, 0.75, 0.76, 0.77, 0.78, 0.79, 0.80, 0.81, 0.82, 0.83, 0.84, 0.85, 0.86, 0.87, 0.88, 0.89, 0.90, 0.91, 0.92, 0.93, 0.94, 0.95, 0.96, 0.97, 0.98, 0.99, 1.00, 0.101, 0.102, 0.103, 0.104, 0.105, 0.106, 0.107, 0.108, 0.109, 0.110, 0.111, 0.112, 0.113, 0.114, 0.115, 0.116, 0.117, 0.118, 0.119, 0.120, 0.121, 0.122, 0.123, 0.124, 0.125, 0.126, 0.127, 0.128, 0.129, 0.130, 0.131, 0.132, 0.133, 0.134, 0.135, 0.136, 0.137, 0.138, 0.139, 0.140, 0.141, 0.142, 0.143, 0.144, 0.145, 0.146, 0.147, 0.148, 0.149, 0.150, 0.151, 0.152, 0.153, 0.154, 0.155, 0.156, 0.157, 0.158, 0.159, 0.160, 0.161, 0.162, 0.163, 0.164, 0.165, 0.166, 0.167, 0.168, 0.169, 0.170, 0.171, 0.172, 0.173, 0.174, 0.175, 0.176, 0.177, 0.178, 0.179, 0.180, 0.181, 0.182, 0.183, 0.184, 0.185, 0.186, 0.187, 0.188, 0.189, 0.190, 0.191, 0.192, 0.193, 0.194, 0.195, 0.196, 0.197, 0.198, 0.199, 0.200]', 'Invoice Processing Issue - Unable to process invoice #12345 due to system error', (SELECT companies_id FROM companies WHERE tax_id = '123456789'));

-- Create default AI model configurations
INSERT INTO local_models_config (model_name, model_type, model_path, max_tokens, temperature, context_window, gpu_required, description) VALUES
('qwen-3', 'text', 'local_llm_models/qwen-3.gguf', 4096, 0.7, 8192, FALSE, 'General purpose AI assistant with strong reasoning capabilities'),
('phi-3', 'text', 'local_llm_models/phi-3.gguf', 2048, 0.6, 4096, FALSE, 'Lightweight instruction model optimized for efficiency'),
('mistral-7b', 'text', 'local_llm_models/mistral-7b.gguf', 8192, 0.8, 16384, TRUE, 'Advanced reasoning model with strong analytical capabilities'),
('whisper-base', 'audio', 'models/whisper-base', 448, 0.0, 1500, FALSE, 'Speech to text transcription model'),
('whisper-large', 'audio', 'models/whisper-large-v3', 448, 0.0, 1500, TRUE, 'High accuracy speech recognition model');

-- Create external API configurations
INSERT INTO external_api_config (provider_name, api_endpoint, api_key_required, models_supported, rate_limit_per_minute, description) VALUES
('OpenAI', 'https://api.openai.com/v1', TRUE, '["gpt-4", "gpt-3.5-turbo", "gpt-4-turbo"]', 1000, 'OpenAI GPT models for advanced text generation and analysis'),
('Anthropic', 'https://api.anthropic.com/v1', TRUE, '["claude-3-opus", "claude-3-sonnet", "claude-3-haiku"]', 50, 'Anthropic Claude models with strong safety and reasoning'),
('Google', 'https://generativelanguage.googleapis.com/v1', TRUE, '["gemini-pro", "gemini-pro-vision"]', 60, 'Google Gemini models for multimodal AI tasks'),
('Cohere', 'https://api.cohere.ai/v1', TRUE, '["command", "command-light", "command-xlarge"]', 100, 'Cohere models specialized in business and enterprise use cases');

-- Create default report templates
INSERT INTO report_templates (template_name, template_type, description, parameters_schema, output_format, is_system_template) VALUES
('Monthly Financial Report', 'financial', 'Comprehensive monthly financial performance report with charts and KPIs', '{"period": "string", "include_charts": "boolean", "currency": "string"}', 'pdf', TRUE),
('Payroll Summary Report', 'hr', 'Monthly payroll summary with salary breakdowns and tax calculations', '{"month": "integer", "year": "integer", "department_filter": "string"}', 'excel', TRUE),
('Ticket SLA Report', 'support', 'Customer support ticket analysis with SLA compliance metrics', '{"period_start": "date", "period_end": "date", "department": "string"}', 'pdf', TRUE),
('AI Insights Summary', 'ai', 'Summary of AI-generated insights and recommendations', '{"insight_type": "string", "min_confidence": "number", "period_days": "integer"}', 'html', TRUE),
('Inventory Status Report', 'inventory', 'Current inventory levels with reorder alerts and valuation', '{"warehouse_filter": "string", "category_filter": "string", "show_valuation": "boolean"}', 'excel', TRUE);

-- Create default notification templates
INSERT INTO notification_templates (template_name, template_type, subject_template, body_template, variables, is_active) VALUES
('Invoice Due Reminder', 'email', 'Invoice {{invoice_number}} Due Soon', 'Dear Customer,\n\nYour invoice {{invoice_number}} for {{amount}} {{currency}} is due on {{due_date}}.\n\nPlease arrange payment to avoid late fees.\n\nBest regards,\n{{company_name}}', '["invoice_number", "amount", "currency", "due_date", "company_name"]', TRUE),
('Password Reset', 'email', 'Password Reset Request', 'Hello {{first_name}},\n\nYou have requested to reset your password. Click the link below to set a new password:\n\n{{reset_link}}\n\nThis link will expire in 24 hours.\n\nIf you did not request this reset, please ignore this email.\n\nBest regards,\n{{company_name}}', '["first_name", "reset_link", "company_name"]', TRUE),
('Payroll Processed', 'email', 'Payroll Processed - {{period}}', 'Dear {{first_name}},\n\nYour payroll for {{period}} has been processed successfully.\n\nGross Amount: {{gross_amount}} {{currency}}\nNet Amount: {{net_amount}} {{currency}}\n\nYou can download your payslip from the employee portal.\n\nBest regards,\nHR Department', '["first_name", "period", "gross_amount", "net_amount", "currency"]', TRUE),
('Ticket Update', 'email', 'Ticket Update: {{ticket_number}}', 'Hello,\n\nYour ticket {{ticket_number}} has been updated.\n\nStatus: {{status}}\nPriority: {{priority}}\n\n{{message}}\n\nBest regards,\nSupport Team', '["ticket_number", "status", "priority", "message"]', TRUE);

-- Create sample SLA policies
INSERT INTO sla_policies (policy_name, description, response_time_minutes, resolution_time_hours, business_hours_only, escalation_levels, is_active) VALUES
('Standard Support', 'Standard customer support SLA for general inquiries', 240, 24, TRUE, '[{"level": 1, "time": "4 hours", "action": "Escalate to senior support"}, {"level": 2, "time": "12 hours", "action": "Escalate to manager"}]', TRUE),
('Premium Support', 'Premium SLA with faster response times', 60, 8, TRUE, '[{"level": 1, "time": "2 hours", "action": "Escalate to senior support"}, {"level": 2, "time": "4 hours", "action": "Escalate to manager"}]', TRUE),
('Critical Support', 'Critical issues requiring immediate attention', 30, 4, FALSE, '[{"level": 1, "time": "1 hour", "action": "Escalate to senior support"}, {"level": 2, "time": "2 hours", "action": "Escalate to director"}]', TRUE),
('Financial Issues', 'SLA for financial and billing related issues', 120, 12, TRUE, '[{"level": 1, "time": "2 hours", "action": "Escalate to finance team"}, {"level": 2, "time": "6 hours", "action": "Escalate to finance manager"}]', TRUE);

-- Create default workflow templates
INSERT INTO workflow_templates (template_name, description, steps, triggers, is_active) VALUES
('Invoice Approval', 'Multi-step invoice approval workflow', '[{"step": 1, "name": "Manager Review", "approvers": ["manager"], "condition": "amount > 50000"}, {"step": 2, "name": "Finance Review", "approvers": ["finance_team"], "condition": "amount > 100000"}, {"step": 3, "name": "CEO Approval", "approvers": ["ceo"], "condition": "amount > 500000"}]', '["invoice_created", "invoice_updated"]', TRUE),
('Employee Onboarding', 'Automated employee onboarding process', '[{"step": 1, "name": "HR Documentation", "action": "send_hr_forms"}, {"step": 2, "name": "IT Setup", "action": "create_accounts"}, {"step": 3, "name": "Manager Introduction", "action": "schedule_meeting"}, {"step": 4, "name": "Training", "action": "enroll_training"}]', '["employee_hired"]', TRUE),
('Ticket Escalation', 'Automatic ticket escalation based on SLA', '[{"step": 1, "name": "First Escalation", "condition": "sla_breach_warning", "action": "notify_manager"}, {"step": 2, "name": "Second Escalation", "condition": "sla_breached", "action": "notify_director"}, {"step": 3, "name": "Final Escalation", "condition": "critical_breach", "action": "create_incident"}]', '["sla_warning", "sla_breach"]', TRUE);

-- Create sample API integrations
INSERT INTO api_integrations (integration_name, provider, api_endpoint, auth_type, credentials, is_active, last_sync) VALUES
('Stripe Payments', 'Stripe', 'https://api.stripe.com/v1', 'bearer', '{"api_key": "encrypted_key"}', TRUE, CURRENT_TIMESTAMP),
('QuickBooks', 'Intuit', 'https://quickbooks.api.intuit.com/v3', 'oauth2', '{"client_id": "client_id", "client_secret": "secret", "refresh_token": "token"}', TRUE, CURRENT_TIMESTAMP),
('Mailchimp', 'Mailchimp', 'https://usX.api.mailchimp.com/3.0', 'apikey', '{"api_key": "encrypted_key"}', TRUE, CURRENT_TIMESTAMP),
('Slack', 'Slack', 'https://slack.com/api', 'oauth2', '{"bot_token": "encrypted_token"}', TRUE, CURRENT_TIMESTAMP),
('Microsoft 365', 'Microsoft', 'https://graph.microsoft.com/v1.0', 'oauth2', '{"tenant_id": "tenant", "client_id": "client", "client_secret": "secret"}', TRUE, CURRENT_TIMESTAMP);

-- ============================================================================
-- MULTI-COMPANY SAMPLE DATA
-- ============================================================================

-- Additional Companies for Multi-Company Testing
INSERT INTO companies (company_name, legal_name, tax_id, registration_number, address_line1, city, postal_code, countries_id, country, phone, email, website, industry, company_size, description, embedding_vector) VALUES
('Global Finance GmbH', 'Global Finance GmbH', 'DE123456789', 'HRB123456', 'Friedrichstraße 123', 'Berlin', '10117', (SELECT countries_id FROM countries WHERE iso_code = 'DE'), 'Germany', '+49301234567', 'contact@globalfinance.de', 'https://globalfinance.de', 'Financial Services', '201-500 employees', 'International financial services with focus on cross-border transactions and compliance', '[0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 0.1, 0.2, 0.3, 0.41, 0.42, 0.43, 0.44, 0.45, 0.46]'),
('TechStart Inc', 'TechStart Inc', 'US123456789', 'REG123456', 'Silicon Valley Blvd 456', 'San Francisco', '94105', (SELECT countries_id FROM countries WHERE iso_code = 'US'), 'United States', '+16501234567', 'hello@techstart.com', 'https://techstart.com', 'Technology', '11-50 employees', 'Innovative startup specializing in AI and machine learning solutions for enterprise clients', '[0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 0.1, 0.2, 0.3, 0.4, 0.51, 0.52, 0.53, 0.54, 0.55, 0.56]');

-- Additional Users for Multi-Company Testing
INSERT INTO users (username, email, password_hash, first_name, last_name, phone, is_verified, embedding_vector) VALUES
('john.doe', 'john.doe@validoai.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LeCtj1rE1rTjY1F2', 'John', 'Doe', '+38160123456', TRUE, '[0.6, 0.7, 0.8, 0.9, 1.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.61, 0.62, 0.63, 0.64, 0.65, 0.66]'),
('jane.smith', 'jane.smith@techcorp.rs', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LeCtj1rE1rTjY1F2', 'Jane', 'Smith', '+38160234567', TRUE, '[0.7, 0.8, 0.9, 1.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.71, 0.72, 0.73, 0.74, 0.75, 0.76]'),
('mike.johnson', 'mike.johnson@globalfinance.de', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LeCtj1rE1rTjY1F2', 'Mike', 'Johnson', '+49301234567', TRUE, '[0.8, 0.9, 1.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.81, 0.82, 0.83, 0.84, 0.85, 0.86]');

-- User-Company Access Relationships (Multi-Company Support)
INSERT INTO user_company_access (user_id, company_id, access_level, role_type, department, job_title, can_switch_to_company, can_manage_company, can_invite_users, can_access_financial_data, status) VALUES
-- John Doe - Access to multiple companies
((SELECT users_id FROM users WHERE username = 'john.doe'), (SELECT companies_id FROM companies WHERE tax_id = '123456789'), 'admin', 'employee', 'IT', 'Senior Developer', TRUE, TRUE, TRUE, TRUE, 'active'),
((SELECT users_id FROM users WHERE username = 'john.doe'), (SELECT companies_id FROM companies WHERE tax_id = '987654321'), 'employee', 'contractor', 'Development', 'Consultant', TRUE, FALSE, FALSE, FALSE, 'active'),
((SELECT users_id FROM users WHERE username = 'john.doe'), (SELECT companies_id FROM companies WHERE tax_id = 'DE123456789'), 'external', 'consultant', 'Advisory', 'Technical Consultant', TRUE, FALSE, FALSE, FALSE, 'active'),

-- Jane Smith - Access to TechCorp and Global Finance
((SELECT users_id FROM users WHERE username = 'jane.smith'), (SELECT companies_id FROM companies WHERE tax_id = '987654321'), 'admin', 'employee', 'Management', 'Project Manager', TRUE, TRUE, TRUE, TRUE, 'active'),
((SELECT users_id FROM users WHERE username = 'jane.smith'), (SELECT companies_id FROM companies WHERE tax_id = 'DE123456789'), 'manager', 'employee', 'Operations', 'Operations Manager', TRUE, FALSE, TRUE, TRUE, 'active'),

-- Mike Johnson - German company owner
((SELECT users_id FROM users WHERE username = 'mike.johnson'), (SELECT companies_id FROM companies WHERE tax_id = 'DE123456789'), 'owner', 'employee', 'Executive', 'CEO', TRUE, TRUE, TRUE, TRUE, 'active'),
((SELECT users_id FROM users WHERE username = 'mike.johnson'), (SELECT companies_id FROM companies WHERE tax_id = '123456789'), 'external', 'partner', 'Partnership', 'Strategic Partner', TRUE, FALSE, FALSE, FALSE, 'active');

-- Company Departments
INSERT INTO company_departments (company_id, department_name, department_code, description, budget_allocated) VALUES
((SELECT companies_id FROM companies WHERE tax_id = '123456789'), 'Information Technology', 'IT', 'Core technology and development department', 5000000.00),
((SELECT companies_id FROM companies WHERE tax_id = '123456789'), 'Human Resources', 'HR', 'Employee management and development', 2000000.00),
((SELECT companies_id FROM companies WHERE tax_id = '123456789'), 'Finance & Accounting', 'FIN', 'Financial management and accounting', 3000000.00),
((SELECT companies_id FROM companies WHERE tax_id = '123456789'), 'Sales & Marketing', 'SALES', 'Sales and marketing operations', 4000000.00),
((SELECT companies_id FROM companies WHERE tax_id = '987654321'), 'Software Development', 'DEV', 'Software development and engineering', 8000000.00),
((SELECT companies_id FROM companies WHERE tax_id = '987654321'), 'Quality Assurance', 'QA', 'Testing and quality assurance', 2000000.00),
((SELECT companies_id FROM companies WHERE tax_id = 'DE123456789'), 'International Finance', 'INT_FIN', 'International financial operations', 10000000.00),
((SELECT companies_id FROM companies WHERE tax_id = 'DE123456789'), 'Compliance', 'COMP', 'Regulatory compliance and risk management', 3000000.00);

-- User Department Assignments
INSERT INTO user_department_assignments (user_id, company_id, department_id, assignment_type, start_date) VALUES
((SELECT users_id FROM users WHERE username = 'admin'), (SELECT companies_id FROM companies WHERE tax_id = '123456789'), (SELECT company_department_id FROM company_departments WHERE department_name = 'Information Technology' AND company_id = (SELECT companies_id FROM companies WHERE tax_id = '123456789')), 'primary', CURRENT_DATE),
((SELECT users_id FROM users WHERE username = 'manager'), (SELECT companies_id FROM companies WHERE tax_id = '123456789'), (SELECT company_department_id FROM company_departments WHERE department_name = 'Human Resources' AND company_id = (SELECT companies_id FROM companies WHERE tax_id = '123456789')), 'primary', CURRENT_DATE),
((SELECT users_id FROM users WHERE username = 'john.doe'), (SELECT companies_id FROM companies WHERE tax_id = '123456789'), (SELECT company_department_id FROM company_departments WHERE department_name = 'Information Technology' AND company_id = (SELECT companies_id FROM companies WHERE tax_id = '123456789')), 'primary', CURRENT_DATE),
((SELECT users_id FROM users WHERE username = 'jane.smith'), (SELECT companies_id FROM companies WHERE tax_id = '987654321'), (SELECT company_department_id FROM company_departments WHERE department_name = 'Software Development' AND company_id = (SELECT companies_id FROM companies WHERE tax_id = '987654321')), 'primary', CURRENT_DATE);

-- Company Invitations (Sample)
INSERT INTO company_invitations (company_id, invited_email, invited_name, invited_by, invitation_token, access_level, role_type, department, job_title, custom_message) VALUES
((SELECT companies_id FROM companies WHERE tax_id = '123456789'), 'newhire@validoai.com', 'New Employee', (SELECT users_id FROM users WHERE username = 'admin'), 'inv_123456789', 'employee', 'employee', 'Information Technology', 'Junior Developer', 'Welcome to ValidoAI! Please accept this invitation to join our team.'),
((SELECT companies_id FROM companies WHERE tax_id = '987654321'), 'consultant@techcorp.rs', 'External Consultant', (SELECT users_id FROM users WHERE username = 'jane.smith'), 'inv_987654321', 'external', 'contractor', 'Software Development', 'Technical Consultant', 'We would like to invite you to work with us on our upcoming project.'),
((SELECT companies_id FROM companies WHERE tax_id = 'DE123456789'), 'partner@globalfinance.de', 'Strategic Partner', (SELECT users_id FROM users WHERE username = 'mike.johnson'), 'inv_456789123', 'external', 'partner', 'Partnership', 'Business Partner', 'Let''s collaborate on international financial opportunities.');

-- User Company Preferences
INSERT INTO user_company_preferences (user_id, company_id, preference_key, preference_value, preference_type) VALUES
((SELECT users_id FROM users WHERE username = 'john.doe'), (SELECT companies_id FROM companies WHERE tax_id = '123456789'), 'dashboard_layout', '{"widgets": ["financial", "tasks", "notifications"]}', 'json'),
((SELECT users_id FROM users WHERE username = 'john.doe'), (SELECT companies_id FROM companies WHERE tax_id = '123456789'), 'theme_preference', 'dark', 'string'),
((SELECT users_id FROM users WHERE username = 'jane.smith'), (SELECT companies_id FROM companies WHERE tax_id = '987654321'), 'notification_frequency', 'daily', 'string'),
((SELECT users_id FROM users WHERE username = 'mike.johnson'), (SELECT companies_id FROM companies WHERE tax_id = 'DE123456789'), 'language', 'de', 'string');

-- Sample Company Switching Audit
INSERT INTO company_switch_audit (user_id, from_company_id, to_company_id, switch_reason, switch_method, ip_address) VALUES
((SELECT users_id FROM users WHERE username = 'john.doe'), (SELECT companies_id FROM companies WHERE tax_id = '123456789'), (SELECT companies_id FROM companies WHERE tax_id = '987654321'), 'project_work', 'ui', '192.168.1.100'),
((SELECT users_id FROM users WHERE username = 'jane.smith'), (SELECT companies_id FROM companies WHERE tax_id = '987654321'), (SELECT companies_id FROM companies WHERE tax_id = 'DE123456789'), 'client_meeting', 'manual', '10.0.0.50');

-- Sample User Company Sessions
INSERT INTO user_company_sessions (user_id, company_id, session_id, ip_address, device_info) VALUES
((SELECT users_id FROM users WHERE username = 'john.doe'), (SELECT companies_id FROM companies WHERE tax_id = '123456789'), 'session_123', '192.168.1.100', '{"browser": "Chrome", "os": "Windows", "device": "Desktop"}'),
((SELECT users_id FROM users WHERE username = 'jane.smith'), (SELECT companies_id FROM companies WHERE tax_id = '987654321'), 'session_456', '10.0.0.50', '{"browser": "Safari", "os": "macOS", "device": "Laptop"}'),
((SELECT users_id FROM users WHERE username = 'mike.johnson'), (SELECT companies_id FROM companies WHERE tax_id = 'DE123456789'), 'session_789', '172.16.0.25', '{"browser": "Firefox", "os": "Linux", "device": "Desktop"}');

-- Create comprehensive data with all relationships
-- This ensures the database has realistic interconnected data for testing
