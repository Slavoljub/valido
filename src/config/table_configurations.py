"""
Table Configurations for Unified CRUD System
Configurations for all PostgreSQL tables with UI components and special features
"""

from src.crud.unified_crud_config import (
    CRUDConfig, ColumnConfig, FilterConfig, TabConfig, 
    AccordionConfig, ModalConfig, SpecialButtonConfig, ValidationRule
)


def get_companies_config() -> CRUDConfig:
    """Get configuration for companies table with special tabs"""
    config = CRUDConfig(
        table_name="companies",
        primary_key="id",
        display_name="Companies",
        description="Business companies and organizations"
    )
    
    # Add columns
    config.add_column(ColumnConfig("company_name", "Company Name", sortable=True, searchable=True))
    config.add_column(ColumnConfig("pib", "PIB", sortable=True, searchable=True))
    config.add_column(ColumnConfig("maticni_broj", "Maticni Broj", sortable=True, searchable=True))
    config.add_column(ColumnConfig("email", "Email", sortable=True, searchable=True))
    config.add_column(ColumnConfig("phone", "Phone", sortable=False, searchable=True))
    config.add_column(ColumnConfig("city", "City", sortable=True, searchable=True))
    config.add_column(ColumnConfig("address", "Address", sortable=False, searchable=True))
    config.add_column(ColumnConfig("created_at", "Created", sortable=True, searchable=False))
    
    # Add filters
    config.add_filter(FilterConfig("is_active", "select", "Status", options=[
        {"value": "true", "label": "Active"},
        {"value": "false", "label": "Inactive"}
    ]))
    config.add_filter(FilterConfig("address_city", "text", "City"))
    
    # Add tabs for related data
    config.add_tab(TabConfig("employees", "Employees", "employees", "company_id"))
    config.add_tab(TabConfig("partners", "Business Partners", "business_partners", "company_id"))
    config.add_tab(TabConfig("products", "Products", "products", "company_id"))
    config.add_tab(TabConfig("transactions", "Financial Transactions", "financial_transactions", "company_id"))
    
    # Add validation rules
    config.add_validation_rule(ValidationRule("company_name", "required", "Company name is required"))
    config.add_validation_rule(ValidationRule("tax_id", "required", "Tax ID is required"))
    config.add_validation_rule(ValidationRule("email", "email", "Invalid email format"))
    
    # Enable special features
    config.ui_components.update({
        'tabs': True,
        'bulk_operations': True,
        'live_editing': True
    })
    
    return config


def get_users_config() -> CRUDConfig:
    """Get configuration for users table"""
    config = CRUDConfig(
        table_name="users",
        primary_key="id",
        display_name="Users",
        description="System users and authentication"
    )
    
    # Add columns
    config.add_column(ColumnConfig("username", "Username", sortable=True, searchable=True))
    config.add_column(ColumnConfig("email", "Email", sortable=True, searchable=True))
    config.add_column(ColumnConfig("is_active", "Status", sortable=True, searchable=False))
    config.add_column(ColumnConfig("last_login", "Last Login", sortable=True, searchable=False))
    config.add_column(ColumnConfig("created_at", "Created", sortable=True, searchable=False))
    
    # Add filters
    config.add_filter(FilterConfig("is_active", "select", "Status", options=[
        {"value": "true", "label": "Active"},
        {"value": "false", "label": "Inactive"}
    ]))
    
    # Add validation rules
    config.add_validation_rule(ValidationRule("username", "required", "Username is required"))
    config.add_validation_rule(ValidationRule("email", "required", "Email is required"))
    config.add_validation_rule(ValidationRule("email", "email", "Invalid email format"))
    
    return config


def get_business_partners_config() -> CRUDConfig:
    """Get configuration for business partners table"""
    config = CRUDConfig(
        table_name="business_partners",
        primary_key="id",
        display_name="Business Partners",
        description="Customers, suppliers, and business contacts"
    )
    
    # Add columns
    config.add_column(ColumnConfig("partner_name", "Partner Name", sortable=True, searchable=True))
    config.add_column(ColumnConfig("partner_type", "Type", sortable=True, searchable=True))
    config.add_column(ColumnConfig("email", "Email", sortable=True, searchable=True))
    config.add_column(ColumnConfig("phone", "Phone", sortable=False, searchable=True))
    config.add_column(ColumnConfig("address_city", "City", sortable=True, searchable=True))
    config.add_column(ColumnConfig("is_active", "Status", sortable=True, searchable=False))
    
    # Add filters
    config.add_filter(FilterConfig("partner_type", "select", "Partner Type", options=[
        {"value": "customer", "label": "Customer"},
        {"value": "supplier", "label": "Supplier"},
        {"value": "vendor", "label": "Vendor"}
    ]))
    config.add_filter(FilterConfig("is_active", "select", "Status", options=[
        {"value": "true", "label": "Active"},
        {"value": "false", "label": "Inactive"}
    ]))
    
    return config


