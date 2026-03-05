-- AI Valido Online Sample Data
-- Date: August 17, 2025, 11:55 PM CEST
-- Provides sample data for reports, LLM embeddings, and testing

INSERT INTO roles (roles_id, role_name, description) VALUES
    (gen_random_uuid(), 'developer', 'Full system access'),
    (gen_random_uuid(), 'admin', 'Full CRUD with read-only company switching'),
    (gen_random_uuid(), 'accountant', 'Financial module access'),
    (gen_random_uuid(), 'manager', 'CRM and inventory management'),
    (gen_random_uuid(), 'hr', 'Limited HR module access'),
    (gen_random_uuid(), 'support', 'Log and ticket management'),
    (gen_random_uuid(), 'demo', 'View/test without saving');

INSERT INTO companies (companies_id, company_name, tax_id, registration_number, address, city, country) VALUES
    (gen_random_uuid(), 'Tech DOO', '123456789', '987654321', 'Bulevar 1', 'Belgrade', 'Serbia'),
    (gen_random_uuid(), 'Ivan Preduzetnik', '987654321', '123456789', 'Knez Mihailova 10', 'Belgrade', 'Serbia'),
    (gen_random_uuid(), 'Manu AD', '456789123', '789123456', 'Ulica 5', 'Novi Sad', 'Serbia');

INSERT INTO fiscal_years (companies_id, year, start_date, end_date, status) VALUES
    ((SELECT companies_id FROM companies WHERE company_name = 'Tech DOO'), 2024, '2024-01-01', '2024-12-31', 'closed'),
    ((SELECT companies_id FROM companies WHERE company_name = 'Tech DOO'), 2025, '2025-01-01', '2025-12-31', 'open'),
    ((SELECT companies_id FROM companies WHERE company_name = 'Ivan Preduzetnik'), 2025, '2025-01-01', '2025-12-31', 'open');

INSERT INTO users (users_id, companies_id, roles_id, username, email, password_hash, first_name, last_name) VALUES
    (gen_random_uuid(), (SELECT companies_id FROM companies WHERE company_name = 'Tech DOO'), (SELECT roles_id FROM roles WHERE role_name = 'developer'), 'dev1', 'dev1@tech.rs', crypt('password', gen_salt('bf')), 'Dejan', 'Dejić'),
    (gen_random_uuid(), (SELECT companies_id FROM companies WHERE company_name = 'Tech DOO'), (SELECT roles_id FROM roles WHERE role_name = 'admin'), 'admin1', 'admin1@tech.rs', crypt('password', gen_salt('bf')), 'Ana', 'Anić'),
    (gen_random_uuid(), (SELECT companies_id FROM companies WHERE company_name = 'Tech DOO'), (SELECT roles_id FROM roles WHERE role_name = 'accountant'), 'acc1', 'acc1@tech.rs', crypt('password', gen_salt('bf')), 'Marko', 'Marković'),
    (gen_random_uuid(), (SELECT companies_id FROM companies WHERE company_name = 'Tech DOO'), (SELECT roles_id FROM roles WHERE role_name = 'manager'), 'mgr1', 'mgr1@tech.rs', crypt('password', gen_salt('bf')), 'Jelena', 'Jelenić'),
    (gen_random_uuid(), (SELECT companies_id FROM companies WHERE company_name = 'Tech DOO'), (SELECT roles_id FROM roles WHERE role_name = 'hr'), 'hr1', 'hr1@tech.rs', crypt('password', gen_salt('bf')), 'Ivana', 'Ivanić'),
    (gen_random_uuid(), (SELECT companies_id FROM companies WHERE company_name = 'Tech DOO'), (SELECT roles_id FROM roles WHERE role_name = 'support'), 'sup1', 'sup1@tech.rs', crypt('password', gen_salt('bf')), 'Nikola', 'Nikolić'),
    (gen_random_uuid(), (SELECT companies_id FROM companies WHERE company_name = 'Tech DOO'), (SELECT roles_id FROM roles WHERE role_name = 'demo'), 'demo1', 'demo1@tech.rs', crypt('password', gen_salt('bf')), 'Demo', 'User');

INSERT INTO accounts_types (type_name) VALUES ('Asset'), ('Liability'), ('Revenue'), ('Expense');
INSERT INTO transactions_types (type_name) VALUES ('Purchase'), ('Sale'), ('Payment'), ('Receipt');
INSERT INTO taxes_types (type_name) VALUES ('PDV'), ('Corporate Tax');
INSERT INTO modules_names (name) VALUES ('Financial'), ('Inventory'), ('CRM'), ('Payroll'), ('Ticketing');
INSERT INTO invoices_statuses (status_name) VALUES ('Draft'), ('Sent'), ('Paid'), ('Overdue');
INSERT INTO tickets_statuses (status_name) VALUES ('open'), ('pending_l1'), ('pending_l2'), ('pending_l3'), ('pending_l4'), ('approved'), ('closed');
INSERT INTO leads_sources (source_name) VALUES ('Website'), ('Referral'), ('Social Media'), ('Cold Call');
INSERT INTO leads_stages (stage_name) VALUES ('Prospect'), ('Qualified'), ('Proposal'), ('Negotiation'), ('Closed Won'), ('Closed Lost');
INSERT INTO opportunities_stages (stage_name) VALUES ('Qualification'), ('Proposal'), ('Negotiation'), ('Closed Won'), ('Closed Lost');
INSERT INTO businesses_forms (form_name) VALUES ('DOO'), ('AD'), ('Preduzetnik'), ('OR');
INSERT INTO businesses_areas (area_name) VALUES ('Technology'), ('Finance'), ('Manufacturing'), ('Services');
INSERT INTO partners_types (type_name) VALUES ('Customer'), ('Supplier'), ('Partner'), ('Vendor');

