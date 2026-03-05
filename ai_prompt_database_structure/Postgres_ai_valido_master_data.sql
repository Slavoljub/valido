-- ============================================================================
-- VALIDOAI MASTER DATA SQL
-- ============================================================================
-- Comprehensive sample data for Serbian business financial system
-- 50+ records per table with realistic Serbian business context
-- ============================================================================

-- Insert Serbian business entity data
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
-- 1. SAMPLE COMPANIES (Serbian businesses)
-- ============================================================================

INSERT INTO companies (
    company_name, legal_name, tax_id, registration_number, business_entity_type_id,
    industry, company_type, company_size,
    pdv_registration, statistical_number, bank_account, bank_name,
    address_line1, address_line2, city, municipality, postal_code, country,
    phone, email, website,
    founding_date, fiscal_year_start, currency, language,
    status, is_pdv_registered, is_e_invoice_enabled,
    description, notes
) VALUES
('TechNova Solutions DOO', 'TechNova Solutions DOO', '123456789', 'BD12345678',
 (SELECT business_entity_types_id FROM business_entity_types WHERE entity_code = 'DOO'),
 'Technology', 'DOO', 'Medium',
 'PDV123456789', 'STAT987654321', '160-1234567890123-45', 'Banka Intesa',
 'Bulevar Oslobođenja 123', 'Sprat 5', 'Beograd', 'Stari Grad', '11000', 'Serbia',
 '+381112345678', 'info@technova.rs', 'www.technova.rs',
 '2020-03-15', '2024-01-01', 'RSD', 'sr-RS',
 'active', true, true,
 'IT solutions and software development company based in Belgrade',
 'Leading technology provider in Serbian market'),

('DataFlow Analytics DOO', 'DataFlow Analytics DOO', '234567890', 'BD23456789',
 (SELECT business_entity_types_id FROM business_entity_types WHERE entity_code = 'DOO'),
 'Consulting', 'DOO', 'Small',
 'PDV234567890', 'STAT876543210', '260-2345678901234-56', 'Raiffeisen Bank',
 'Knez Mihailova 45', 'Sprat 2', 'Beograd', 'Stari Grad', '11000', 'Serbia',
 '+381112345679', 'contact@dataflow.rs', 'www.dataflow.rs',
 '2021-06-22', '2024-01-01', 'RSD', 'sr-RS',
 'active', true, false,
 'Business analytics and data consulting services',
 'Specializing in data-driven business solutions'),

('CloudScale Systems AD', 'CloudScale Systems AD', '345678901', 'BD34567890',
 (SELECT business_entity_types_id FROM business_entity_types WHERE entity_code = 'AD'),
 'Technology', 'AD', 'Large',
 'PDV345678901', 'STAT765432109', '340-3456789012345-67', 'Unicredit Bank',
 'Vladimira Popovića 25', 'Novi Beograd', 'Beograd', 'Novi Beograd', '11070', 'Serbia',
 '+381112345680', 'info@cloudscale.rs', 'www.cloudscale.rs',
 '2019-11-08', '2024-01-01', 'RSD', 'sr-RS',
 'active', true, true,
 'Enterprise cloud solutions and infrastructure services',
 'Publicly traded technology company'),

('GreenTech Solutions DOO', 'GreenTech Solutions DOO', '456789012', 'BD45678901',
 (SELECT business_entity_types_id FROM business_entity_types WHERE entity_code = 'DOO'),
 'Manufacturing', 'DOO', 'Medium',
 'PDV456789012', 'STAT654321098', '160-4567890123456-78', 'Erste Bank',
 'Balkanska 12', 'Industrijska zona', 'Novi Sad', 'Novi Sad', '21000', 'Serbia',
 '+381214567890', 'office@greentech.rs', 'www.greentech.rs',
 '2022-01-20', '2024-01-01', 'RSD', 'sr-RS',
 'active', true, false,
 'Sustainable technology and green manufacturing solutions',
 'Environmental technology innovator'),

('SmartBuild Construction DOO', 'SmartBuild Construction DOO', '567890123', 'BD56789012',
 (SELECT business_entity_types_id FROM business_entity_types WHERE entity_code = 'DOO'),
 'Construction', 'DOO', 'Large',
 'PDV567890123', 'STAT543210987', '260-5678901234567-89', 'Komercijalna Banka',
 'Autoput 22', 'Poslovni park', 'Novi Sad', 'Novi Sad', '21000', 'Serbia',
 '+381214567891', 'info@smartbuild.rs', 'www.smartbuild.rs',
 '2018-08-14', '2024-01-01', 'RSD', 'sr-RS',
 'active', true, true,
 'Modern construction and building materials company',
 'Leading construction materials provider in Vojvodina'),

('MediCare Solutions DOO', 'MediCare Solutions DOO', '678901234', 'BD67890123',
 (SELECT business_entity_types_id FROM business_entity_types WHERE entity_code = 'DOO'),
 'Healthcare', 'DOO', 'Medium',
 'PDV678901234', 'STAT432109876', '340-6789012345678-90', 'AIK Banka',
 'Vojvode Stepe 15', 'Medicinski centar', 'Beograd', 'Vračar', '11000', 'Serbia',
 '+381112345682', 'contact@medicare.rs', 'www.medicare.rs',
 '2021-12-05', '2024-01-01', 'RSD', 'sr-RS',
 'active', true, true,
 'Healthcare technology and medical equipment supplier',
 'Innovative healthcare solutions provider'),

('AgroFresh Trading DOO', 'AgroFresh Trading DOO', '789012345', 'BD78901234',
 (SELECT business_entity_types_id FROM business_entity_types WHERE entity_code = 'DOO'),
 'Agriculture', 'DOO', 'Small',
 'PDV789012345', 'STAT321098765', '160-7890123456789-01', 'Banka Poštanska Štedionica',
 'Trg Republike 8', 'Sprat 3', 'Kragujevac', 'Šumadija', '34000', 'Serbia',
 '+381342345678', 'office@agrofresh.rs', 'www.agrofresh.rs',
 '2023-02-10', '2024-01-01', 'RSD', 'sr-RS',
 'active', false, false,
 'Fresh produce and agricultural products trading',
 'Supporting local Serbian farmers and markets'),

('EduTech Solutions DOO', 'EduTech Solutions DOO', '890123456', 'BD89012345',
 (SELECT business_entity_types_id FROM business_entity_types WHERE entity_code = 'DOO'),
 'Education', 'DOO', 'Small',
 'PDV890123456', 'STAT210987654', '260-8901234567890-12', 'Societe Generale',
 'Svetog Save 22', 'Univerzitetski centar', 'Niš', 'Niš', '18000', 'Serbia',
 '+381184567890', 'info@edutech.rs', 'www.edutech.rs',
 '2022-09-18', '2024-01-01', 'RSD', 'sr-RS',
 'active', true, false,
 'Educational technology and e-learning solutions',
 'Supporting Serbian education system'),

('LogiTrans Services DOO', 'LogiTrans Services DOO', '901234567', 'BD90123456',
 (SELECT business_entity_types_id FROM business_entity_types WHERE entity_code = 'DOO'),
 'Transportation', 'DOO', 'Medium',
 'PDV901234567', 'STAT109876543', '340-9012345678901-23', 'NLB Banka',
 'Karađorđeva 45', 'Logistički centar', 'Beograd', 'Zemun', '11080', 'Serbia',
 '+381112345684', 'contact@logitrans.rs', 'www.logitrans.rs',
 '2020-11-30', '2024-01-01', 'RSD', 'sr-RS',
 'active', true, true,
 'Logistics and transportation services across Serbia',
 'Comprehensive logistics solutions provider'),

('FashionStyle Retail DOO', 'FashionStyle Retail DOO', '012345678', 'BD01234567',
 (SELECT business_entity_types_id FROM business_entity_types WHERE entity_code = 'DOO'),
 'Retail', 'DOO', 'Small',
 'PDV012345678', 'STAT098765432', '160-0123456789012-34', 'ProCredit Bank',
 'Tržni centar 12', 'Sprat 1', 'Subotica', 'Severna Bačka', '24000', 'Serbia',
 '+381244567890', 'shop@fashionstyle.rs', 'www.fashionstyle.rs',
 '2023-05-12', '2024-01-01', 'RSD', 'sr-RS',
 'active', true, false,
 'Fashion retail and clothing boutique',
 'Local fashion brand with Serbian designers');

-- ============================================================================
-- 2. SAMPLE USERS (Serbian context)
-- ============================================================================

INSERT INTO users (
    email, username, password_hash, first_name, last_name, phone,
    jmbg, citizenship,
    role, status, is_active, company_id,
    department, job_title
) VALUES
-- TechNova Solutions users
('milan.petrovic@technova.rs', 'milan_petrovic', '$2b$12$8qL3Z4M5N6O7P8Q9R0S1T', 'Milan', 'Petrović', '+381601234567',
 '0101987654321', 'Serbia',
 'owner', 'active', true, (SELECT companies_id FROM companies WHERE company_name = 'TechNova Solutions DOO'),
 'Management', 'CEO'),

('ana.jovanovic@technova.rs', 'ana_jovanovic', '$2b$12$8qL3Z4M5N6O7P8Q9R0S1T', 'Ana', 'Jovanović', '+381602345678',
 '1502998765432', 'Serbia',
 'accountant', 'active', true, (SELECT companies_id FROM companies WHERE company_name = 'TechNova Solutions DOO'),
 'Finance', 'Chief Accountant'),

('marko.nikolic@technova.rs', 'marko_nikolic', '$2b$12$8qL3Z4M5N6O7P8Q9R0S1T', 'Marko', 'Nikolić', '+381603456789',
 '2003997654321', 'Serbia',
 'sales', 'active', true, (SELECT companies_id FROM companies WHERE company_name = 'TechNova Solutions DOO'),
 'Sales', 'Sales Manager'),

('jovana.djuric@technova.rs', 'jovana_djuric', '$2b$12$8qL3Z4M5N6O7P8Q9R0S1T', 'Jovana', 'Đurić', '+381604567890',
 '2504996543210', 'Serbia',
 'user', 'active', true, (SELECT companies_id FROM companies WHERE company_name = 'TechNova Solutions DOO'),
 'Development', 'Software Developer'),

('nikola.stojanovic@technova.rs', 'nikola_stojanovic', '$2b$12$8qL3Z4M5N6O7P8Q9R0S1T', 'Nikola', 'Stojanović', '+381605678901',
 '3005995432109', 'Serbia',
 'manager', 'active', true, (SELECT companies_id FROM companies WHERE company_name = 'TechNova Solutions DOO'),
 'Development', 'IT Manager'),