def get_products_config() -> CRUDConfig:
    """Get configuration for products table"""
    config = CRUDConfig(
        table_name="products",
        primary_key="id",
        display_name="Products",
        description="Product catalog and inventory items"
    )
    
    # Add columns
    config.add_column(ColumnConfig("product_code", "Product Code", sortable=True, searchable=True))
    config.add_column(ColumnConfig("product_name", "Product Name", sortable=True, searchable=True))
    config.add_column(ColumnConfig("product_category", "Category", sortable=True, searchable=True))
    config.add_column(ColumnConfig("unit_price", "Price", sortable=True, searchable=False))
    config.add_column(ColumnConfig("current_stock", "Stock", sortable=True, searchable=False))
    config.add_column(ColumnConfig("is_active", "Status", sortable=True, searchable=False))
    
    # Add filters
    config.add_filter(FilterConfig("product_category", "text", "Category"))
    config.add_filter(FilterConfig("is_active", "select", "Status", options=[
        {"value": "true", "label": "Active"},
        {"value": "false", "label": "Inactive"}
    ]))
    
    return config


def get_financial_transactions_config() -> CRUDConfig:
    """Get configuration for financial transactions table"""
    config = CRUDConfig(
        table_name="financial_transactions",
        primary_key="financial_transactions_id",
        display_name="Financial Transactions",
        description="All financial transactions and accounting entries"
    )
    
    # Add columns
    config.add_column(ColumnConfig("transaction_date", "Date", sortable=True, searchable=False))
    config.add_column(ColumnConfig("transaction_type", "Type", sortable=True, searchable=True))
    config.add_column(ColumnConfig("description", "Description", sortable=False, searchable=True))
    config.add_column(ColumnConfig("debit_amount", "Debit", sortable=True, searchable=False))
    config.add_column(ColumnConfig("credit_amount", "Credit", sortable=True, searchable=False))
    config.add_column(ColumnConfig("status", "Status", sortable=True, searchable=False))
    
    # Add filters
    config.add_filter(FilterConfig("transaction_type", "select", "Transaction Type", options=[
        {"value": "ledger", "label": "General Ledger"},
        {"value": "bank_statement", "label": "Bank Statement"},
        {"value": "inventory", "label": "Inventory"},
        {"value": "payroll", "label": "Payroll"}
    ]))
    config.add_filter(FilterConfig("status", "select", "Status", options=[
        {"value": "draft", "label": "Draft"},
        {"value": "posted", "label": "Posted"},
        {"value": "voided", "label": "Voided"}
    ]))
    
    return config


def get_employees_config() -> CRUDConfig:
    """Get configuration for employees table"""
    config = CRUDConfig(
        table_name="employees",
        primary_key="employees_id",
        display_name="Employees",
        description="Employee records and HR data"
    )
    
    # Add columns
    config.add_column(ColumnConfig("employee_code", "Employee Code", sortable=True, searchable=True))
    config.add_column(ColumnConfig("first_name", "First Name", sortable=True, searchable=True))
    config.add_column(ColumnConfig("last_name", "Last Name", sortable=True, searchable=True))
    config.add_column(ColumnConfig("job_title", "Job Title", sortable=True, searchable=True))
    config.add_column(ColumnConfig("department", "Department", sortable=True, searchable=True))
    config.add_column(ColumnConfig("employment_status", "Status", sortable=True, searchable=False))
    config.add_column(ColumnConfig("hire_date", "Hire Date", sortable=True, searchable=False))
    
    # Add filters
    config.add_filter(FilterConfig("employment_status", "select", "Employment Status", options=[
        {"value": "active", "label": "Active"},
        {"value": "terminated", "label": "Terminated"},
        {"value": "suspended", "label": "Suspended"}
    ]))
    config.add_filter(FilterConfig("department", "text", "Department"))
    
    return config


def get_warehouses_config() -> CRUDConfig:
    """Get configuration for warehouses table"""
    config = CRUDConfig(
        table_name="warehouses",
        primary_key="warehouses_id",
        display_name="Warehouses",
        description="Warehouse and inventory locations"
    )

    # Add columns
    config.add_column(ColumnConfig("warehouse_code", "Code", sortable=True, searchable=True))
    config.add_column(ColumnConfig("warehouse_name", "Name", sortable=True, searchable=True))
    config.add_column(ColumnConfig("address_city", "City", sortable=True, searchable=True))
    config.add_column(ColumnConfig("contact_person", "Contact Person", sortable=True, searchable=True))
    config.add_column(ColumnConfig("phone", "Phone", sortable=False, searchable=True))
    config.add_column(ColumnConfig("is_main_warehouse", "Main Warehouse", sortable=True, searchable=False))
    config.add_column(ColumnConfig("is_active", "Active", sortable=True, searchable=False))

    # Add filters
    config.add_filter(FilterConfig("is_main_warehouse", "select", "Main Warehouse", options=[
        {"value": "true", "label": "Yes"},
        {"value": "false", "label": "No"}
    ]))
    config.add_filter(FilterConfig("is_active", "select", "Status", options=[
        {"value": "true", "label": "Active"},
        {"value": "false", "label": "Inactive"}
    ]))

    return config


