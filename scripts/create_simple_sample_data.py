#!/usr/bin/env python3
"""
Create Simple Sample Data for Unified CRUD System
Simple data that matches existing table structures
"""

import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.database.unified_db_manager import UnifiedDatabaseManager

def create_simple_sample_data():
    """Create simple sample data that matches existing table structures"""
    print("📊 Creating Simple Sample Data")
    print("=" * 40)

    db_manager = UnifiedDatabaseManager()

    with db_manager.get_connection() as conn:
        cursor = conn.cursor()

        # Simple data that matches existing table structures
        sample_data = {
            'companies': [
                ("Test Company", "user_123", "Test Company Ltd", "123456789", "12345", "Test Street 1", "11000", "Belgrade", "+38111234567", "test@company.com", "www.testcompany.com", datetime.now(), datetime.now()),
                ("Demo Corp", "user_456", "Demo Corporation", "987654321", "67890", "Demo Avenue 2", "21000", "Novi Sad", "+38121555666", "demo@corp.com", "www.democorp.com", datetime.now(), datetime.now()),
            ],

            'business_partners': [
                ("Partner 1", "customer", "partner1@test.com", "+38111111111", "Partner Address 1", "Belgrade", "Serbia", "111111111", 1, datetime.now(), datetime.now()),
                ("Partner 2", "supplier", "partner2@test.com", "+38122222222", "Partner Address 2", "Novi Sad", "Serbia", "222222222", 1, datetime.now(), datetime.now()),
            ],

            'products': [
                ("Product 1", "PRD001", "First test product", "Electronics", 100.00, 80.00, 10, 1, datetime.now(), datetime.now()),
                ("Product 2", "PRD002", "Second test product", "Software", 50.00, 40.00, 20, 1, datetime.now(), datetime.now()),
            ],

            'countries': [
                ("Serbia", "RS", "Belgrade", "Europe", 7000000, 77474.0, datetime.now()),
                ("Croatia", "HR", "Zagreb", "Europe", 4000000, 56594.0, datetime.now()),
            ],

            'employees': [
                ("John", "Doe", "john@test.com", "+38133333333", "IT", "Developer", 2500.00, "2023-01-15", 1, datetime.now(), datetime.now()),
                ("Jane", "Smith", "jane@test.com", "+38144444444", "HR", "Manager", 3000.00, "2023-02-20", 1, datetime.now(), datetime.now()),
            ],

            'financial_transactions': [
                (datetime.now().date(), "Test transaction 1", 100.50, "income", "Services", "REF001", 1, datetime.now()),
                (datetime.now().date(), "Test transaction 2", 75.25, "expense", "Supplies", "REF002", 1, datetime.now()),
            ],

            'warehouses': [
                ("WH001", "Main Warehouse", "Warehouse Street 1", "Belgrade", "11000", "John Manager", "+38155555555", 1, 1, datetime.now(), datetime.now()),
                ("WH002", "Secondary Warehouse", "Warehouse Street 2", "Novi Sad", "21000", "Jane Supervisor", "+38166666666", 0, 1, datetime.now(), datetime.now()),
            ]
        }

        # Insert sample data
        for table_name, records in sample_data.items():
            print(f"📝 Inserting data into {table_name} ({len(records)} records)")

            for record in records:
                try:
                    # Get actual column count
                    cursor.execute(f"PRAGMA table_info({table_name})")
                    columns = cursor.fetchall()
                    column_count = len(columns)

                    # Adjust record to match column count
                    if len(record) > column_count:
                        record = record[:column_count]
                    elif len(record) < column_count:
                        # Pad with None for missing columns
                        record = list(record) + [None] * (column_count - len(record))

                    # Build INSERT statement
                    placeholders = ','.join(['?' for _ in record])
                    column_names = [col[1] for col in columns]
                    query = f"INSERT INTO {table_name} ({','.join(column_names)}) VALUES ({placeholders})"

                    cursor.execute(query, record)
                    print(f"  ✅ Inserted record into {table_name}")

                except Exception as e:
                    print(f"  ❌ Error inserting into {table_name}: {e}")
                    print(f"     Record length: {len(record)}, Column count: {column_count}")

        conn.commit()

        # Verify data insertion
        print("\n🔍 Verifying Sample Data")
        print("-" * 30)

        for table_name in sample_data.keys():
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                print(f"  📊 {table_name}: {count} records")
            except Exception as e:
                print(f"  ❌ Error checking {table_name}: {e}")

        # Also check some data
        print("\n📋 Sample Data Preview")
        print("-" * 25)

        for table_name in ['companies', 'users', 'products']:
            try:
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 1")
                row = cursor.fetchone()
                if row:
                    print(f"  📄 {table_name}: {dict(row) if hasattr(row, '__iter__') else row}")
            except Exception as e:
                print(f"  ❌ Error previewing {table_name}: {e}")

    print("\n✅ Simple sample data creation completed!")

if __name__ == "__main__":
    create_simple_sample_data()