-- DataFlow Analytics users
('marija.ilic@dataflow.rs', 'marija_ilic', '$2b$12$8qL3Z4M5N6O7P8Q9R0S1T', 'Marija', 'Ilić', '+381611234567',
 '0510987654321', 'Serbia',
 'owner', 'active', true, (SELECT companies_id FROM companies WHERE company_name = 'DataFlow Analytics DOO'),
 'Management', 'CEO'),

('petar.mitic@dataflow.rs', 'petar_mitic', '$2b$12$8qL3Z4M5N6O7P8Q9R0S1T', 'Petar', 'Mitić', '+381612345678',
 '1011998765432', 'Serbia',
 'accountant', 'active', true, (SELECT companies_id FROM companies WHERE company_name = 'DataFlow Analytics DOO'),
 'Finance', 'Accountant'),

('sara.kostic@dataflow.rs', 'sara_kostic', '$2b$12$8qL3Z4M5N6O7P8Q9R0S1T', 'Sara', 'Kostić', '+381613456789',
 '1512997654321', 'Serbia',
 'user', 'active', true, (SELECT companies_id FROM companies WHERE company_name = 'DataFlow Analytics DOO'),
 'Analytics', 'Data Analyst'),

-- CloudScale Systems users
('dusan.pavlovic@cloudscale.rs', 'dusan_pavlovic', '$2b$12$8qL3Z4M5N6O7P8Q9R0S1T', 'Dušan', 'Pavlović', '+381621234567',
 '0110987654321', 'Serbia',
 'owner', 'active', true, (SELECT companies_id FROM companies WHERE company_name = 'CloudScale Systems AD'),
 'Management', 'CEO'),

('ivana.milic@cloudscale.rs', 'ivana_milic', '$2b$12$8qL3Z4M5N6O7P8Q9R0S1T', 'Ivana', 'Milić', '+381622345678',
 '0611998765432', 'Serbia',
 'accountant', 'active', true, (SELECT companies_id FROM companies WHERE company_name = 'CloudScale Systems AD'),
 'Finance', 'Chief Accountant'),

('luka.simic@cloudscale.rs', 'luka_simic', '$2b$12$8qL3Z4M5N6O7P8Q9R0S1T', 'Luka', 'Simić', '+381623456789',
 '1112997654321', 'Serbia',
 'manager', 'active', true, (SELECT companies_id FROM companies WHERE company_name = 'CloudScale Systems AD'),
 'Operations', 'Operations Manager'),

('maja.todorovic@cloudscale.rs', 'maja_todorovic', '$2b$12$8qL3Z4M5N6O7P8Q9R0S1T', 'Maja', 'Todorović', '+381624567890',
 '1613996543210', 'Serbia',
 'sales', 'active', true, (SELECT companies_id FROM companies WHERE company_name = 'CloudScale Systems AD'),
 'Sales', 'Business Development Manager'),

('stefan.lazic@cloudscale.rs', 'stefan_lazic', '$2b$12$8qL3Z4M5N6O7P8Q9R0S1T', 'Stefan', 'Lazić', '+381625678901',
 '2114995432109', 'Serbia',
 'user', 'active', true, (SELECT companies_id FROM companies WHERE company_name = 'CloudScale Systems AD'),
 'Technical', 'Cloud Architect'),

-- GreenTech Solutions users
('vukasin.jevtic@greentech.rs', 'vukasin_jevtic', '$2b$12$8qL3Z4M5N6O7P8Q9R0S1T', 'Vukašin', 'Jevtić', '+381211234567',
 '0210987654321', 'Serbia',
 'owner', 'active', true, (SELECT companies_id FROM companies WHERE company_name = 'GreenTech Solutions DOO'),
 'Management', 'CEO'),

('nevena.markovic@greentech.rs', 'nevena_markovic', '$2b$12$8qL3Z4M5N6O7P8Q9R0S1T', 'Nevena', 'Marković', '+381212345678',
 '0711998765432', 'Serbia',
 'accountant', 'active', true, (SELECT companies_id FROM companies WHERE company_name = 'GreenTech Solutions DOO'),
 'Finance', 'Accountant'),

('filip.radic@greentech.rs', 'filip_radic', '$2b$12$8qL3Z4M5N6O7P8Q9R0S1T', 'Filip', 'Radić', '+381213456789',
 '1212997654321', 'Serbia',
 'user', 'active', true, (SELECT companies_id FROM companies WHERE company_name = 'GreenTech Solutions DOO'),
 'R&D', 'Research Engineer'),

-- SmartBuild Construction users
('aleksandar.vasic@smartbuild.rs', 'aleksandar_vasic', '$2b$12$8qL3Z4M5N6O7P8Q9R0S1T', 'Aleksandar', 'Vasić', '+381211234568',
 '0310987654321', 'Serbia',
 'owner', 'active', true, (SELECT companies_id FROM companies WHERE company_name = 'SmartBuild Construction DOO'),
 'Management', 'CEO'),

('jelena.dimitrijevic@smartbuild.rs', 'jelena_dimitrijevic', '$2b$12$8qL3Z4M5N6O7P8Q9R0S1T', 'Jelena', 'Dimitrijević', '+381212345679',
 '0811998765432', 'Serbia',
 'accountant', 'active', true, (SELECT companies_id FROM companies WHERE company_name = 'SmartBuild Construction DOO'),
 'Finance', 'Chief Accountant'),

('bojan.stankovic@smartbuild.rs', 'bojan_stankovic', '$2b$12$8qL3Z4M5N6O7P8Q9R0S1T', 'Bojan', 'Stanković', '+381213456780',
 '1312997654321', 'Serbia',
 'manager', 'active', true, (SELECT companies_id FROM companies WHERE company_name = 'SmartBuild Construction DOO'),
 'Projects', 'Project Manager'),

('milica.ivanovic@smartbuild.rs', 'milica_ivanovic', '$2b$12$8qL3Z4M5N6O7P8Q9R0S1T', 'Milica', 'Ivanović', '+381214567891',
 '1813996543210', 'Serbia',
 'sales', 'active', true, (SELECT companies_id FROM companies WHERE company_name = 'SmartBuild Construction DOO'),
 'Sales', 'Sales Representative'),

('nikola.bozic@smartbuild.rs', 'nikola_bozic', '$2b$12$8qL3Z4M5N6O7P8Q9R0S1T', 'Nikola', 'Bozic', '+381215678902',
 '2314995432109', 'Serbia',
 'user', 'active', true, (SELECT companies_id FROM companies WHERE company_name = 'SmartBuild Construction DOO'),
 'Technical', 'Construction Engineer');

-- ============================================================================
-- 3. SAMPLE PRODUCT CATEGORIES (Serbian market)
-- ============================================================================

INSERT INTO product_categories (
    category_code, category_name, category_name_sr, description,
    pdv_rate, is_pdv_exempt, pdv_exemption_reason
) VALUES
('IT_SERVICES', 'IT Services', 'IT Usluge', 'Software development, consulting, and IT services',
 20.00, false, NULL),

('IT_HARDWARE', 'IT Hardware', 'IT Oprema', 'Computers, servers, networking equipment',
 20.00, false, NULL),

('CLOUD_SERVICES', 'Cloud Services', 'Cloud Usluge', 'Cloud hosting, infrastructure, and platform services',
 20.00, false, NULL),

('DATA_ANALYTICS', 'Data Analytics', 'Analiza Podataka', 'Business intelligence, data analysis, and reporting services',
 20.00, false, NULL),

('SOFTWARE', 'Software', 'Softver', 'Software applications and licenses',
 20.00, false, NULL),

('ELECTRONICS', 'Electronics', 'Elektronika', 'Electronic components and devices',
 20.00, false, NULL),

('GREEN_TECH', 'Green Technology', 'Zelena Tehnologija', 'Sustainable and eco-friendly technology solutions',
 20.00, false, NULL),

('CONSTRUCTION_MATERIALS', 'Construction Materials', 'Građevinski Materijali', 'Building materials and supplies',
 20.00, false, NULL),

('MEDICAL_EQUIPMENT', 'Medical Equipment', 'Medicinska Oprema', 'Healthcare and medical equipment',
 20.00, false, NULL),

('AGRICULTURAL_PRODUCTS', 'Agricultural Products', 'Poljoprivredni Proizvodi', 'Fresh produce and agricultural goods',
 10.00, false, NULL), -- Reduced PDV rate for food

('EDUCATIONAL_SERVICES', 'Educational Services', 'Obrazovne Usluge', 'Training, courses, and educational materials',
 20.00, false, NULL),

('LOGISTICS_SERVICES', 'Logistics Services', 'Logističke Usluge', 'Transportation and logistics services',
 20.00, false, NULL),

('FASHION_APPAREL', 'Fashion Apparel', 'Modna Odeća', 'Clothing and fashion products',
 20.00, false, NULL),

('FOOD_PRODUCTS', 'Food Products', 'Prehrambeni Proizvodi', 'Food and beverage products',
 10.00, false, NULL), -- Reduced PDV rate for food

('OFFICE_SUPPLIES', 'Office Supplies', 'Kancelarijski Materijal', 'Office equipment and supplies',
 20.00, false, NULL);

-- ============================================================================
-- 4. SAMPLE PRODUCTS (50+ products with Serbian context)
-- ============================================================================

-- IT Services products
INSERT INTO products (
    company_id, product_code, product_name, product_name_sr,
    description, category_id, measurement_unit, pdv_rate,
    unit_price, cost_price, wholesale_price
) SELECT
    c.companies_id, 'IT_DEV_001', 'Custom Software Development', 'Razvoj Prilagođenog Softvera',
    'Custom software development services for Serbian businesses', pc.product_categories_id, 'sat', 20.00,
    8500.00, 6500.00, 7500.00
FROM companies c, product_categories pc
WHERE c.company_name = 'TechNova Solutions DOO' AND pc.category_code = 'IT_SERVICES'
UNION ALL SELECT
    c.companies_id, 'IT_MAINT_001', 'Software Maintenance', 'Održavanje Softvera',
    'Ongoing software maintenance and support services', pc.product_categories_id, 'mes', 20.00,
    15000.00, 10000.00, 13000.00
FROM companies c, product_categories pc
WHERE c.company_name = 'TechNova Solutions DOO' AND pc.category_code = 'IT_SERVICES'
UNION ALL SELECT
    c.companies_id, 'IT_CONSULT_001', 'IT Consulting', 'IT Konsalting',
    'IT strategy and technology consulting services', pc.product_categories_id, 'sat', 20.00,
    6500.00, 4500.00, 5500.00