def get_ai_models_system_config() -> CRUDConfig:
    """Get configuration for ai_models_system table"""
    config = CRUDConfig(
        table_name="ai_models_system",
        primary_key="ai_models_system_id",
        display_name="AI Models",
        description="AI models and machine learning systems"
    )

    # Add columns
    config.add_column(ColumnConfig("model_name", "Model Name", sortable=True, searchable=True))
    config.add_column(ColumnConfig("model_code", "Model Code", sortable=True, searchable=True))
    config.add_column(ColumnConfig("model_type", "Type", sortable=True, searchable=True))
    config.add_column(ColumnConfig("model_family", "Family", sortable=True, searchable=True))
    config.add_column(ColumnConfig("model_size", "Size", sortable=True, searchable=True))
    config.add_column(ColumnConfig("performance_score", "Performance", sortable=True, searchable=False))
    config.add_column(ColumnConfig("is_active", "Active", sortable=True, searchable=False))

    # Add filters
    config.add_filter(FilterConfig("model_type", "select", "Model Type", options=[
        {"value": "ai_model", "label": "AI Model"},
        {"value": "ml_algorithm", "label": "ML Algorithm"},
        {"value": "ml_model", "label": "ML Model"}
    ]))
    config.add_filter(FilterConfig("model_family", "text", "Model Family"))
    config.add_filter(FilterConfig("is_active", "select", "Status", options=[
        {"value": "true", "label": "Active"},
        {"value": "false", "label": "Inactive"}
    ]))

    return config


def get_ai_insights_data_config() -> CRUDConfig:
    """Get configuration for ai_insights_data table"""
    config = CRUDConfig(
        table_name="ai_insights_data",
        primary_key="ai_insights_data_id",
        display_name="AI Insights",
        description="AI insights and training data"
    )

    # Add columns
    config.add_column(ColumnConfig("data_type", "Data Type", sortable=True, searchable=True))
    config.add_column(ColumnConfig("title", "Title", sortable=True, searchable=True))
    config.add_column(ColumnConfig("category", "Category", sortable=True, searchable=True))
    config.add_column(ColumnConfig("source", "Source", sortable=True, searchable=True))
    config.add_column(ColumnConfig("validation_status", "Validation Status", sortable=True, searchable=False))
    config.add_column(ColumnConfig("quality_score", "Quality Score", sortable=True, searchable=False))
    config.add_column(ColumnConfig("is_active", "Active", sortable=True, searchable=False))

    # Add filters
    config.add_filter(FilterConfig("data_type", "select", "Data Type", options=[
        {"value": "insight", "label": "Insight"},
        {"value": "training_data", "label": "Training Data"}
    ]))
    config.add_filter(FilterConfig("validation_status", "select", "Validation Status", options=[
        {"value": "pending", "label": "Pending"},
        {"value": "validated", "label": "Validated"},
        {"value": "rejected", "label": "Rejected"}
    ]))
    config.add_filter(FilterConfig("is_active", "select", "Status", options=[
        {"value": "true", "label": "Active"},
        {"value": "false", "label": "Inactive"}
    ]))

    return config


def get_communication_system_config() -> CRUDConfig:
    """Get configuration for communication_system table"""
    config = CRUDConfig(
        table_name="communication_system",
        primary_key="communication_system_id",
        display_name="Communications",
        description="Email, notifications, and communication system"
    )

    # Add columns
    config.add_column(ColumnConfig("communication_type", "Type", sortable=True, searchable=True))
    config.add_column(ColumnConfig("subject", "Subject", sortable=True, searchable=True))
    config.add_column(ColumnConfig("category", "Category", sortable=True, searchable=True))
    config.add_column(ColumnConfig("priority", "Priority", sortable=True, searchable=False))
    config.add_column(ColumnConfig("status", "Status", sortable=True, searchable=False))
    config.add_column(ColumnConfig("sent_at", "Sent At", sortable=True, searchable=False))
    config.add_column(ColumnConfig("total_recipients", "Recipients", sortable=True, searchable=False))

    # Add filters
    config.add_filter(FilterConfig("communication_type", "select", "Communication Type", options=[
        {"value": "email", "label": "Email"},
        {"value": "notification", "label": "Notification"},
        {"value": "push", "label": "Push Message"}
    ]))
    config.add_filter(FilterConfig("status", "select", "Status", options=[
        {"value": "draft", "label": "Draft"},
        {"value": "scheduled", "label": "Scheduled"},
        {"value": "sent", "label": "Sent"},
        {"value": "delivered", "label": "Delivered"}
    ]))
    config.add_filter(FilterConfig("priority", "select", "Priority", options=[
        {"value": "low", "label": "Low"},
        {"value": "normal", "label": "Normal"},
        {"value": "high", "label": "High"},
        {"value": "urgent", "label": "Urgent"}
    ]))

    return config


