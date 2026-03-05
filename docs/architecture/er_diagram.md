# ER diagram – validoai unified schema

```mermaid
erDiagram
  companies ||--o{ users : employs
  companies ||--o{ employees_companies : "staffs"
  employees ||--o{ employees_companies : "assigned_to"
  users ||--o{ roles_users : "has_role"
  roles ||--o{ roles_users : "granted_to"
  roles ||--o{ permissions_roles : "contains_perm"
  permissions ||--o{ permissions_roles : "belongs_to_role"
  users ||--o{ api_keys : "owns"
  users ||--o{ employees : "represents" %% optional login link
  employees ||--o{ payroll_contributions : "pays"
  employees ||--o{ contracts : "under"
  contracts ||--o{ payslips : "produces"
  companies ||--o{ products : "offers"
  users ||--o{ orders : "places"
  orders ||--|{ order_items : "includes"
  orders ||--o{ payments : "settled_by"
  companies ||--o{ bank_statements : "imports"
  bank_statements ||--|{ bank_transactions : "contains"
  companies ||--o{ fiscal_devices : "uses"
  companies ||--o{ invoices : "issues"
  invoices ||--|{ invoice_items : "details"
  invoices ||--|| receipts : "generates"
  journals ||--|{ ledger_entries : "logs"
  chart_accounts ||--|{ ledger_entries : "posted_to"
  companies ||--|{ chart_accounts : "maintains"
  ai_vectors }o--|| companies : "belongs"

  %% key columns excerpt
  users{
    uuid users_id PK
    uuid companies_id FK
    uuid employees_id nullable FK
    string username
    string email
  }
  employees{
    uuid employees_id PK
    string first_name
    string last_name
    uuid users_id nullable FK
  }
  employees_companies{
    uuid employees_companies_id PK
    uuid employees_id FK
    uuid companies_id FK
    date start_date
    date end_date
  }
```

Employees may exist without a linked user account. When login access is needed, a `users` row references `employees_id`, and RBAC roles govern permissions across multiple companies via the `employees_companies` junction.