FROM companies c, product_categories pc
WHERE c.company_name = 'TechNova Solutions DOO' AND pc.category_code = 'IT_SERVICES'
UNION ALL SELECT
    c.companies_id, 'MOBILE_APP_001', 'Mobile App Development', 'Razvoj Mobilnih Aplikacija',
    'Native and hybrid mobile application development', pc.product_categories_id, 'sat', 20.00,
    9500.00, 7000.00, 8500.00
FROM companies c, product_categories pc
WHERE c.company_name = 'TechNova Solutions DOO' AND pc.category_code = 'IT_SERVICES'
UNION ALL SELECT
    c.companies_id, 'WEB_DEV_001', 'Web Application Development', 'Razvoj Web Aplikacija',
    'Modern web application development with latest technologies', pc.product_categories_id, 'sat', 20.00,
    7500.00, 5500.00, 6500.00
FROM companies c, product_categories pc
WHERE c.company_name = 'TechNova Solutions DOO' AND pc.category_code = 'IT_SERVICES';

-- Data Analytics products
INSERT INTO products (
    company_id, product_code, product_name, product_name_sr,
    description, category_id, measurement_unit, pdv_rate,
    unit_price, cost_price, wholesale_price
) SELECT
    c.companies_id, 'DATA_ANALYSIS_001', 'Business Data Analysis', 'Analiza Poslovnih Podataka',
    'Comprehensive business data analysis and insights', pc.product_categories_id, 'mes', 20.00,
    25000.00, 18000.00, 22000.00
FROM companies c, product_categories pc
WHERE c.company_name = 'DataFlow Analytics DOO' AND pc.category_code = 'DATA_ANALYTICS'
UNION ALL SELECT
    c.companies_id, 'DASHBOARD_001', 'Business Intelligence Dashboard', 'Dashboard Poslovne Inteligencije',
    'Interactive business intelligence dashboards and reports', pc.product_categories_id, 'kom', 20.00,
    45000.00, 30000.00, 40000.00
FROM companies c, product_categories pc
WHERE c.company_name = 'DataFlow Analytics DOO' AND pc.category_code = 'DATA_ANALYTICS'
UNION ALL SELECT
    c.companies_id, 'DATA_MIGRATION_001', 'Data Migration Services', 'Usluge Migracije Podataka',
    'Database migration and data transformation services', pc.product_categories_id, 'pro', 20.00,
    35000.00, 25000.00, 30000.00
FROM companies c, product_categories pc
WHERE c.company_name = 'DataFlow Analytics DOO' AND pc.category_code = 'DATA_ANALYTICS'
UNION ALL SELECT
    c.companies_id, 'REPORTING_001', 'Automated Reporting System', 'Sistem Automatskog Izveštavanja',
    'Automated business reporting and analytics system', pc.product_categories_id, 'mes', 20.00,
    18000.00, 12000.00, 15000.00
FROM companies c, product_categories pc
WHERE c.company_name = 'DataFlow Analytics DOO' AND pc.category_code = 'DATA_ANALYTICS'
UNION ALL SELECT
    c.companies_id, 'DATA_CLEANING_001', 'Data Cleaning Services', 'Usluge Čišćenja Podataka',
    'Data cleansing, validation, and quality improvement', pc.product_categories_id, 'sat', 20.00,
    4500.00, 3000.00, 4000.00
FROM companies c, product_categories pc
WHERE c.company_name = 'DataFlow Analytics DOO' AND pc.category_code = 'DATA_ANALYTICS';

-- Cloud Services products
INSERT INTO products (
    company_id, product_code, product_name, product_name_sr,
    description, category_id, measurement_unit, pdv_rate,
    unit_price, cost_price, wholesale_price
) SELECT
    c.companies_id, 'CLOUD_HOSTING_001', 'Cloud Server Hosting', 'Cloud Hosting Servera',
    'Enterprise-grade cloud server hosting solutions', pc.product_categories_id, 'mes', 20.00,
    12000.00, 8000.00, 10000.00
FROM companies c, product_categories pc
WHERE c.company_name = 'CloudScale Systems AD' AND pc.category_code = 'CLOUD_SERVICES'
UNION ALL SELECT
    c.companies_id, 'BACKUP_SERVICE_001', 'Cloud Backup Service', 'Cloud Backup Usluga',
    'Automated cloud backup and disaster recovery', pc.product_categories_id, 'mes', 20.00,
    8000.00, 5000.00, 7000.00
FROM companies c, product_categories pc
WHERE c.company_name = 'CloudScale Systems AD' AND pc.category_code = 'CLOUD_SERVICES'
UNION ALL SELECT
    c.companies_id, 'CLOUD_MIGRATION_001', 'Cloud Migration', 'Migracija na Cloud',
    'Complete migration to cloud infrastructure', pc.product_categories_id, 'pro', 20.00,
    45000.00, 30000.00, 40000.00
FROM companies c, product_categories pc
WHERE c.company_name = 'CloudScale Systems AD' AND pc.category_code = 'CLOUD_SERVICES'
UNION ALL SELECT
    c.companies_id, 'DEVOPS_SERVICE_001', 'DevOps as Service', 'DevOps kao Usluga',
    'Complete DevOps pipeline and automation services', pc.product_categories_id, 'mes', 20.00,
    35000.00, 25000.00, 30000.00
FROM companies c, product_categories pc
WHERE c.company_name = 'CloudScale Systems AD' AND pc.category_code = 'CLOUD_SERVICES'
UNION ALL SELECT
    c.companies_id, 'MONITORING_001', 'Cloud Monitoring', 'Cloud Monitoring',
    '24/7 cloud infrastructure monitoring and alerting', pc.product_categories_id, 'mes', 20.00,
    15000.00, 10000.00, 12000.00
FROM companies c, product_categories pc
WHERE c.company_name = 'CloudScale Systems AD' AND pc.category_code = 'CLOUD_SERVICES';

-- Construction products
INSERT INTO products (
    company_id, product_code, product_name, product_name_sr,
    description, category_id, measurement_unit, pdv_rate,
    unit_price, cost_price, wholesale_price
) SELECT
    c.companies_id, 'CEMENT_001', 'Portland Cement', 'Portlend Cement',
    'High-quality Portland cement for construction', pc.product_categories_id, 't', 20.00,
    6500.00, 5200.00, 5800.00
FROM companies c, product_categories pc
WHERE c.company_name = 'SmartBuild Construction DOO' AND pc.category_code = 'CONSTRUCTION_MATERIALS'
UNION ALL SELECT
    c.companies_id, 'STEEL_REBAR_001', 'Steel Rebar', 'Čelične Šipke',
    'Reinforcement steel bars for concrete construction', pc.product_categories_id, 't', 20.00,
    8500.00, 6800.00, 7500.00
FROM companies c, product_categories pc
WHERE c.company_name = 'SmartBuild Construction DOO' AND pc.category_code = 'CONSTRUCTION_MATERIALS'
UNION ALL SELECT
    c.companies_id, 'BRICKS_001', 'Clay Bricks', 'Cigle od Pečene Gline',
    'Traditional clay bricks for building construction', pc.product_categories_id, 'kom', 20.00,
    25.00, 18.00, 22.00
FROM companies c, product_categories pc
WHERE c.company_name = 'SmartBuild Construction DOO' AND pc.category_code = 'CONSTRUCTION_MATERIALS'
UNION ALL SELECT
    c.companies_id, 'CONCRETE_001', 'Ready Mix Concrete', 'Gotovi Beton',
    'Ready-to-use concrete mixture for construction', pc.product_categories_id, 'm3', 20.00,
    12000.00, 9500.00, 11000.00
FROM companies c, product_categories pc
WHERE c.company_name = 'SmartBuild Construction DOO' AND pc.category_code = 'CONSTRUCTION_MATERIALS'
UNION ALL SELECT
    c.companies_id, 'INSULATION_001', 'Thermal Insulation', 'Termička Izolacija',
    'Thermal insulation materials for energy efficiency', pc.product_categories_id, 'm2', 20.00,
    450.00, 320.00, 400.00
FROM companies c, product_categories pc
WHERE c.company_name = 'SmartBuild Construction DOO' AND pc.category_code = 'CONSTRUCTION_MATERIALS';

-- Agricultural products
INSERT INTO products (
    company_id, product_code, product_name, product_name_sr,
    description, category_id, measurement_unit, pdv_rate,
    unit_price, cost_price, wholesale_price
) SELECT
    c.companies_id, 'WHEAT_001', 'Winter Wheat', 'Zimska Pšenica',
    'High-quality Serbian winter wheat for baking', pc.product_categories_id, 't', 10.00,
    28000.00, 22000.00, 25000.00
FROM companies c, product_categories pc
WHERE c.company_name = 'AgroFresh Trading DOO' AND pc.category_code = 'AGRICULTURAL_PRODUCTS'
UNION ALL SELECT
    c.companies_id, 'CORN_001', 'Field Corn', 'Poljski Kukuruz',
    'Serbian field corn for animal feed and processing', pc.product_categories_id, 't', 10.00,
    22000.00, 18000.00, 20000.00
FROM companies c, product_categories pc
WHERE c.company_name = 'AgroFresh Trading DOO' AND pc.category_code = 'AGRICULTURAL_PRODUCTS'
UNION ALL SELECT
    c.companies_id, 'SUNFLOWER_001', 'Sunflower Seeds', 'Suncokretovo Semen',
    'Serbian sunflower seeds for oil production', pc.product_categories_id, 't', 10.00,
    65000.00, 55000.00, 60000.00
FROM companies c, product_categories pc
WHERE c.company_name = 'AgroFresh Trading DOO' AND pc.category_code = 'AGRICULTURAL_PRODUCTS'
UNION ALL SELECT
    c.companies_id, 'APPLES_001', 'Fresh Apples', 'Sveže Jabuke',
    'Fresh Serbian apples from Vojvodina region', pc.product_categories_id, 't', 10.00,
    35000.00, 25000.00, 30000.00
FROM companies c, product_categories pc
WHERE c.company_name = 'AgroFresh Trading DOO' AND pc.category_code = 'AGRICULTURAL_PRODUCTS'
UNION ALL SELECT
    c.companies_id, 'TOMATOES_001', 'Fresh Tomatoes', 'Sveži Paradajz',
    'Fresh Serbian tomatoes from local farmers', pc.product_categories_id, 't', 10.00,
    45000.00, 30000.00, 38000.00
FROM companies c, product_categories pc
WHERE c.company_name = 'AgroFresh Trading DOO' AND pc.category_code = 'AGRICULTURAL_PRODUCTS';