def get_chat_sessions_config() -> CRUDConfig:
    """Get configuration for chat_sessions table"""
    config = CRUDConfig(
        table_name="chat_sessions",
        primary_key="chat_sessions_id",
        display_name="Chat Sessions",
        description="AI chat sessions and conversations"
    )

    # Add columns
    config.add_column(ColumnConfig("session_id", "Session ID", sortable=True, searchable=True))
    config.add_column(ColumnConfig("session_title", "Title", sortable=True, searchable=True))
    config.add_column(ColumnConfig("model_used", "AI Model", sortable=True, searchable=True))
    config.add_column(ColumnConfig("is_active", "Active", sortable=True, searchable=False))
    config.add_column(ColumnConfig("last_activity", "Last Activity", sortable=True, searchable=False))
    config.add_column(ColumnConfig("message_count", "Messages", sortable=True, searchable=False))
    config.add_column(ColumnConfig("total_tokens", "Tokens Used", sortable=True, searchable=False))

    # Add filters
    config.add_filter(FilterConfig("is_active", "select", "Status", options=[
        {"value": "true", "label": "Active"},
        {"value": "false", "label": "Inactive"}
    ]))
    config.add_filter(FilterConfig("model_used", "text", "AI Model"))

    return config


def get_chat_messages_config() -> CRUDConfig:
    """Get configuration for chat_messages table"""
    config = CRUDConfig(
        table_name="chat_messages",
        primary_key="chat_messages_id",
        display_name="Chat Messages",
        description="Individual chat messages and interactions"
    )

    # Add columns
    config.add_column(ColumnConfig("message_type", "Type", sortable=True, searchable=True))
    config.add_column(ColumnConfig("message_content", "Content", sortable=False, searchable=True))
    config.add_column(ColumnConfig("token_count", "Tokens", sortable=True, searchable=False))
    config.add_column(ColumnConfig("message_order", "Order", sortable=True, searchable=False))
    config.add_column(ColumnConfig("is_deleted", "Deleted", sortable=True, searchable=False))
    config.add_column(ColumnConfig("created_at", "Created", sortable=True, searchable=False))

    # Add filters
    config.add_filter(FilterConfig("message_type", "select", "Message Type", options=[
        {"value": "user", "label": "User"},
        {"value": "assistant", "label": "Assistant"},
        {"value": "system", "label": "System"},
        {"value": "tool", "label": "Tool"}
    ]))
    config.add_filter(FilterConfig("is_deleted", "select", "Status", options=[
        {"value": "true", "label": "Deleted"},
        {"value": "false", "label": "Active"}
    ]))

    return config


def get_chat_artifacts_memory_config() -> CRUDConfig:
    """Get configuration for chat_artifacts_memory table"""
    config = CRUDConfig(
        table_name="chat_artifacts_memory",
        primary_key="chat_artifacts_memory_id",
        display_name="Chat Artifacts",
        description="Chat artifacts and memory storage"
    )

    # Add columns
    config.add_column(ColumnConfig("artifact_type", "Type", sortable=True, searchable=True))
    config.add_column(ColumnConfig("artifact_name", "Name", sortable=True, searchable=True))
    config.add_column(ColumnConfig("content_type", "Content Type", sortable=True, searchable=True))
    config.add_column(ColumnConfig("mime_type", "MIME Type", sortable=True, searchable=False))
    config.add_column(ColumnConfig("artifact_size", "Size (bytes)", sortable=True, searchable=False))
    config.add_column(ColumnConfig("importance_score", "Importance", sortable=True, searchable=False))

    # Add filters
    config.add_filter(FilterConfig("artifact_type", "select", "Artifact Type", options=[
        {"value": "artifact", "label": "Artifact"},
        {"value": "memory", "label": "Memory"}
    ]))
    config.add_filter(FilterConfig("content_type", "select", "Content Type", options=[
        {"value": "file", "label": "File"},
        {"value": "image", "label": "Image"},
        {"value": "document", "label": "Document"},
        {"value": "conversation_buffer", "label": "Conversation Buffer"},
        {"value": "entity_memory", "label": "Entity Memory"},
        {"value": "vector_memory", "label": "Vector Memory"}
    ]))

    return config


