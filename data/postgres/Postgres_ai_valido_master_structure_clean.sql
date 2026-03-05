-- ============================================================================
-- VALIDOAI MASTER DATABASE STRUCTURE - CLEAN VERSION
-- ============================================================================
-- Simplified version that works with standard PostgreSQL installation
-- Focuses on core AI features and Unicode support
-- ============================================================================

-- ============================================================================
-- DATABASE CONNECTION INFO
-- ============================================================================
-- Host: localhost
-- Port: 5432
-- Database: ai_valido_online
-- Username: postgres
-- Password: postgres

-- Connect to the database
-- \c ai_valido_online postgres;

-- ============================================================================
-- EXTENSIONS (ONLY AVAILABLE ONES)
-- ============================================================================

-- Basic extensions that should be available
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";
CREATE EXTENSION IF NOT EXISTS "pg_buffercache";
CREATE EXTENSION IF NOT EXISTS "pg_prewarm";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "btree_gist";
CREATE EXTENSION IF NOT EXISTS "btree_gin";
CREATE EXTENSION IF NOT EXISTS "unaccent";
CREATE EXTENSION IF NOT EXISTS "fuzzystrmatch";

-- ============================================================================
-- SECURITY ROLES
-- ============================================================================

-- Create roles for different access levels
DO $$
BEGIN
    -- Only create roles if they don't exist
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'ai_valido_superadmin') THEN
        CREATE ROLE ai_valido_superadmin LOGIN PASSWORD 'superadmin123';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'ai_valido_admin') THEN
        CREATE ROLE ai_valido_admin LOGIN PASSWORD 'admin123';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'ai_valido_user') THEN
        CREATE ROLE ai_valido_user LOGIN PASSWORD 'user123';
    END IF;
END
$$;

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE ai_valido_online TO ai_valido_superadmin;
GRANT ALL PRIVILEGES ON DATABASE ai_valido_online TO ai_valido_admin;

-- ============================================================================
-- CORE TABLES
-- ============================================================================

