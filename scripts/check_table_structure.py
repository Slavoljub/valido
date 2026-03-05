#!/usr/bin/env python3
"""
Check Table Structure
Examine the actual structure of existing tables
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.database.unified_db_manager import UnifiedDatabaseManager

def check_table_structure():
    """Check the structure of key tables"""
    print("🔍 Checking Table Structure")
    print("=" * 50)

    db_manager = UnifiedDatabaseManager()

    # Tables to check
    tables_to_check = [
        'companies',
        'users',
        'business_partners',
        'products',
        'countries'
    ]

    with db_manager.get_connection() as conn:
        cursor = conn.cursor()

        for table_name in tables_to_check:
            print(f"\n📋 {table_name.upper()}")
            print("-" * 30)

            try:
                # Get table info
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = cursor.fetchall()

                if columns:
                    print(f"Found {len(columns)} columns:")
                    for col in columns:
                        col_name = col[1]
                        col_type = col[2]
                        is_pk = "PRIMARY KEY" if col[5] else ""
                        is_not_null = "NOT NULL" if col[3] else ""
                        default = f"DEFAULT {col[4]}" if col[4] else ""

                        print(f"  {col_name} {col_type} {is_pk} {is_not_null} {default}".strip())
                else:
                    print("Table not found or empty")

                # Check if table has data
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                print(f"Records: {count}")

            except Exception as e:
                print(f"Error checking table {table_name}: {e}")

    print("\n✅ Table structure check completed!")

if __name__ == "__main__":
    check_table_structure()