def get_search_system_config() -> CRUDConfig:
    """Get configuration for search_system table"""
    config = CRUDConfig(
        table_name="search_system",
        primary_key="search_system_id",
        display_name="Search System",
        description="Search queries and vector embeddings"
    )

    # Add columns
    config.add_column(ColumnConfig("search_type", "Type", sortable=True, searchable=True))
    config.add_column(ColumnConfig("entity_type", "Entity Type", sortable=True, searchable=True))
    config.add_column(ColumnConfig("query_text", "Query Text", sortable=False, searchable=True))
    config.add_column(ColumnConfig("search_category", "Category", sortable=True, searchable=True))
    config.add_column(ColumnConfig("results_count", "Results", sortable=True, searchable=False))
    config.add_column(ColumnConfig("search_time_ms", "Time (ms)", sortable=True, searchable=False))
    config.add_column(ColumnConfig("is_successful", "Successful", sortable=True, searchable=False))

    # Add filters
    config.add_filter(FilterConfig("search_type", "select", "Search Type", options=[
        {"value": "index", "label": "Index"},
        {"value": "query", "label": "Query"},
        {"value": "embedding", "label": "Embedding"}
    ]))
    config.add_filter(FilterConfig("is_successful", "select", "Status", options=[
        {"value": "true", "label": "Successful"},
        {"value": "false", "label": "Failed"}
    ]))
    config.add_filter(FilterConfig("entity_type", "text", "Entity Type"))

    return config


def get_api_integrations_config() -> CRUDConfig:
    """Get configuration for api_integrations table"""
    config = CRUDConfig(
        table_name="api_integrations",
        primary_key="api_integrations_id",
        display_name="API Integrations",
        description="API keys, webhooks, and integrations"
    )

    # Add columns
    config.add_column(ColumnConfig("integration_type", "Type", sortable=True, searchable=True))
    config.add_column(ColumnConfig("name", "Name", sortable=True, searchable=True))
    config.add_column(ColumnConfig("description", "Description", sortable=False, searchable=True))
    config.add_column(ColumnConfig("is_active", "Active", sortable=True, searchable=False))
    config.add_column(ColumnConfig("rate_limit", "Rate Limit", sortable=True, searchable=False))
    config.add_column(ColumnConfig("last_used_at", "Last Used", sortable=True, searchable=False))

    # Add filters
    config.add_filter(FilterConfig("integration_type", "select", "Integration Type", options=[
        {"value": "api_key", "label": "API Key"},
        {"value": "webhook", "label": "Webhook"},
        {"value": "file_attachment", "label": "File Attachment"}
    ]))
    config.add_filter(FilterConfig("is_active", "select", "Status", options=[
        {"value": "true", "label": "Active"},
        {"value": "false", "label": "Inactive"}
    ]))

    return config


def get_system_configuration_config() -> CRUDConfig:
    """Get configuration for system_configuration table"""
    config = CRUDConfig(
        table_name="system_configuration",
        primary_key="system_configuration_id",
        display_name="System Configuration",
        description="System settings and configuration"
    )

    # Add columns
    config.add_column(ColumnConfig("config_key", "Config Key", sortable=True, searchable=True))
    config.add_column(ColumnConfig("config_category", "Category", sortable=True, searchable=True))
    config.add_column(ColumnConfig("config_type", "Type", sortable=True, searchable=True))
    config.add_column(ColumnConfig("is_system_config", "System Config", sortable=True, searchable=False))
    config.add_column(ColumnConfig("is_user_editable", "User Editable", sortable=True, searchable=False))
    config.add_column(ColumnConfig("created_at", "Created", sortable=True, searchable=False))

    # Add filters
    config.add_filter(FilterConfig("config_type", "select", "Config Type", options=[
        {"value": "system", "label": "System"},
        {"value": "cache", "label": "Cache"},
        {"value": "pwa", "label": "PWA"},
        {"value": "automation", "label": "Automation"},
        {"value": "backup", "label": "Backup"}
    ]))
    config.add_filter(FilterConfig("config_category", "text", "Category"))
    config.add_filter(FilterConfig("is_system_config", "select", "System Config", options=[
        {"value": "true", "label": "Yes"},
        {"value": "false", "label": "No"}
    ]))

    return config


def get_audit_monitoring_config() -> CRUDConfig:
    """Get configuration for audit_monitoring table"""
    config = CRUDConfig(
        table_name="audit_monitoring",
        primary_key="audit_monitoring_id",
        display_name="Audit & Monitoring",
        description="System audit logs and performance monitoring"
    )

    # Add columns
    config.add_column(ColumnConfig("audit_type", "Type", sortable=True, searchable=True))
    config.add_column(ColumnConfig("action", "Action", sortable=True, searchable=True))
    config.add_column(ColumnConfig("resource_type", "Resource Type", sortable=True, searchable=True))
    config.add_column(ColumnConfig("metric_name", "Metric Name", sortable=True, searchable=True))
    config.add_column(ColumnConfig("metric_value", "Metric Value", sortable=True, searchable=False))
    config.add_column(ColumnConfig("recorded_at", "Recorded At", sortable=True, searchable=False))

    # Add filters
    config.add_filter(FilterConfig("audit_type", "select", "Audit Type", options=[
        {"value": "audit", "label": "Audit"},
        {"value": "performance", "label": "Performance"},
        {"value": "cache", "label": "Cache"},
        {"value": "task", "label": "Task"}
    ]))
    config.add_filter(FilterConfig("resource_type", "text", "Resource Type"))
    config.add_filter(FilterConfig("metric_name", "text", "Metric Name"))

    return config