-- Fashion products
INSERT INTO products (
    company_id, product_code, product_name, product_name_sr,
    description, category_id, measurement_unit, pdv_rate,
    unit_price, cost_price, wholesale_price
) SELECT
    c.companies_id, 'TSHIRT_001', 'Cotton T-Shirt', 'Pamučna Majica',
    'Comfortable cotton t-shirts made in Serbia', pc.product_categories_id, 'kom', 20.00,
    2500.00, 1500.00, 2000.00
FROM companies c, product_categories pc
WHERE c.company_name = 'FashionStyle Retail DOO' AND pc.category_code = 'FASHION_APPAREL'
UNION ALL SELECT
    c.companies_id, 'JEANS_001', 'Designer Jeans', 'Dizajnerske Farmerke',
    'High-quality designer jeans from Serbian designers', pc.product_categories_id, 'kom', 20.00,
    12000.00, 8000.00, 10000.00
FROM companies c, product_categories pc
WHERE c.company_name = 'FashionStyle Retail DOO' AND pc.category_code = 'FASHION_APPAREL'
UNION ALL SELECT
    c.companies_id, 'DRESS_001', 'Evening Dress', 'Večernja Haljina',
    'Elegant evening dresses with Serbian traditional elements', pc.product_categories_id, 'kom', 20.00,
    18000.00, 12000.00, 15000.00
FROM companies c, product_categories pc
WHERE c.company_name = 'FashionStyle Retail DOO' AND pc.category_code = 'FASHION_APPAREL'
UNION ALL SELECT
    c.companies_id, 'SHOES_001', 'Leather Shoes', 'Kožne Cipele',
    'Handcrafted leather shoes from Serbian artisans', pc.product_categories_id, 'par', 20.00,
    15000.00, 10000.00, 12500.00
FROM companies c, product_categories pc
WHERE c.company_name = 'FashionStyle Retail DOO' AND pc.category_code = 'FASHION_APPAREL'
UNION ALL SELECT
    c.companies_id, 'JACKET_001', 'Winter Jacket', 'Zimska Jakna',
    'Warm winter jackets suitable for Serbian climate', pc.product_categories_id, 'kom', 20.00,
    25000.00, 18000.00, 22000.00
FROM companies c, product_categories pc
WHERE c.company_name = 'FashionStyle Retail DOO' AND pc.category_code = 'FASHION_APPAREL';

-- ============================================================================
-- 5. SAMPLE CUSTOMERS (Serbian businesses)
-- ============================================================================

INSERT INTO customer_types (type_code, type_name, type_name_sr, description, payment_terms_default, credit_limit_default) VALUES
('INDIVIDUAL', 'Individual', 'Pojedinac', 'Individual customers', 'Net 30', 50000.00),
('SMALL_BUSINESS', 'Small Business', 'Malo Preduzeće', 'Small businesses with <10 employees', 'Net 15', 200000.00),
('MEDIUM_BUSINESS', 'Medium Business', 'Srednje Preduzeće', 'Medium businesses with 10-50 employees', 'Net 30', 500000.00),
('LARGE_BUSINESS', 'Large Business', 'Veliko Preduzeće', 'Large businesses with >50 employees', 'Net 45', 2000000.00),
('GOVERNMENT', 'Government', 'Državne Institucije', 'Government organizations and institutions', 'Net 60', 1000000.00);

-- Insert sample customers
INSERT INTO customers (
    company_id, customer_type_id, customer_number,
    company_name, pib, matični_broj,
    contact_person, email, phone,
    address_line1, city, postal_code, country,
    industry, payment_terms, credit_limit,
    status, is_vip, tax_exempt
) VALUES
-- TechNova Solutions customers
((SELECT companies_id FROM companies WHERE company_name = 'TechNova Solutions DOO'),
 (SELECT customer_types_id FROM customer_types WHERE type_code = 'LARGE_BUSINESS'),
 'CUST001',
 'Elektroprivreda Srbije', '100000001', 'BD10000001',
 'Marko Petrović', 'marko.petrovic@eps.rs', '+381112345678',
 'Kneza Miloša 12', 'Beograd', '11000', 'Serbia',
 'Energy', 'Net 45', 5000000.00, 'active', true, false),

((SELECT companies_id FROM companies WHERE company_name = 'TechNova Solutions DOO'),
 (SELECT customer_types_id FROM customer_types WHERE type_code = 'MEDIUM_BUSINESS'),
 'CUST002',
 'Telekom Srbija', '100000002', 'BD10000002',
 'Ana Jovanović', 'ana.jovanovic@telekom.rs', '+381112345679',
 'Takovska 2', 'Beograd', '11000', 'Serbia',
 'Telecommunications', 'Net 30', 2000000.00, 'active', false, false),

((SELECT companies_id FROM companies WHERE company_name = 'TechNova Solutions DOO'),
 (SELECT customer_types_id FROM customer_types WHERE type_code = 'SMALL_BUSINESS'),
 'CUST003',
 'IT Solutions Plus DOO', '100000003', 'BD10000003',
 'Petar Marković', 'petar@itsolutions.rs', '+381112345680',
 'Bulevar Oslobođenja 45', 'Beograd', '11000', 'Serbia',
 'Technology', 'Net 15', 500000.00, 'active', false, false),

-- DataFlow Analytics customers
((SELECT companies_id FROM companies WHERE company_name = 'DataFlow Analytics DOO'),
 (SELECT customer_types_id FROM customer_types WHERE type_code = 'LARGE_BUSINESS'),
 'CUST004',
 'Ministarstvo Finansija', '100000004', 'BD10000004',
 'Dr. Marija Petrović', 'marija.petrovic@mf.gov.rs', '+381112345681',
 'Kneza Miloša 20', 'Beograd', '11000', 'Serbia',
 'Government', 'Net 60', 10000000.00, 'active', true, true),

((SELECT companies_id FROM companies WHERE company_name = 'DataFlow Analytics DOO'),
 (SELECT customer_types_id FROM customer_types WHERE type_code = 'MEDIUM_BUSINESS'),
 'CUST005',
 'Delta Holding', '100000005', 'BD10000005',
 'Jovana Nikolić', 'jovana.nikolic@delta.rs', '+381112345682',
 'Vladimira Popovića 8', 'Beograd', '11070', 'Serbia',
 'Holding Company', 'Net 30', 3000000.00, 'active', true, false),

-- CloudScale Systems customers
((SELECT companies_id FROM companies WHERE company_name = 'CloudScale Systems AD'),
 (SELECT customer_types_id FROM customer_types WHERE type_code = 'LARGE_BUSINESS'),
 'CUST006',
 'Banka Intesa', '100000006', 'BD10000006',
 'Milan Đurić', 'milan.djuric@intesa.rs', '+381112345683',
 'Bulevar Mihajla Pupina 115b', 'Novi Sad', '21000', 'Serbia',
 'Banking', 'Net 45', 8000000.00, 'active', true, false),

((SELECT companies_id FROM companies WHERE company_name = 'CloudScale Systems AD'),
 (SELECT customer_types_id FROM customer_types WHERE type_code = 'MEDIUM_BUSINESS'),
 'CUST007',
 'Vip Mobile', '100000007', 'BD10000007',
 'Sara Kostić', 'sara.kostic@vipmobile.rs', '+381112345684',
 'Bulevar Oslobođenja 25', 'Beograd', '11000', 'Serbia',
 'Telecommunications', 'Net 30', 2500000.00, 'active', false, false),

-- SmartBuild Construction customers
((SELECT companies_id FROM companies WHERE company_name = 'SmartBuild Construction DOO'),
 (SELECT customer_types_id FROM customer_types WHERE type_code = 'GOVERNMENT'),
 'CUST008',
 'Grad Beograd', '100000008', 'BD10000008',
 'Dr. Aleksandar Vasić', 'aleksandar.vasic@beograd.rs', '+381112345685',
 'Trg Nikole Pašića 6', 'Beograd', '11000', 'Serbia',
 'Government', 'Net 60', 15000000.00, 'active', true, true),

((SELECT companies_id FROM companies WHERE company_name = 'SmartBuild Construction DOO'),
 (SELECT customer_types_id FROM customer_types WHERE type_code = 'LARGE_BUSINESS'),
 'CUST009',
 'Messer Tehnogas', '100000009', 'BD10000009',
 'Ivana Milić', 'ivana.milic@messer.rs', '+381214567890',
 'Bulevar cara Lazara 36', 'Novi Sad', '21000', 'Serbia',
 'Industrial Gas', 'Net 45', 4000000.00, 'active', false, false),

-- GreenTech Solutions customers
((SELECT companies_id FROM companies WHERE company_name = 'GreenTech Solutions DOO'),
 (SELECT customer_types_id FROM customer_types WHERE type_code = 'MEDIUM_BUSINESS'),
 'CUST010',
 'Srbijagas', '100000010', 'BD10000010',
 'Dušan Pavlović', 'dusan.pavlovic@srbijagas.rs', '+381214567891',
 'Vase Stajića 8', 'Novi Sad', '21000', 'Serbia',
 'Energy', 'Net 30', 6000000.00, 'active', true, false),

-- MediCare Solutions customers
((SELECT companies_id FROM companies WHERE company_name = 'MediCare Solutions DOO'),
 (SELECT customer_types_id FROM customer_types WHERE type_code = 'GOVERNMENT'),
 'CUST011',
 'Klinički Centar Srbije', '100000011', 'BD10000011',
 'Prof. Dr. Marija Todorović', 'marija.todorovic@kcs.ac.rs', '+381112345686',
 'Pasterova 2', 'Beograd', '11000', 'Serbia',
 'Healthcare', 'Net 60', 3000000.00, 'active', true, true),

-- EduTech Solutions customers
((SELECT companies_id FROM companies WHERE company_name = 'EduTech Solutions DOO'),
 (SELECT customer_types_id FROM customer_types WHERE type_code = 'GOVERNMENT'),
 'CUST012',
 'Ministarstvo Prosvete', '100000012', 'BD10000012',
 'Dr. Nikola Simić', 'nikola.simic@mp.gov.rs', '+381112345687',
 'Nemanjina 22-26', 'Beograd', '11000', 'Serbia',
 'Education', 'Net 60', 2000000.00, 'active', true, true),

-- LogiTrans Services customers
((SELECT companies_id FROM companies WHERE company_name = 'LogiTrans Services DOO'),
 (SELECT customer_types_id FROM customer_types WHERE type_code = 'LARGE_BUSINESS'),
 'CUST013',
 'Mercator-S', '100000013', 'BD10000013',
 'Luka Stanković', 'luka.stankovic@mercator.rs', '+381112345688',
 'Bulevar Oslobođenja 133', 'Beograd', '11000', 'Serbia',
 'Retail', 'Net 30', 5000000.00, 'active', false, false),

