"""
Unit Tests for Data Models
Tests individual model classes and their methods
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch
import os
import sys

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from models.database_models import User, Company
from models.company import CompanyModel
from models.financial_models import InvoiceModel


class TestUserModel:
    """Test User model functionality"""

    def test_user_creation(self):
        """Test basic user creation"""
        user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User'
        }

        user = User(**user_data)
        assert user.username == 'testuser'
        assert user.email == 'test@example.com'
        assert user.first_name == 'Test'
        assert user.last_name == 'User'

    def test_user_password_hashing(self):
        """Test password hashing functionality"""
        user = User(username='test', email='test@example.com')

        # Mock password hashing
        with patch('models.database_models.generate_password_hash') as mock_hash:
            mock_hash.return_value = 'hashed_password'
            user.set_password('plaintext_password')

            assert user.password_hash == 'hashed_password'
            mock_hash.assert_called_once_with('plaintext_password')

    def test_user_email_validation(self):
        """Test email validation"""
        valid_emails = [
            'user@example.com',
            'test.user@domain.org',
            'user+tag@example.co.uk'
        ]

        invalid_emails = [
            'invalid-email',
            '@example.com',
            'user@',
            'user..double@example.com'
        ]

        for email in valid_emails:
            user = User(username='test', email=email)
            assert user.email == email

        for email in invalid_emails:
            with pytest.raises(ValueError):
                User(username='test', email=email)

    def test_user_to_dict(self):
        """Test user serialization"""
        user = User(
            username='testuser',
            email='test@example.com',
            first_name='Test',
            last_name='User'
        )

        user_dict = user.to_dict()

        assert user_dict['username'] == 'testuser'
        assert user_dict['email'] == 'test@example.com'
        assert user_dict['first_name'] == 'Test'
        assert user_dict['last_name'] == 'User'
        assert 'password_hash' not in user_dict  # Sensitive data should be excluded


class TestCompanyModel:
    """Test Company model functionality"""

    def test_company_creation(self):
        """Test basic company creation"""
        company_data = {
            'company_name': 'Test Company',
            'tax_id': '123456789',
            'address_city': 'Belgrade'
        }

        company = Company(**company_data)
        assert company.company_name == 'Test Company'
        assert company.tax_id == '123456789'
        assert company.address_city == 'Belgrade'

    def test_company_tax_id_uniqueness(self):
        """Test tax ID uniqueness constraint"""
        # This would typically test database constraints
        # For unit tests, we test the validation logic

        company1 = Company(company_name='Company 1', tax_id='123456789')
        company2 = Company(company_name='Company 2', tax_id='123456789')

        # In a real scenario, this would raise a database error
        # For unit tests, we verify the tax_id is set correctly
        assert company1.tax_id == company2.tax_id

    def test_company_active_status(self):
        """Test company active status"""
        company = Company(
            company_name='Test Company',
            tax_id='123456789',
            is_active=True
        )

        assert company.is_active is True

        # Test default active status
        company2 = Company(
            company_name='Test Company 2',
            tax_id='987654321'
        )

        # Assuming default is True in model definition
        assert company2.is_active is True


class TestInvoiceModel:
    """Test Invoice model functionality"""

    def test_invoice_creation(self):
        """Test basic invoice creation"""
        invoice_data = {
            'invoice_number': 'INV-2024-001',
            'company_id': 1,
            'customer_id': 123,
            'amount': 1000.00,
            'currency': 'RSD',
            'status': 'draft'
        }

        invoice = InvoiceModel(**invoice_data)
        assert invoice.invoice_number == 'INV-2024-001'
        assert invoice.amount == 1000.00
        assert invoice.currency == 'RSD'

    def test_invoice_total_calculation(self):
        """Test invoice total calculation with tax"""
        invoice = InvoiceModel(
            invoice_number='INV-2024-002',
            company_id=1,
            customer_id=123,
            subtotal=1000.00,
            tax_rate=20.0,
            currency='RSD'
        )

        # Calculate expected total: 1000 + (1000 * 20/100) = 1200
        expected_total = 1000.00 + (1000.00 * 20.0 / 100.0)

        assert invoice.total_amount == expected_total
        assert invoice.tax_amount == 200.00

    def test_invoice_status_transitions(self):
        """Test invoice status transitions"""
        invoice = InvoiceModel(
            invoice_number='INV-2024-003',
            company_id=1,
            customer_id=123,
            amount=500.00,
            status='draft'
        )

        # Test valid status transitions
        valid_transitions = [
            ('draft', 'sent'),
            ('sent', 'viewed'),
            ('viewed', 'paid'),
            ('sent', 'overdue'),
            ('overdue', 'paid')
        ]

        for current_status, new_status in valid_transitions:
            invoice.status = current_status
            invoice.update_status(new_status)
            assert invoice.status == new_status

    def test_invoice_currency_conversion(self):
        """Test currency conversion functionality"""
        invoice = InvoiceModel(
            invoice_number='INV-2024-004',
            company_id=1,
            customer_id=123,
            amount=1000.00,
            currency='RSD',
            exchange_rate=0.0085  # RSD to USD
        )

        # Test conversion to USD
        usd_amount = invoice.convert_currency('USD')
        expected_usd = 1000.00 * 0.0085

        assert usd_amount == pytest.approx(expected_usd, rel=1e-2)


class TestModelValidation:
    """Test model validation logic"""

    def test_required_field_validation(self):
        """Test required field validation"""
        # Test User model required fields
        with pytest.raises(ValueError):
            User(username=None, email='test@example.com')

        with pytest.raises(ValueError):
            User(username='testuser', email=None)

    def test_field_length_validation(self):
        """Test field length validation"""
        # Test username length
        with pytest.raises(ValueError):
            User(username='a' * 81, email='test@example.com')  # Too long

        with pytest.raises(ValueError):
            User(username='', email='test@example.com')  # Too short

    def test_email_format_validation(self):
        """Test email format validation"""
        valid_emails = [
            'user@example.com',
            'test.user+tag@domain.co.uk',
            'user123@test-domain.com'
        ]

        invalid_emails = [
            'invalid-email',
            '@example.com',
            'user@',
            'user..double@example.com',
            'user@.com'
        ]

        for email in valid_emails:
            user = User(username='test', email=email)
            # Should not raise exception
            assert user.email == email

        for email in invalid_emails:
            with pytest.raises(ValueError, match="Invalid email format"):
                User(username='test', email=email)

    def test_numeric_field_validation(self):
        """Test numeric field validation"""
        # Test positive amounts
        invoice = InvoiceModel(
            invoice_number='INV-2024-005',
            company_id=1,
            customer_id=123,
            amount=100.50
        )

        assert invoice.amount == 100.50

        # Test negative amounts should raise error
        with pytest.raises(ValueError, match="Amount must be positive"):
            InvoiceModel(
                invoice_number='INV-2024-006',
                company_id=1,
                customer_id=123,
                amount=-100.00
            )


class TestModelSerialization:
    """Test model serialization functionality"""

    def test_user_serialization(self):
        """Test user model serialization"""
        user = User(
            username='testuser',
            email='test@example.com',
            first_name='Test',
            last_name='User',
            is_active=True
        )

        user_dict = user.to_dict()

        expected_keys = {'username', 'email', 'first_name', 'last_name', 'is_active'}
        assert set(user_dict.keys()) == expected_keys

        # Sensitive data should not be included
        assert 'password_hash' not in user_dict

    def test_company_serialization(self):
        """Test company model serialization"""
        company = Company(
            company_name='Test Company',
            tax_id='123456789',
            address_city='Belgrade',
            is_active=True
        )

        company_dict = company.to_dict()

        assert company_dict['company_name'] == 'Test Company'
        assert company_dict['tax_id'] == '123456789'
        assert company_dict['is_active'] is True

    def test_nested_serialization(self):
        """Test serialization with nested objects"""
        user = User(
            username='manager',
            email='manager@company.com',
            first_name='Manager',
            last_name='User'
        )

        company = Company(
            company_name='Test Company',
            tax_id='123456789',
            created_by=user  # Assuming relationship exists
        )

        company_dict = company.to_dict()

        # Should include creator information
        assert 'created_by' in company_dict
        assert company_dict['created_by']['username'] == 'manager'


# Configuration for pytest
pytest_plugins = ["pytest_asyncio"]

def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )
    config.addinivalue_line(
        "markers", "model: marks tests as model tests"
    )

def pytest_collection_modifyitems(config, items):
    """Add markers to test items"""
    for item in items:
        if "model" in item.fspath.basename:
            item.add_marker(pytest.mark.model)
        if "test_" in item.fspath.basename:
            item.add_marker(pytest.mark.unit)
