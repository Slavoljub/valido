-- validoai – full postgres schema (dev reset)
-- generated on 2025-08-28
-- WARNING: dropping all objects ‑ use ONLY in local development!

-- =========================
-- 1. drop existing schema
-- =========================
DO $$
DECLARE
    _stmt text;
BEGIN
    -- drop tables
    FOR _stmt IN (
        SELECT 'DROP TABLE IF EXISTS ' || quote_ident(schemaname) || '.' || quote_ident(tablename) || ' CASCADE;' as stmt
        FROM pg_tables
        WHERE schemaname IN ('public')
    ) LOOP
        EXECUTE _stmt;
    END LOOP;

    -- drop sequences
    FOR _stmt IN (
        SELECT 'DROP SEQUENCE IF EXISTS ' || quote_ident(sequence_schema) || '.' || quote_ident(sequence_name) || ' CASCADE;' as stmt
        FROM information_schema.sequences
        WHERE sequence_schema IN ('public')
    ) LOOP
        EXECUTE _stmt;
    END LOOP;
END $$;

-- =========================
-- 2. create extensions
-- =========================
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS pgvector;

-- =========================
-- 3. core tables
-- =========================
CREATE TABLE company (
    id                    UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name                  VARCHAR(255) NOT NULL,
    legal_name            VARCHAR(255),
    tax_id                VARCHAR(32) UNIQUE,
    registration_number   VARCHAR(32),
    industry              VARCHAR(128),
    company_type          VARCHAR(32),
    created_at            TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at            TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE "user" (
    id            UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id    UUID NOT NULL REFERENCES company(id) ON DELETE CASCADE,
    email         VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name    VARCHAR(128),
    last_name     VARCHAR(128),
    role          VARCHAR(64) DEFAULT 'user',
    is_active     BOOLEAN DEFAULT TRUE,
    created_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_user_company ON "user" (company_id);

-- invoices
CREATE TABLE invoice (
    id            UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id    UUID NOT NULL REFERENCES company(id) ON DELETE CASCADE,
    customer_name VARCHAR(255) NOT NULL,
    total_amount  NUMERIC(18,2) NOT NULL,
    status        VARCHAR(32)   DEFAULT 'draft',
    issue_date    DATE,
    due_date      DATE,
    created_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE invoice_item (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    invoice_id  UUID NOT NULL REFERENCES invoice(id) ON DELETE CASCADE,
    description TEXT,
    quantity    NUMERIC(18,4) NOT NULL DEFAULT 1,
    unit_price  NUMERIC(18,4) NOT NULL,
    total       NUMERIC(18,4) NOT NULL
);

-- =========================
-- 4. email marketing
-- =========================
CREATE TABLE email_template (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id  UUID NOT NULL REFERENCES company(id) ON DELETE CASCADE,
    name        VARCHAR(128) NOT NULL,
    subject     VARCHAR(255) NOT NULL,
    body_html   TEXT NOT NULL,
    created_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE email_campaign (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    template_id     UUID NOT NULL REFERENCES email_template(id) ON DELETE CASCADE,
    scheduled_at    TIMESTAMP,
    status          VARCHAR(32) DEFAULT 'draft',
    created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE email_recipient (
    id             UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    campaign_id    UUID NOT NULL REFERENCES email_campaign(id) ON DELETE CASCADE,
    email          VARCHAR(255) NOT NULL,
    sent_at        TIMESTAMP,
    status         VARCHAR(32) DEFAULT 'pending'
);

-- =========================
-- 5. ai models & embeddings
-- =========================
CREATE TABLE ai_model (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name            VARCHAR(128) NOT NULL,
    provider        VARCHAR(64)  NOT NULL,
    model_name      VARCHAR(128) NOT NULL,
    is_local        BOOLEAN DEFAULT FALSE,
    context_size    INTEGER,
    created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE ai_insight (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id  UUID NOT NULL REFERENCES company(id) ON DELETE CASCADE,
    source      VARCHAR(64),
    vector      VECTOR(768),
    payload     JSONB,
    created_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_insight_vector ON ai_insight USING ivfflat (vector vector_cosine_ops);

-- =========================
-- 6. workflow / audit tables (new)
-- =========================
CREATE TABLE notification (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id     UUID NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
    message     TEXT NOT NULL,
    is_read     BOOLEAN DEFAULT FALSE,
    created_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE api_key (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id     UUID NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
    key_hash    TEXT    NOT NULL,
    expires_at  TIMESTAMP,
    created_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- =========================
-- 7. views & materialized views
-- =========================
CREATE VIEW v_invoice_totals AS
SELECT i.company_id,
       SUM(i.total_amount) AS total_revenue,
       COUNT(*)            AS invoice_count
FROM invoice i
GROUP BY i.company_id;

-- =========================
-- 8. done
-- =========================
RAISE NOTICE 'schema created successfully';