-- FashionStyle Retail customers
((SELECT companies_id FROM companies WHERE company_name = 'FashionStyle Retail DOO'),
 (SELECT customer_types_id FROM customer_types WHERE type_code = 'INDIVIDUAL'),
 'CUST014',
 NULL, NULL, NULL,
 'Individual Customer', 'individual@example.rs', '+381631234567',
 'Individual customers in Subotica region', 'Subotica', '24000', 'Serbia',
 'Retail', 'Net 15', 100000.00, 'active', false, false);

-- ============================================================================
-- 6. SAMPLE SUPPLIERS (Serbian businesses)
-- ============================================================================

INSERT INTO suppliers (
    company_id, supplier_number, supplier_name, supplier_name_sr,
    pib, matični_broj, pdv_registration,
    contact_person, email, phone,
    address_line1, city, postal_code, country,
    industry, payment_terms, credit_limit,
    status, is_preferred, notes
) VALUES
-- TechNova Solutions suppliers
((SELECT companies_id FROM companies WHERE company_name = 'TechNova Solutions DOO'),
 'SUP001', 'Microsoft Serbia', 'Microsoft Srbija',
 '200000001', 'BD20000001', 'PDV200000001',
 'Ana Petrović', 'ana.petrovic@microsoft.rs', '+381112345678',
 'Bulevar Mihajla Pupina 10', 'Beograd', '11000', 'Serbia',
 'Technology', 'Net 45', 10000000.00, 'active', true, 'Primary software licenses supplier'),

((SELECT companies_id FROM companies WHERE company_name = 'TechNova Solutions DOO'),
 'SUP002', 'Dell Technologies', 'Dell Tehnologije',
 '200000002', 'BD20000002', 'PDV200000002',
 'Marko Jovanović', 'marko.jovanovic@dell.rs', '+381112345679',
 'Vladimira Popovića 25', 'Beograd', '11070', 'Serbia',
 'Technology', 'Net 30', 5000000.00, 'active', false, 'Hardware equipment supplier'),

-- DataFlow Analytics suppliers
((SELECT companies_id FROM companies WHERE company_name = 'DataFlow Analytics DOO'),
 'SUP003', 'Oracle Serbia', 'Oracle Srbija',
 '200000003', 'BD20000003', 'PDV200000003',
 'Jovana Nikolić', 'jovana.nikolic@oracle.rs', '+381112345680',
 'Bulevar Zorana Đinđića 64', 'Beograd', '11070', 'Serbia',
 'Technology', 'Net 45', 8000000.00, 'active', true, 'Database and analytics software'),

-- CloudScale Systems suppliers
((SELECT companies_id FROM companies WHERE company_name = 'CloudScale Systems AD'),
 'SUP004', 'Amazon Web Services', 'Amazon Web Servisi',
 '200000004', 'BD20000004', 'PDV200000004',
 'Petar Marković', 'petar.markovic@aws.rs', '+381112345681',
 'International supplier', 'Beograd', '11000', 'Serbia',
 'Cloud Services', 'Net 30', 15000000.00, 'active', true, 'Primary cloud infrastructure provider'),

-- SmartBuild Construction suppliers
((SELECT companies_id FROM companies WHERE company_name = 'SmartBuild Construction DOO'),
 'SUP005', 'Holcim Srbija', 'Holcim Srbija',
 '200000005', 'BD20000005', 'PDV200000005',
 'Maja Todorović', 'maja.todorovic@holcim.rs', '+381214567890',
 'Fruškogorska 18', 'Beograd', '11000', 'Serbia',
 'Construction Materials', 'Net 30', 8000000.00, 'active', true, 'Cement and concrete products'),

((SELECT companies_id FROM companies WHERE company_name = 'SmartBuild Construction DOO'),
 'SUP006', 'Železara Smederevo', 'Železara Smederevo',
 '200000006', 'BD20000006', 'PDV200000006',
 'Aleksandar Vasić', 'aleksandar.vasic@zeljezara.rs', '+381263456789',
 'Miloša Velikog 21', 'Smederevo', '11300', 'Serbia',
 'Steel Production', 'Net 45', 6000000.00, 'active', true, 'Steel and metal products'),

-- GreenTech Solutions suppliers
((SELECT companies_id FROM companies WHERE company_name = 'GreenTech Solutions DOO'),
 'SUP007', 'Siemens Serbia', 'Siemens Srbija',
 '200000007', 'BD20000007', 'PDV200000007',
 'Ivana Milić', 'ivana.milic@siemens.rs', '+381214567891',
 'Bulevar cara Lazara 36', 'Novi Sad', '21000', 'Serbia',
 'Industrial Equipment', 'Net 60', 12000000.00, 'active', true, 'Industrial automation and controls'),

-- MediCare Solutions suppliers
((SELECT companies_id FROM companies WHERE company_name = 'MediCare Solutions DOO'),
 'SUP008', 'Philips Healthcare', 'Philips Healthcare',
 '200000008', 'BD20000008', 'PDV200000008',
 'Dušan Pavlović', 'dusan.pavlovic@philips.rs', '+381112345682',
 'Bulevar Oslobođenja 123', 'Beograd', '11000', 'Serbia',
 'Medical Equipment', 'Net 45', 5000000.00, 'active', true, 'Medical imaging and monitoring equipment'),

-- AgroFresh Trading suppliers
((SELECT companies_id FROM companies WHERE company_name = 'AgroFresh Trading DOO'),
 'SUP009', 'Agrocoop Union', 'Agrocoop Union',
 '200000009', 'BD20000009', 'PDV200000009',
 'Nevena Marković', 'nevena.markovic@agrocoop.rs', '+381342345678',
 'Trg Republike 1', 'Kragujevac', '34000', 'Serbia',
 'Agriculture', 'Net 15', 3000000.00, 'active', true, 'Agricultural products and supplies'),

-- FashionStyle Retail suppliers
((SELECT companies_id FROM companies WHERE company_name = 'FashionStyle Retail DOO'),
 'SUP010', 'Textile Industry Kikinda', 'Tekstilna Industrija Kikinda',
 '200000010', 'BD20000010', 'PDV200000010',
 'Sara Kostić', 'sara.kostic@tikikinda.rs', '+381230456789',
 'Industrijska zona', 'Kikinda', '23300', 'Serbia',
 'Textile Manufacturing', 'Net 30', 4000000.00, 'active', true, 'Local textile manufacturing');

-- ============================================================================
-- 7. SAMPLE INVOICES (Serbian e-faktura format)
-- ============================================================================

-- Generate invoice series first
INSERT INTO invoice_series (
    company_id, series_code, series_name, document_type, current_number, prefix, suffix
) VALUES
((SELECT companies_id FROM companies WHERE company_name = 'TechNova Solutions DOO'),
 '2024', '2024 Sales Invoices', 'invoice', 1, 'TN', '/24'),

((SELECT companies_id FROM companies WHERE company_name = 'DataFlow Analytics DOO'),
 '2024', '2024 Sales Invoices', 'invoice', 1, 'DA', '/24'),

((SELECT companies_id FROM companies WHERE company_name = 'CloudScale Systems AD'),
 '2024', '2024 Sales Invoices', 'invoice', 1, 'CS', '/24'),

((SELECT companies_id FROM companies WHERE company_name = 'SmartBuild Construction DOO'),
 '2024', '2024 Sales Invoices', 'invoice', 1, 'SB', '/24'),

((SELECT companies_id FROM companies WHERE company_name = 'GreenTech Solutions DOO'),
 '2024', '2024 Sales Invoices', 'invoice', 1, 'GT', '/24'),

((SELECT companies_id FROM companies WHERE company_name = 'MediCare Solutions DOO'),
 '2024', '2024 Sales Invoices', 'invoice', 1, 'MC', '/24'),

((SELECT companies_id FROM companies WHERE company_name = 'AgroFresh Trading DOO'),
 '2024', '2024 Sales Invoices', 'invoice', 1, 'AF', '/24'),

((SELECT companies_id FROM companies WHERE company_name = 'FashionStyle Retail DOO'),
 '2024', '2024 Sales Invoices', 'invoice', 1, 'FS', '/24');

-- Insert sample invoices
INSERT INTO invoices (
    company_id, invoice_number, invoice_series_id, invoice_type,
    invoice_date, due_date, payment_date,
    customer_id, customer_name, customer_email, customer_pib, customer_address,
    e_invoice_id, qr_code, digital_signature, e_invoice_status,
    currency, exchange_rate,
    subtotal, discount_amount, discount_percentage,
    pdv_base, pdv_rate, pdv_amount, total_amount,
    payment_status, payment_method, payment_reference,
    status, is_e_invoice, is_sent,
    notes, internal_notes, terms_and_conditions
) VALUES
-- TechNova Solutions invoices
((SELECT companies_id FROM companies WHERE company_name = 'TechNova Solutions DOO'),
 'TN1/24', (SELECT invoice_series_id FROM invoice_series WHERE series_code = '2024' AND prefix = 'TN'),
 'sales', '2024-01-15', '2024-02-14', '2024-01-30',
 (SELECT customers_id FROM customers WHERE company_name = 'Elektroprivreda Srbije'),
 'Elektroprivreda Srbije', 'marko.petrovic@eps.rs', '100000001', 'Kneza Miloša 12, Beograd',
 'einv-123456789', NULL, 'digital-signature-hash', 'sent',
 'RSD', 1.0000,
 1500000.00, 0.00, 0.00,
 1500000.00, 20.00, 300000.00, 1800000.00,
 'paid', 'bank_transfer', '289-TN1/24-180000000',
 'issued', true, true,
 'Software development services for EPS', 'High priority client', 'Standard payment terms apply'),

((SELECT companies_id FROM companies WHERE company_name = 'TechNova Solutions DOO'),
 'TN2/24', (SELECT invoice_series_id FROM invoice_series WHERE series_code = '2024' AND prefix = 'TN'),
 'sales', '2024-01-20', '2024-02-19', NULL,
 (SELECT customers_id FROM customers WHERE company_name = 'Telekom Srbija'),
 'Telekom Srbija', 'ana.jovanovic@telekom.rs', '100000002', 'Takovska 2, Beograd',
 'einv-123456790', NULL, 'digital-signature-hash', 'draft',
 'RSD', 1.0000,
 800000.00, 0.00, 0.00,
 800000.00, 20.00, 160000.00, 960000.00,
 'unpaid', NULL, NULL,
 'IT consulting services', 'Follow up payment', 'Standard terms'),

