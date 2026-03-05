# AI Valido Online Project Description

## Overview
AI Valido Online is a scalable ERP system for Serbian businesses, managing financial accounting, inventory, CRM, payroll, and ticketing, with support for 10 petabytes of data. It ensures compliance with Serbian regulations (PDV, SEF e-invoicing, APR filings) and implements RBAC with PostgreSQL roles (`ai_valido_developer`, `ai_valido_admin`, etc.) and RLS based on `companies_id`. Seven user roles are defined: `developer` (full access), `admin` (full CRUD, read-only company switching), `accountant` (CRU on financial tables), `manager` (CRUD on CRM/inventory), `hr` (limited view/download), `support` (logs and tickets), and `demo` (view/test without saving). The system uses PostgreSQL, `/v1` APIs with Bearer token authentication, and a Tailwind-based UI with Flowbite, FlyonUI, DaisyUI, Pagedone, TailGrids, Simple-DataTables, and Preline. It integrates local LLMs (DistilBERT, Llama 2, Mistral, Phi-2, Gemma) with TensorFlow for image processing, supports yearly reports, email scheduling, backups, fiscal year management, and a tiered ticketing system (L1-L4).

## Objectives
- **Financial Management**: Automate general ledger, AR/AP, bank reconciliation, tax reporting, and Serbian business reports (Balance Sheet, Income Statement, Cash Flow, VAT).
- **Inventory Management**: Track items, transactions, and warehouses with FIFO/average cost valuation.
- **CRM Integration**: Manage leads, opportunities, and contacts.
- **Scalability**: Handle 10PB with partitioning, sharding, and caching.
- **Serbian Compliance**: Support PDV (20%), SEF e-invoicing, and APR filings.
- **Security**: Use PostgreSQL roles, RLS, and Bearer token-protected APIs.
- **AI Integration**: Local LLMs and TensorFlow for invoice parsing, chat, and UI/form generation.
- **User Experience**: Responsive, multi-language UI with dynamic dashboards and charts.
- **Reporting and Automation**: Generate business reports, schedule emails, manage tickets, and log history.
- **Demo Access**: Allow feature exploration without data persistence.

## Key Features
- **Database Schema**: Plural table names (e.g., `companies`, `users`) with `companies_id` foreign keys. Reference tables replace ENUMs. Includes audit fields.
- **Financial Modules**: General ledger, AR/AP, bank accounts, fixed assets, budgets, tax registers, and fiscal year management.
- **Inventory Modules**: Item tracking, transactions, and warehouse management.
- **CRM Modules**: Contacts, leads, and opportunities.
- **Ticketing Module**: L1-L4 support with `tickets` and `tickets_statuses` tables.
- **History Logging**: `table_history_logs` tracks changes across tables.
- **Scalability**: Range partitioning, Citus sharding, BRIN/B-tree/HNSW indexes, archival tables.
- **Reporting**: Temporary/unlogged tables, views, and materialized views for Balance Sheet, Income Statement, Cash Flow, VAT, and yearly reports.
- **RBAC and RLS**: PostgreSQL roles with RLS on `companies_id` and user association.
- **API Design**: `/v1` routes with Bearer token authentication, defined in `routes_permissions`.
- **Compliance**: PDV, SEF XML, APR filings, fiscal year procedures.
- **AI Integration**: LLMs and TensorFlow for chat, form generation, UI generation, and image processing.
- **Backup**: Automated with `pg_dump` and `pg_cron`.
- **UI Components**: Flowbite (tables, timelines, carousels), FlyonUI, DaisyUI calendars, Pagedone/TailGrids calendars, Simple-DataTables, Preline, and AI-generated charts.

## User Types and Permissions
- **Developer (`ai_valido_developer`)**:
  - **Privileges**: Full access to all tables, routes, and columns. Can switch companies, edit configurations, toggle modules, and manage fiscal years.
  - **Use Cases**: System setup, debugging, enabling modules, and UI generation.
  - **RLS**: `USING (true)`.
  - **PostgreSQL Role**: Full `GRANT ALL`.
- **Admin (`ai_valido_admin`)**:
  - **Privileges**: Full CRUD on all tables for their `companies_id`, read-only company switching, and limited configuration editing.
  - **Use Cases**: Manage company data, approve tickets, and view other companies.
  - **RLS**: `USING (companies_id = (SELECT companies_id FROM users WHERE users_id = current_setting('app.current_user_id')::UUID))`.
  - **PostgreSQL Role**: `GRANT SELECT, INSERT, UPDATE, DELETE`.
- **Accountant (`ai_valido_accountant`)**:
  - **Privileges**: CRU with soft delete on financial tables (`general_ledgers_transactions`, `invoices_receivable`, `invoices_payable`, etc.). Hard delete via tickets.
  - **Use Cases**: Process invoices, calculate PDV, and manage tax filings.
  - **RLS**: Same as `admin` with table restrictions.
  - **PostgreSQL Role**: `GRANT SELECT, INSERT, UPDATE` on financial tables.
