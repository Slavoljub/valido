#!/usr/bin/env python3
"""
Check Database Tables - Verify all unified CRUD tables exist
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.database.unified_db_manager import UnifiedDatabaseManager

def check_database_tables():
    """Check all tables in the database"""
    print("📊 Checking Database Tables")
    print("=" * 40)

    db_manager = UnifiedDatabaseManager()

    with db_manager.get_connection() as conn:
        cursor = conn.cursor()

        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        all_tables = [row[0] for row in cursor.fetchall()]

        # Filter to our unified CRUD tables
        unified_tables = []
        crud_tables = [
            'companies', 'users', 'business_partners', 'products', 'countries',
            'employees', 'financial_transactions', 'business_config', 'business_entities',
            'user_access', 'fiscal_years', 'chart_of_accounts', 'warehouses',
            'ai_models_system', 'ai_insights_data', 'communication_system',
            'chat_sessions', 'chat_messages', 'chat_artifacts_memory', 'search_system',
            'api_integrations', 'system_configuration', 'audit_monitoring',
            'task_automation', 'background_processing'
        ]

        for table in all_tables:
            if table in crud_tables:
                unified_tables.append(table)

        print(f"📋 Total tables in database: {len(all_tables)}")
        print(f"🎯 Unified CRUD tables: {len(unified_tables)}")

        print("\n✅ Unified CRUD Tables:")
        for table in sorted(unified_tables):
            print(f"  - {table}")

        print(f"\n📊 Summary:")
        print(f"  - Expected: {len(crud_tables)} tables")
        print(f"  - Found: {len(unified_tables)} tables")
        print(f"  - Missing: {len(crud_tables) - len(unified_tables)} tables")

        if len(unified_tables) == len(crud_tables):
            print("\n🎉 SUCCESS: All unified CRUD tables are present!")
        else:
            missing = set(crud_tables) - set(unified_tables)
            print(f"\n⚠️  Missing tables: {sorted(missing)}")

        # Check record counts
        print("\n📈 Table Record Counts:")
        for table in sorted(unified_tables):
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"  {table}: {count} records")
            except Exception as e:
                print(f"  {table}: Error - {e}")

if __name__ == "__main__":
    check_database_tables()