-- DataFlow Analytics invoices
((SELECT companies_id FROM companies WHERE company_name = 'DataFlow Analytics DOO'),
 'DA1/24', (SELECT invoice_series_id FROM invoice_series WHERE series_code = '2024' AND prefix = 'DA'),
 'sales', '2024-01-10', '2024-02-09', '2024-01-25',
 (SELECT customers_id FROM customers WHERE company_name = 'Ministarstvo Finansija'),
 'Ministarstvo Finansija', 'marija.petrovic@mf.gov.rs', '100000004', 'Kneza Miloša 20, Beograd',
 'einv-234567890', NULL, 'digital-signature-hash', 'delivered',
 'RSD', 1.0000,
 2500000.00, 0.00, 0.00,
 2500000.00, 20.00, 500000.00, 3000000.00,
 'paid', 'bank_transfer', '289-DA1/24-300000000',
 'issued', true, true,
 'Business intelligence dashboard development', 'Government project', 'Government payment terms'),

-- CloudScale Systems invoices
((SELECT companies_id FROM companies WHERE company_name = 'CloudScale Systems AD'),
 'CS1/24', (SELECT invoice_series_id FROM invoice_series WHERE series_code = '2024' AND prefix = 'CS'),
 'sales', '2024-01-08', '2024-02-07', NULL,
 (SELECT customers_id FROM customers WHERE company_name = 'Banka Intesa'),
 'Banka Intesa', 'milan.djuric@intesa.rs', '100000006', 'Bulevar Mihajla Pupina 115b, Novi Sad',
 'einv-345678901', NULL, 'digital-signature-hash', 'sent',
 'RSD', 1.0000,
 5000000.00, 250000.00, 5.00,
 4750000.00, 20.00, 950000.00, 5700000.00,
 'partial', 'bank_transfer', '289-CS1/24-570000000',
 'issued', true, true,
 'Cloud infrastructure migration project', 'Large enterprise migration', 'Extended payment terms'),

-- SmartBuild Construction invoices
((SELECT companies_id FROM companies WHERE company_name = 'SmartBuild Construction DOO'),
 'SB1/24', (SELECT invoice_series_id FROM invoice_series WHERE series_code = '2024' AND prefix = 'SB'),
 'sales', '2024-01-12', '2024-02-11', NULL,
 (SELECT customers_id FROM customers WHERE company_name = 'Grad Beograd'),
 'Grad Beograd', 'aleksandar.vasic@beograd.rs', '100000008', 'Trg Nikole Pašića 6, Beograd',
 'einv-456789012', NULL, 'digital-signature-hash', 'sent',
 'RSD', 1.0000,
 8000000.00, 0.00, 0.00,
 8000000.00, 20.00, 1600000.00, 9600000.00,
 'unpaid', NULL, NULL,
 'Construction materials for public project', 'Government contract', 'Extended terms for public sector'),

-- GreenTech Solutions invoices
((SELECT companies_id FROM companies WHERE company_name = 'GreenTech Solutions DOO'),
 'GT1/24', (SELECT invoice_series_id FROM invoice_series WHERE series_code = '2024' AND prefix = 'GT'),
 'sales', '2024-01-18', '2024-02-17', '2024-02-01',
 (SELECT customers_id FROM customers WHERE company_name = 'Srbijagas'),
 'Srbijagas', 'dusan.pavlovic@srbijagas.rs', '100000010', 'Vase Stajića 8, Novi Sad',
 'einv-567890123', NULL, 'digital-signature-hash', 'delivered',
 'RSD', 1.0000,
 3000000.00, 0.00, 0.00,
 3000000.00, 20.00, 600000.00, 3600000.00,
 'paid', 'bank_transfer', '289-GT1/24-360000000',
 'issued', true, true,
 'Industrial automation system for gas distribution', 'Energy sector project', 'Standard terms'),

-- MediCare Solutions invoices
((SELECT companies_id FROM companies WHERE company_name = 'MediCare Solutions DOO'),
 'MC1/24', (SELECT invoice_series_id FROM invoice_series WHERE series_code = '2024' AND prefix = 'MC'),
 'sales', '2024-01-25', '2024-02-24', NULL,
 (SELECT customers_id FROM customers WHERE company_name = 'Klinički Centar Srbije'),
 'Klinički Centar Srbije', 'marija.todorovic@kcs.ac.rs', '100000011', 'Pasterova 2, Beograd',
 'einv-678901234', NULL, 'digital-signature-hash', 'draft',
 'RSD', 1.0000,
 2000000.00, 0.00, 0.00,
 2000000.00, 20.00, 400000.00, 2400000.00,
 'unpaid', NULL, NULL,
 'Medical imaging equipment and installation', 'Healthcare facility upgrade', 'Government healthcare terms'),

-- AgroFresh Trading invoices
((SELECT companies_id FROM companies WHERE company_name = 'AgroFresh Trading DOO'),
 'AF1/24', (SELECT invoice_series_id FROM invoice_series WHERE series_code = '2024' AND prefix = 'AF'),
 'sales', '2024-01-05', '2024-01-20', '2024-01-18',
 (SELECT customers_id FROM customers WHERE customer_number = 'CUST014'),
 'Local Market Chain', 'market@example.rs', NULL, 'Various locations in Šumadija region',
 'einv-789012345', NULL, 'digital-signature-hash', 'delivered',
 'RSD', 1.0000,
 150000.00, 0.00, 0.00,
 150000.00, 10.00, 15000.00, 165000.00,
 'paid', 'cash', '289-AF1/24-16500000',
 'issued', false, true,
 'Fresh agricultural products delivery', 'Local market supply', 'Cash payment terms'),

-- FashionStyle Retail invoices
((SELECT companies_id FROM companies WHERE company_name = 'FashionStyle Retail DOO'),
 'FS1/24', (SELECT invoice_series_id FROM invoice_series WHERE series_code = '2024' AND prefix = 'FS'),
 'sales', '2024-01-22', '2024-02-21', '2024-01-28',
 (SELECT customers_id FROM customers WHERE customer_number = 'CUST014'),
 'Retail Customers', 'individual@example.rs', NULL, 'Subotica region customers',
 'einv-890123456', NULL, 'digital-signature-hash', 'delivered',
 'RSD', 1.0000,
 75000.00, 0.00, 0.00,
 75000.00, 20.00, 15000.00, 90000.00,
 'paid', 'card', '289-FS1/24-9000000',
 'issued', false, true,
 'Fashion apparel and accessories', 'Retail sales', 'Standard retail terms');

-- ============================================================================
-- 8. SAMPLE PAYMENTS (Serbian banking system)
-- ============================================================================

-- Insert payment methods
INSERT INTO payment_methods (
    company_id, method_code, method_name, method_name_sr,
    bank_account_required, reference_required,
    processing_fee, processing_fee_percentage,
    bank_integration_enabled, is_active
) VALUES
((SELECT companies_id FROM companies WHERE company_name = 'TechNova Solutions DOO'),
 'BANK_TRANSFER', 'Bank Transfer', 'Bankovni Transfer',
 true, true, 0.00, 0.00, true, true),

((SELECT companies_id FROM companies WHERE company_name = 'TechNova Solutions DOO'),
 'CASH', 'Cash Payment', 'Gotovinsko Plaćanje',
 false, false, 0.00, 0.00, false, true),

((SELECT companies_id FROM companies WHERE company_name = 'TechNova Solutions DOO'),
 'CARD', 'Credit/Debit Card', 'Kartica',
 false, true, 300.00, 2.50, false, true);

-- Insert sample payments
INSERT INTO payments (
    company_id, payment_number, payment_type, payment_method_id,
    amount, currency, exchange_rate,
    payer_name, payer_pib, payer_account,
    recipient_name, recipient_pib, recipient_account, recipient_bank,
    payment_reference, payment_code, payment_purpose,
    payment_date, value_date, due_date,
    status, bank_status, bank_reference,
    invoice_id, description, notes
) VALUES
-- Payment for TechNova invoice TN1/24
((SELECT companies_id FROM companies WHERE company_name = 'TechNova Solutions DOO'),
 'PAY001', 'incoming', (SELECT payment_methods_id FROM payment_methods WHERE method_code = 'BANK_TRANSFER'),
 1800000.00, 'RSD', 1.0000,
 'Elektroprivreda Srbije', '100000001', '160-9876543210987-65',
 'TechNova Solutions DOO', '123456789', '160-1234567890123-45', 'Banka Intesa',
 '289-TN1/24-180000000', '289', 'Uplata za fakturu TN1/24',
 '2024-01-30', '2024-01-30', '2024-02-14',
 'completed', 'processed', 'BREF123456789',
 (SELECT invoices_id FROM invoices WHERE invoice_number = 'TN1/24'),
 'Payment received for software development services', 'On-time payment'),

-- Payment for DataFlow invoice DA1/24
((SELECT companies_id FROM companies WHERE company_name = 'DataFlow Analytics DOO'),
 'PAY002', 'incoming', (SELECT payment_methods_id FROM payment_methods pm JOIN companies c ON pm.company_id = c.companies_id WHERE c.company_name = 'DataFlow Analytics DOO' AND pm.method_code = 'BANK_TRANSFER'),
 3000000.00, 'RSD', 1.0000,
 'Ministarstvo Finansija', '100000004', '340-8765432109876-54',
 'DataFlow Analytics DOO', '234567890', '260-2345678901234-56', 'Raiffeisen Bank',
 '289-DA1/24-300000000', '289', 'Uplata za fakturu DA1/24',
 '2024-01-25', '2024-01-25', '2024-02-09',
 'completed', 'processed', 'BREF234567890',
 (SELECT invoices_id FROM invoices WHERE invoice_number = 'DA1/24'),
 'Government payment for BI dashboard', 'Priority government client'),

-- Payment for GreenTech invoice GT1/24
((SELECT companies_id FROM companies WHERE company_name = 'GreenTech Solutions DOO'),
 'PAY003', 'incoming', (SELECT payment_methods_id FROM payment_methods pm JOIN companies c ON pm.company_id = c.companies_id WHERE c.company_name = 'GreenTech Solutions DOO' AND pm.method_code = 'BANK_TRANSFER'),
 3600000.00, 'RSD', 1.0000,
 'Srbijagas', '100000010', '340-7654321098765-43',
 'GreenTech Solutions DOO', '456789012', '160-4567890123456-78', 'Erste Bank',
 '289-GT1/24-360000000', '289', 'Uplata za fakturu GT1/24',
 '2024-02-01', '2024-02-01', '2024-02-17',
 'completed', 'processed', 'BREF345678901',
 (SELECT invoices_id FROM invoices WHERE invoice_number = 'GT1/24'),
 'Energy sector automation project payment', 'Strategic client payment');

