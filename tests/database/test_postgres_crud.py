#!/usr/bin/env python3
"""
PostgreSQL CRUD Operations Test Suite
=====================================
Comprehensive tests for all CRUD operations with PostgreSQL
"""

import os
import sys
import unittest
import uuid
from datetime import datetime, timedelta
from decimal import Decimal

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from models import Company, User, Invoice, InvoiceItem, Customer, Product, init_db, get_db_session
from config import get_db_config
import psycopg2
import psycopg2.extras

class TestPostgreSQLConnection(unittest.TestCase):
    """Test PostgreSQL connection and basic operations"""

    def setUp(self):
        """Set up test environment"""
        self.config = get_db_config().get_current_config()
        self.assertEqual(self.config['type'], 'postgresql', "Database type should be PostgreSQL")

    def test_connection(self):
        """Test database connection"""
        try:
            conn = psycopg2.connect(
                host=self.config['host'],
                port=self.config['port'],
                database=self.config['database'],
                user=self.config['user'],
                password=self.config['password']
            )
            self.assertIsNotNone(conn)

            # Test basic query
            cur = conn.cursor()
            cur.execute('SELECT 1 as test')
            result = cur.fetchone()
            self.assertEqual(result[0], 1)

            cur.close()
            conn.close()

        except Exception as e:
            self.fail(f"Database connection failed: {e}")

    def test_table_existence(self):
        """Test that all required tables exist"""
        required_tables = [
            'companies', 'users', 'invoices', 'invoice_items',
            'customers', 'products', 'business_entity_types'
        ]

        try:
            conn = psycopg2.connect(
                host=self.config['host'],
                port=self.config['port'],
                database=self.config['database'],
                user=self.config['user'],
                password=self.config['password']
            )

            cur = conn.cursor()
            cur.execute("""
                SELECT tablename FROM pg_tables
                WHERE schemaname = 'public'
            """)

            existing_tables = [row[0] for row in cur.fetchall()]

            for table in required_tables:
                self.assertIn(table, existing_tables, f"Table {table} should exist")

            cur.close()
            conn.close()

        except Exception as e:
            self.fail(f"Table check failed: {e}")