def get_task_automation_config() -> CRUDConfig:
    """Get configuration for task_automation table"""
    config = CRUDConfig(
        table_name="task_automation",
        primary_key="task_automation_id",
        display_name="Task Automation",
        description="Automated tasks and scheduled jobs"
    )

    # Add columns
    config.add_column(ColumnConfig("task_name", "Task Name", sortable=True, searchable=True))
    config.add_column(ColumnConfig("task_type", "Type", sortable=True, searchable=True))
    config.add_column(ColumnConfig("schedule_cron", "Schedule", sortable=False, searchable=True))
    config.add_column(ColumnConfig("is_active", "Active", sortable=True, searchable=False))
    config.add_column(ColumnConfig("last_run", "Last Run", sortable=True, searchable=False))
    config.add_column(ColumnConfig("next_run", "Next Run", sortable=True, searchable=False))
    config.add_column(ColumnConfig("run_count", "Run Count", sortable=True, searchable=False))
    config.add_column(ColumnConfig("success_count", "Success Count", sortable=True, searchable=False))

    # Add filters
    config.add_filter(FilterConfig("task_type", "select", "Task Type", options=[
        {"value": "automation", "label": "Automation"},
        {"value": "backup", "label": "Backup"},
        {"value": "report", "label": "Report"},
        {"value": "sync", "label": "Sync"}
    ]))
    config.add_filter(FilterConfig("is_active", "select", "Status", options=[
        {"value": "true", "label": "Active"},
        {"value": "false", "label": "Inactive"}
    ]))

    return config


def get_background_processing_config() -> CRUDConfig:
    """Get configuration for background_processing table"""
    config = CRUDConfig(
        table_name="background_processing",
        primary_key="background_processing_id",
        display_name="Background Processing",
        description="Background jobs and processing tasks"
    )

    # Add columns
    config.add_column(ColumnConfig("processing_type", "Type", sortable=True, searchable=True))
    config.add_column(ColumnConfig("job_name", "Job Name", sortable=True, searchable=True))
    config.add_column(ColumnConfig("status", "Status", sortable=True, searchable=True))
    config.add_column(ColumnConfig("priority", "Priority", sortable=True, searchable=False))
    config.add_column(ColumnConfig("progress", "Progress", sortable=True, searchable=False))
    config.add_column(ColumnConfig("scheduled_at", "Scheduled At", sortable=True, searchable=False))
    config.add_column(ColumnConfig("started_at", "Started At", sortable=True, searchable=False))
    config.add_column(ColumnConfig("completed_at", "Completed At", sortable=True, searchable=False))

    # Add filters
    config.add_filter(FilterConfig("processing_type", "select", "Processing Type", options=[
        {"value": "job", "label": "Job"},
        {"value": "pwa_queue", "label": "PWA Queue"},
        {"value": "webhook_delivery", "label": "Webhook Delivery"}
    ]))
    config.add_filter(FilterConfig("status", "select", "Status", options=[
        {"value": "pending", "label": "Pending"},
        {"value": "processing", "label": "Processing"},
        {"value": "completed", "label": "Completed"},
        {"value": "failed", "label": "Failed"}
    ]))
    config.add_filter(FilterConfig("priority", "select", "Priority", options=[
        {"value": "1", "label": "Low"},
        {"value": "5", "label": "Normal"},
        {"value": "10", "label": "High"}
    ]))

    return config


def get_all_table_configs() -> dict:
    """Get all table configurations"""
    return {
        "companies": get_companies_config(),
        "users": get_users_config(),
        "business_partners": get_business_partners_config(),
        "products": get_products_config(),
        "financial_transactions": get_financial_transactions_config(),
        "employees": get_employees_config(),
        "countries": get_countries_config(),
        "business_config": get_business_config_config(),
        "business_entities": get_business_entities_config(),
        "user_access": get_user_access_config(),
        "fiscal_years": get_fiscal_years_config(),
        "chart_of_accounts": get_chart_of_accounts_config(),
        "warehouses": get_warehouses_config(),
        "ai_models_system": get_ai_models_system_config(),
        "ai_insights_data": get_ai_insights_data_config(),
        "communication_system": get_communication_system_config(),
        "chat_sessions": get_chat_sessions_config(),
        "chat_messages": get_chat_messages_config(),
        "chat_artifacts_memory": get_chat_artifacts_memory_config(),
        "search_system": get_search_system_config(),
        "api_integrations": get_api_integrations_config(),
        "system_configuration": get_system_configuration_config(),
        "audit_monitoring": get_audit_monitoring_config(),
        "task_automation": get_task_automation_config(),
        "background_processing": get_background_processing_config(),
    }