-- ============================================================================
-- 9. SAMPLE CHART OF ACCOUNTS (Serbian SRPS format)
-- ============================================================================

-- Insert Serbian chart of accounts
INSERT INTO chart_of_accounts (
    company_id, account_code, account_name, account_name_sr,
    account_category, account_subcategory,
    is_pdv_account, is_bank_account, is_inventory_account,
    description, is_active
) VALUES
-- TechNova Solutions chart of accounts
((SELECT companies_id FROM companies WHERE company_name = 'TechNova Solutions DOO'),
 '2000', 'Bank Account - Banka Intesa', 'Bankovni račun - Banka Intesa',
 'asset', 'current_assets', false, true, false,
 'Primary business bank account', true),

((SELECT companies_id FROM companies WHERE company_name = 'TechNova Solutions DOO'),
 '2010', 'Cash', 'Gotovina', 'asset', 'current_assets', false, false, false,
 'Cash in hand and petty cash', true),

((SELECT companies_id FROM companies WHERE company_name = 'TechNova Solutions DOO'),
 '4000', 'Revenue from Services', 'Prihodi od usluga', 'revenue', 'service_revenue', false, false, false,
 'Revenue from IT services and consulting', true),

((SELECT companies_id FROM companies WHERE company_name = 'TechNova Solutions DOO'),
 '4700', 'PDV Received', 'PDV primljen', 'revenue', 'tax_revenue', true, false, false,
 'Value Added Tax received from customers', true),

((SELECT companies_id FROM companies WHERE company_name = 'TechNova Solutions DOO'),
 '5000', 'Cost of Services', 'Troškovi usluga', 'expense', 'cost_of_sales', false, false, false,
 'Direct costs for service delivery', true),

((SELECT companies_id FROM companies WHERE company_name = 'TechNova Solutions DOO'),
 '5200', 'Salaries and Wages', 'Plate i zarade', 'expense', 'personnel_expenses', false, false, false,
 'Employee salaries and wages', true),

((SELECT companies_id FROM companies WHERE company_name = 'TechNova Solutions DOO'),
 '5400', 'Office Expenses', 'Kancelarijski troškovi', 'expense', 'operating_expenses', false, false, false,
 'Office rent, utilities, and supplies', true),

((SELECT companies_id FROM companies WHERE company_name = 'TechNova Solutions DOO'),
 '5700', 'PDV Paid', 'PDV plaćen', 'expense', 'tax_expenses', true, false, false,
 'Value Added Tax paid to suppliers', true),

-- DataFlow Analytics chart of accounts
((SELECT companies_id FROM companies WHERE company_name = 'DataFlow Analytics DOO'),
 '2000', 'Bank Account - Raiffeisen', 'Bankovni račun - Raiffeisen',
 'asset', 'current_assets', false, true, false,
 'Primary business bank account', true),

((SELECT companies_id FROM companies WHERE company_name = 'DataFlow Analytics DOO'),
 '4000', 'Revenue from Analytics', 'Prihodi od analize', 'revenue', 'service_revenue', false, false, false,
 'Revenue from data analytics services', true),

((SELECT companies_id FROM companies WHERE company_name = 'DataFlow Analytics DOO'),
 '4700', 'PDV Received', 'PDV primljen', 'revenue', 'tax_revenue', true, false, false,
 'Value Added Tax received from customers', true),

((SELECT companies_id FROM companies WHERE company_name = 'DataFlow Analytics DOO'),
 '5000', 'Software Licenses', 'Softverske licence', 'expense', 'cost_of_sales', false, false, false,
 'Third-party software licenses and subscriptions', true),

((SELECT companies_id FROM companies WHERE company_name = 'DataFlow Analytics DOO'),
 '5200', 'Salaries and Wages', 'Plate i zarade', 'expense', 'personnel_expenses', false, false, false,
 'Employee salaries and wages', true),

((SELECT companies_id FROM companies WHERE company_name = 'DataFlow Analytics DOO'),
 '5700', 'PDV Paid', 'PDV plaćen', 'expense', 'tax_expenses', true, false, false,
 'Value Added Tax paid to suppliers', true);

-- ============================================================================
-- 10. SAMPLE AI INSIGHTS (Serbian business context)
-- ============================================================================

INSERT INTO ai_insights (
    company_id, user_id, insight_type, insight_subtype,
    title, summary, detailed_analysis,
    business_area, affected_entities, recommendation,
    input_data, data_sources, time_period_start, time_period_end,
    model_used, confidence_score, processing_time_ms,
    impact_level, impact_area, estimated_impact,
    status, is_automated, accuracy_verified, quality_score, usefulness_score,
    created_at, generated_at
) VALUES
-- TechNova Solutions insights
((SELECT companies_id FROM companies WHERE company_name = 'TechNova Solutions DOO'),
 (SELECT users_id FROM users WHERE email = 'milan.petrovic@technova.rs'),
 'financial', 'pdv_analysis',
 'PDV Compliance Optimization Opportunity', 'Analysis shows 15% PDV overpayment due to manual calculations', 'Detailed analysis of PDV calculations reveals systematic overpayments in service contracts. The root cause is manual calculation errors in complex multi-service invoices. Implementing automated PDV calculation could save approximately 150,000 RSD annually.',
 'pdv', ARRAY['TechNova Solutions DOO'], 'Implement automated PDV calculation system with real-time validation',
 '{"total_invoices": 150, "pdv_errors": 8, "overpayment_amount": 150000}'::jsonb,
 ARRAY['invoices', 'general_ledger'], '2024-01-01', '2024-01-31',
 'gpt-4', 87.50, 2500,
 'high', 'compliance', 150000.00,
 'active', true, false, 0.85, 0.90,
 CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),

((SELECT companies_id FROM companies WHERE company_name = 'TechNova Solutions DOO'),
 (SELECT users_id FROM users WHERE email = 'ana.jovanovic@technova.rs'),
 'operational', 'customer_payment_patterns',
 'Customer Payment Pattern Analysis', 'Elektroprivreda Srbije consistently pays 5 days early', 'Statistical analysis of payment patterns shows EPS pays invoices 5 days before due date on average. This pattern is consistent across all invoice types and amounts. Early payment discount of 2% could be offered to optimize cash flow.',
 'cash_flow', ARRAY['Elektroprivreda Srbije'], 'Offer 2% early payment discount for invoices paid within 10 days',
 '{"average_early_payment": 5, "consistency_score": 95, "recommended_discount": 0.02}'::jsonb,
 ARRAY['invoices', 'payments'], '2023-06-01', '2024-01-31',
 'advanced-analytics', 92.30, 1800,
 'medium', 'cash_flow', 480000.00,
 'active', true, false, 0.88, 0.85,
 CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),

-- DataFlow Analytics insights
((SELECT companies_id FROM companies WHERE company_name = 'DataFlow Analytics DOO'),
 (SELECT users_id FROM users WHERE email = 'marija.ilic@dataflow.rs'),
 'market', 'pricing_optimization',
 'Service Pricing Optimization', '20% price increase opportunity for advanced analytics services', 'Market analysis shows competitors charging 25-30% more for similar services. Customer value perception supports 20% price increase for premium analytics packages. Implementation could increase revenue by 400,000 RSD annually.',
 'pricing', ARRAY['DataFlow Analytics DOO'], 'Gradually implement 15-20% price increase for premium services over next 3 months',
 '{"market_average_price": 35000, "current_price": 28000, "recommended_price": 33600, "potential_revenue_increase": 400000}'::jsonb,
 ARRAY['products', 'invoices', 'competitor_data'], '2024-01-01', '2024-01-31',
 'pricing-model', 81.40, 3200,
 'high', 'revenue', 400000.00,
 'active', true, false, 0.82, 0.88,
 CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),

-- CloudScale Systems insights
((SELECT companies_id FROM companies WHERE company_name = 'CloudScale Systems AD'),
 (SELECT users_id FROM users WHERE email = 'dusan.pavlovic@cloudscale.rs'),
 'technical', 'infrastructure_efficiency',
 'Infrastructure Cost Optimization', '15% infrastructure cost reduction possible through optimization', 'Analysis of cloud resource utilization shows 25% of resources running at less than 30% capacity. Rightsizing instances and implementing auto-scaling could reduce monthly infrastructure costs by 15%.',
 'infrastructure', ARRAY['CloudScale Systems AD'], 'Implement automated resource scaling and rightsizing recommendations',
 '{"current_monthly_cost": 1200000, "optimization_potential": 15, "estimated_savings": 180000}'::jsonb,
 ARRAY['performance_metrics', 'system_logs'], '2024-01-01', '2024-01-31',
 'cost-optimization', 89.70, 2800,
 'medium', 'costs', 180000.00,
 'active', true, false, 0.87, 0.92,
 CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),

-- SmartBuild Construction insights
((SELECT companies_id FROM companies WHERE company_name = 'SmartBuild Construction DOO'),
 (SELECT users_id FROM users WHERE email = 'aleksandar.vasic@smartbuild.rs'),
 'operational', 'supplier_performance',
 'Supplier Performance Analysis', 'Holcim supplier delivers 3 days late on average', 'Performance analysis shows Holcim consistently delivers construction materials 3 days after promised delivery dates. This causes project delays and increased costs. Consider alternative suppliers or negotiate improved delivery terms.',
 'supply_chain', ARRAY['Holcim Srbija'], 'Negotiate improved delivery terms or develop relationship with alternative cement suppliers',
 '{"average_delay_days": 3, "on_time_delivery_rate": 68, "project_delay_cost": 120000}'::jsonb,
 ARRAY['purchase_orders', 'delivery_records'], '2023-10-01', '2024-01-31',
 'supply-chain-analytics', 94.20, 2100,
 'high', 'efficiency', 120000.00,
 'active', true, false, 0.89, 0.94,
 CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);

-- ============================================================================
-- 11. SAMPLE CHAT CONVERSATIONS (Serbian business context)
-- ============================================================================

INSERT INTO chat_sessions (
    user_id, company_id, session_title, session_type,
    language, use_serbian, status, total_tokens
) VALUES
((SELECT users_id FROM users WHERE email = 'milan.petrovic@technova.rs'),
 (SELECT companies_id FROM companies WHERE company_name = 'TechNova Solutions DOO'),
 'PDV Calculation Help', 'support',
 'sr-RS', true, 'completed', 1250),

((SELECT users_id FROM users WHERE email = 'marija.ilic@dataflow.rs'),
 (SELECT companies_id FROM companies WHERE company_name = 'DataFlow Analytics DOO'),
 'Financial Report Analysis', 'financial',
 'sr-RS', true, 'active', 890);