class TestCompanyCRUD(unittest.TestCase):
    """Test Company CRUD operations"""

    def setUp(self):
        """Set up test environment"""
        self.config = get_db_config().get_current_config()
        self.conn = psycopg2.connect(
            host=self.config['host'],
            port=self.config['port'],
            database=self.config['database'],
            user=self.config['user'],
            password=self.config['password']
        )
        self.cur = self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        # Clean up any existing test data
        self.cur.execute("DELETE FROM companies WHERE company_name LIKE 'Test Company%'")
        self.conn.commit()

    def tearDown(self):
        """Clean up test environment"""
        if hasattr(self, 'cur'):
            self.cur.close()
        if hasattr(self, 'conn'):
            self.conn.close()

    def test_create_company(self):
        """Test company creation"""
        company_data = {
            'companies_id': str(uuid.uuid4()),
            'company_name': 'Test Company DOO',
            'legal_name': 'Test Company d.o.o.',
            'tax_id': f'123456789',
            'registration_number': f'987654321',
            'business_entity_type_id': str(uuid.uuid4()),
            'industry': 'Technology',
            'company_type': 'DOO',
            'pdv_registration': 'PDV123456',
            'address_line1': 'Test Address 123',
            'city': 'Belgrade',
            'phone': '+381 11 123 4567',
            'email': 'test@company.rs',
            'is_pdv_registered': True,
            'status': 'active'
        }

        # Insert company
        columns = ', '.join(company_data.keys())
        placeholders = ', '.join(['%s'] * len(company_data))
        values = list(company_data.values())

        query = f"INSERT INTO companies ({columns}) VALUES ({placeholders})"
        self.cur.execute(query, values)
        self.conn.commit()

        # Verify insertion
        self.cur.execute("SELECT * FROM companies WHERE company_name = %s", (company_data['company_name'],))
        result = self.cur.fetchone()

        self.assertIsNotNone(result)
        self.assertEqual(result['company_name'], company_data['company_name'])
        self.assertEqual(result['tax_id'], company_data['tax_id'])

    def test_read_company(self):
        """Test company reading"""
        # First create a company
        company_data = {
            'companies_id': str(uuid.uuid4()),
            'company_name': 'Read Test Company',
            'legal_name': 'Read Test Company d.o.o.',
            'tax_id': '111111111',
            'registration_number': '222222222',
            'status': 'active'
        }

        columns = ', '.join(company_data.keys())
        placeholders = ', '.join(['%s'] * len(company_data))
        values = list(company_data.values())

        query = f"INSERT INTO companies ({columns}) VALUES ({placeholders})"
        self.cur.execute(query, values)
        self.conn.commit()

        # Test reading
        self.cur.execute("SELECT * FROM companies WHERE tax_id = %s", (company_data['tax_id'],))
        result = self.cur.fetchone()

        self.assertIsNotNone(result)
        self.assertEqual(result['company_name'], company_data['company_name'])

    def test_update_company(self):
        """Test company updating"""
        # First create a company
        company_data = {
            'companies_id': str(uuid.uuid4()),
            'company_name': 'Update Test Company',
            'legal_name': 'Update Test Company d.o.o.',
            'tax_id': '333333333',
            'registration_number': '444444444',
            'status': 'active'
        }

        columns = ', '.join(company_data.keys())
        placeholders = ', '.join(['%s'] * len(company_data))
        values = list(company_data.values())

        query = f"INSERT INTO companies ({columns}) VALUES ({placeholders})"
        self.cur.execute(query, values)
        self.conn.commit()

        # Update company
        new_name = 'Updated Test Company'
        self.cur.execute(
            "UPDATE companies SET company_name = %s, updated_at = CURRENT_TIMESTAMP WHERE tax_id = %s",
            (new_name, company_data['tax_id'])
        )
        self.conn.commit()

        # Verify update
        self.cur.execute("SELECT company_name FROM companies WHERE tax_id = %s", (company_data['tax_id'],))
        result = self.cur.fetchone()
        self.assertEqual(result['company_name'], new_name)

    def test_delete_company(self):
        """Test company deletion"""
        # First create a company
        company_data = {
            'companies_id': str(uuid.uuid4()),
            'company_name': 'Delete Test Company',
            'legal_name': 'Delete Test Company d.o.o.',
            'tax_id': '555555555',
            'registration_number': '666666666',
            'status': 'active'
        }

        columns = ', '.join(company_data.keys())
        placeholders = ', '.join(['%s'] * len(company_data))
        values = list(company_data.values())

        query = f"INSERT INTO companies ({columns}) VALUES ({placeholders})"
        self.cur.execute(query, values)
        self.conn.commit()

        # Delete company (soft delete by updating status)
        self.cur.execute(
            "UPDATE companies SET status = 'deleted', updated_at = CURRENT_TIMESTAMP WHERE tax_id = %s",
            (company_data['tax_id'],)
        )
        self.conn.commit()

        # Verify deletion
        self.cur.execute("SELECT status FROM companies WHERE tax_id = %s", (company_data['tax_id'],))
        result = self.cur.fetchone()
        self.assertEqual(result['status'], 'deleted')