- **Manager (`ai_valido_manager`)**:
  - **Privileges**: CRUD with soft delete on CRM/inventory tables, password resets, and configuration requests via tickets.
  - **Use Cases**: Manage clients, reset passwords, and configure features.
  - **RLS**: Same as `admin` with table restrictions.
  - **PostgreSQL Role**: `GRANT SELECT, INSERT, UPDATE, DELETE` on CRM/inventory tables.
- **HR (`ai_valido_hr`)**:
  - **Privileges**: Read-only on `payrolls`, `employees_data`, with CSV/PDF downloads.
  - **Use Cases**: View payroll and request data access changes.
  - **RLS**: Same as `admin` with table restrictions.
  - **PostgreSQL Role**: `GRANT SELECT` on HR tables.
- **Support (`ai_valido_support`)**:
  - **Privileges**: Read-only on logs/configs, CRUD on `tickets` for L1-L3, escalate to L4 (`developer`).
  - **Use Cases**: Troubleshoot issues and log tickets.
  - **RLS**: `USING (true)` for logs, restricted for other tables.
  - **PostgreSQL Role**: `GRANT SELECT` on logs, `INSERT, UPDATE` on `tickets`.
- **Demo (`ai_valido_demo`)**:
  - **Privileges**: View/test all features with temporary tables, no data persistence.
  - **Use Cases**: Explore system functionality.
  - **RLS**: Same as `admin` with `SELECT ONLY`.
  - **PostgreSQL Role**: `GRANT SELECT` on all tables.

### Permission Tables
- **routes_permissions**:
  ```sql
  CREATE TABLE routes_permissions (
      routes_permissions_id UUID PRIMARY KEY,
      roles_id UUID REFERENCES roles(roles_id),
      route_path VARCHAR(255) NOT NULL,
      methods VARCHAR(50) NOT NULL,
      allowed_columns TEXT[],
      allow_access BOOLEAN DEFAULT FALSE,
      description TEXT,
      notes TEXT,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
  );
  ```
- Controls access to API routes (e.g., `/v1/invoices/*`) and columns.

### Database Implementation
- **PostgreSQL**:
  - Scalability: Citus sharding, range partitioning, BRIN/B-tree/HNSW indexes.
  - RLS: Policies based on `companies_id` and `current_setting('app.current_user_id')`.
  - History Logging: `table_history_logs` with triggers for all tables.
  - Fiscal Years: `fiscal_years` table with `open_fiscal_year` and `close_fiscal_year` procedures.
