#!/usr/bin/env python3
"""
ValidoAI Implementation Test Script
====================================
Tests the actual implementation of the ValidoAI system
"""

import os
import sys
import psycopg2
import psycopg2.extras
from datetime import datetime

def test_database_connection():
    """Test PostgreSQL database connection"""
    print("🧪 Testing Database Connection...")

    try:
        conn = psycopg2.connect(
            host=os.environ.get('DB_HOST', 'localhost'),
            database=os.environ.get('DB_NAME', 'ai_valido_online'),
            user=os.environ.get('DB_USER', 'postgres'),
            password=os.environ.get('DB_PASSWORD', 'postgres'),
            port=os.environ.get('DB_PORT', '5432')
        )

        cur = conn.cursor()
        cur.execute('SELECT version()')
        version = cur.fetchone()
        cur.close()
        conn.close()

        print(f"✅ Database connection successful")
        print(f"   PostgreSQL version: {version[0].split(' ')[1]}")
        return True

    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def test_table_structure():
    """Test if all tables exist with correct structure"""
    print("\n🧪 Testing Table Structure...")

    required_tables = [
        'business_entity_types', 'companies', 'users', 'user_roles', 'user_role_assignments',
        'product_categories', 'products', 'customers', 'customer_types', 'suppliers',
        'invoices', 'invoice_items', 'general_ledger', 'payments', 'payment_methods',
        'chart_of_accounts', 'account_types', 'ai_insights', 'chat_sessions',
        'chat_messages', 'system_settings', 'performance_metrics', 'system_logs'
    ]

    try:
        conn = psycopg2.connect(
            host=os.environ.get('DB_HOST', 'localhost'),
            database=os.environ.get('DB_NAME', 'ai_valido_online'),
            user=os.environ.get('DB_USER', 'postgres'),
            password=os.environ.get('DB_PASSWORD', 'postgres'),
            port=os.environ.get('DB_PORT', '5432')
        )

        cur = conn.cursor()

        # Get all tables
        cur.execute("""
            SELECT tablename
            FROM pg_tables
            WHERE schemaname = 'public'
        """)

        existing_tables = [row[0] for row in cur.fetchall()]
        missing_tables = []

        for table in required_tables:
            if table not in existing_tables:
                missing_tables.append(table)

        if missing_tables:
            print(f"❌ Missing tables: {missing_tables}")
            return False
        else:
            print(f"✅ All {len(required_tables)} tables exist")
            return True

    except Exception as e:
        print(f"❌ Table structure test failed: {e}")
        return False
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()

def test_data_integrity():
    """Test data integrity and counts"""
    print("\n🧪 Testing Data Integrity...")

    try:
        conn = psycopg2.connect(
            host=os.environ.get('DB_HOST', 'localhost'),
            database=os.environ.get('DB_NAME', 'ai_valido_online'),
            user=os.environ.get('DB_USER', 'postgres'),
            password=os.environ.get('DB_PASSWORD', 'postgres'),
            port=os.environ.get('DB_PORT', '5432')
        )

        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        # Test key data counts
        tests = [
            ('companies', 'SELECT COUNT(*) as count FROM companies WHERE status = \'active\'', 5),
            ('users', 'SELECT COUNT(*) as count FROM users WHERE status = \'active\'', 10),
            ('products', 'SELECT COUNT(*) as count FROM products WHERE is_active = true', 20),
            ('customers', 'SELECT COUNT(*) as count FROM customers WHERE status = \'active\'', 10),
            ('invoices', 'SELECT COUNT(*) as count FROM invoices', 8),
        ]

        all_passed = True

        for table, query, min_expected in tests:
            cur.execute(query)
            result = cur.fetchone()
            count = result['count']

            if count >= min_expected:
                print(f"✅ {table}: {count} records (expected: {min_expected}+)")
            else:
                print(f"❌ {table}: {count} records (expected: {min_expected}+)")
                all_passed = False

        # Test Serbian-specific features
        cur.execute("SELECT COUNT(*) as count FROM business_entity_types")
        serbian_entities = cur.fetchone()['count']

        if serbian_entities >= 4:
            print(f"✅ Serbian business entities: {serbian_entities}")
        else:
            print(f"❌ Serbian business entities: {serbian_entities} (expected: 4+)")
            all_passed = False

        # Test PDV functionality
        cur.execute("SELECT COUNT(*) as count FROM product_categories WHERE pdv_rate > 0")
        pdv_categories = cur.fetchone()['count']

        if pdv_categories > 0:
            print(f"✅ PDV-enabled categories: {pdv_categories}")
        else:
            print("❌ No PDV-enabled categories found"
            all_passed = False

        cur.close()
        conn.close()

        return all_passed

    except Exception as e:
        print(f"❌ Data integrity test failed: {e}")
        return False

def test_flask_routes():
    """Test Flask application routes"""
    print("\n🧪 Testing Flask Application...")

    try:
        from app_postgres import app

        with app.test_client() as client:
            # Test health endpoint
            response = client.get('/health')
            if response.status_code == 200:
                print("✅ Health endpoint working")
                return True
            else:
                print(f"❌ Health endpoint failed: {response.status_code}")
                return False

    except Exception as e:
        print(f"❌ Flask test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 ValidoAI Implementation Test Suite")
    print("=" * 50)

    tests = [
        ("Database Connection", test_database_connection),
        ("Table Structure", test_table_structure),
        ("Data Integrity", test_data_integrity),
        ("Flask Routes", test_flask_routes),
    ]

    results = []

    for test_name, test_func in tests:
        print(f"\n🔬 Running {test_name}...")
        result = test_func()
        results.append((test_name, result))

    print("\n" + "=" * 50)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 50)

    passed = 0
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1

    print(f"\nOverall Score: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        print("ValidoAI system is ready for production use.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} tests failed.")
        print("Please check the implementation and fix any issues.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
