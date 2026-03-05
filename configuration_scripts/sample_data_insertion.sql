-- sample_data_insertion.sql
-- generates realistic bookkeeping sample data for 3 fiscal years (~5k invoices, ~50k ledger lines)
-- compatible with postgresql 13+ (uses generate_series).  for sqlite/mysql run `scripts/seed_sample_finance.py` instead.

-- prerequisites: schema created (see setup_full_postgres_schema.sql)
-- WARNING: intended for dev; do NOT run in production.

BEGIN;

-- 1. companies & users --------------------------------------------------------
INSERT INTO company(id, name, legal_name, tax_id, industry, company_type)
VALUES
    (uuid_generate_v4(), 'Alfa d.o.o.', 'Alfa Društvo sa ograničenom odgovornošću', '10000001', 'IT', 'doo'),
    (uuid_generate_v4(), 'Beta ad',    'Beta Akcionarsko društvo',              '10000002', 'Manufacturing', 'ad'),
    (uuid_generate_v4(), 'Gamma PR',   'Gamma Preduzetnik',                     '10000003', 'Consulting', 'preduzetnik');

WITH c AS (
    SELECT id FROM company
)
INSERT INTO "user"(id, company_id, email, password_hash, role)
SELECT uuid_generate_v4(), id, concat('user', row_number() over (), '@example.rs'), 'pbkdf2$dev', 'admin'
FROM c;

-- 2. vat rates ---------------------------------------------------------------
INSERT INTO vat_rate(id, code, percent) VALUES
 (uuid_generate_v4(), 'PDV20', 20.0),
 (uuid_generate_v4(), 'PDV10', 10.0),
 (uuid_generate_v4(), 'PDV0',  0.0);

-- 3. products ----------------------------------------------------------------
WITH comp AS (SELECT id AS company_id FROM company),
     vr AS (SELECT id AS vat_rate_id FROM vat_rate ORDER BY percent DESC)
INSERT INTO product(id, company_id, sku, name, unit, vat_rate_id, default_price)
SELECT uuid_generate_v4(), comp.company_id,
       concat('SKU', gen.random_int(1000, 9999)),
       concat('Product ', gen.random_int(1,500)),
       'pcs',
       vr.vat_rate_id,
       gen.random_int(500,5000)/100.0
FROM comp CROSS JOIN LATERAL vr LIMIT 50;

-- 4. invoices & items (3 years) ---------------------------------------------
DO $$
DECLARE
    comp   record;
    inv_id uuid;
    prod   record;
    start_date date := date_trunc('year', current_date) - interval '3 years';
BEGIN
    FOR comp IN SELECT id FROM company LOOP
        FOR i IN 1..1800 LOOP  -- ~1800 invoices per company (~5k total)
            inv_id := uuid_generate_v4();
            INSERT INTO invoice(id, company_id, customer_name, total_amount, status, issue_date, due_date, currency)
            VALUES(inv_id, comp.id, concat('Kupac ', gen.random_int(1,300)), 0, 'posted', start_date + gen.random_int(0, 1095), start_date + gen.random_int(0,1095)+30, 'RSD');
            -- add 3-7 items per invoice
            FOR j IN 1..gen.random_int(3,7) LOOP
                SELECT * INTO prod FROM product WHERE company_id = comp.id ORDER BY random() LIMIT 1;
                INSERT INTO invoice_item(id, invoice_id, description, qty, unit_price, vat_rate_id, total)
                VALUES(uuid_generate_v4(), inv_id, prod.name, gen.random_int(1,10), prod.default_price, prod.vat_rate_id, prod.default_price*gen.random_int(1,10));
            END LOOP;
        END LOOP;
    END LOOP;
END $$;

-- 5. payments ----------------------------------------------------------------
INSERT INTO payment(id, invoice_id, company_id, method, amount, paid_at)
SELECT uuid_generate_v4(), i.id, i.company_id, 'bank', i.total_amount,
       i.issue_date + gen.random_int(1,60)
FROM invoice i
WHERE random() < 0.7;  -- 70% paid

-- 6. ledger entries ----------------------------------------------------------
INSERT INTO journal(id, company_id, name, period_from, period_to)
SELECT uuid_generate_v4(), id, concat('Glavna knjiga ', extract(year from current_date)-2,'-', extract(year from current_date)) , current_date-interval '3 years', current_date
FROM company;

-- simplistic ledger entry mirroring invoice totals (debit receivable, credit revenue)
INSERT INTO ledger_entry(id, journal_id, account_id, date, description, debit, credit, currency)
SELECT uuid_generate_v4(), j.id, null, i.issue_date, concat('Invoice ', i.id), i.total_amount, 0, 'RSD'
FROM invoice i JOIN journal j ON j.company_id = i.company_id;

COMMIT;
