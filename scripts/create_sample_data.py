#!/usr/bin/env python3
"""
Create Sample Data for Unified CRUD System
Populate tables with test data for demonstration
"""

import sys
from pathlib import Path
from datetime import datetime, date

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.database.unified_db_manager import UnifiedDatabaseManager

def create_sample_data():
    """Create sample data for the unified CRUD system"""
    print("📊 Creating Sample Data")
    print("=" * 40)

    db_manager = UnifiedDatabaseManager()

    with db_manager.get_connection() as conn:
        cursor = conn.cursor()

        # Sample data for each table
        sample_data = {
            'companies': [
                ("ACME Corporation", "123456789", "12345", "Main Street 123", "Belgrade", "11000", "Serbia", "+38111234567", "contact@acme.com", "www.acme.com", date(2010, 1, 1), "ACME Corp", "RS123456789", "Technology", "large", None, "company_logo.png", "Leading technology company", None, "Europe/Belgrade", "RSD", 1, 1, 1, None, 1, datetime.now(), datetime.now()),
                ("Tech Solutions Ltd", "987654321", "67890", "Business Avenue 456", "Novi Sad", "21000", "Serbia", "+38121555666", "info@techsolutions.com", "www.techsolutions.com", date(2015, 6, 15), "Tech Solutions", "RS987654321", "IT Services", "medium", None, "tech_logo.png", "IT consulting and solutions", None, "Europe/Belgrade", "RSD", 1, 1, 1, None, 1, datetime.now(), datetime.now()),
                ("Global Industries", "555666777", "11223", "Industrial Zone 789", "Kragujevac", "34000", "Serbia", "+38134333000", "sales@globalindustries.com", "www.globalindustries.com", date(2005, 3, 20), "Global Industries Inc", "RS555666777", "Manufacturing", "enterprise", None, "global_logo.png", "Industrial manufacturing and distribution", None, "Europe/Belgrade", "RSD", 1, 1, 1, None, 1, datetime.now(), datetime.now()),
            ],

            'users': [
                ("admin", "admin@valido.ai", "hashed_password", "Administrator", "System", "+38111111111", None, date(1990, 1, 1), "M", "Serbia", "English, Serbian", "Europe/Belgrade", 1, None, 1, None, 1, None, 0, datetime.now(), datetime.now(), 100, None, None, datetime.now()),
                ("john.doe", "john.doe@acme.com", "hashed_password", "John", "Doe", "+38122222222", None, date(1985, 5, 15), "M", "Serbia", "English, Serbian", "Europe/Belgrade", 1, None, 1, None, 1, None, 0, datetime.now(), datetime.now(), 85, None, None, datetime.now()),
                ("jane.smith", "jane.smith@techsolutions.com", "hashed_password", "Jane", "Smith", "+38133333333", None, date(1992, 8, 22), "F", "Serbia", "English, German", "Europe/Belgrade", 1, None, 1, None, 1, None, 0, datetime.now(), datetime.now(), 90, None, None, datetime.now()),
            ],

            'business_partners': [
                ("Tech Corp", "vendor", "tech@corp.com", "+38144444444", "Innovation Street 100", "Belgrade", "Serbia", "123456789", 1, datetime.now(), datetime.now()),
                ("Supply Co", "supplier", "supply@co.com", "+38155555555", "Supply Road 200", "Novi Sad", "Serbia", "987654321", 1, datetime.now(), datetime.now()),
                ("Client Solutions", "client", "client@solutions.com", "+38166666666", "Client Avenue 300", "Belgrade", "Serbia", "555666777", 1, datetime.now(), datetime.now()),
            ],

            'products': [
                ("Laptop Pro 15", "LP15-001", "High-performance business laptop", "Electronics", 1200.00, 900.00, 50, 1, datetime.now(), datetime.now()),
                ("Office Suite Pro", "OSP-2024", "Complete office productivity suite", "Software", 299.99, 199.99, 100, 1, datetime.now(), datetime.now()),
                ("Wireless Mouse", "WM-001", "Ergonomic wireless mouse", "Accessories", 25.99, 15.99, 200, 1, datetime.now(), datetime.now()),
                ("Projector HD", "PJ-HD-001", "High-definition conference projector", "Electronics", 899.99, 650.00, 15, 1, datetime.now(), datetime.now()),
            ],

            'countries': [
                ("Serbia", "RS", "Belgrade", "Europe", 6840000, 77474.0, datetime.now()),
                ("Croatia", "HR", "Zagreb", "Europe", 4076000, 56594.0, datetime.now()),
                ("Slovenia", "SI", "Ljubljana", "Europe", 2107000, 20273.0, datetime.now()),
                ("Bosnia and Herzegovina", "BA", "Sarajevo", "Europe", 3281000, 51197.0, datetime.now()),
            ],

            'employees': [
                ("Marko", "Petrovic", "marko.petrovic@acme.com", "+38177777777", "IT", "Software Developer", 3500.00, "2020-03-15", 1, datetime.now(), datetime.now()),
                ("Ana", "Jovanovic", "ana.jovanovic@techsolutions.com", "+38188888888", "HR", "HR Manager", 2800.00, "2019-11-20", 1, datetime.now(), datetime.now()),
                ("Milan", "Nikolic", "milan.nikolic@globalindustries.com", "+38199999999", "Finance", "Accountant", 3200.00, "2021-01-10", 1, datetime.now(), datetime.now()),
            ],

            'financial_transactions': [
                (date(2024, 1, 15), "Office supplies purchase", 150.75, "expense", "Office Supplies", "Invoice #001", 1, datetime.now()),
                (date(2024, 1, 20), "Service revenue", 2500.00, "income", "Services", "Invoice #002", 1, datetime.now()),
                (date(2024, 1, 25), "Equipment purchase", 3500.00, "expense", "Equipment", "Invoice #003", 1, datetime.now()),
                (date(2024, 2, 1), "Consulting fee", 1800.00, "income", "Consulting", "Invoice #004", 1, datetime.now()),
            ],

            'business_config': [
                ("account_type", "asset", "Asset Account", "Balance Sheet", "General asset account", 1, 1, None, None, None, 2, None, 1, 0, None, datetime.now(), datetime.now()),
                ("account_type", "liability", "Liability Account", "Balance Sheet", "General liability account", 1, 1, None, None, None, 2, None, 1, 0, None, datetime.now(), datetime.now()),
                ("transaction_type", "sale", "Sales Transaction", "Income Statement", "Customer sales", 1, 1, None, None, None, 2, None, 1, 0, None, datetime.now(), datetime.now()),
                ("currency", "rsd", "Serbian Dinar", None, "Serbian national currency", 1, 1, None, None, "RSD", 2, None, 1, 0, None, datetime.now(), datetime.now()),
            ],

            'warehouses': [
                ("WH001", "Main Warehouse", "Industrial Street 1", "Belgrade", "11000", "John Manager", "+38111111111", 1, 1, datetime.now(), datetime.now()),
                ("WH002", "Secondary Warehouse", "Storage Road 2", "Novi Sad", "21000", "Jane Supervisor", "+38122222222", 0, 1, datetime.now(), datetime.now()),
            ],

            'ai_models_system': [
                ("GPT-4", "gpt4", "ai_model", "OpenAI", "large", 9.8, 1, datetime.now(), datetime.now()),
                ("Claude-3", "claude3", "ai_model", "Anthropic", "large", 9.5, 1, datetime.now(), datetime.now()),
                ("Llama-3", "llama3", "ai_model", "Meta", "large", 8.9, 1, datetime.now(), datetime.now()),
            ],

            'system_configuration': [
                ("app_name", "system", "string", "ValidoAI", 1, 1, datetime.now(), datetime.now()),
                ("max_file_size", "system", "integer", "16777216", 1, 1, datetime.now(), datetime.now()),
                ("default_language", "ui", "string", "en", 1, 1, datetime.now(), datetime.now()),
                ("maintenance_mode", "system", "boolean", "false", 1, 0, datetime.now(), datetime.now()),
            ]
        }

        # Insert sample data
        for table_name, records in sample_data.items():
            print(f"📝 Inserting data into {table_name} ({len(records)} records)")

            for record in records:
                try:
                    # Build INSERT statement
                    placeholders = ','.join(['?' for _ in record])
                    columns = get_table_columns(table_name)
                    if columns:
                        query = f"INSERT INTO {table_name} ({','.join(columns)}) VALUES ({placeholders})"
                        cursor.execute(query, record)
                        print(f"  ✅ Inserted record into {table_name}")
                    else:
                        print(f"  ⚠️  No columns found for {table_name}")

                except Exception as e:
                    print(f"  ❌ Error inserting into {table_name}: {e}")

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

    print("\n✅ Sample data creation completed!")

def get_table_columns(table_name):
    """Get column names for a table"""
    try:
        db_manager = UnifiedDatabaseManager()
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = [row[1] for row in cursor.fetchall()]
            return columns
    except Exception as e:
        print(f"Error getting columns for {table_name}: {e}")
        return None

if __name__ == "__main__":
    create_sample_data()
