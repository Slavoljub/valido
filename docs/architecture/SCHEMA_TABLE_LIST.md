# unified table catalogue – validoai serbia compliance

all domain tables follow the same structural contract:

| column | type | purpose |
|--------|------|---------|
| **{table}_id** | uuid pk | surrogated identifier generated via `uuid_generate_v4()` |
| **is_deleted** | boolean | soft-delete flag (default false) |
| **comments** | text | freeform annotations, integration notes |
| **created_at** | timestamptz | insert timestamp |
| **updated_at** | timestamptz | last update timestamp |

history tables: `{table}_history` replicate all business columns + `operation_type`, `operation_timestamp`, `user_id`.

> triggers `log_{table}_changes()` are generated automatically via ddl template (see `configuration_scripts/templates/base_audit.sql.j2`).  all changes are appended; prod log archives can be offloaded to cold storage for ≥100 PB scale.

---

## core
```sql
company(
  company_id uuid pk,
  name varchar(255) not null,
  legal_name varchar(255),
  tax_id varchar(32) unique,
  ... meta columns ...
)

user(
  user_id uuid pk,
  company_id fk→company,
  email varchar(255) unique not null,
  password_hash varchar(255) not null,
  role varchar(64),
  ... meta ...
)
```

## bookkeeping
```sql
chart_account(chart_account_id uuid pk, company_id fk, number varchar(8), name, type, parent_id ... meta)
journal(journal_id uuid pk, company_id fk, name, period_from, period_to ... meta)
ledger_entry(ledger_entry_id uuid pk, journal_id fk, account_id fk, date, description, debit, credit, currency ... meta)
```

## invoicing / payments
```sql
invoice(invoice_id uuid pk, company_id fk, customer_name, total_amount, status, issue_date, due_date, currency ... meta)
invoice_item(invoice_item_id uuid pk, invoice_id fk, description, qty, unit_price, vat_rate_id fk, total ... meta)
payment(payment_id uuid pk, invoice_id fk, company_id fk, method, amount, paid_at ... meta)
```

## inventory
```sql
product(product_id uuid pk, company_id fk, sku, name, unit, vat_rate_id fk, default_price ... meta)
warehouse(warehouse_id uuid pk, company_id fk, name, location ... meta)
stock_move(stock_move_id uuid pk, product_id fk, warehouse_id fk, qty, move_type, move_date ... meta)
```

## payroll
```sql
employee(employee_id uuid pk, company_id fk, first_name, last_name, jmbg unique, hire_date, position ... meta)
contract(contract_id uuid pk, employee_id fk, start_date, end_date, salary_gross, salary_net, currency ... meta)
payslip(payslip_id uuid pk, contract_id fk, period_from, period_to, total_gross, total_net, paid_at ... meta)
```

## fiscalization
```sql
fiscal_device(fiscal_device_id uuid pk, company_id fk, pfr_type, location, cert_serial, activated_at ... meta)
receipt(receipt_id uuid pk, invoice_id fk, fiscal_device_id fk, pfr_signature, qr_code, reported_at, offline ... meta)
```

## taxation
```sql
tax_obligation(tax_obligation_id uuid pk, company_id fk, tax_type, period, base, tax ... meta)
payroll_contribution(payroll_contribution_id uuid pk, employee_id fk, obligation_type, base, amount, period ... meta)
```

## ai / embeddings
```sql
ai_model(ai_model_id uuid pk, name, provider, model_name, is_local, context_size ... meta)
ai_vector(ai_vector_id uuid pk, company_id fk, source_table, record_id, vector, payload ... meta)
```

## audit & api
```sql
api_key(api_key_id uuid pk, user_id fk, key_hash, expires_at ... meta)
notification(notification_id uuid pk, user_id fk, message, is_read ... meta)
change_log(change_log_id uuid pk, table_name, record_id, user_id, action, diff ... meta)
```

---

### scale-out strategy to 100 PB
1. **time/tenant partitioning** – partitions per fiscal year per company for high-volume tables (ledger_entry, receipt, ai_vector).  postgres native partition pruning keeps query latency low.
2. **sharding** – citus or yugabytedb layer distributes partitions across nodes.
3. **cold storage** – history tables older than N years exported to parquet/S3 via `COPY` for cheap archival.

---

### ddl generation
template at `configuration_scripts/templates/base_table.sql.j2` ensures:
* id column `{table}_id uuid primary key`
* meta columns & default values
* history table & audit trigger auto-generated

rendered per db engine via `scripts/render_schema.py --db postgres` etc.

## employee multi-company junction
```sql
employee_company(
  employee_company_id uuid pk,
  employee_id fk→employee,
  company_id fk→company,
  start_date date,
  end_date date,
  role varchar(64),
  ... meta ...
)
```

## ecommerce
```sql
product(product_id uuid pk, company_id fk, sku, name, unit, vat_rate_id fk, default_price ... meta)
order(order_id uuid pk, company_id fk, customer_id nullable, total_amount, status, placed_at ... meta)
order_item(order_item_id uuid pk, order_id fk, product_id fk, qty, unit_price, vat_rate_id, total ... meta)
payment(payment_id uuid pk, order_id fk, method, amount, paid_at, status ... meta)
```

## banking integration
```sql
bank_statement(bank_statement_id uuid pk, company_id fk, account_number, currency, period_from, period_to, imported_at ... meta)
bank_transaction(bank_transaction_id uuid pk, bank_statement_id fk, txn_date, description, amount, balance, matched_invoice_id nullable ... meta)
```