class TestInvoiceCRUD(unittest.TestCase):
    """Test Invoice CRUD operations"""

    def setUp(self):
        """Set up test environment"""
        self.config = get_db_config().get_current_config()
        self.conn = psycopg2.connect(
            host=self.config['host'],
            port=self.config['port'],
            database=self.config['database'],
            user=self.config['user'],
            password=self.config['password']
        )
        self.cur = self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        # Create test company for invoices
        self.test_company_id = str(uuid.uuid4())
        company_data = {
            'companies_id': self.test_company_id,
            'company_name': 'Invoice Test Company',
            'legal_name': 'Invoice Test Company d.o.o.',
            'tax_id': '777777777',
            'registration_number': '888888888',
            'status': 'active'
        }

        columns = ', '.join(company_data.keys())
        placeholders = ', '.join(['%s'] * len(company_data))
        values = list(company_data.values())

        query = f"INSERT INTO companies ({columns}) VALUES ({placeholders})"
        self.cur.execute(query, values)
        self.conn.commit()

    def tearDown(self):
        """Clean up test environment"""
        if hasattr(self, 'cur'):
            self.cur.close()
        if hasattr(self, 'conn'):
            self.conn.close()

    def test_create_invoice(self):
        """Test invoice creation"""
        invoice_data = {
            'invoices_id': str(uuid.uuid4()),
            'invoice_number': 'INV-001-2024',
            'company_id': self.test_company_id,
            'invoice_date': datetime.now(),
            'due_date': datetime.now() + timedelta(days=30),
            'subtotal': 1000.00,
            'pdv_amount': 200.00,
            'total_amount': 1200.00,
            'currency': 'RSD',
            'payment_status': 'pending',
            'pdv_rate': 20.0,
            'status': 'issued'
        }

        # Insert invoice
        columns = ', '.join(invoice_data.keys())
        placeholders = ', '.join(['%s'] * len(invoice_data))
        values = list(invoice_data.values())

        query = f"INSERT INTO invoices ({columns}) VALUES ({placeholders})"
        self.cur.execute(query, values)
        self.conn.commit()

        # Verify insertion
        self.cur.execute("SELECT * FROM invoices WHERE invoice_number = %s", (invoice_data['invoice_number'],))
        result = self.cur.fetchone()

        self.assertIsNotNone(result)
        self.assertEqual(result['total_amount'], 1200.00)
        self.assertEqual(result['currency'], 'RSD')

    def test_invoice_with_items(self):
        """Test invoice with line items"""
        # Create invoice
        invoice_id = str(uuid.uuid4())
        invoice_data = {
            'invoices_id': invoice_id,
            'invoice_number': 'INV-002-2024',
            'company_id': self.test_company_id,
            'invoice_date': datetime.now(),
            'due_date': datetime.now() + timedelta(days=30),
            'subtotal': 500.00,
            'pdv_amount': 100.00,
            'total_amount': 600.00,
            'currency': 'RSD',
            'status': 'issued'
        }

        columns = ', '.join(invoice_data.keys())
        placeholders = ', '.join(['%s'] * len(invoice_data))
        values = list(invoice_data.values())

        query = f"INSERT INTO invoices ({columns}) VALUES ({placeholders})"
        self.cur.execute(query, values)
        self.conn.commit()

        # Add invoice items
        items_data = [
            {
                'invoice_items_id': str(uuid.uuid4()),
                'invoice_id': invoice_id,
                'line_number': 1,
                'description': 'Test Product 1',
                'quantity': 2,
                'unit_price': 200.00,
                'line_total': 400.00,
                'pdv_rate': 20.0
            },
            {
                'invoice_items_id': str(uuid.uuid4()),
                'invoice_id': invoice_id,
                'line_number': 2,
                'description': 'Test Product 2',
                'quantity': 1,
                'unit_price': 100.00,
                'line_total': 100.00,
                'pdv_rate': 20.0
            }
        ]

        for item in items_data:
            columns = ', '.join(item.keys())
            placeholders = ', '.join(['%s'] * len(item))
            values = list(item.values())

            query = f"INSERT INTO invoice_items ({columns}) VALUES ({placeholders})"
            self.cur.execute(query, values)

        self.conn.commit()

        # Verify items were added
        self.cur.execute("SELECT COUNT(*) as item_count FROM invoice_items WHERE invoice_id = %s", (invoice_id,))
        result = self.cur.fetchone()
        self.assertEqual(result['item_count'], 2)

