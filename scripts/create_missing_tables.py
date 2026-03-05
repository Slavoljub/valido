#!/usr/bin/env python3
"""
Create Missing Tables
Create only the tables that don't exist in the database
"""

import sys
import os
import re
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.database.unified_db_manager import UnifiedDatabaseManager

def convert_postgresql_to_sqlite_type(pg_type: str) -> str:
    """Convert PostgreSQL types to SQLite types"""
    type_mapping = {
        'UUID': 'TEXT',
        'VARCHAR': 'TEXT',
        'TEXT': 'TEXT',
        'INTEGER': 'INTEGER',
        'BIGINT': 'INTEGER',
        'DECIMAL': 'REAL',
        'BOOLEAN': 'INTEGER',
        'DATE': 'TEXT',
        'TIMESTAMP': 'TEXT',
        'JSONB': 'TEXT',
        'VECTOR': 'TEXT',
    }

    for pg, sqlite in type_mapping.items():
        if pg_type.upper().startswith(pg):
            return sqlite

    return 'TEXT'

def convert_column_definition(column_def: str) -> str:
    """Convert PostgreSQL column definition to SQLite"""
    # Remove PostgreSQL-specific syntax
    column_def = re.sub(r'DEFAULT gen_random_uuid\(\)', "DEFAULT (lower(hex(randomblob(4))) || '-' || lower(hex(randomblob(2))) || '-4' || substr(lower(hex(randomblob(2))),2) || '-' || substr('89ab',abs(random()) % 4 + 1, 1) || substr(lower(hex(randomblob(2))),2) || '-' || lower(hex(randomblob(6))))", column_def)
    column_def = re.sub(r'DEFAULT CURRENT_TIMESTAMP', 'DEFAULT CURRENT_TIMESTAMP', column_def)
    column_def = re.sub(r'ON DELETE CASCADE', '', column_def)
    column_def = re.sub(r'ON DELETE SET NULL', '', column_def)

    # Convert types
    def replace_type(match):
        return convert_postgresql_to_sqlite_type(match.group(1))

    column_def = re.sub(r'\b(\w+)(\(\d+(?:,\d+)?\))?', replace_type, column_def)

    return column_def

def create_missing_tables():
    """Create only the missing tables"""
    print("🗄️  Creating Missing Tables")
    print("=" * 40)

    # Tables we know exist
    existing_tables = [
        'companies',
        'users',
        'ai_artifact_versions',
        'ai_chat_artifacts',
        'ai_chat_messages',
        'ai_contexts',
        'ai_models',
        'ai_prompts',
        'ai_rate_limits',
        'ai_response_logs',
        'ai_safety_violations',
        'analysis',
        'analysis_logs',
        'api_integrations',
        'artifact_versions',
        'artifacts',
        'chat_artifacts',
        'chat_messages',
        'chat_sessions',
        'demo_companies',
        'error_logs',
        'errors',
        'example_questions',
        'files',
        'invoices',
        'notifications',
        'open_ai_log',
        'openai_logs',
        'question_categories',
        'settings',
        'support_tickets',
        'support_users',
        'ticket_activity',
        'ticket_attachments',
        'ticket_messages',
        'tickets',
        'transactions',
        'user',
        'webhook_events',
        'webhook_subscriptions'
    ]

    # Tables we need from unified CRUD
    required_tables = [
        'business_partners',
        'products',
        'countries',
        'business_config',
        'business_entities',
        'user_access',
        'fiscal_years',
        'chart_of_accounts',
        'warehouses',
        'ai_models_system',
        'ai_insights_data',
        'communication_system',
        'search_system',
        'system_configuration',
        'audit_monitoring',
        'task_automation',
        'background_processing',
        'employees',
        'financial_transactions'
    ]

    # Find missing tables
    missing_tables = [table for table in required_tables if table not in existing_tables]

    print(f"📋 Found {len(missing_tables)} missing tables:")
    for table in missing_tables:
        print(f"  - {table}")

    if not missing_tables:
        print("\n✅ All required tables already exist!")
        return

    # Parse PostgreSQL schema
    schema_file = Path(project_root) / "ai_prompt_database_structure" / "Postgres_ai_valido_optimized.sql"

    if not schema_file.exists():
        print(f"❌ Schema file not found: {schema_file}")
        return

    with open(schema_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Get database manager
    db_manager = UnifiedDatabaseManager()

    created_count = 0

    with db_manager.get_connection() as conn:
        cursor = conn.cursor()

        for table_name in missing_tables:
            print(f"\n🛠️  Creating table: {table_name}")

            # Find table definition in schema
            pattern = rf'CREATE TABLE {table_name}\s*\((.*?)\);'
            match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)

            if match:
                table_def = match.group(1).strip()

                # Convert to SQLite
                lines = [line.strip() for line in table_def.split('\n') if line.strip() and not line.strip().startswith('--')]

                sqlite_lines = []
                for line in lines:
                    line = line.rstrip(',')
                    converted = convert_column_definition(line)
                    sqlite_lines.append(converted)

                create_sql = f"CREATE TABLE IF NOT EXISTS {table_name} (\n    {',\n    '.join(sqlite_lines)}\n);"

                try:
                    cursor.execute(create_sql)
                    print(f"  ✅ Successfully created {table_name}")
                    created_count += 1

                except Exception as e:
                    print(f"  ❌ Error creating {table_name}: {e}")

            else:
                print(f"  ⚠️  Table definition not found for {table_name}")

        conn.commit()

    print(f"\n📊 Successfully created {created_count} out of {len(missing_tables)} missing tables")

    # Verify created tables
    print("\n🔍 Verifying Created Tables")
    print("-" * 30)

    with db_manager.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")

        all_tables = [row[0] for row in cursor.fetchall()]
        unified_tables = [table for table in all_tables if table in required_tables]

        print(f"📋 Total tables: {len(all_tables)}")
        print(f"📋 Unified CRUD tables: {len(unified_tables)}")

        for table in sorted(unified_tables):
            print(f"  ✅ {table}")

    print("\n✅ Missing tables creation completed!")

if __name__ == "__main__":
    create_missing_tables()