def get_countries_config() -> CRUDConfig:
    """Get configuration for countries table"""
    config = CRUDConfig(
        table_name="countries",
        primary_key="countries_id",
        display_name="Countries",
        description="Country information and data"
    )

    # Add columns
    config.add_column(ColumnConfig("iso_code", "ISO Code", sortable=True, searchable=True))
    config.add_column(ColumnConfig("name", "Name", sortable=True, searchable=True))
    config.add_column(ColumnConfig("native_name", "Native Name", sortable=True, searchable=True))
    config.add_column(ColumnConfig("capital", "Capital", sortable=True, searchable=True))
    config.add_column(ColumnConfig("region", "Region", sortable=True, searchable=True))
    config.add_column(ColumnConfig("population", "Population", sortable=True, searchable=False))
    config.add_column(ColumnConfig("area_km2", "Area (km²)", sortable=True, searchable=False))

    # Add filters
    config.add_filter(FilterConfig("region", "text", "Region"))
    config.add_filter(FilterConfig("iso_code", "text", "ISO Code"))

    return config


def get_business_config_config() -> CRUDConfig:
    """Get configuration for business_config table"""
    config = CRUDConfig(
        table_name="business_config",
        primary_key="business_config_id",
        display_name="Business Configuration",
        description="Business configuration and settings"
    )

    # Add columns
    config.add_column(ColumnConfig("config_type", "Type", sortable=True, searchable=True))
    config.add_column(ColumnConfig("type_code", "Code", sortable=True, searchable=True))
    config.add_column(ColumnConfig("type_name", "Name", sortable=True, searchable=True))
    config.add_column(ColumnConfig("category", "Category", sortable=True, searchable=True))
    config.add_column(ColumnConfig("is_system_type", "System Type", sortable=True, searchable=False))
    config.add_column(ColumnConfig("is_active", "Active", sortable=True, searchable=False))

    # Add filters
    config.add_filter(FilterConfig("config_type", "select", "Config Type", options=[
        {"value": "account_type", "label": "Account Type"},
        {"value": "transaction_type", "label": "Transaction Type"},
        {"value": "tax_type", "label": "Tax Type"},
        {"value": "currency", "label": "Currency"}
    ]))
    config.add_filter(FilterConfig("is_active", "select", "Status", options=[
        {"value": "true", "label": "Active"},
        {"value": "false", "label": "Inactive"}
    ]))

    return config


def get_business_entities_config() -> CRUDConfig:
    """Get configuration for business_entities table"""
    config = CRUDConfig(
        table_name="business_entities",
        primary_key="business_entities_id",
        display_name="Business Entities",
        description="Business forms and areas"
    )

    # Add columns
    config.add_column(ColumnConfig("entity_type", "Type", sortable=True, searchable=True))
    config.add_column(ColumnConfig("entity_code", "Code", sortable=True, searchable=True))
    config.add_column(ColumnConfig("entity_name", "Name", sortable=True, searchable=True))
    config.add_column(ColumnConfig("is_system_entity", "System Entity", sortable=True, searchable=False))
    config.add_column(ColumnConfig("is_active", "Active", sortable=True, searchable=False))

    # Add filters
    config.add_filter(FilterConfig("entity_type", "select", "Entity Type", options=[
        {"value": "business_form", "label": "Business Form"},
        {"value": "business_area", "label": "Business Area"},
        {"value": "partner_type", "label": "Partner Type"}
    ]))
    config.add_filter(FilterConfig("is_active", "select", "Status", options=[
        {"value": "true", "label": "Active"},
        {"value": "false", "label": "Inactive"}
    ]))

    return config


def get_user_access_config() -> CRUDConfig:
    """Get configuration for user_access table"""
    config = CRUDConfig(
        table_name="user_access",
        primary_key="user_access_id",
        display_name="User Access",
        description="User permissions and access control"
    )

    # Add columns
    config.add_column(ColumnConfig("access_type", "Access Type", sortable=True, searchable=True))
    config.add_column(ColumnConfig("status", "Status", sortable=True, searchable=True))
    config.add_column(ColumnConfig("access_level", "Access Level", sortable=True, searchable=True))
    config.add_column(ColumnConfig("role_name", "Role Name", sortable=True, searchable=True))
    config.add_column(ColumnConfig("permission_name", "Permission", sortable=True, searchable=True))
    config.add_column(ColumnConfig("is_active", "Active", sortable=True, searchable=False))

    # Add filters
    config.add_filter(FilterConfig("access_type", "select", "Access Type", options=[
        {"value": "company_access", "label": "Company Access"},
        {"value": "role", "label": "Role"},
        {"value": "permission", "label": "Permission"},
        {"value": "assignment", "label": "Assignment"}
    ]))
    config.add_filter(FilterConfig("status", "select", "Status", options=[
        {"value": "active", "label": "Active"},
        {"value": "inactive", "label": "Inactive"},
        {"value": "pending", "label": "Pending"}
    ]))

    return config