class TestDataValidation(unittest.TestCase):
    """Test data validation and integrity"""

    def setUp(self):
        """Set up test environment"""
        self.config = get_db_config().get_current_config()
        self.conn = psycopg2.connect(
            host=self.config['host'],
            port=self.config['port'],
            database=self.config['database'],
            user=self.config['user'],
            password=self.config['password']
        )
        self.cur = self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    def tearDown(self):
        """Clean up test environment"""
        if hasattr(self, 'cur'):
            self.cur.close()
        if hasattr(self, 'conn'):
            self.conn.close()

    def test_unique_constraints(self):
        """Test unique constraints"""
        # Test company tax_id uniqueness
        company_data = {
            'companies_id': str(uuid.uuid4()),
            'company_name': 'Unique Test Company',
            'legal_name': 'Unique Test Company d.o.o.',
            'tax_id': '999999999',
            'registration_number': '000000000',
            'status': 'active'
        }

        # Insert first company
        columns = ', '.join(company_data.keys())
        placeholders = ', '.join(['%s'] * len(company_data))
        values = list(company_data.values())

        query = f"INSERT INTO companies ({columns}) VALUES ({placeholders})"
        self.cur.execute(query, values)
        self.conn.commit()

        # Try to insert duplicate tax_id (should fail)
        duplicate_data = company_data.copy()
        duplicate_data['companies_id'] = str(uuid.uuid4())
        duplicate_data['company_name'] = 'Duplicate Company'

        with self.assertRaises(psycopg2.IntegrityError):
            self.cur.execute(query, list(duplicate_data.values()))

        self.conn.rollback()

    def test_foreign_key_constraints(self):
        """Test foreign key constraints"""
        # Try to create invoice with non-existent company (should fail)
        fake_company_id = str(uuid.uuid4())
        invoice_data = {
            'invoices_id': str(uuid.uuid4()),
            'invoice_number': 'INV-999-2024',
            'company_id': fake_company_id,  # Non-existent company
            'invoice_date': datetime.now(),
            'due_date': datetime.now() + timedelta(days=30),
            'total_amount': 1000.00,
            'status': 'draft'
        }

        columns = ', '.join(invoice_data.keys())
        placeholders = ', '.join(['%s'] * len(invoice_data))
        values = list(invoice_data.values())

        query = f"INSERT INTO invoices ({columns}) VALUES ({placeholders})"

        with self.assertRaises(psycopg2.IntegrityError):
            self.cur.execute(query, values)

        self.conn.rollback()

    def test_data_types(self):
        """Test data type validation"""
        # Test numeric fields
        company_data = {
            'companies_id': str(uuid.uuid4()),
            'company_name': 'Data Type Test Company',
            'legal_name': 'Data Type Test Company d.o.o.',
            'tax_id': '123456789',
            'registration_number': '987654321',
            'status': 'active'
        }

        columns = ', '.join(company_data.keys())
        placeholders = ', '.join(['%s'] * len(company_data))
        values = list(company_data.values())

        query = f"INSERT INTO companies ({columns}) VALUES ({placeholders})"
        self.cur.execute(query, values)
        self.conn.commit()

        # Verify data types
        self.cur.execute("SELECT * FROM companies WHERE tax_id = %s", (company_data['tax_id'],))
        result = self.cur.fetchone()

        self.assertIsInstance(result['companies_id'], str)  # UUID
        self.assertIsInstance(result['company_name'], str)
        self.assertIsInstance(result['status'], str)

class TestReporting(unittest.TestCase):
    """Test reporting and analytics capabilities"""

    def setUp(self):
        """Set up test environment"""
        self.config = get_db_config().get_current_config()
        self.conn = psycopg2.connect(
            host=self.config['host'],
            port=self.config['port'],
            database=self.config['database'],
            user=self.config['user'],
            password=self.config['password']
        )
        self.cur = self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    def tearDown(self):
        """Clean up test environment"""
        if hasattr(self, 'cur'):
            self.cur.close()
        if hasattr(self, 'conn'):
            self.conn.close()

    def test_company_report(self):
        """Test company reporting"""
        self.cur.execute("""
            SELECT
                status,
                COUNT(*) as company_count,
                AVG(LENGTH(company_name)) as avg_name_length
            FROM companies
            WHERE status = 'active'
            GROUP BY status
        """)

        result = self.cur.fetchone()
        if result:
            self.assertIn('company_count', result)
            self.assertIn('status', result)

    def test_invoice_report(self):
        """Test invoice reporting"""
        self.cur.execute("""
            SELECT
                payment_status,
                COUNT(*) as invoice_count,
                SUM(total_amount) as total_value,
                AVG(total_amount) as avg_value
            FROM invoices
            GROUP BY payment_status
        """)

        results = self.cur.fetchall()
        if results:
            for result in results:
                self.assertIn('payment_status', result)
                self.assertIn('invoice_count', result)
                self.assertIn('total_value', result)

    def test_financial_summary(self):
        """Test financial summary reporting"""
        self.cur.execute("""
            SELECT
                DATE_TRUNC('month', invoice_date) as month,
                COUNT(*) as invoice_count,
                SUM(subtotal) as total_subtotal,
                SUM(pdv_amount) as total_pdv,
                SUM(total_amount) as total_amount
            FROM invoices
            WHERE status = 'issued'
            GROUP BY DATE_TRUNC('month', invoice_date)
            ORDER BY month DESC
            LIMIT 12
        """)

        results = self.cur.fetchall()
        if results:
            for result in results:
                self.assertIn('month', result)
                self.assertIn('total_amount', result)