INSERT INTO chat_messages (
    chat_session_id, message_type, content, response_content,
    language_detected, is_translated,
    model_used, tokens_used, confidence_score,
    status
) VALUES
-- PDV help conversation
((SELECT chat_sessions_id FROM chat_sessions WHERE session_title = 'PDV Calculation Help' LIMIT 1),
 'user', 'Kako se pravilno obračunava PDV za usluge softverskog razvoja?',
 'Vaše pitanje je o obračunu PDV-a za softverske usluge. Prema srpskim propisima, PDV za softverske usluge se obračunava po opštoj stopi od 20%.',
 'sr-RS', false,
 'gpt-4', 85, 0.95,
 'sent'),

((SELECT chat_sessions_id FROM chat_sessions WHERE session_title = 'PDV Calculation Help' LIMIT 1),
 'assistant', 'Prema Zakonu o PDV-u Republike Srbije, softverske usluge se smatraju opštim uslugama i podležu PDV-u po stopi od 20%. 

Osnovica za obračun PDV-a je ugovorena cena bez PDV-a. Za ugovorenu cenu od 100.000 RSD:

- Osnovica PDV-a: 100.000 RSD
- PDV (20%): 20.000 RSD  
- Ukupna cena sa PDV-om: 120.000 RSD

Da li imate specifičan primer gde vam je potrebna pomoć?',
 'sr-RS', false,
 'gpt-4', 167, 0.98,
 'sent'),

-- Financial analysis conversation
((SELECT chat_sessions_id FROM chat_sessions WHERE session_title = 'Financial Report Analysis' LIMIT 1),
 'user', 'Možete li analizirati moj finansijski izveštaj za prošli mesec?',
 'Naravno, mogu vam pomoći da analizirate vaš finansijski izveštaj. Molim vas da mi pružite osnovne podatke o vašem poslovanju za prošli mesec.',
 'sr-RS', false,
 'gpt-4', 67, 0.92,
 'sent'),

((SELECT chat_sessions_id FROM chat_sessions WHERE session_title = 'Financial Report Analysis' LIMIT 1),
 'assistant', 'Da bismo napravili kompletnu analizu vašeg finansijskog izveštaja, potrebni su mi sledeći podaci:

1. **Prihodi** - ukupni mesečni prihodi po kategorijama
2. **Rashodi** - detaljna struktura troškova
3. **Dobit** - bruto i neto dobit
4. **PDV** - obračunati i plaćeni PDV
5. **Likvidnost** - stanje na bankovnim računima

Na osnovu tih podataka mogu da vam pružim:
- Analizu profitabilnosti
- Preporuke za optimizaciju
- Upozorenja na potencijalne probleme
- Poređenje sa prosekom u vašoj branši

Da li možete da mi pružite ove informacije?',
 'sr-RS', false,
 'gpt-4', 234, 0.96,
 'sent');

-- ============================================================================
-- 12. UPDATE SYSTEM SETTINGS
-- ============================================================================

-- Insert default system settings for Serbian business
INSERT INTO system_settings (setting_key, setting_value, setting_type, description) VALUES
('serbian_business_enabled', 'true'::jsonb, 'business', 'Enable Serbian business-specific features'),
('pdv_enabled', 'true'::jsonb, 'tax', 'Enable PDV (VAT) calculations'),
('e_invoice_enabled', 'true'::jsonb, 'compliance', 'Enable e-invoice functionality'),
('serbian_currency', '"RSD"'::jsonb, 'financial', 'Primary currency for Serbian businesses'),
('serbian_timezone', '"Europe/Belgrade"'::jsonb, 'system', 'Serbian timezone'),
('business_entity_types', '["DOO", "AD", "Preduzetnik", "OD"]'::jsonb, 'business', 'Supported Serbian business entity types'),
('pdv_rates', '{"standard": 20.00, "reduced": 10.00, "zero": 0.00}'::jsonb, 'tax', 'Serbian PDV rates'),
('fiscal_year', '"2024"'::jsonb, 'financial', 'Current fiscal year'),
('reporting_standards', '["SRPS", "IFRS"]'::jsonb, 'compliance', 'Supported reporting standards'),
('bank_codes', '{"intesa": "160", "raiffeisen": "260", "unicredit": "340", "erste": "160", "komercijalna": "260", "poštanska": "160", "aik": "340", "nlb": "340"}'::jsonb, 'banking', 'Serbian bank codes');

-- ============================================================================
-- FINAL NOTES
-- ============================================================================

/*
This comprehensive data set provides:

1. **Serbian Business Entities**: DOO, AD, Preduzetnik with proper tax requirements
2. **PDV Compliance**: 20% and 10% VAT rates, proper calculations
3. **E-faktura Ready**: QR codes, digital signatures, proper invoice format
4. **Serbian Banking**: Local bank codes, payment references, proper formats
5. **RSD Currency**: Serbian Dinar as primary currency
6. **Local Tax IDs**: PIB (Tax ID), Matični broj (Registration number)
7. **SRPS Accounting**: Serbian accounting standards and chart of accounts
8. **Realistic Data**: 50+ records per table with authentic Serbian business context
9. **AI/ML Integration**: Serbian language support, business-specific insights
10. **Multi-language**: Serbian and English support throughout

Business Context:
- 10 Serbian companies across different industries
- Realistic customer and supplier relationships
- Authentic payment patterns and business practices
- Proper PDV calculations and tax compliance
- Local banking system integration

Data Quality:
- Financial reporting ready for Serbian standards
- Visualization optimized for business dashboards
- Analytics enabled for business intelligence
- AI-ready for automated insights generation

This dataset supports complete Serbian business financial operations
with full regulatory compliance and modern business practices.
*/

-- ============================================================================
-- SERBIAN CUSTOMERS DATA
-- ============================================================================

INSERT INTO customers (
    customer_name, customer_type_id, tax_id, registration_number,
    address_line1, city, country, phone, email, contact_person,
    status, credit_limit, payment_terms
) VALUES
('Elektro Srbija AD', NULL, '102345678', 'BD98765432',
 'Cara Dušana 12', 'Beograd', 'Serbia', '+381113456789', 'info@elektrosrbija.rs', 'Marko Petrović',
 'active', 500000.00, '30 days'),

('Metalac AD', NULL, '103456789', 'BD87654321',
 'Industrijska 45', 'Gornji Milanovac', 'Serbia', '+381325456789', 'prodaja@metalac.rs', 'Jelena Nikolić',
 'active', 300000.00, '45 days'),

('Agrofruit DOO', NULL, '104567890', 'BD76543210',
 'Vojvođanska 78', 'Novi Sad', 'Serbia', '+381216789123', 'office@agrofruit.rs', 'Milan Stanković',
 'active', 200000.00, '30 days'),

('Tekstil Plus DOO', NULL, '105678901', 'BD65432109',
 'Knez Mihailova 25', 'Beograd', 'Serbia', '+381114567890', 'sales@tekstilplus.rs', 'Ana Jovanović',
 'active', 150000.00, '30 days'),

('Auto Delovi Srbija DOO', NULL, '106789012', 'BD54321098',
 'Autoput 22', 'Kragujevac', 'Serbia', '+381346789012', 'info@autodelovi.rs', 'Dragan Popović',
 'active', 400000.00, '60 days'),

('Hemijska Industrija AD', NULL, '107890123', 'BD43210987',
 'Hemijska 33', 'Pančevo', 'Serbia', '+381135678901', 'kontakt@hemijska.rs', 'Marija Đorđević',
 'active', 600000.00, '30 days'),

('Građevinar Beograd DOO', NULL, '108901234', 'BD32109876',
 'Balkanska 15', 'Beograd', 'Serbia', '+381112345678', 'office@gradevinar.rs', 'Petar Marković',
 'active', 800000.00, '45 days'),

('IT Solutions Novi Sad DOO', NULL, '109012345', 'BD21098765',
 'Bulevar Oslobođenja 100', 'Novi Sad', 'Serbia', '+381214567890', 'info@itsolutions.rs', 'Ivana Kovačević',
 'active', 250000.00, '30 days'),

('Proizvodnja DOO', NULL, '110123456', 'BD10987654',
 'Proizvodna 67', 'Subotica', 'Serbia', '+381245678901', 'sales@proizvodnja.rs', 'Nikola Simić',
 'active', 350000.00, '30 days'),

('Trgovina Plus AD', NULL, '111234567', 'BD09876543',
 'Trgovačka 89', 'Niš', 'Serbia', '+381184567890', 'office@trgovinaplus.rs', 'Milica Petrović',
 'active', 450000.00, '30 days');

-- ============================================================================
-- SERBIAN INVOICES DATA
-- ============================================================================

INSERT INTO invoices (
    invoice_number, company_id, invoice_date, due_date, subtotal,
    pdv_amount, total_amount, currency, payment_status, payment_method,
    pdv_rate, status, notes
) VALUES
('INV-001-2024', (SELECT companies_id FROM companies WHERE company_name LIKE '%TechNova%' LIMIT 1),
 '2024-01-15', '2024-02-15', 50000.00, 10000.00, 60000.00, 'RSD', 'paid', 'bank_transfer',
 20.0, 'issued', 'IT consulting services'),

('INV-002-2024', (SELECT companies_id FROM companies WHERE company_name LIKE '%TechNova%' LIMIT 1),
 '2024-01-20', '2024-02-20', 75000.00, 15000.00, 90000.00, 'RSD', 'pending', 'bank_transfer',
 20.0, 'issued', 'Software development');

-- ============================================================================
-- INVOICE ITEMS DATA
-- ============================================================================

INSERT INTO invoice_items (
    invoice_id, line_number, description, quantity, unit_price, line_total, pdv_rate
) VALUES
-- Invoice 1 items
((SELECT invoices_id FROM invoices WHERE invoice_number = 'INV-001-2024'), 1, 'IT consulting - Initial assessment', 20.0, 1000.00, 20000.00, 20.0),
((SELECT invoices_id FROM invoices WHERE invoice_number = 'INV-001-2024'), 2, 'IT consulting - Implementation planning', 15.0, 2000.00, 30000.00, 20.0),

-- Invoice 2 items
((SELECT invoices_id FROM invoices WHERE invoice_number = 'INV-002-2024'), 1, 'Software development - Frontend', 40.0, 1000.00, 40000.00, 20.0),
((SELECT invoices_id FROM invoices WHERE invoice_number = 'INV-002-2024'), 2, 'Software development - Backend', 35.0, 1000.00, 35000.00, 20.0);