def get_fiscal_years_config() -> CRUDConfig:
    """Get configuration for fiscal_years table"""
    config = CRUDConfig(
        table_name="fiscal_years",
        primary_key="fiscal_years_id",
        display_name="Fiscal Years",
        description="Financial year management"
    )

    # Add columns
    config.add_column(ColumnConfig("year", "Year", sortable=True, searchable=True))
    config.add_column(ColumnConfig("start_date", "Start Date", sortable=True, searchable=False))
    config.add_column(ColumnConfig("end_date", "End Date", sortable=True, searchable=False))
    config.add_column(ColumnConfig("is_current", "Current", sortable=True, searchable=False))
    config.add_column(ColumnConfig("is_closed", "Closed", sortable=True, searchable=False))

    # Add filters
    config.add_filter(FilterConfig("is_current", "select", "Current Year", options=[
        {"value": "true", "label": "Yes"},
        {"value": "false", "label": "No"}
    ]))
    config.add_filter(FilterConfig("is_closed", "select", "Closed", options=[
        {"value": "true", "label": "Yes"},
        {"value": "false", "label": "No"}
    ]))

    return config


def get_chart_of_accounts_config() -> CRUDConfig:
    """Get configuration for chart_of_accounts table"""
    config = CRUDConfig(
        table_name="chart_of_accounts",
        primary_key="chart_of_accounts_id",
        display_name="Chart of Accounts",
        description="Accounting chart of accounts"
    )

    # Add columns
    config.add_column(ColumnConfig("account_number", "Account Number", sortable=True, searchable=True))
    config.add_column(ColumnConfig("account_name", "Account Name", sortable=True, searchable=True))
    config.add_column(ColumnConfig("account_level", "Level", sortable=True, searchable=False))
    config.add_column(ColumnConfig("is_active", "Active", sortable=True, searchable=False))
    config.add_column(ColumnConfig("opening_balance", "Opening Balance", sortable=True, searchable=False))
    config.add_column(ColumnConfig("current_balance", "Current Balance", sortable=True, searchable=False))

    # Add filters
    config.add_filter(FilterConfig("account_level", "select", "Account Level", options=[
        {"value": "1", "label": "Level 1"},
        {"value": "2", "label": "Level 2"},
        {"value": "3", "label": "Level 3"},
        {"value": "4", "label": "Level 4"}
    ]))
    config.add_filter(FilterConfig("is_active", "select", "Status", options=[
        {"value": "true", "label": "Active"},
        {"value": "false", "label": "Inactive"}
    ]))

    return config


def get_batch_configs() -> dict:
    """Get configurations organized by batches for parallel processing"""
    return {
        "batch_1": {
            "companies": get_companies_config(),
            "users": get_users_config(),
        },
        "batch_2": {
            "business_partners": get_business_partners_config(),
            "products": get_products_config(),
        },
        "batch_3": {
            "financial_transactions": get_financial_transactions_config(),
            "employees": get_employees_config(),
        },
        "batch_4": {
            "countries": get_countries_config(),
            "business_config": get_business_config_config(),
        },
        "batch_5": {
            "business_entities": get_business_entities_config(),
            "user_access": get_user_access_config(),
        },
        "batch_6": {
            "fiscal_years": get_fiscal_years_config(),
            "chart_of_accounts": get_chart_of_accounts_config(),
        },
        "batch_7": {
            "warehouses": get_warehouses_config(),
            "ai_models_system": get_ai_models_system_config(),
        },
        "batch_8": {
            "ai_insights_data": get_ai_insights_data_config(),
            "communication_system": get_communication_system_config(),
        },
        "batch_9": {
            "chat_sessions": get_chat_sessions_config(),
            "chat_messages": get_chat_messages_config(),
        },
        "batch_10": {
            "chat_artifacts_memory": get_chat_artifacts_memory_config(),
            "search_system": get_search_system_config(),
        },
        "batch_11": {
            "api_integrations": get_api_integrations_config(),
            "system_configuration": get_system_configuration_config(),
        },
        "batch_12": {
            "audit_monitoring": get_audit_monitoring_config(),
            "task_automation": get_task_automation_config(),
        },
        "batch_13": {
            "background_processing": get_background_processing_config(),
        }
    }
