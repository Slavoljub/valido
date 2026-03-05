# comprehensive bookkeeping & finance schema for serbian businesses

> draft 28-08-2025  •  status: in review

this document specifies a unified relational schema that can be deployed on **postgresql**, **sqlite** and **mysql** (with minimal tweaks) and forms the basis for validoai’s real-time dashboard and ai analytics.  the design complies with rs regulations – (pdv – vat, poslovne knjige, fiskalni zakoni).

## domain overview

| domain | purpose |
|--------|---------|
| core           | companies, users, permissions |
| bookkeeping    | chart of accounts, journals, ledger entries, vat books |
| invoicing      | invoices, invoice items, payments |
| inventory      | products, stock moves, warehouses |
| payroll        | employees, contracts, payslips |
| taxation       | vat rates, tax obligations, tax reports |
| ai / vectors   | pgvector embeddings, analytic insights |
| audit / logs   | api keys, notification, change log |

## ddl (vendor-agnostic)

```sql
-- extension hints (postgres only)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS pgvector;
```

### core tables
```sql
company(id uuid pk, …)
user(id uuid pk, company_id fk→company, email unique, role, …)
permission(id, name, description)
user_permission(user_id fk→user, permission_id fk→permission)
```

### bookkeeping (računovodstvo)
```sql
chart_account(id uuid pk, company_id, number varchar(8) unique, name, type(enum asset/liab/…), parent_id nullable)
journal(id uuid pk, company_id, name, period_from, period_to)
ledger_entry(id uuid pk, journal_id fk, account_id fk, date, description, debit numeric, credit numeric, currency char(3))
vat_book(Id uuid pk, company_id, period, vat_rate_id fk, base numeric, tax numeric)
vat_rate(id uuid pk, code varchar(4), percent numeric(5,2))
```

### invoicing & payments
```sql
invoice(id uuid pk, company_id, customer_name, total_amount, status, issue_date, due_date, currency)
invoice_item(id uuid pk, invoice_id fk, description, qty, unit_price, vat_rate_id, total)
payment(id uuid pk, invoice_id fk nullable, company_id, method, amount, paid_at)
```

### inventory (magacin)
```sql
product(id uuid pk, company_id, sku, name, unit, vat_rate_id, default_price)
warehouse(id uuid pk, company_id, name, location)
stock_move(id uuid pk, product_id fk, warehouse_id fk, qty, move_type(enum in/out), move_date)
```

### payroll (obračun zarada)
```sql
employee(id uuid pk, company_id, first_name, last_name, jmbg unique, hire_date, position)
contract(id uuid pk, employee_id fk, start_date, end_date, salary_gross, salary_net, currency)
payslip(id uuid pk, contract_id fk, period_from, period_to, total_gross, total_net, paid_at)
```

### fiscalization (real-time e-receipt)
```sql
fiscal_device(id uuid pk, company_id, pfr_type enum('V-PFR','L-PFR'), location, cert_serial, activated_at)
receipt(id uuid pk, invoice_id fk, fiscal_device_id fk, pfr_signature varchar(512), qr_code text, reported_at timestamp, offline boolean default false)
```

### taxation & payroll contributions
```sql
tax_obligation(id uuid pk, company_id, tax_type enum('corporate','vat','payroll'), period, base numeric, tax numeric, created_at)
payroll_contribution(id uuid pk, employee_id fk, obligation_type enum('pension_emp','health_emp','unemployment_emp','pension_empr','health_empr'), base numeric, amount numeric, period)
```

> the schema supports Serbian standard rates (corporate 15 %, vat 20 %/10 %, payroll totals 37.9 %) but stores actual percentage per record to allow historical changes.

### ai embeddings & insights
```sql
ai_model(id uuid pk, name, provider, model_name, is_local, context_size)
ai_vector(id uuid pk, company_id, source_table, record_id, vector vector(768), payload jsonb)
```

### audit
```sql
api_key(id uuid pk, user_id, key_hash, expires_at)
notification(id uuid pk, user_id, message, is_read)
change_log(id uuid pk, table_name, record_id, user_id, action, diff jsonb, changed_at)
```

## multi-db considerations

| feature | postgresql | sqlite | mysql |
|---------|-----------|--------|-------|
| uuid native | ✅ uuid-ossp | emulated via text | via `uuid()` func |
| jsonb | ✅ | text | json |
| vector | ✅ pgvector | **n/a** (fallback faiss index) | **n/a** |
| partial indexes | ✅ | – | – |

fallback strategies include creating `vector` table only on postgres; other dbs store embeddings in separate file-based faiss index.

## sample data generator

script `scripts/seed_sample_finance.py` will:
1. create 3 example companies, 50 products, 200 invoices with items & vat rates.  
2. produce 1 fiscal year of ledger entries balanced per company.  
3. write embeddings with sentence-transformers (`paraphrase-multilingual-mpnet`) into `ai_vector`.

## ai / reporting use-cases

* **similar invoice search** – cosine similarity on `ai_vector.vector`.  
* **cash-flow prediction** – timeseries from `payment` + ledger.  
* **vat liability report** – join `vat_book`, `invoice_item`.

## open tasks

- [ ] finalise enum values for account types & payment methods
- [ ] write db-agnostic ddl autogenerator (jinja templates)
- [ ] extend sample generator for payroll
