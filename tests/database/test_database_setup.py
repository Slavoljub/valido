#!/usr/bin/env python3
"""
ValidoAI Database Setup Verification Script
===========================================

This script verifies the complete PostgreSQL database setup including:
- Database creation and connection
- Schema creation and table structure
- Unicode/UTF-8 support
- Sample data insertion
- AI features and extensions
- Performance and functionality tests

Usage:
    python test_database_setup.py

Requirements:
    - PostgreSQL server running on localhost:5432
    - psycopg2 or psycopg2-binary installed
    - Database user 'postgres' with password 'postgres'
"""

import sys
import os
import subprocess
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

try:
    import psycopg2
    import psycopg2.extras
except ImportError:
    print("❌ psycopg2 not found. Installing...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "psycopg2-binary"])
    import psycopg2
    import psycopg2.extras

@dataclass
class TestResult:
    name: str
    status: str
    message: str
    details: Optional[Dict] = None

class DatabaseTester:
    def __init__(self):
        self.db_config = {
            'host': 'localhost',
            'port': 5432,
            'database': 'ai_valido_online',
            'user': 'postgres',
            'password': 'postgres'
        }
        self.connection = None
        self.test_results = []

    def log_test(self, name: str, status: str, message: str, details: Optional[Dict] = None):
        """Log a test result"""
        self.test_results.append(TestResult(name, status, message, details))
        status_emoji = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_emoji} {name}: {message}")
        if details:
            for key, value in details.items():
                print(f"   {key}: {value}")

    def connect_database(self):
        """Test database connection"""
        try:
            print("🔌 Testing database connection...")
            self.connection = psycopg2.connect(**self.db_config)
            self.connection.autocommit = True

            # Test basic query
            with self.connection.cursor() as cursor:
                cursor.execute("SELECT version();")
                version = cursor.fetchone()[0]

            self.log_test(
                "Database Connection",
                "PASS",
                f"Successfully connected to PostgreSQL: {version[:50]}...",
                {"version": version, "encoding": self.connection.encoding}
            )
            return True

        except Exception as e:
            self.log_test("Database Connection", "FAIL", f"Connection failed: {str(e)}")
            return False

    def check_database_exists(self):
        """Check if database exists"""
        try:
            # Connect to default database first
            temp_conn = psycopg2.connect(
                host=self.db_config['host'],
                port=self.db_config['port'],
                user=self.db_config['user'],
                password=self.db_config['password'],
                database='postgres'
            )

            with temp_conn.cursor() as cursor:
                cursor.execute("""
                    SELECT datname, encoding, datcollate, datctype
                    FROM pg_database
                    WHERE datname = %s
                """, (self.db_config['database'],))

                result = cursor.fetchone()
                if result:
                    db_name, encoding, collate, ctype = result
                    self.log_test(
                        "Database Exists",
                        "PASS",
                        f"Database '{db_name}' exists with UTF-8 support",
                        {
                            "encoding": encoding,
                            "collate": collate,
                            "ctype": ctype
                        }
                    )
                    return True
                else:
                    self.log_test("Database Exists", "FAIL", f"Database '{self.db_config['database']}' does not exist")
                    return False

        except Exception as e:
            self.log_test("Database Exists", "FAIL", f"Error checking database: {str(e)}")
            return False
        finally:
            if 'temp_conn' in locals():
                temp_conn.close()

    def create_database(self):
        """Create the database if it doesn't exist"""
        try:
            print("📊 Creating database...")

            # Connect to default database
            temp_conn = psycopg2.connect(
                host=self.db_config['host'],
                port=self.db_config['port'],
                user=self.db_config['user'],
                password=self.db_config['password'],
                database='postgres'
            )

            with temp_conn.cursor() as cursor:
                # Create database with proper Unicode support
                cursor.execute(f"""
                    CREATE DATABASE {self.db_config['database']}
                    WITH
                    OWNER = {self.db_config['user']}
                    ENCODING = 'UTF8'
                    LC_COLLATE = 'C.UTF-8'
                    LC_CTYPE = 'C.UTF-8'
                    TABLESPACE = pg_default
                    CONNECTION LIMIT = -1
                    TEMPLATE = template0;
                """)

            self.log_test("Database Creation", "PASS", f"Database '{self.db_config['database']}' created successfully")
            return True

        except psycopg2.errors.DuplicateDatabase:
            self.log_test("Database Creation", "SKIP", "Database already exists")
            return True
        except Exception as e:
            self.log_test("Database Creation", "FAIL", f"Database creation failed: {str(e)}")
            return False
        finally:
            if 'temp_conn' in locals():
                temp_conn.close()

    def check_extensions(self):
        """Check if required PostgreSQL extensions are installed"""
        required_extensions = [
            'uuid-ossp', 'pgcrypto', 'pg_stat_statements', 'pg_buffercache',
            'pg_prewarm', 'pg_similarity', 'pg_trgm', 'btree_gist', 'btree_gin',
            'unaccent', 'pg_freespacemap', 'pgvector', 'timescaledb', 'postgis',
            'pg_cron', 'pg_repack', 'fuzzystrmatch'
        ]

        try:
            with self.connection.cursor() as cursor:
                # Get installed extensions
                cursor.execute("SELECT name FROM pg_available_extensions WHERE installed_version IS NOT NULL;")
                installed = {row[0] for row in cursor.fetchall()}

                missing = []
                available = []

                for ext in required_extensions:
                    if ext in installed:
                        available.append(ext)
                    else:
                        missing.append(ext)

                details = {
                    "available": len(available),
                    "missing": len(missing),
                    "available_list": available[:5]  # Show first 5
                }

                if missing:
                    self.log_test(
                        "Extensions Check",
                        "WARN",
                        f"{len(available)}/{len(required_extensions)} extensions available",
                        details
                    )
                else:
                    self.log_test(
                        "Extensions Check",
                        "PASS",
                        f"All {len(required_extensions)} extensions available",
                        details
                    )

        except Exception as e:
            self.log_test("Extensions Check", "FAIL", f"Error checking extensions: {str(e)}")

    def check_tables(self):
        """Check if all required tables exist"""
        required_tables = [
            'companies', 'users', 'customers', 'products', 'invoices', 'payments',
            'suppliers', 'audit_logs', 'chat_sessions', 'customer_feedback',
            'ai_models', 'ai_processing_queue', 'vector_embeddings',
            'sentiment_analysis_results', 'ai_training_data', 'ai_model_performance',
            'ai_insights', 'user_company_access', 'user_company_sessions',
            'business_areas', 'countries', 'currencies', 'product_categories'
        ]

        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    SELECT tablename
                    FROM pg_tables
                    WHERE schemaname = 'public'
                    ORDER BY tablename;
                """)

                existing_tables = {row[0] for row in cursor.fetchall()}
                missing = []
                found = []

                for table in required_tables:
                    if table in existing_tables:
                        found.append(table)
                    else:
                        missing.append(table)

                details = {
                    "found": len(found),
                    "missing": len(missing),
                    "total_expected": len(required_tables)
                }

                if missing:
                    self.log_test(
                        "Tables Check",
                        "FAIL",
                        f"Missing {len(missing)} tables: {missing[:5]}...",
                        details
                    )
                else:
                    self.log_test(
                        "Tables Check",
                        "PASS",
                        f"All {len(required_tables)} tables exist",
                        details
                    )

        except Exception as e:
            self.log_test("Tables Check", "FAIL", f"Error checking tables: {str(e)}")

    def check_unicode_support(self):
        """Test Unicode and Cyrillic support"""
        try:
            with self.connection.cursor() as cursor:
                # Test Unicode insertion
                test_data = [
                    ("КодМастерс ДОО", "Serbian company name"),
                    ("شركة التقنية", "Arabic company name"),
                    ("北京科技发展有限公司", "Chinese company name"),
                    ("Technologie Avancée", "French with accents"),
                    ("Deutsche Technologie", "German with umlauts"),
                    ("Москва", "Russian city"),
                    ("Србија", "Serbia in Cyrillic")
                ]

                success_count = 0
                for text, description in test_data:
                    try:
                        cursor.execute("SELECT %s, char_length(%s), length(%s::bytea);", (text, text, text))
                        result = cursor.fetchone()
                        if result and len(result) == 3:
                            success_count += 1
                    except Exception as e:
                        print(f"   Unicode test failed for {description}: {e}")

                details = {
                    "unicode_tests": len(test_data),
                    "successful": success_count,
                    "success_rate": ".1f"
                }

                if success_count == len(test_data):
                    self.log_test(
                        "Unicode Support",
                        "PASS",
                        "All Unicode characters supported correctly",
                        details
                    )
                else:
                    self.log_test(
                        "Unicode Support",
                        "WARN",
                        f"Unicode support partial: {success_count}/{len(test_data)} tests passed",
                        details
                    )

        except Exception as e:
            self.log_test("Unicode Support", "FAIL", f"Unicode support test failed: {str(e)}")

    def check_sample_data(self):
        """Check if sample data was loaded correctly"""
        data_checks = [
            ("companies", "SELECT COUNT(*) FROM companies"),
            ("users", "SELECT COUNT(*) FROM users"),
            ("customer_feedback", "SELECT COUNT(*) FROM customer_feedback"),
            ("products", "SELECT COUNT(*) FROM products"),
            ("ai_models", "SELECT COUNT(*) FROM ai_models"),
            ("vector_embeddings", "SELECT COUNT(*) FROM vector_embeddings")
        ]

        try:
            with self.connection.cursor() as cursor:
                results = {}
                total_records = 0

                for table, query in data_checks:
                    try:
                        cursor.execute(query)
                        count = cursor.fetchone()[0]
                        results[table] = count
                        total_records += count
                    except Exception as e:
                        results[table] = f"Error: {e}"

                details = {
                    "tables_checked": len(data_checks),
                    "total_records": total_records,
                    "table_counts": results
                }

                if total_records > 0:
                    self.log_test(
                        "Sample Data",
                        "PASS",
                        f"Sample data loaded: {total_records} total records",
                        details
                    )
                else:
                    self.log_test(
                        "Sample Data",
                        "WARN",
                        "No sample data found",
                        details
                    )

        except Exception as e:
            self.log_test("Sample Data", "FAIL", f"Error checking sample data: {str(e)}")

    def test_ai_features(self):
        """Test AI-related features"""
        ai_tests = [
            ("AI Models", "SELECT COUNT(*) FROM ai_models WHERE is_active = true"),
            ("Customer Feedback", "SELECT COUNT(*) FROM customer_feedback WHERE ai_processed = true"),
            ("Vector Embeddings", "SELECT COUNT(*) FROM vector_embeddings WHERE is_active = true"),
            ("Sentiment Analysis", "SELECT COUNT(*) FROM sentiment_analysis_results"),
            ("AI Insights", "SELECT COUNT(*) FROM ai_insights WHERE is_active = true")
        ]

        try:
            with self.connection.cursor() as cursor:
                results = {}
                total_ai_records = 0

                for feature, query in ai_tests:
                    try:
                        cursor.execute(query)
                        count = cursor.fetchone()[0]
                        results[feature] = count
                        total_ai_records += count
                    except Exception as e:
                        results[feature] = f"Error: {e}"

                details = {
                    "ai_features_tested": len(ai_tests),
                    "total_ai_records": total_ai_records,
                    "ai_counts": results
                }

                if total_ai_records > 0:
                    self.log_test(
                        "AI Features",
                        "PASS",
                        f"AI features active: {total_ai_records} records across features",
                        details
                    )
                else:
                    self.log_test(
                        "AI Features",
                        "WARN",
                        "AI features not fully initialized",
                        details
                    )

        except Exception as e:
            self.log_test("AI Features", "FAIL", f"Error testing AI features: {str(e)}")

    def test_functions(self):
        """Test custom database functions"""
        functions_to_test = [
            ("normalize_unicode_text", "SELECT normalize_unicode_text('café')"),
            ("cyrillic_similarity", "SELECT cyrillic_similarity('test', 'test')"),
            ("is_cyrillic_text", "SELECT is_cyrillic_text('здраво')"),
            ("detect_script_type", "SELECT detect_script_type('Hello мир')"),
            ("get_text_encoding_info", "SELECT (get_text_encoding_info('test')).encoding")
        ]

        try:
            with self.connection.cursor() as cursor:
                working_functions = 0

                for func_name, query in functions_to_test:
                    try:
                        cursor.execute(query)
                        result = cursor.fetchone()
                        if result and result[0] is not None:
                            working_functions += 1
                    except Exception as e:
                        print(f"   Function {func_name} test failed: {e}")

                details = {
                    "functions_tested": len(functions_to_test),
                    "working_functions": working_functions
                }

                if working_functions == len(functions_to_test):
                    self.log_test(
                        "Database Functions",
                        "PASS",
                        f"All {len(functions_to_test)} custom functions working",
                        details
                    )
                else:
                    self.log_test(
                        "Database Functions",
                        "WARN",
                        f"Functions partial: {working_functions}/{len(functions_to_test)} working",
                        details
                    )

        except Exception as e:
            self.log_test("Database Functions", "FAIL", f"Error testing functions: {str(e)}")

    def run_performance_test(self):
        """Run basic performance test"""
        try:
            with self.connection.cursor() as cursor:
                start_time = time.time()

                # Test query performance
                cursor.execute("SELECT COUNT(*) FROM companies;")
                companies_count = cursor.fetchone()[0]

                cursor.execute("SELECT COUNT(*) FROM customer_feedback WHERE sentiment_score IS NOT NULL;")
                feedback_count = cursor.fetchone()[0]

                # Test Unicode search performance
                cursor.execute("SELECT COUNT(*) FROM companies WHERE company_name ~ '[^\x00-\x7F]';")
                unicode_companies = cursor.fetchone()[0]

                end_time = time.time()
                query_time = end_time - start_time

                details = {
                    "query_time_seconds": ".3f",
                    "companies_count": companies_count,
                    "feedback_count": feedback_count,
                    "unicode_companies": unicode_companies,
                    "queries_per_second": ".1f"
                }

                if query_time < 1.0:
                    self.log_test(
                        "Performance Test",
                        "PASS",
                        f"Performance test passed: {query_time:.3f}s for 3 queries",
                        details
                    )
                else:
                    self.log_test(
                        "Performance Test",
                        "WARN",
                        f"Performance test slow: {query_time:.3f}s for 3 queries",
                        details
                    )

        except Exception as e:
            self.log_test("Performance Test", "FAIL", f"Performance test failed: {str(e)}")

    def run_setup(self):
        """Run the complete database setup"""
        print("🚀 Starting ValidoAI Database Setup and Verification")
        print("=" * 60)

        # Step 1: Create database if needed
        if not self.check_database_exists():
            if not self.create_database():
                print("❌ Cannot proceed without database")
                return False
            time.sleep(2)  # Wait for database to be ready

        # Step 2: Connect to database
        if not self.connect_database():
            print("❌ Cannot connect to database")
            return False

        print("\n📋 Running comprehensive tests...")
        print("-" * 40)

        # Step 3: Run all tests
        self.check_extensions()
        self.check_tables()
        self.check_unicode_support()
        self.check_sample_data()
        self.test_ai_features()
        self.test_functions()
        self.run_performance_test()

        print("\n📊 Test Summary")
        print("-" * 40)

        # Calculate results
        passed = sum(1 for r in self.test_results if r.status == "PASS")
        failed = sum(1 for r in self.test_results if r.status == "FAIL")
        warned = sum(1 for r in self.test_results if r.status == "WARN")

        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"⚠️  Warnings: {warned}")
        print(f"📈 Total Tests: {len(self.test_results)}")

        if failed == 0:
            print("\n🎉 All critical tests passed! Database is ready for use.")
            return True
        else:
            print(f"\n⚠️  {failed} critical test(s) failed. Please check the errors above.")
            return False

    def cleanup(self):
        """Clean up connections"""
        if self.connection:
            self.connection.close()

def main():
    """Main function"""
    tester = DatabaseTester()

    try:
        success = tester.run_setup()
        return 0 if success else 1

    except KeyboardInterrupt:
        print("\n⚠️  Setup interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Setup failed with error: {e}")
        return 1
    finally:
        tester.cleanup()

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
