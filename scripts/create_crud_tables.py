#!/usr/bin/env python3
"""
Create Essential CRUD Tables
Create the minimal tables needed for unified CRUD system
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.database.unified_db_manager import UnifiedDatabaseManager

def create_essential_tables():
    """Create essential tables for unified CRUD system"""
    print("🗄️  Creating Essential CRUD Tables")
    print("=" * 50)

    # Table creation SQL
    table_schemas = {
        'business_partners': '''
            CREATE TABLE IF NOT EXISTS business_partners (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                partner_name TEXT NOT NULL,
                partner_type TEXT,
                email TEXT,
                phone TEXT,
                address TEXT,
                city TEXT,
                country TEXT,
                tax_id TEXT,
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''',

        'products': '''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_name TEXT NOT NULL,
                product_code TEXT,
                description TEXT,
                category TEXT,
                price REAL,
                cost REAL,
                stock_quantity INTEGER DEFAULT 0,
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''',

        'countries': '''
            CREATE TABLE IF NOT EXISTS countries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                iso_code TEXT,
                capital TEXT,
                region TEXT,
                population INTEGER,
                area_km2 REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''',

        'employees': '''
            CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                email TEXT,
                phone TEXT,
                department TEXT,
                position TEXT,
                salary REAL,
                hire_date DATE,
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''',

        'financial_transactions': '''
            CREATE TABLE IF NOT EXISTS financial_transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                transaction_date DATE NOT NULL,
                description TEXT,
                amount REAL NOT NULL,
                transaction_type TEXT,
                category TEXT,
                reference TEXT,
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        '''
    }

    # Get database manager
    db_manager = UnifiedDatabaseManager()

    created_count = 0

    with db_manager.get_connection() as conn:
        cursor = conn.cursor()

        for table_name, schema in table_schemas.items():
            print(f"🛠️  Creating table: {table_name}")

            try:
                cursor.execute(schema)
                print(f"  ✅ Successfully created {table_name}")
                created_count += 1

            except Exception as e:
                print(f"  ❌ Error creating {table_name}: {e}")

        conn.commit()

    print(f"\n📊 Successfully created {created_count} essential tables")

    # Verify created tables
    print("\n🔍 Verifying Created Tables")
    print("-" * 30)

    with db_manager.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name IN ('business_partners', 'products', 'countries', 'employees', 'financial_transactions') ORDER BY name")

        created_tables = [row[0] for row in cursor.fetchall()]

        print(f"📋 Essential CRUD tables: {len(created_tables)}")
        for table in created_tables:
            print(f"  ✅ {table}")

    print("\n✅ Essential CRUD tables creation completed!")

if __name__ == "__main__":
    create_essential_tables()