class TestSerbianBusinessLogic(unittest.TestCase):
    """Test Serbian-specific business logic"""

    def setUp(self):
        """Set up test environment"""
        self.config = get_db_config().get_current_config()
        self.conn = psycopg2.connect(
            host=self.config['host'],
            port=self.config['port'],
            database=self.config['database'],
            user=self.config['user'],
            password=self.config['password']
        )
        self.cur = self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    def tearDown(self):
        """Clean up test environment"""
        if hasattr(self, 'cur'):
            self.cur.close()
        if hasattr(self, 'conn'):
            self.conn.close()

    def test_pdv_calculations(self):
        """Test PDV (VAT) calculations"""
        # Test PDV calculation for different rates
        test_cases = [
            (1000.00, 20.0, 200.00, 1200.00),  # Standard rate
            (1000.00, 10.0, 100.00, 1100.00),  # Reduced rate
            (1000.00, 0.0, 0.00, 1000.00),     # Exempt
        ]

        for subtotal, pdv_rate, expected_pdv, expected_total in test_cases:
            actual_pdv = subtotal * (pdv_rate / 100)
            actual_total = subtotal + actual_pdv

            self.assertAlmostEqual(actual_pdv, expected_pdv, places=2)
            self.assertAlmostEqual(actual_total, expected_total, places=2)

    def test_payment_reference_generation(self):
        """Test Serbian payment reference generation"""
        from src.serbian_gov_services import SerbianBusinessService

        service = SerbianBusinessService()

        # Test payment reference generation
        invoice_number = "INV-001-2024"
        reference = service.generate_payment_reference(invoice_number, 1200.00)

        self.assertIsNotNone(reference)
        self.assertTrue(len(reference) > 0)
        self.assertTrue(reference.startswith('97'))

    def test_business_entity_types(self):
        """Test Serbian business entity types"""
        self.cur.execute("SELECT * FROM business_entity_types LIMIT 5")

        results = self.cur.fetchall()
        if results:
            for result in results:
                self.assertIn('entity_name', result)
                self.assertIn('entity_name_sr', result)  # Serbian name
                self.assertIn('business_entity_types_id', result)

def run_postgres_tests():
    """Run all PostgreSQL tests"""
    print("🧪 PostgreSQL CRUD Test Suite")
    print("=" * 50)

    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add test classes
    test_classes = [
        TestPostgreSQLConnection,
        TestCompanyCRUD,
        TestInvoiceCRUD,
        TestDataValidation,
        TestReporting,
        TestSerbianBusinessLogic
    ]

    for test_class in test_classes:
        suite.addTests(loader.loadTestsFromTestCase(test_class))

    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print("\n" + "=" * 60)
    print("📊 POSTGRESQL TEST SUMMARY")
    print("=" * 60)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")

    if result.failures:
        print("\n❌ FAILURES:")
        for test, traceback in result.failures:
            print(f"  - {test}")

    if result.errors:
        print("\n💥 ERRORS:")
        for test, traceback in result.errors:
            print(f"  - {test}")

    if result.wasSuccessful():
        print("\n🎉 ALL POSTGRESQL TESTS PASSED!")
        print("✅ Database operations working correctly")
        print("✅ CRUD functionality verified")
        print("✅ Serbian business logic validated")
        return 0
    else:
        print("\n⚠️  SOME TESTS FAILED")
        print("Check the logs above for error details")
        return 1

if __name__ == '__main__':
    sys.exit(run_postgres_tests())

