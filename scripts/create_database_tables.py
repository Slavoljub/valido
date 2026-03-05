#!/usr/bin/env python3
"""
Create Database Tables from PostgreSQL Schema
Converts PostgreSQL schema to SQLite-compatible format
"""

import sys
import os
import re
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.database.unified_db_manager import UnifiedDatabaseManager

def parse_postgresql_schema(schema_file: str) -> dict:
    """Parse PostgreSQL schema file and extract table definitions"""
    with open(schema_file, 'r', encoding='utf-8') as f:
        content = f.read()

    tables = {}
    table_pattern = r'CREATE TABLE (\w+)\s*\((.*?)\);'
    matches = re.findall(table_pattern, content, re.DOTALL | re.IGNORECASE)

    for table_name, table_definition in matches:
        if not table_name.startswith('financial_transactions_20'):  # Skip partition tables
            tables[table_name] = parse_table_definition(table_definition)

    return tables

def parse_table_definition(table_def: str) -> dict:
    """Parse table definition and extract columns"""
    lines = [line.strip() for line in table_def.split('\n') if line.strip()]

    columns = []
    constraints = []
    foreign_keys = []

    for line in lines:
        if line.startswith('--') or line == '':
            continue

        # Remove trailing comma
        line = line.rstrip(',')

        if 'PRIMARY KEY' in line:
            # Primary key constraint
            constraints.append(line)
        elif 'REFERENCES' in line:
            # Foreign key
            foreign_keys.append(line)
        elif 'UNIQUE' in line:
            # Unique constraint
            constraints.append(line)
        else:
            # Column definition
            columns.append(line)

    return {
        'columns': columns,
        'constraints': constraints,
        'foreign_keys': foreign_keys
    }

def convert_postgresql_to_sqlite_type(pg_type: str) -> str:
    """Convert PostgreSQL types to SQLite types"""
    type_mapping = {
        'UUID': 'TEXT',
        'VARCHAR': 'TEXT',
        'TEXT': 'TEXT',
        'INTEGER': 'INTEGER',
        'BIGINT': 'INTEGER',
        'DECIMAL': 'REAL',
        'BOOLEAN': 'INTEGER',  # SQLite uses 0/1 for boolean
        'DATE': 'TEXT',
        'TIMESTAMP': 'TEXT',
        'JSONB': 'TEXT',
        'VECTOR': 'TEXT',  # Vector embeddings as text
    }

    for pg, sqlite in type_mapping.items():
        if pg_type.upper().startswith(pg):
            return sqlite

    return 'TEXT'  # Default fallback

def convert_column_definition(column_def: str) -> str:
    """Convert PostgreSQL column definition to SQLite"""
    # Remove PostgreSQL-specific syntax
    column_def = re.sub(r'DEFAULT gen_random_uuid\(\)', 'DEFAULT (lower(hex(randomblob(4))) || \'-\' || lower(hex(randomblob(2))) || \'-4\' || substr(lower(hex(randomblob(2))),2) || \'-\' || substr(\'89ab\',abs(random()) % 4 + 1, 1) || substr(lower(hex(randomblob(2))),2) || \'-\' || lower(hex(randomblob(6))))', column_def)
    column_def = re.sub(r'DEFAULT CURRENT_TIMESTAMP', 'DEFAULT CURRENT_TIMESTAMP', column_def)
    column_def = re.sub(r'ON DELETE CASCADE', '', column_def)
    column_def = re.sub(r'ON DELETE SET NULL', '', column_def)

    # Convert types
    def replace_type(match):
        return convert_postgresql_to_sqlite_type(match.group(1))

    column_def = re.sub(r'\b(\w+)(\(\d+(?:,\d+)?\))?', replace_type, column_def)

    return column_def

def generate_sqlite_schema(tables: dict) -> str:
    """Generate SQLite schema from parsed PostgreSQL tables"""
    schema_lines = []

    for table_name, table_info in tables.items():
        schema_lines.append(f"\n-- {table_name} table")
        schema_lines.append(f"CREATE TABLE IF NOT EXISTS {table_name} (")

        all_lines = table_info['columns'] + table_info['constraints'] + table_info['foreign_keys']
        converted_lines = []

        for line in all_lines:
            converted_line = convert_column_definition(line)
            converted_lines.append(f"    {converted_line}")

        schema_lines.append(',\n'.join(converted_lines))
        schema_lines.append(");")

    return '\n'.join(schema_lines)

def create_database_tables():
    """Main function to create database tables"""
    print("🗄️  Creating Database Tables from PostgreSQL Schema")
    print("=" * 60)

    # Path to PostgreSQL schema
    schema_file = Path(project_root) / "ai_prompt_database_structure" / "Postgres_ai_valido_optimized.sql"

    if not schema_file.exists():
        print(f"❌ Schema file not found: {schema_file}")
        return False

    try:
        # Parse PostgreSQL schema
        print(f"📄 Parsing PostgreSQL schema: {schema_file}")
        tables = parse_postgresql_schema(str(schema_file))
        print(f"📋 Found {len(tables)} tables in schema")

        # Generate SQLite schema
        print("🔄 Converting to SQLite schema...")
        sqlite_schema = generate_sqlite_schema(tables)

        # Get database manager
        db_manager = UnifiedDatabaseManager()

        # Execute schema
        print("⚡ Creating tables in database...")
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()

            # Split schema into individual statements
            statements = [stmt.strip() for stmt in sqlite_schema.split(';') if stmt.strip()]

            created_tables = 0
            for statement in statements:
                if statement.startswith('CREATE TABLE'):
                    try:
                        cursor.execute(statement)
                        table_name = statement.split()[5]  # Extract table name
                        print(f"  ✅ Created table: {table_name}")
                        created_tables += 1
                    except Exception as e:
                        print(f"  ❌ Error creating table: {e}")

            conn.commit()
            print(f"📊 Successfully created {created_tables} tables")

        print("\n✅ Database tables creation completed!")
        return True

    except Exception as e:
        print(f"❌ Error creating database tables: {e}")
        return False

def verify_tables():
    """Verify that tables were created successfully"""
    print("\n🔍 Verifying Created Tables")
    print("-" * 30)

    try:
        db_manager = UnifiedDatabaseManager()

        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")

            tables = cursor.fetchall()
            print(f"📋 Found {len(tables)} tables in database:")

            for table in tables:
                table_name = table[0]
                if not table_name.startswith('sqlite_'):
                    print(f"  ✅ {table_name}")

        return True

    except Exception as e:
        print(f"❌ Error verifying tables: {e}")
        return False

if __name__ == "__main__":
    # Create tables
    success = create_database_tables()

    if success:
        # Verify tables
        verify_tables()

        print("\n🎉 Database setup completed successfully!")
        print("\n📝 Next steps:")
        print("  1. Test the unified CRUD routes")
        print("  2. Add sample data if needed")
        print("  3. Run the application")
    else:
        print("\n❌ Database setup failed!")
        sys.exit(1)
