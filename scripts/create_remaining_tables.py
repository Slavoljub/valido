#!/usr/bin/env python3
"""
Create Remaining Tables for Unified CRUD System
Create the remaining 23 tables from the PostgreSQL schema
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.database.unified_db_manager import UnifiedDatabaseManager

def create_remaining_tables():
    """Create the remaining 23 tables for the unified CRUD system"""
    print("🗄️  Creating Remaining Tables")
    print("=" * 50)

    # Tables we still need to create
    remaining_tables = {
        'business_config': '''
            CREATE TABLE IF NOT EXISTS business_config (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                config_type TEXT NOT NULL,
                type_code TEXT NOT NULL,
                type_name TEXT NOT NULL,
                category TEXT,
                description TEXT,
                is_system_type INTEGER DEFAULT 0,
                is_active INTEGER DEFAULT 1,
                tax_rate REAL,
                tax_category TEXT,
                currency_symbol TEXT,
                decimal_places INTEGER DEFAULT 2,
                exchange_rate REAL,
                affects_cash INTEGER DEFAULT 1,
                requires_approval INTEGER DEFAULT 0,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(config_type, type_code)
            )
        ''',

        'business_entities': '''
            CREATE TABLE IF NOT EXISTS business_entities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entity_type TEXT NOT NULL,
                entity_code TEXT NOT NULL,
                entity_name TEXT NOT NULL,
                description TEXT,
                is_system_entity INTEGER DEFAULT 0,
                is_active INTEGER DEFAULT 1,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(entity_type, entity_code)
            )
        ''',

        'user_access': '''
            CREATE TABLE IF NOT EXISTS user_access (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                company_id INTEGER,
                access_type TEXT NOT NULL,
                status TEXT DEFAULT 'active',
                access_level TEXT,
                role_name TEXT,
                permission_name TEXT,
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''',

        'fiscal_years': '''
            CREATE TABLE IF NOT EXISTS fiscal_years (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                year INTEGER NOT NULL,
                start_date DATE NOT NULL,
                end_date DATE NOT NULL,
                is_current INTEGER DEFAULT 0,
                is_closed INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''',

        'chart_of_accounts': '''
            CREATE TABLE IF NOT EXISTS chart_of_accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                account_number TEXT NOT NULL UNIQUE,
                account_name TEXT NOT NULL,
                account_level INTEGER,
                is_active INTEGER DEFAULT 1,
                opening_balance REAL DEFAULT 0.0,
                current_balance REAL DEFAULT 0.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''',

        'warehouses': '''
            CREATE TABLE IF NOT EXISTS warehouses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                warehouse_code TEXT NOT NULL UNIQUE,
                warehouse_name TEXT NOT NULL,
                address_street TEXT,
                address_city TEXT,
                address_postal_code TEXT,
                contact_person TEXT,
                phone TEXT,
                is_main_warehouse INTEGER DEFAULT 0,
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''',

        'ai_models_system': '''
            CREATE TABLE IF NOT EXISTS ai_models_system (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                model_name TEXT NOT NULL,
                model_code TEXT NOT NULL,
                model_type TEXT,
                model_family TEXT,
                model_size TEXT,
                performance_score REAL,
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''',

        'ai_insights_data': '''
            CREATE TABLE IF NOT EXISTS ai_insights_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                data_type TEXT NOT NULL,
                title TEXT NOT NULL,
                category TEXT,
                source TEXT,
                validation_status TEXT DEFAULT 'pending',
                quality_score REAL,
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''',

        'communication_system': '''
            CREATE TABLE IF NOT EXISTS communication_system (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                communication_type TEXT NOT NULL,
                subject TEXT,
                category TEXT,
                priority TEXT DEFAULT 'normal',
                status TEXT DEFAULT 'draft',
                sent_at TIMESTAMP,
                total_recipients INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''',

        'chat_sessions': '''
            CREATE TABLE IF NOT EXISTS chat_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                session_title TEXT,
                model_used TEXT,
                is_active INTEGER DEFAULT 1,
                last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                message_count INTEGER DEFAULT 0,
                total_tokens INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''',

        'chat_messages': '''
            CREATE TABLE IF NOT EXISTS chat_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER,
                message_type TEXT NOT NULL,
                message_content TEXT NOT NULL,
                token_count INTEGER DEFAULT 0,
                message_order INTEGER DEFAULT 0,
                is_deleted INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''',

        'chat_artifacts_memory': '''
            CREATE TABLE IF NOT EXISTS chat_artifacts_memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                artifact_type TEXT NOT NULL,
                artifact_name TEXT NOT NULL,
                content_type TEXT,
                mime_type TEXT,
                artifact_size INTEGER,
                importance_score REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''',

        'search_system': '''
            CREATE TABLE IF NOT EXISTS search_system (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                search_type TEXT NOT NULL,
                entity_type TEXT,
                query_text TEXT,
                search_category TEXT,
                results_count INTEGER DEFAULT 0,
                search_time_ms INTEGER DEFAULT 0,
                is_successful INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''',

        'system_configuration': '''
            CREATE TABLE IF NOT EXISTS system_configuration (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                config_key TEXT NOT NULL UNIQUE,
                config_category TEXT,
                config_type TEXT,
                config_value TEXT,
                is_system_config INTEGER DEFAULT 0,
                is_user_editable INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''',

        'audit_monitoring': '''
            CREATE TABLE IF NOT EXISTS audit_monitoring (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                audit_type TEXT NOT NULL,
                action TEXT,
                resource_type TEXT,
                metric_name TEXT,
                metric_value REAL,
                recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''',

        'task_automation': '''
            CREATE TABLE IF NOT EXISTS task_automation (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_name TEXT NOT NULL,
                task_type TEXT,
                schedule_cron TEXT,
                is_active INTEGER DEFAULT 1,
                last_run TIMESTAMP,
                next_run TIMESTAMP,
                run_count INTEGER DEFAULT 0,
                success_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''',

        'background_processing': '''
            CREATE TABLE IF NOT EXISTS background_processing (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                processing_type TEXT NOT NULL,
                job_name TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                priority INTEGER DEFAULT 5,
                progress REAL DEFAULT 0.0,
                scheduled_at TIMESTAMP,
                started_at TIMESTAMP,
                completed_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        '''
    }

    # Get database manager
    db_manager = UnifiedDatabaseManager()

    created_count = 0
    existing_count = 0

    with db_manager.get_connection() as conn:
        cursor = conn.cursor()

        for table_name, schema in remaining_tables.items():
            print(f"🛠️  Creating table: {table_name}")

            try:
                cursor.execute(schema)
                print(f"  ✅ Successfully created {table_name}")
                created_count += 1

            except Exception as e:
                if "already exists" in str(e).lower():
                    print(f"  ⚠️  {table_name} already exists")
                    existing_count += 1
                else:
                    print(f"  ❌ Error creating {table_name}: {e}")

        conn.commit()

    print(f"\n📊 Results:")
    print(f"  ✅ Created: {created_count} tables")
    print(f"  ⚠️  Already existed: {existing_count} tables")
    print(f"  📋 Total processed: {len(remaining_tables)} tables")

    # Verify all tables
    print("\n🔍 Verifying All Unified CRUD Tables")
    print("-" * 40)

    with db_manager.get_connection() as conn:
        cursor = conn.cursor()

        # Check which tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")

        all_tables = [row[0] for row in cursor.fetchall()]

        # Filter to our unified CRUD tables
        unified_tables = []
        for table in all_tables:
            if table in remaining_tables or table in ['companies', 'users', 'business_partners', 'products', 'countries', 'employees', 'financial_transactions']:
                unified_tables.append(table)

        print(f"📋 Total unified CRUD tables: {len(unified_tables)}")
        print("Tables:")
        for table in sorted(unified_tables):
            print(f"  ✅ {table}")

        # Check if we have the expected number
        expected_tables = len(remaining_tables) + 7  # 23 remaining + 7 we already had
        if len(unified_tables) >= expected_tables:
            print(f"\n🎉 SUCCESS: All {expected_tables} unified CRUD tables are ready!")
        else:
            print(f"\n⚠️  Missing {expected_tables - len(unified_tables)} tables")

    print("\n✅ Remaining tables creation completed!")

if __name__ == "__main__":
    create_remaining_tables()