- **Materialized Views**:
  - **Balance Sheet**:
    ```sql
    CREATE MATERIALIZED VIEW balance_sheets AS
    SELECT
        c.companies_id,
        c.company_name,
        fy.year,
        SUM(CASE WHEN at.type_name = 'Asset' THEN gl.debit_amount - gl.credit_amount ELSE 0 END) AS total_assets,
        SUM(CASE WHEN at.type_name = 'Liability' THEN gl.credit_amount - gl.debit_amount ELSE 0 END) AS total_liabilities,
        SUM(CASE WHEN at.type_name IN ('Revenue', 'Expense') THEN gl.debit_amount - gl.credit_amount ELSE 0 END) AS equity
    FROM companies c
    JOIN fiscal_years fy ON c.companies_id = fy.companies_id
    JOIN general_ledgers_transactions gl ON c.companies_id = gl.companies_id
    JOIN charts_of_accounts coa ON gl.charts_of_accounts_id = coa.charts_of_accounts_id
    JOIN accounts_types at ON coa.accounts_types_id = at.accounts_types_id
    WHERE gl.deleted_at IS NULL AND fy.status = 'closed'
    GROUP BY c.companies_id, c.company_name, fy.year
    WITH DATA;
    ```
  - **Income Statement**:
    ```sql
    CREATE MATERIALIZED VIEW income_statements AS
    SELECT
        c.companies_id,
        c.company_name,
        fy.year,
        SUM(CASE WHEN at.type_name = 'Revenue' THEN gl.credit_amount - gl.debit_amount ELSE 0 END) AS total_revenue,
        SUM(CASE WHEN at.type_name = 'Expense' THEN gl.debit_amount - gl.credit_amount ELSE 0 END) AS total_expenses,
        SUM(CASE WHEN at.type_name = 'Revenue' THEN gl.credit_amount - gl.debit_amount ELSE 0 END) -
        SUM(CASE WHEN at.type_name = 'Expense' THEN gl.debit_amount - gl.credit_amount ELSE 0 END) AS net_income
    FROM companies c
    JOIN fiscal_years fy ON c.companies_id = fy.companies_id
    JOIN general_ledgers_transactions gl ON c.companies_id = gl.companies_id
    JOIN charts_of_accounts coa ON gl.charts_of_accounts_id = coa.charts_of_accounts_id
    JOIN accounts_types at ON coa.accounts_types_id = at.accounts_types_id
    WHERE gl.deleted_at IS NULL AND fy.status = 'closed'
    GROUP BY c.companies_id, c.company_name, fy.year
    WITH DATA;
    ```
  - **Cash Flow Statement**:
    ```sql
    CREATE MATERIALIZED VIEW cash_flow_statements AS
    SELECT
        c.companies_id,
        c.company_name,
        fy.year,
        SUM(CASE WHEN tt.type_name = 'Receipt' THEN bs.amount ELSE 0 END) AS cash_inflows,
        SUM(CASE WHEN tt.type_name = 'Payment' THEN bs.amount ELSE 0 END) AS cash_outflows,
        SUM(CASE WHEN tt.type_name = 'Receipt' THEN bs.amount ELSE -bs.amount END) AS net_cash_flow
    FROM companies c
    JOIN fiscal_years fy ON c.companies_id = fy.companies_id
    JOIN banks_statements bs ON c.companies_id = bs.companies_id
    JOIN transactions_types tt ON bs.transactions_types_id = tt.transactions_types_id
    WHERE bs.deleted_at IS NULL AND fy.status = 'closed'
    GROUP BY c.companies_id, c.company_name, fy.year
    WITH DATA;
    ```
  - **VAT Report**:
    ```sql
    CREATE MATERIALIZED VIEW vat_reports AS
    SELECT
        c.companies_id,
        c.company_name,
        fy.year,
        tr.period_start,
        tr.period_end,
        SUM(tr.taxable_amount) AS total_taxable,
        SUM(tr.tax_amount) AS total_vat
    FROM companies c
    JOIN fiscal_years fy ON c.companies_id = fy.companies_id
    JOIN taxes_registers tr ON c.companies_id = tr.companies_id
    WHERE tr.taxes_types_id = (SELECT taxes_types_id FROM taxes_types WHERE type_name = 'PDV')
    AND tr.deleted_at IS NULL AND fy.status = 'closed'
    GROUP BY c.companies_id, c.company_name, fy.year, tr.period_start, tr.period_end
    WITH DATA;
    ```

### Backend Design
- **Flask with SQLC**:
  - Routes dynamically generated from `routes_permissions`:
    ```python
    from flask import Flask, jsonify, request
    from functools import wraps
    import jwt

    app = Flask(__name__)

    def require_token(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            token = request.headers.get('Authorization')
            if not token or not token.startswith('Bearer '):
                return jsonify({'error': 'Token required'}), 401
            try:
                data = jwt.decode(token.replace('Bearer ', ''), 'secret_key', algorithms=['HS256'])
                current_user_id = data['user_id']
                app.config['current_user_id'] = current_user_id
            except:
                return jsonify({'error': 'Invalid token'}), 401
            return f(*args, **kwargs)
        return decorated

    @app.route('/v1/<path:route_path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
    @require_token
    def dynamic_route(route_path):
        user_id = app.config['current_user_id']
        with db_connection() as conn:
            role_id = conn.execute("SELECT roles_id FROM users WHERE users_id = %s", (user_id,)).fetchone()[0]
            permission = conn.execute(
                "SELECT allow_access, methods FROM routes_permissions WHERE roles_id = %s AND route_path = %s",
                (role_id, f"/v1/{route_path}")
            ).fetchone()
            if not permission or not permission['allow_access'] or request.method not in permission['methods']:
                return jsonify({'error': 'Access denied'}), 403
            # Execute CRUD operation
            return jsonify({'status': 'success'})
    ```
- **Tailwind Dashboard**:
  - Responsive dashboard with Flowbite sidebar, DaisyUI cards, and Pagedone/TailGrids layouts:
    ```html
    <div class="flex">
        <aside class="w-64 bg-gray-800 text-white p-4">
            <nav class="hs-sidebar-nav">
                <a href="/dashboard" class="hs-sidebar-link">Dashboard</a>
                <a href="/v1/invoices" class="hs-sidebar-link">Invoices</a>
                <a href="/v1/tickets" class="hs-sidebar-link">Tickets</a>
            </nav>
        </aside>
        <main class="flex-1 p-6">
            <div class="pagedone-card">
                <h1 class="text-2xl font-bold">Financial Overview</h1>
                <div id="sales-chart" class="apexcharts-canvas"></div>
            </div>
        </main>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/apexcharts"></script>
    <script>
        new ApexCharts(document.querySelector("#sales-chart"), {
            series: [{name: "Sales", data: [10000, 15000, 12000]}],
            chart: {type: "bar"}
        }).render();
    </script>
    ```