-- Countries with Unicode support
DROP TABLE IF EXISTS countries CASCADE;
CREATE TABLE countries (
    countries_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    country_code VARCHAR(3) UNIQUE NOT NULL,
    iso_code VARCHAR(2) UNIQUE NOT NULL,
    country_name VARCHAR(100) NOT NULL,
    country_name_sr VARCHAR(100), -- Serbian name
    currency_code VARCHAR(3),
    phone_code VARCHAR(5),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Currencies
DROP TABLE IF EXISTS currencies CASCADE;
CREATE TABLE currencies (
    currencies_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    code VARCHAR(3) UNIQUE NOT NULL,
    name VARCHAR(50) NOT NULL,
    name_sr VARCHAR(50), -- Serbian name
    symbol VARCHAR(10),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Business entity types
DROP TABLE IF EXISTS business_entity_types CASCADE;
CREATE TABLE business_entity_types (
    business_entity_types_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    entity_code VARCHAR(20) UNIQUE NOT NULL,
    entity_name VARCHAR(100) NOT NULL,
    entity_name_sr VARCHAR(100), -- Serbian name
    description TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Business areas
DROP TABLE IF EXISTS business_areas CASCADE;
CREATE TABLE business_areas (
    business_areas_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    area_code VARCHAR(20) UNIQUE NOT NULL,
    area_name VARCHAR(100) NOT NULL,
    area_name_sr VARCHAR(100), -- Serbian name
    description TEXT,
    tax_rates JSONB,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Main companies table with Unicode support
DROP TABLE IF EXISTS companies CASCADE;
CREATE TABLE companies (
    companies_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_name VARCHAR(255) NOT NULL,
    legal_name VARCHAR(255),
    tax_id VARCHAR(20) UNIQUE NOT NULL,
    registration_number VARCHAR(20) UNIQUE,
    business_entity_type_id UUID REFERENCES business_entity_types(business_entity_types_id),
    business_area_id UUID REFERENCES business_areas(business_areas_id),
    country_id UUID REFERENCES countries(countries_id),

    -- Address information with Unicode support
    address_line1 VARCHAR(255),
    address_line2 VARCHAR(255),
    city VARCHAR(100),
    postal_code VARCHAR(20),
    phone VARCHAR(20),
    email VARCHAR(255),
    website VARCHAR(255),

    -- Company details
    founding_date DATE,
    currency_id UUID REFERENCES currencies(currencies_id),
    status VARCHAR(20) DEFAULT 'active',
    is_pdv_registered BOOLEAN DEFAULT false,

    -- Business information with Unicode support
    description TEXT, -- Company description in any language
    business_description TEXT, -- Detailed business description
    strengths TEXT,
    weaknesses TEXT,
    opportunities TEXT,
    threats TEXT,

    -- Financial information
    employee_count INTEGER,
    annual_revenue DECIMAL(15,2),
    market_share DECIMAL(5,2),
    customer_count INTEGER,
    product_count INTEGER,

    -- AI and analytics
    embedding_vector TEXT, -- Store as base64 or simplified format
    tags JSONB,
    custom_fields JSONB,

    -- Status
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by UUID,
    updated_by UUID
);

-- Users table with Unicode support
DROP TABLE IF EXISTS users CASCADE;
CREATE TABLE users (
    users_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    companies_id UUID REFERENCES companies(companies_id),
    username VARCHAR(100) UNIQUE,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(20),

    -- Personal information with Unicode support
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    full_name VARCHAR(255), -- For easier searching in any language

    -- Authentication
    password_hash VARCHAR(255),
    is_active BOOLEAN DEFAULT true,
    email_verified BOOLEAN DEFAULT false,
    phone_verified BOOLEAN DEFAULT false,

    -- Profile with Unicode support
    bio TEXT,
    avatar_url VARCHAR(500),
    timezone VARCHAR(50) DEFAULT 'Europe/Belgrade',
    language VARCHAR(5) DEFAULT 'sr-RS',

    -- Preferences
    theme VARCHAR(20) DEFAULT 'light',
    notifications_enabled BOOLEAN DEFAULT true,

    -- Role and permissions
    user_role VARCHAR(50) DEFAULT 'user',
    permissions JSONB,

    -- Audit
    last_login TIMESTAMP,
    login_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by UUID,
    updated_by UUID
);

-- Customer feedback with full Unicode support
DROP TABLE IF EXISTS customer_feedback CASCADE;
CREATE TABLE customer_feedback (
    customer_feedback_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    companies_id UUID NOT NULL REFERENCES companies(companies_id),
    customers_id UUID,
    users_id UUID REFERENCES users(users_id),

    -- Content with full Unicode support
    feedback_type VARCHAR(20) DEFAULT 'review',
    feedback_source VARCHAR(20) DEFAULT 'website',
    title VARCHAR(255),
    content TEXT NOT NULL, -- Supports any Unicode language
    content_language VARCHAR(5) DEFAULT 'sr-RS', -- Language code
    content_hash VARCHAR(64),

    -- Sentiment analysis
    sentiment_score DECIMAL(3,2), -- -1.0 to 1.0
    sentiment_label VARCHAR(20), -- positive, negative, neutral
    sentiment_confidence DECIMAL(3,2),

    -- AI analysis
    topics_detected JSONB,
    keywords_extracted JSONB,
    urgency_level VARCHAR(20), -- low, medium, high, critical
    intent_detected VARCHAR(50),
    entities_mentioned JSONB,

    -- Response tracking
    response_required BOOLEAN DEFAULT false,
    response_status VARCHAR(20) DEFAULT 'pending',
    response_priority VARCHAR(20) DEFAULT 'medium',
    assigned_to UUID REFERENCES users(users_id),
    responded_at TIMESTAMP,
    response_content TEXT,

    -- Customer satisfaction
    rating_given INTEGER CHECK (rating_given >= 1 AND rating_given <= 5),
    nps_score INTEGER CHECK (nps_score >= 0 AND nps_score <= 10),
    would_recommend BOOLEAN,

    -- AI processing
    ai_processed BOOLEAN DEFAULT false,
    ai_processed_at TIMESTAMP,
    ai_model_used VARCHAR(100),
    ai_processing_duration_ms INTEGER,

    -- Metadata
    tags JSONB,
    custom_fields JSONB,
    is_public BOOLEAN DEFAULT false,
    is_anonymous BOOLEAN DEFAULT false,

    -- Audit
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(users_id),
    updated_by UUID REFERENCES users(users_id)
);

-- AI Models registry
DROP TABLE IF EXISTS ai_models CASCADE;
CREATE TABLE ai_models (
    ai_models_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    companies_id UUID REFERENCES companies(companies_id),
    model_name VARCHAR(100) NOT NULL,
    model_type VARCHAR(50) NOT NULL,
    provider VARCHAR(50) NOT NULL,
    model_family VARCHAR(50),

    -- Configuration
    model_version VARCHAR(20),
    model_size VARCHAR(20),
    context_window INTEGER DEFAULT 4096,
    max_tokens INTEGER,
    temperature DECIMAL(3,2) DEFAULT 0.7,
    api_key_required BOOLEAN DEFAULT true,

    -- Capabilities
    supported_languages JSONB,
    supported_tasks JSONB,
    model_limitations TEXT,

    -- Status
    is_active BOOLEAN DEFAULT true,
    deployment_status VARCHAR(20) DEFAULT 'available',
    usage_count INTEGER DEFAULT 0,

    -- Cost management
    cost_per_request DECIMAL(6,4),
    monthly_cost_limit DECIMAL(10,2),
    current_monthly_cost DECIMAL(10,2) DEFAULT 0,

    -- Audit
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(users_id),
    updated_by UUID REFERENCES users(users_id)
);

-- ============================================================================
-- INDEXES FOR PERFORMANCE AND SEARCH
-- ============================================================================

-- Companies indexes
CREATE INDEX IF NOT EXISTS idx_companies_active ON companies (is_active) WHERE is_active = true;
CREATE INDEX IF NOT EXISTS idx_companies_tax_id ON companies (tax_id);
CREATE INDEX IF NOT EXISTS idx_companies_business_entity ON companies (business_entity_type_id);
CREATE INDEX IF NOT EXISTS idx_companies_business_area ON companies (business_area_id);

-- Full-text search indexes with Unicode support
CREATE INDEX IF NOT EXISTS idx_companies_fts ON companies
USING GIN (to_tsvector('simple', company_name || ' ' || COALESCE(description, '')));
CREATE INDEX IF NOT EXISTS idx_companies_name_normalized ON companies (lower(unaccent(company_name)));

-- Users indexes
CREATE INDEX IF NOT EXISTS idx_users_active ON users (is_active) WHERE is_active = true;
CREATE INDEX IF NOT EXISTS idx_users_email ON users (email);
CREATE INDEX IF NOT EXISTS idx_users_company ON users (companies_id);
CREATE INDEX IF NOT EXISTS idx_users_fts ON users
USING GIN (to_tsvector('simple', first_name || ' ' || last_name || ' ' || COALESCE(bio, '')));

-- Customer feedback indexes
CREATE INDEX IF NOT EXISTS idx_customer_feedback_company ON customer_feedback (companies_id);
CREATE INDEX IF NOT EXISTS idx_customer_feedback_sentiment ON customer_feedback (sentiment_label);
CREATE INDEX IF NOT EXISTS idx_customer_feedback_urgency ON customer_feedback (urgency_level);
CREATE INDEX IF NOT EXISTS idx_customer_feedback_created ON customer_feedback (created_at DESC);
CREATE INDEX IF NOT EXISTS idx_customer_feedback_fts ON customer_feedback
USING GIN (to_tsvector('simple', title || ' ' || content));

-- AI Models indexes
CREATE INDEX IF NOT EXISTS idx_ai_models_active ON ai_models (is_active) WHERE is_active = true;
CREATE INDEX IF NOT EXISTS idx_ai_models_provider ON ai_models (provider);
CREATE INDEX IF NOT EXISTS idx_ai_models_type ON ai_models (model_type);

-- ============================================================================
-- UNICODE TEXT FUNCTIONS
-- ============================================================================

-- Function to normalize Unicode text for better search
CREATE OR REPLACE FUNCTION normalize_unicode_text(input_text TEXT)
RETURNS TEXT AS $$
BEGIN
    IF input_text IS NULL THEN
        RETURN '';
    END IF;

    -- Convert to lowercase
    input_text := LOWER(input_text);

    -- Remove accents and diacritics
    BEGIN
        input_text := unaccent(input_text);
    EXCEPTION
        WHEN undefined_function THEN
            -- Fallback if unaccent is not available
            input_text := input_text;
    END;

    -- Remove special characters but keep Unicode letters, numbers, and spaces
    input_text := REGEXP_REPLACE(input_text, '[^\w\s]', ' ', 'g');
    input_text := REGEXP_REPLACE(input_text, '\s+', ' ', 'g');
    input_text := TRIM(input_text);

    RETURN input_text;
END;
$$ language 'plpgsql' IMMUTABLE;

-- Function for Unicode similarity search
CREATE OR REPLACE FUNCTION unicode_similarity(text1 TEXT, text2 TEXT)
RETURNS REAL AS $$
DECLARE
    norm_text1 TEXT;
    norm_text2 TEXT;
BEGIN
    -- Normalize both texts
    norm_text1 := normalize_unicode_text(text1);
    norm_text2 := normalize_unicode_text(text2);

    -- Return similarity using PostgreSQL's built-in similarity function
    RETURN SIMILARITY(norm_text1, norm_text2);
END;
$$ language 'plpgsql' IMMUTABLE;

-- Function to detect script type
CREATE OR REPLACE FUNCTION detect_script_type(input_text TEXT)
RETURNS TEXT AS $$
BEGIN
    IF input_text IS NULL THEN
        RETURN 'unknown';
    END IF;

    -- Check for Cyrillic script (Serbian, Russian, etc.)
    IF input_text ~ '[\u0400-\u04FF\u0500-\u052F]' THEN
        RETURN 'cyrillic';
    -- Check for Arabic script
    ELSIF input_text ~ '[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]' THEN
        RETURN 'arabic';
    -- Check for Chinese/Japanese/Korean
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

-- Function to get text encoding information
CREATE OR REPLACE FUNCTION get_text_encoding_info(input_text TEXT)
RETURNS JSONB AS $$
BEGIN
    RETURN jsonb_build_object(
        'script_type', detect_script_type(input_text),
        'length_bytes', LENGTH(input_text::bytea),
        'length_chars', CHAR_LENGTH(input_text),
        'contains_unicode', input_text ~ '[^\x00-\x7F]',
        'encoding', 'UTF8'
    );
END;
$$ language 'plpgsql' IMMUTABLE;

-- ============================================================================
-- BASIC DATA INSERTION
-- ============================================================================

-- Insert countries with Unicode support
INSERT INTO countries (country_code, iso_code, country_name, country_name_sr) VALUES
('SRB', 'RS', 'Serbia', 'Србија'),
('USA', 'US', 'United States', 'Сједињене Америчке Државе'),
('DEU', 'DE', 'Germany', 'Немачка'),
('FRA', 'FR', 'France', 'Француска'),
('GBR', 'GB', 'United Kingdom', 'Уједињено Краљевство'),
('ITA', 'IT', 'Italy', 'Италија'),
('ESP', 'ES', 'Spain', 'Шпанија'),
('RUS', 'RU', 'Russia', 'Русија'),
('CHN', 'CN', 'China', 'Кина'),
('JPN', 'JP', 'Japan', 'Јапан'),
('IND', 'IN', 'India', 'Индија'),
('ARE', 'AE', 'United Arab Emirates', 'Уједињени Арапски Емирати'),
('SAU', 'SA', 'Saudi Arabia', 'Саудијска Арабија')
ON CONFLICT (iso_code) DO NOTHING;

-- Insert currencies
INSERT INTO currencies (code, name, name_sr, symbol) VALUES
('RSD', 'Serbian Dinar', 'Српски динар', 'RSD'),
('EUR', 'Euro', 'Евро', '€'),
('USD', 'US Dollar', 'Амерички долар', '$'),
('GBP', 'British Pound', 'Британска фунта', '£'),
('CHF', 'Swiss Franc', 'Швајцарски франак', 'CHF'),
('JPY', 'Japanese Yen', 'Јапански јен', '¥'),
('CNY', 'Chinese Yuan', 'Кинески јуан', '¥'),
('RUB', 'Russian Ruble', 'Руска рубља', '₽'),
('AED', 'UAE Dirham', 'УАЕ дирхам', 'AED'),
('SAR', 'Saudi Riyal', 'Саудијски ријал', 'SAR'),
('INR', 'Indian Rupee', 'Индијска рупија', '₹')
ON CONFLICT (code) DO NOTHING;

-- Insert business entity types with Unicode support
INSERT INTO business_entity_types (entity_code, entity_name, entity_name_sr) VALUES
('DOO', 'Limited Liability Company', 'Друштво са ограниченом одговорношћу'),
('AD', 'Joint Stock Company', 'Акционарско друштво'),
('KD', 'General Partnership', 'Командитно друштво'),
('OR', 'Entrepreneur', 'Предузетник'),
('UD', 'Cooperative', 'Задруга')
ON CONFLICT (entity_code) DO NOTHING;

-- Insert business areas with Unicode support
INSERT INTO business_areas (area_code, area_name, area_name_sr, tax_rates) VALUES
('IT', 'Information Technology', 'Информационе технологије', '{"pdv_rate": 20.0, "income_tax_rate": 15.0}'),
('MANUFACT', 'Manufacturing', 'Производња', '{"pdv_rate": 20.0, "income_tax_rate": 15.0}'),
('CONSTR', 'Construction', 'Градевинске делатности', '{"pdv_rate": 20.0, "income_tax_rate": 15.0}'),
('TRADE', 'Wholesale & Retail Trade', 'Трговина', '{"pdv_rate": 20.0, "income_tax_rate": 15.0}'),
('SERVICES', 'Professional Services', 'Професионалне услуге', '{"pdv_rate": 20.0, "income_tax_rate": 15.0}'),
('AGRIC', 'Agriculture', 'Пољопривреда', '{"pdv_rate": 10.0, "income_tax_rate": 10.0}'),
('ENERGY', 'Energy & Utilities', 'Енергетика', '{"pdv_rate": 20.0, "income_tax_rate": 15.0}'),
('TRANSP', 'Transportation', 'Транспорт', '{"pdv_rate": 20.0, "income_tax_rate": 15.0}'),
('FINANCE', 'Financial Services', 'Финансијске услуге', '{"pdv_rate": 20.0, "income_tax_rate": 15.0}'),
('HEALTH', 'Healthcare', 'Здравство', '{"pdv_rate": 20.0, "income_tax_rate": 15.0}')
ON CONFLICT (area_code) DO NOTHING;

-- ============================================================================
-- VIEWS FOR COMMON QUERIES
-- ============================================================================

-- View for active companies with full details
CREATE OR REPLACE VIEW v_active_companies AS
SELECT
    c.companies_id,
    c.company_name,
    c.legal_name,
    c.tax_id,
    c.description,
    c.business_description,
    c.city,
    c.country_id,
    co.country_name,
    co.country_name_sr,
    c.business_area_id,
    ba.area_name,
    ba.area_name_sr,
    c.business_entity_type_id,
    bet.entity_name,
    bet.entity_name_sr,
    c.employee_count,
    c.annual_revenue,
    c.created_at,
    c.updated_at
FROM companies c
LEFT JOIN countries co ON c.country_id = co.countries_id
LEFT JOIN business_areas ba ON c.business_area_id = ba.business_areas_id
LEFT JOIN business_entity_types bet ON c.business_entity_type_id = bet.business_entity_types_id
WHERE c.is_active = true;

-- View for customer feedback analytics
CREATE OR REPLACE VIEW v_customer_feedback_analytics AS
SELECT
    cf.companies_id,
    c.company_name,
    COUNT(*) as total_feedbacks,
    AVG(cf.sentiment_score) as avg_sentiment,
    COUNT(CASE WHEN cf.sentiment_label = 'positive' THEN 1 END) as positive_count,
    COUNT(CASE WHEN cf.sentiment_label = 'negative' THEN 1 END) as negative_count,
    COUNT(CASE WHEN cf.sentiment_label = 'neutral' THEN 1 END) as neutral_count,
    AVG(cf.rating_given) as avg_rating,
    AVG(cf.nps_score) as avg_nps,
    COUNT(CASE WHEN cf.urgency_level = 'high' THEN 1 END) as urgent_count,
    COUNT(CASE WHEN cf.urgency_level = 'critical' THEN 1 END) as critical_count
FROM customer_feedback cf
JOIN companies c ON cf.companies_id = c.companies_id
WHERE cf.created_at >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY cf.companies_id, c.company_name;

-- ============================================================================
-- BASIC TRIGGERS
-- ============================================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply updated_at triggers
CREATE TRIGGER update_companies_updated_at BEFORE UPDATE ON companies
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_customer_feedback_updated_at BEFORE UPDATE ON customer_feedback
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- FINAL SETUP
-- ============================================================================

-- Grant permissions to roles
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO ai_valido_admin;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO ai_valido_user;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO ai_valido_admin, ai_valido_user;

-- Set default privileges for future tables
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO ai_valido_admin;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO ai_valido_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT USAGE ON SEQUENCES TO ai_valido_admin, ai_valido_user;

-- ============================================================================
-- COMPLETION MESSAGE
-- ============================================================================

DO $$
BEGIN
    RAISE NOTICE 'ValidoAI Database Setup Completed Successfully!';
    RAISE NOTICE 'Database: ai_valido_online';
    RAISE NOTICE 'Unicode Support: Full UTF-8';
    RAISE NOTICE 'AI Features: Ready for integration';
    RAISE NOTICE 'Next: Run Postgres_ai_valido_master_data.sql to load sample data';
END $$;
