#!/usr/bin/env python3
"""
Add Sample Data to Unified CRUD System
Add realistic sample data to all tables for testing
"""

import sys
import os
from pathlib import Path
from datetime import datetime, date
import random

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.database.unified_db_manager import UnifiedDatabaseManager

def generate_sample_data():
    """Generate comprehensive sample data for testing"""
    print("📊 Adding Sample Data to Unified CRUD System")
    print("=" * 50)

    db_manager = UnifiedDatabaseManager()

    with db_manager.get_connection() as conn:
        cursor = conn.cursor()

        # Sample data for different tables
        sample_data = {
            'companies': [
                ("Tech Solutions Inc", "tech123", "Technology Solutions", "123456789", "12345", "Innovation Street 1", "11000", "Belgrade", "+38111234567", "info@techsolutions.com", "www.techsolutions.com", datetime.now(), datetime.now()),
                ("Global Manufacturing", "global456", "Global Manufacturing Ltd", "987654321", "67890", "Industrial Zone 2", "21000", "Novi Sad", "+38121555666", "sales@globalmfg.com", "www.globalmfg.com", datetime.now(), datetime.now()),
                ("Consulting Partners", "consult789", "Consulting Partners LLC", "555666777", "11223", "Business Center 3", "34000", "Kragujevac", "+38134333000", "contact@consulting.com", "www.consulting.com", datetime.now(), datetime.now()),
            ],

            'business_partners': [
                ("Supplier Corp", "supplier", "supplier@corp.com", "+38111111111", "Supply Street 1", "Belgrade", "Serbia", "111111111", 1, datetime.now(), datetime.now()),
                ("Client Solutions", "client", "client@solutions.com", "+38122222222", "Client Avenue 2", "Novi Sad", "Serbia", "222222222", 1, datetime.now(), datetime.now()),
                ("Partner Services", "partner", "partner@services.com", "+38133333333", "Partner Road 3", "Belgrade", "Serbia", "333333333", 1, datetime.now(), datetime.now()),
            ],

            'products': [
                ("Laptop Pro 15", "LP15-001", "High-performance business laptop", "Electronics", 1200.00, 900.00, 15, 1, datetime.now(), datetime.now()),
                ("Office Suite Pro", "OSP-2024", "Complete productivity suite", "Software", 299.99, 199.99, 50, 1, datetime.now(), datetime.now()),
                ("Wireless Mouse", "WM-001", "Ergonomic wireless mouse", "Accessories", 25.99, 15.99, 100, 1, datetime.now(), datetime.now()),
                ("Projector HD", "PJ-HD-001", "High-definition projector", "Electronics", 899.99, 650.00, 8, 1, datetime.now(), datetime.now()),
            ],

            'countries': [
                ("Serbia", "RS", "Belgrade", "Europe", 7000000, 77474.0, datetime.now()),
                ("Croatia", "HR", "Zagreb", "Europe", 4000000, 56594.0, datetime.now()),
                ("Slovenia", "SI", "Ljubljana", "Europe", 2100000, 20273.0, datetime.now()),
                ("Bosnia and Herzegovina", "BA", "Sarajevo", "Europe", 3300000, 51197.0, datetime.now()),
            ],

            'employees': [
                ("Marko", "Petrovic", "marko@techsolutions.com", "+38144444444", "IT", "Software Developer", 3500.00, "2020-03-15", 1, datetime.now(), datetime.now()),
                ("Ana", "Jovanovic", "ana@globalmfg.com", "+38155555555", "HR", "HR Manager", 2800.00, "2019-11-20", 1, datetime.now(), datetime.now()),
                ("Milan", "Nikolic", "milan@consulting.com", "+38166666666", "Finance", "Accountant", 3200.00, "2021-01-10", 1, datetime.now(), datetime.now()),
            ],

            'financial_transactions': [
                (date(2024, 1, 15), "Office supplies purchase", 150.75, "expense", "Office Supplies", "REF001", 1, datetime.now()),
                (date(2024, 1, 20), "Service revenue", 2500.00, "income", "Services", "REF002", 1, datetime.now()),
                (date(2024, 1, 25), "Equipment purchase", 3500.00, "expense", "Equipment", "REF003", 1, datetime.now()),
                (date(2024, 2, 1), "Consulting fee", 1800.00, "income", "Consulting", "REF004", 1, datetime.now()),
            ],

            'warehouses': [
                ("WH001", "Main Warehouse", "Industrial Street 1", "Belgrade", "11000", "John Manager", "+38177777777", 1, 1, datetime.now(), datetime.now()),
                ("WH002", "Secondary Warehouse", "Storage Road 2", "Novi Sad", "21000", "Jane Supervisor", "+38188888888", 0, 1, datetime.now(), datetime.now()),
            ],

            'business_config': [
                ("account_type", "asset", "Asset Account", "Balance Sheet", "General asset account", 1, 1, None, None, None, 2, None, 1, 0, None, datetime.now(), datetime.now()),
                ("account_type", "liability", "Liability Account", "Balance Sheet", "General liability account", 1, 1, None, None, None, 2, None, 1, 0, None, datetime.now(), datetime.now()),
                ("transaction_type", "sale", "Sales Transaction", "Income Statement", "Customer sales", 1, 1, None, None, None, 2, None, 1, 0, None, datetime.now(), datetime.now()),
                ("currency", "rsd", "Serbian Dinar", None, "Serbian national currency", 1, 1, None, None, "RSD", 2, None, 1, 0, None, datetime.now(), datetime.now()),
            ]
        }

        # Insert sample data
        inserted_count = 0
        for table_name, records in sample_data.items():
            print(f"📝 Adding data to {table_name} ({len(records)} records)...")

            for record in records:
                try:
                    # Get column count and pad record if needed
                    cursor.execute(f"PRAGMA table_info({table_name})")
                    columns = cursor.fetchall()
                    column_count = len(columns)

                    if len(record) < column_count:
                        record = list(record) + [None] * (column_count - len(record))
                    elif len(record) > column_count:
                        record = record[:column_count]

                    placeholders = ','.join(['?' for _ in record])
                    column_names = [col[1] for col in columns]
                    query = f"INSERT OR IGNORE INTO {table_name} ({','.join(column_names)}) VALUES ({placeholders})"

                    cursor.execute(query, record)
                    inserted_count += 1
                    print(f"  ✅ Added record to {table_name}")

                except Exception as e:
                    print(f"  ❌ Error adding to {table_name}: {e}")

        conn.commit()

        # Verify data insertion
        print(f"\n📊 Verification - Added {inserted_count} records")
        print("-" * 40)

        for table_name in sample_data.keys():
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                print(f"  📄 {table_name}: {count} records")
            except Exception as e:
                print(f"  ❌ Error checking {table_name}: {e}")

        print("\n✅ Sample data addition completed!")

if __name__ == "__main__":
    generate_sample_data()
