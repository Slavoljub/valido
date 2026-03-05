#!/usr/bin/env python3
"""
Add Real Serbian Business Data
===============================
Add comprehensive, realistic business data to make the system production-ready
"""

from dotenv import load_dotenv
load_dotenv()

import psycopg2
from src.config import db_config
import uuid
from datetime import datetime, timedelta
import random

class BusinessDataAdder:
    """Add realistic Serbian business data"""

    def __init__(self):
        self.config = db_config.get_current_config()
        self.conn = None
        self.cur = None
        self.companies = []
        self.customers = []

    def connect(self):
        """Connect to database"""
        try:
            self.conn = psycopg2.connect(
                host=self.config['host'],
                port=self.config['port'],
                database=self.config['database'],
                user=self.config['user'],
                password=self.config['password']
            )
            self.cur = self.conn.cursor()
            print("✅ Connected to database")

            # Load existing data
            self.load_existing_data()

        except Exception as e:
            print(f"❌ Database connection error: {e}")
            raise

    def load_existing_data(self):
        """Load existing companies and customers"""
        try:
            self.cur.execute("SELECT companies_id, company_name FROM companies WHERE status = 'active'")
            self.companies = self.cur.fetchall()

            self.cur.execute("SELECT customers_id, company_name FROM customers WHERE status = 'active'")
            self.customers = self.cur.fetchall()

            print(f"📊 Loaded {len(self.companies)} companies and {len(self.customers)} customers")
        except Exception as e:
            print(f"⚠️ Error loading existing data: {e}")

    def disconnect(self):
        """Disconnect from database"""
        if self.cur:
            self.cur.close()
        if self.conn:
            self.conn.close()
        print("✅ Disconnected from database")

    def add_more_customers(self):
        """Add more Serbian customers"""
        print("\n🤝 Adding More Customers...")

        new_customers = [
            {
                'company_name': 'Telekom Srbija AD',
                'pib': '101234567',
                'matični_broj': 'BD11111111',
                'address_line1': 'Bulevar Vojvode Mišića 9',
                'city': 'Beograd',
                'country': 'Serbia',
                'phone': '+381112345678',
                'email': 'info@telekom.rs',
                'status': 'active',
                'credit_limit': 1000000.00,
                'payment_terms': '30 days'
            },
            {
                'company_name': 'Elektroprivreda Srbije',
                'pib': '102345678',
                'matični_broj': 'BD22222222',
                'address_line1': 'Cara Dušana 69',
                'city': 'Beograd',
                'country': 'Serbia',
                'phone': '+381112987654',
                'email': 'info@eps.rs',
                'status': 'active',
                'credit_limit': 2000000.00,
                'payment_terms': '45 days'
            },
            {
                'company_name': 'Srbijagas AD',
                'pib': '103456789',
                'matični_broj': 'BD33333333',
                'address_line1': 'Vojislava Ilića 92',
                'city': 'Novi Sad',
                'country': 'Serbia',
                'phone': '+381214567890',
                'email': 'info@srbijagas.rs',
                'status': 'active',
                'credit_limit': 1500000.00,
                'payment_terms': '30 days'
            },
            {
                'company_name': 'Pošta Srbije AD',
                'pib': '104567890',
                'matični_broj': 'BD44444444',
                'address_line1': 'Takovska 2',
                'city': 'Beograd',
                'country': 'Serbia',
                'phone': '+381113456789',
                'email': 'info@posta.rs',
                'status': 'active',
                'credit_limit': 800000.00,
                'payment_terms': '30 days'
            },
            {
                'company_name': 'Srbija Voz AD',
                'pib': '105678901',
                'matični_broj': 'BD55555555',
                'address_line1': 'Nemanjina 6',
                'city': 'Beograd',
                'country': 'Serbia',
                'phone': '+381112345678',
                'email': 'info@srbijavoz.rs',
                'status': 'active',
                'credit_limit': 1200000.00,
                'payment_terms': '30 days'
            }
        ]

        added_count = 0
        for customer in new_customers:
            try:
                # Check if customer already exists
                self.cur.execute("SELECT COUNT(*) FROM customers WHERE pib = %s", (customer['pib'],))
                if self.cur.fetchone()[0] == 0:
                    self.cur.execute("""
                        INSERT INTO customers (
                            customers_id, company_name, pib, matični_broj,
                            address_line1, city, country, phone, email,
                            status, credit_limit, payment_terms,
                            created_at, updated_at
                        ) VALUES (
                            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                            CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
                        )
                    """, (
                        str(uuid.uuid4()),
                        customer['company_name'],
                        customer['pib'],
                        customer['matični_broj'],
                        customer['address_line1'],
                        customer['city'],
                        customer['country'],
                        customer['phone'],
                        customer['email'],
                        customer['status'],
                        customer['credit_limit'],
                        customer['payment_terms']
                    ))
                    added_count += 1
                else:
                    print(f"⚠️ Customer {customer['company_name']} already exists")
            except Exception as e:
                print(f"⚠️ Error adding customer {customer['company_name']}: {e}")

        self.conn.commit()
        print(f"✅ Added {added_count} new customers")

        # Reload customers list
        self.load_existing_data()

    def add_comprehensive_invoices(self):
        """Add comprehensive invoice data"""
        print("\n🧾 Adding Comprehensive Invoices...")

        if not self.companies or not self.customers:
            print("⚠️ Not enough companies or customers to create invoices")
            return

        # Invoice templates with realistic Serbian business services
        invoice_templates = [
            {
                'description': 'IT konsultantske usluge - analiza sistema',
                'unit_price': 85000.00,
                'quantity': 1
            },
            {
                'description': 'Razvoj mobilne aplikacije - iOS i Android',
                'unit_price': 250000.00,
                'quantity': 1
            },
            {
                'description': 'Održavanje serverske infrastrukture',
                'unit_price': 45000.00,
                'quantity': 3
            },
            {
                'description': 'Implementacija ERP sistema',
                'unit_price': 180000.00,
                'quantity': 1
            },
            {
                'description': 'Konsultantske usluge - digitalna transformacija',
                'unit_price': 120000.00,
                'quantity': 2
            },
            {
                'description': 'Razvoj e-commerce platforme',
                'unit_price': 350000.00,
                'quantity': 1
            },
            {
                'description': 'Tehnička podrška - mesečna usluga',
                'unit_price': 25000.00,
                'quantity': 6
            },
            {
                'description': 'Obuka zaposlenih - digitalne veštine',
                'unit_price': 15000.00,
                'quantity': 15
            }
        ]

        added_count = 0
        base_date = datetime(2024, 1, 1)

        # Create 50 invoices
        for i in range(50):
            try:
                # Random date within 2024
                invoice_date = base_date + timedelta(days=random.randint(0, 300))
                due_date = invoice_date + timedelta(days=random.randint(15, 60))

                company_id = random.choice(self.companies)[0]
                customer = random.choice(self.customers)
                customer_id = customer[0]
                customer_name = customer[1]

                # Create invoice header
                invoice_id = str(uuid.uuid4())
                subtotal = 0
                items = []

                # Add 1-5 random line items
                num_items = random.randint(1, 5)
                for j in range(num_items):
                    template = random.choice(invoice_templates)
                    quantity = random.randint(1, template['quantity'])
                    unit_price = template['unit_price'] * random.uniform(0.8, 1.2)  # Price variation
                    line_total = quantity * unit_price
                    subtotal += line_total

                    items.append({
                        'description': template['description'],
                        'quantity': quantity,
                        'unit_price': unit_price,
                        'line_total': line_total
                    })

                pdv_amount = subtotal * 0.20  # 20% PDV
                total_amount = subtotal + pdv_amount

                # Insert invoice
                self.cur.execute("""
                    INSERT INTO invoices (
                        invoices_id, invoice_number, company_id, customer_id, customer_name,
                        invoice_date, due_date, subtotal, pdv_amount, total_amount,
                        currency, payment_status, status, created_at, updated_at
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                        CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
                    )
                """, (
                    invoice_id,
                    '04d',
                    company_id,
                    customer_id,
                    customer_name,
                    invoice_date.strftime('%Y-%m-%d'),
                    due_date.strftime('%Y-%m-%d'),
                    subtotal,
                    pdv_amount,
                    total_amount,
                    'RSD',
                    random.choice(['paid', 'pending', 'overdue']),
                    'issued'
                ))

                # Insert invoice items
                for idx, item in enumerate(items, 1):
                    self.cur.execute("""
                        INSERT INTO invoice_items (
                            invoice_items_id, invoice_id, line_number, description,
                            quantity, unit_price, line_total, pdv_rate, created_at, updated_at
                        ) VALUES (
                            %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
                        )
                    """, (
                        str(uuid.uuid4()),
                        invoice_id,
                        idx,
                        item['description'],
                        item['quantity'],
                        item['unit_price'],
                        item['line_total'],
                        20.0
                    ))

                added_count += 1

            except Exception as e:
                print(f"⚠️ Error creating invoice {i+1}: {e}")

        self.conn.commit()
        print(f"✅ Added {added_count} comprehensive invoices with line items")

    def add_user_activity_data(self):
        """Add user activity and performance data"""
        print("\n👤 Adding User Activity Data...")

        # Add some chat sessions
        if self.companies:
            for i in range(10):
                try:
                    session_id = str(uuid.uuid4())
                    company = random.choice(self.companies)
                    user_names = ['admin', 'manager', 'accountant', 'sales', 'user']

                    self.cur.execute("""
                        INSERT INTO chat_sessions (
                            chat_sessions_id, session_name, user_id, company_id,
                            status, created_at, updated_at
                        ) VALUES (
                            %s, %s, %s, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
                        )
                    """, (
                        session_id,
                        f"Chat Session {i+1}",
                        random.choice(user_names),
                        company[0],
                        random.choice(['active', 'completed', 'archived'])
                    ))

                except Exception as e:
                    print(f"⚠️ Error creating chat session {i+1}: {e}")

        # Add performance metrics
        for i in range(20):
            try:
                metric_types = ['response_time', 'cpu_usage', 'memory_usage', 'disk_usage', 'network_io']
                metric_type = random.choice(metric_types)

                # Generate realistic values based on metric type
                if metric_type == 'response_time':
                    value = random.uniform(0.1, 2.5)  # seconds
                elif metric_type in ['cpu_usage', 'memory_usage', 'disk_usage']:
                    value = random.uniform(10, 90)  # percentage
                else:
                    value = random.uniform(1000, 100000)  # bytes per second

                self.cur.execute("""
                    INSERT INTO performance_metrics (
                        performance_metrics_id, metric_name, metric_value, unit,
                        timestamp, created_at
                    ) VALUES (
                        %s, %s, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
                    )
                """, (
                    str(uuid.uuid4()),
                    metric_type,
                    value,
                    'seconds' if metric_type == 'response_time' else 'percent' if metric_type in ['cpu_usage', 'memory_usage', 'disk_usage'] else 'bytes_per_sec'
                ))

            except Exception as e:
                print(f"⚠️ Error creating performance metric {i+1}: {e}")

        self.conn.commit()
        print("✅ Added user activity and performance data")

    def run_all_additions(self):
        """Run all data additions"""
        print("🚀 STARTING BUSINESS DATA ADDITION")
        print("=" * 40)

        try:
            self.connect()

            self.add_more_customers()
            self.add_comprehensive_invoices()
            self.add_user_activity_data()

            print("\n🎉 BUSINESS DATA ADDITION COMPLETED!")
            print("=" * 40)

            # Show final statistics
            print("\n📊 FINAL DATABASE STATUS:")
            print("-" * 30)

            try:
                self.cur.execute("SELECT COUNT(*) FROM customers WHERE status = 'active'")
                customers = self.cur.fetchone()[0]

                self.cur.execute("SELECT COUNT(*) FROM invoices WHERE status = 'issued'")
                invoices = self.cur.fetchone()[0]

                self.cur.execute("SELECT COUNT(*) FROM invoice_items")
                invoice_items = self.cur.fetchone()[0]

                self.cur.execute("SELECT COUNT(*) FROM chat_sessions")
                chat_sessions = self.cur.fetchone()[0]

                self.cur.execute("SELECT COUNT(*) FROM performance_metrics")
                metrics = self.cur.fetchone()[0]

                print("12")
                print("12")
                print("12")
                print("12")
                print("12")

            except Exception as e:
                print(f"⚠️ Error getting final stats: {e}")

        except Exception as e:
            print(f"❌ Data addition failed: {e}")
        finally:
            self.disconnect()

if __name__ == '__main__':
    adder = BusinessDataAdder()
    adder.run_all_additions()
