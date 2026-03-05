#!/usr/bin/env python3
"""
ValidoAI PostgreSQL CLI Testing Tool
Comprehensive CLI for testing PostgreSQL database functionality
"""

import sys
import os
import argparse
import subprocess
import json
from datetime import datetime
from pathlib import Path
import psycopg2
from psycopg2 import sql

class PostgresTester:
    """PostgreSQL Testing and Management CLI"""

    def __init__(self, host='localhost', port=5432, database='validoai_test', user='postgres', password=None):
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password
        self.connection = None

    def connect(self):
        """Establish database connection"""
        try:
            self.connection = psycopg2.connect(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password
            )
            self.connection.autocommit = True
            print(f"✅ Connected to PostgreSQL database: {self.database}")
            return True
        except Exception as e:
            print(f"❌ Failed to connect to database: {e}")
            return False

    def disconnect(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            print("✅ Disconnected from database")

    def execute_sql_file(self, file_path):
        """Execute SQL file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                sql_content = f.read()

            with self.connection.cursor() as cursor:
                cursor.execute(sql_content)
                print(f"✅ Successfully executed SQL file: {file_path}")

        except Exception as e:
            print(f"❌ Error executing SQL file {file_path}: {e}")

    def run_query(self, query, params=None, fetch='all'):
        """Execute a query and return results"""
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, params or [])

                if fetch == 'one':
                    result = cursor.fetchone()
                elif fetch == 'all':
                    result = cursor.fetchall()
                else:
                    result = None

                return result

        except Exception as e:
            print(f"❌ Query execution error: {e}")
            return None

    def test_schema_creation(self):
        """Test database schema creation"""
        print("🧪 Testing Database Schema Creation...")

        try:
            # Check if main tables exist
            tables = [
                'countries', 'companies', 'users', 'user_company_access',
                'user_company_sessions', 'company_switch_audit', 'company_invitations',
                'user_company_preferences', 'company_departments', 'user_department_assignments',
                'user_roles', 'user_permissions', 'fiscal_years', 'chart_of_accounts',
                'general_ledger', 'invoices', 'invoice_items', 'bank_accounts',
                'bank_statements', 'crm_contacts', 'crm_leads', 'crm_opportunities',
                'employees', 'payroll', 'inventory', 'warehouses', 'ai_insights',
                'ai_training_data', 'llm_embeddings', 'notifications', 'tickets',
                'audit_logs', 'settings'
            ]

            for table in tables:
                result = self.run_query(
                    "SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = %s)",
                    [table],
                    fetch='one'
                )

                if result and result[0]:
                    print(f"  ✅ Table '{table}' exists")
                else:
                    print(f"  ❌ Table '{table}' missing")

            # Check extensions
            extensions = ['vector', 'pg_stat_statements', 'pg_buffercache', 'pg_similarity', 'pg_trgm']
            for ext in extensions:
                result = self.run_query(
                    "SELECT EXISTS (SELECT 1 FROM pg_extension WHERE extname = %s)",
                    [ext],
                    fetch='one'
                )

                if result and result[0]:
                    print(f"  ✅ Extension '{ext}' installed")
                else:
                    print(f"  ⚠️  Extension '{ext}' not found")

        except Exception as e:
            print(f"❌ Schema test error: {e}")

    def test_multi_company_setup(self):
        """Test multi-company user access setup"""
        print("\n🏢 Testing Multi-Company Setup...")

        try:
            # Create test countries
            countries_data = [
                ('RS', 'SRB', '688', 'Serbia', 'Belgrade', '🇷🇸'),
                ('US', 'USA', '840', 'United States', 'Washington D.C.', '🇺🇸'),
                ('DE', 'DEU', '276', 'Germany', 'Berlin', '🇩🇪')
            ]

            for iso_code, iso_code_3, iso_numeric, name, capital, flag in countries_data:
                self.run_query("""
                    INSERT INTO countries (iso_code, iso_code_3, iso_numeric, name, capital, flag_emoji)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (iso_code) DO NOTHING
                """, [iso_code, iso_code_3, iso_numeric, name, capital, flag])

            print("  ✅ Test countries created")

            # Create test companies
            companies_data = [
                ('ValidoAI Tech', '123456789', 'REG001', 'RS'),
                ('TechCorp Solutions', '987654321', 'REG002', 'RS'),
                ('Global Finance Ltd', '456789123', 'REG003', 'US')
            ]

            company_ids = []
            for name, tax_id, reg_num, country_code in companies_data:
                result = self.run_query("""
                    INSERT INTO companies (company_name, tax_id, registration_number, countries_id)
                    VALUES (%s, %s, %s, (SELECT countries_id FROM countries WHERE iso_code = %s))
                    ON CONFLICT (tax_id) DO UPDATE SET company_name = EXCLUDED.company_name
                    RETURNING companies_id
                """, [name, tax_id, reg_num, country_code], fetch='one')

                if result:
                    company_ids.append(result[0])
                    print(f"  ✅ Company '{name}' created/updated")

            # Create test users
            users_data = [
                ('admin@validoai.com', 'System Administrator', 'admin'),
                ('manager@validoai.com', 'John Manager', 'manager'),
                ('accountant@validoai.com', 'Jane Accountant', 'accountant')
            ]

            user_ids = []
            for email, name, username in users_data:
                result = self.run_query("""
                    INSERT INTO users (username, email, password_hash, first_name, last_name)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (email) DO UPDATE SET username = EXCLUDED.username
                    RETURNING users_id
                """, [username, email, 'hashed_password', name.split()[0], name.split()[1]], fetch='one')

                if result:
                    user_ids.append(result[0])
                    print(f"  ✅ User '{name}' created/updated")

            # Create user-company access relationships
            if len(user_ids) >= 2 and len(company_ids) >= 2:
                # Admin has access to all companies
                for company_id in company_ids:
                    self.run_query("""
                        INSERT INTO user_company_access (user_id, company_id, access_level, can_manage_company)
                        VALUES (%s, %s, 'admin', true)
                        ON CONFLICT (user_id, company_id) DO NOTHING
                    """, [user_ids[0], company_id])

                # Manager has access to first two companies
                for i in range(min(2, len(company_ids))):
                    self.run_query("""
                        INSERT INTO user_company_access (user_id, company_id, access_level, can_manage_company)
                        VALUES (%s, %s, 'manager', false)
                        ON CONFLICT (user_id, company_id) DO NOTHING
                    """, [user_ids[1], company_ids[i]])

                # Accountant has access to first company only
                self.run_query("""
                    INSERT INTO user_company_access (user_id, company_id, access_level, can_access_financial_data)
                    VALUES (%s, %s, 'employee', true)
                    ON CONFLICT (user_id, company_id) DO NOTHING
                """, [user_ids[2], company_ids[0]])

                print("  ✅ User-company access relationships created")

            return company_ids, user_ids

        except Exception as e:
            print(f"❌ Multi-company setup error: {e}")
            return [], []

    def test_company_switching(self, user_ids, company_ids):
        """Test company switching functionality"""
        print("\n🔄 Testing Company Switching...")

        try:
            if not user_ids or not company_ids:
                print("  ⚠️  No users or companies available for switching test")
                return

            # Test company switching audit
            self.run_query("""
                INSERT INTO company_switch_audit (user_id, from_company_id, to_company_id, switch_reason, switch_method)
                VALUES (%s, %s, %s, 'manual', 'cli')
            """, [user_ids[0], company_ids[0], company_ids[1]])

            print("  ✅ Company switching audit recorded")

            # Test user company session
            self.run_query("""
                INSERT INTO user_company_sessions (user_id, company_id, session_id, ip_address)
                VALUES (%s, %s, 'test_session_123', '127.0.0.1')
                ON CONFLICT DO NOTHING
            """, [user_ids[0], company_ids[0]])

            print("  ✅ User company session created")

            # Test getting user's accessible companies
            accessible_companies = self.run_query("""
                SELECT c.company_name, uca.access_level, uca.can_manage_company
                FROM user_company_access uca
                JOIN companies c ON uca.company_id = c.companies_id
                WHERE uca.user_id = %s AND uca.status = 'active'
                ORDER BY c.company_name
            """, [user_ids[0]])

            if accessible_companies:
                print(f"  ✅ User has access to {len(accessible_companies)} companies:")
                for company in accessible_companies:
                    print(f"    - {company[0]} ({company[1]})")

        except Exception as e:
            print(f"❌ Company switching test error: {e}")

    def test_department_management(self, company_ids):
        """Test company department and user assignment management"""
        print("\n🏬 Testing Department Management...")

        try:
            if not company_ids:
                print("  ⚠️  No companies available for department test")
                return

            # Create departments
            departments = [
                ('Information Technology', 'IT', company_ids[0]),
                ('Human Resources', 'HR', company_ids[0]),
                ('Finance & Accounting', 'FIN', company_ids[0]),
                ('Sales & Marketing', 'SALES', company_ids[0])
            ]

            dept_ids = []
            for name, code, company_id in departments:
                result = self.run_query("""
                    INSERT INTO company_departments (company_id, department_name, department_code)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (company_id, department_name) DO NOTHING
                    RETURNING company_department_id
                """, [company_id, name, code], fetch='one')

                if result:
                    dept_ids.append(result[0])
                    print(f"  ✅ Department '{name}' created")

            # Create nested departments (IT sub-departments)
            if dept_ids:
                it_sub_depts = [
                    ('Software Development', 'IT-SD', dept_ids[0]),
                    ('DevOps & Infrastructure', 'IT-DEVOPS', dept_ids[0]),
                    ('Quality Assurance', 'IT-QA', dept_ids[0])
                ]

                for name, code, parent_id in it_sub_depts:
                    self.run_query("""
                        INSERT INTO company_departments (company_id, department_name, department_code, parent_department_id)
                        VALUES (%s, %s, %s, %s)
                        ON CONFLICT (company_id, department_name) DO NOTHING
                    """, [company_ids[0], name, code, parent_id])

                print("  ✅ Sub-departments created")

        except Exception as e:
            print(f"❌ Department management test error: {e}")

    def test_performance_metrics(self):
        """Test database performance and metrics"""
        print("\n📊 Testing Performance Metrics...")

        try:
            # Get table sizes
            table_sizes = self.run_query("""
                SELECT
                    schemaname,
                    tablename,
                    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size,
                    pg_total_relation_size(schemaname||'.'||tablename) as size_bytes
                FROM pg_tables
                WHERE schemaname = 'public'
                ORDER BY size_bytes DESC
                LIMIT 10
            """)

            if table_sizes:
                print("  📏 Top 10 largest tables:")
                for schema, table, size, size_bytes in table_sizes:
                    print("12")

            # Get index information
            index_count = self.run_query("""
                SELECT COUNT(*) as count
                FROM pg_indexes
                WHERE schemaname = 'public'
            """, fetch='one')

            if index_count:
                print(f"  📊 Total indexes: {index_count[0]}")

            # Get extension information
            extensions = self.run_query("""
                SELECT name, default_version, installed_version
                FROM pg_available_extensions
                WHERE installed_version IS NOT NULL
                ORDER BY name
            """)

            if extensions:
                print(f"  🔧 Installed extensions: {len(extensions)}")
                for name, default_ver, installed_ver in extensions:
                    print("12")

        except Exception as e:
            print(f"❌ Performance metrics error: {e}")

    def generate_test_report(self):
        """Generate comprehensive test report"""
        print("\n📋 Generating Test Report...")

        try:
            report = {
                "timestamp": datetime.now().isoformat(),
                "database": self.database,
                "host": self.host,
                "port": self.port,
                "tests": {}
            }

            # Count records in key tables
            tables_to_count = [
                'countries', 'companies', 'users', 'user_company_access',
                'user_company_sessions', 'company_departments', 'employees',
                'invoices', 'tickets', 'ai_insights'
            ]

            report["record_counts"] = {}
            for table in tables_to_count:
                try:
                    result = self.run_query(f"SELECT COUNT(*) FROM {table}", fetch='one')
                    report["record_counts"][table] = result[0] if result else 0
                except:
                    report["record_counts"][table] = 0

            # Get database size
            db_size = self.run_query("""
                SELECT pg_size_pretty(pg_database_size(current_database())) as size
            """, fetch='one')
            report["database_size"] = db_size[0] if db_size else "Unknown"

            # Get PostgreSQL version
            version = self.run_query("SELECT version()", fetch='one')
            report["postgresql_version"] = version[0] if version else "Unknown"

            # Save report
            with open('postgres_test_report.json', 'w') as f:
                json.dump(report, f, indent=2)

            print("  ✅ Test report saved to: postgres_test_report.json")

            # Display summary
            print("\n📊 Test Summary:")
            print(f"  Database: {report['database']}")
            print(f"  Size: {report['database_size']}")
            print(f"  PostgreSQL: {report['postgresql_version'][:50]}...")

            print("\n📈 Record Counts:")
            for table, count in report["record_counts"].items():
                print(f"    {table}: {count:,}")

        except Exception as e:
            print(f"❌ Report generation error: {e}")

def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(description='ValidoAI PostgreSQL Testing CLI')
    parser.add_argument('--host', default='localhost', help='Database host')
    parser.add_argument('--port', type=int, default=5432, help='Database port')
    parser.add_argument('--database', default='validoai_test', help='Database name')
    parser.add_argument('--user', default='postgres', help='Database user')
    parser.add_argument('--password', help='Database password')
    parser.add_argument('--sql-file', help='Execute SQL file')
    parser.add_argument('--schema-only', action='store_true', help='Test schema creation only')
    parser.add_argument('--multi-company', action='store_true', help='Test multi-company functionality')
    parser.add_argument('--performance', action='store_true', help='Run performance tests')
    parser.add_argument('--all', action='store_true', help='Run all tests')

    args = parser.parse_args()

    # Initialize tester
    tester = PostgresTester(
        host=args.host,
        port=args.port,
        database=args.database,
        user=args.user,
        password=args.password
    )

    print("🚀 ValidoAI PostgreSQL CLI Tester")
    print("=" * 50)

    # Connect to database
    if not tester.connect():
        print("❌ Failed to connect to database")
        return 1

    try:
        # Execute SQL file if specified
        if args.sql_file:
            if os.path.exists(args.sql_file):
                tester.execute_sql_file(args.sql_file)
            else:
                print(f"❌ SQL file not found: {args.sql_file}")

        # Run specific tests
        if args.schema_only or args.all:
            tester.test_schema_creation()

        if args.multi_company or args.all:
            company_ids, user_ids = tester.test_multi_company_setup()
            if company_ids and user_ids:
                tester.test_company_switching(user_ids, company_ids)
                tester.test_department_management(company_ids)

        if args.performance or args.all:
            tester.test_performance_metrics()

        # Always generate report
        tester.generate_test_report()

        print("\n✅ PostgreSQL CLI Testing Complete!")

    finally:
        tester.disconnect()

    return 0

if __name__ == "__main__":
    sys.exit(main())