INSERT INTO charts_of_accounts (companies_id, account_number, accounts_types_id, account_name, pdv_rate) VALUES
    ((SELECT companies_id FROM companies WHERE company_name = 'Tech DOO'), '1001', (SELECT accounts_types_id FROM accounts_types WHERE type_name = 'Asset'), 'Cash', 0.00),
    ((SELECT companies_id FROM companies WHERE company_name = 'Tech DOO'), '2001', (SELECT accounts_types_id FROM accounts_types WHERE type_name = 'Revenue'), 'Sales', 20.00);

INSERT INTO general_ledgers_transactions (companies_id, fiscal_years_id, transaction_date, charts_of_accounts_id, transactions_types_id, debit_amount, credit_amount, description) VALUES
    ((SELECT companies_id FROM companies WHERE company_name = 'Tech DOO'), (SELECT fiscal_years_id FROM fiscal_years WHERE year = 2025), '2025-01-15', (SELECT charts_of_accounts_id FROM charts_of_accounts WHERE account_number = '1001'), (SELECT transactions_types_id FROM transactions_types WHERE type_name = 'Receipt'), 10000.00, 0.00, 'Client payment'),
    ((SELECT companies_id FROM companies WHERE company_name = 'Tech DOO'), (SELECT fiscal_years_id FROM fiscal_years WHERE year = 2025), '2025-02-10', (SELECT charts_of_accounts_id FROM charts_of_accounts WHERE account_number = '2001'), (SELECT transactions_types_id FROM transactions_types WHERE type_name = 'Sale'), 0.00, 15000.00, 'Software sale');

INSERT INTO invoices_receivable (companies_id, fiscal_years_id, invoice_number, invoice_date, due_date, total_amount, invoices_statuses_id) VALUES
    ((SELECT companies_id FROM companies WHERE company_name = 'Tech DOO'), (SELECT fiscal_years_id FROM fiscal_years WHERE year = 2025), 'INV001', '2025-01-10', '2025-02-10', 12000.00, (SELECT invoices_statuses_id FROM invoices_statuses WHERE status_name = 'Sent')),
    ((SELECT companies_id FROM companies WHERE company_name = 'Tech DOO'), (SELECT fiscal_years_id FROM fiscal_years WHERE year = 2025), 'INV002', '2025-02-15', '2025-03-15', 18000.00, (SELECT invoices_statuses_id FROM invoices_statuses WHERE status_name = 'Overdue'));

INSERT INTO llm_embeddings (entity_type, entity_id, embedding_vector, context_text, companies_id) VALUES
    ('invoice', (SELECT invoices_receivable_id FROM invoices_receivable WHERE invoice_number = 'INV001'), '[0.1, 0.2, ..., 0.3]'::vector, 'Sale of software license, urgent payment required', (SELECT companies_id FROM companies WHERE company_name = 'Tech DOO')),
    ('invoice', (SELECT invoices_receivable_id FROM invoices_receivable WHERE invoice_number = 'INV002'), '[0.4, 0.5, ..., 0.6]'::vector, 'Consulting services, overdue payment', (SELECT companies_id FROM companies WHERE company_name = 'Tech DOO')),
    ('lead', (SELECT crm_leads_id FROM crm_leads WHERE lead_name = 'Project X'), '[0.7, 0.8, ..., 0.9]'::vector, 'Software project, high potential', (SELECT companies_id FROM companies WHERE company_name = 'Tech DOO'));

INSERT INTO crm_leads (companies_id, leads_sources_id, leads_stages_id, lead_name, expected_revenue) VALUES
    ((SELECT companies_id FROM companies WHERE company_name = 'Tech DOO'), (SELECT leads_sources_id FROM leads_sources WHERE source_name = 'Referral'), (SELECT leads_stages_id FROM leads_stages WHERE stage_name = 'Qualified'), 'Project X', 50000.00),
    ((SELECT companies_id FROM companies WHERE company_name = 'Tech DOO'), (SELECT leads_sources_id FROM leads_sources WHERE source_name = 'Website'), (SELECT leads_stages_id FROM leads_stages WHERE stage_name = 'Prospect'), 'Project Y', 30000.00);

INSERT INTO routes_permissions (roles_id, route_path, methods, allowed_columns, allow_access) VALUES
    ((SELECT roles_id FROM roles WHERE role_name = 'developer'), '/v1/*', 'GET,POST,PUT,DELETE', '{}', true),
    ((SELECT roles_id FROM roles WHERE role_name = 'admin'), '/v1/*', 'GET,POST,PUT,DELETE', '{}', true),
    ((SELECT roles_id FROM roles WHERE role_name = 'accountant'), '/v1/invoices/*', 'GET,POST,PUT', '{"invoice_number", "total_amount"}', true),
    ((SELECT roles_id FROM roles WHERE role_name = 'manager'), '/v1/crm/*', 'GET,POST,PUT,DELETE', '{"lead_name", "expected_revenue"}', true),
    ((SELECT roles_id FROM roles WHERE role_name = 'hr'), '/v1/payrolls', 'GET', '{"gross_amount", "net_amount"}', true),
    ((SELECT roles_id FROM roles WHERE role_name = 'support'), '/v1/tickets', 'GET,POST,PUT', '{"title", "description"}', true),
    ((SELECT roles_id FROM roles WHERE role_name = 'demo'), '/v1/*', 'GET', '{}', true);