### AI Integration
- **LLMs**: DistilBERT, Llama 2, Mistral, Phi-2, Gemma for chat, form generation, and UI generation.
- **TensorFlow**:
  - Used for invoice image parsing:
    ```python
    import tensorflow as tf
    from PIL import Image
    def parse_invoice_image(image_path):
        img = Image.open(image_path)
        model = tf.keras.models.load_model('./models/ocr_model')
        text = model.predict(img)
        return text
    ```
- **Chat Route**:
  ```python
  @app.route('/v1/chat', methods=['POST'])
  @require_token
  def chat():
      data = request.json
      query = data.get('query')
      llm = AutoModelForCausalLM.from_pretrained('./models/llama2')
      with db_connection() as conn:
          context = conn.execute(
              "SELECT context_text FROM llm_embeddings WHERE companies_id = %s LIMIT 5",
              (get_company_id(app.config['current_user_id']),)
          ).fetchall()
      response = llm(f"Query: {query}\nContext: {[r['context_text'] for r in context]}")
      return jsonify({'response': response})
  ```

### Swagger/OpenAPI
- **Implementation**:
  ```python
  from flask_swagger_ui import get_swaggerui_blueprint
  SWAGGER_URL = '/swagger'
  API_URL = '/static/swagger.json'
  swaggerui_blueprint = get_swaggerui_blueprint(SWAGGER_URL, API_URL, config={'app_name': "AI Valido Online"})
  app.register_blueprint(swaggerui_blueprint)
  ```
- **swagger.json**:
  ```json
  {
      "openapi": "3.0.0",
      "info": {"title": "AI Valido Online API", "version": "1.0"},
      "components": {
          "securitySchemes": {
              "bearerAuth": {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"}
          }
      },
      "paths": {
          "/v1/invoices": {
              "get": {
                  "security": [{"bearerAuth": []}],
                  "responses": {"200": {"description": "List invoices"}}
              }
          }
      }
  }
  ```

### Automated UI Component Generation
- **Options**: Flowbite (tables, timelines, carousels), DaisyUI (calendars, cards), Pagedone (calendars, blocks), TailGrids (calendars), Preline (accordions, tabs), ApexCharts/Flowbite-Svelte (charts).
- **Implementation**:
  ```python
  @app.route('/v1/settings/generate-ui', methods=['POST'])
  @require_token
  def generate_ui():
      data = request.json
      prompt = data.get('prompt')
      component = data.get('component')  # e.g., 'Flowbite', 'ApexCharts'
      llm = AutoModelForCausalLM.from_pretrained('./models/gemma')
      html = llm(f"Generate {component} HTML for: {prompt}")
      return jsonify({'html': html, 'options': ['Flowbite', 'DaisyUI', 'Pagedone', 'TailGrids', 'Preline', 'ApexCharts']})
  ```

### Ticketing Module
- **L1-L4 Support**:
  - L1: `support` creates tickets (`open`, `pending_l1`).
  - L2: `support` escalates to `pending_l2`.
  - L3: `manager` handles `pending_l3`.
  - L4: `developer` resolves `pending_l4` or approves (`approved`/`closed`).
- **Table**: `tickets_statuses` defines statuses.

### Serbian Business Reports
- **Balance Sheet**: Assets, liabilities, equity.
- **Income Statement**: Revenue, expenses, net income.
- **Cash Flow Statement**: Inflows, outflows, net cash flow.
- **VAT Report**: Taxable amounts and VAT per period.
- **API Endpoint**: `/v1/reports/{balance-sheet,income-statement,cash-flow,vat}`.

## Technical Stack
- **Backend**: Flask, `sqlc`, JWT, Swagger.
- **Frontend**: Tailwind CSS, Flowbite, FlyonUI, DaisyUI, Pagedone, TailGrids, Simple-DataTables, Preline, ApexCharts.
- **Database**: PostgreSQL with `pgvector`, `pgcrypto`, `pg_cron`, Citus.
- **AI**: DistilBERT, Llama 2, Mistral, Phi-2, Gemma, TensorFlow.

## Development Plan
- **Iteration 1 (Days 1-10)**: Schema, sample data, RLS, `/v1` APIs, Swagger, UI setup.
- **Iteration 2 (Days 11-20)**: LLM/TensorFlow integration, reports, ticketing, fiscal year procedures.
- **Iteration 3 (Days 21-30)**: Dashboard, sharding, backups, deployment.

## Future Enhancements
- Predictive analytics, real-time dashboards, mobile app, multi-tenant SaaS, external API integrations, advanced charts, workflow automation, AI chat enhancements, document management, customizable dashboards.

## Conclusion
AI Valido Online delivers a scalable, compliant ERP with advanced AI, secure APIs, and a responsive UI, ready within 30 days.