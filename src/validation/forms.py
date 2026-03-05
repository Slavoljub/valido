"""
Comprehensive Forms Module for ValidoAI
Provides form validation, error handling, and Serbian-specific form patterns
"""

from typing import Dict, List, Any, Optional, Union, Tuple
from flask import request, flash, redirect, url_for, render_template
from flask_wtf import FlaskForm
from wtforms import (
    StringField, IntegerField, FloatField, DecimalField, BooleanField, 
    DateField, DateTimeField, EmailField, URLField, PasswordField, 
    TextAreaField, SelectField, SelectMultipleField, FileField, 
    HiddenField, SubmitField, FieldList, FormField
)
from wtforms.validators import (
    DataRequired, Email, URL, Length, NumberRange, Optional as OptionalValidator,
    ValidationError as WTFormsValidationError
)
from wtforms.widgets import TextInput, PasswordInput, TextArea
import re
from datetime import datetime, date
from decimal import Decimal

from .validators import (
    ValidationManager, ValidatorFactory, ValidationError,
    StringValidator, IntegerValidator, FloatValidator, DecimalValidator,
    BooleanValidator, DateValidator, DateTimeValidator, EmailValidator,
    URLValidator, PhoneValidator, IPValidator, JSONValidator, ListValidator,
    DictValidator, FileValidator, PasswordValidator, CurrencyValidator,
    PercentageValidator, UUIDValidator, ColorValidator, CreditCardValidator,
    PostalCodeValidator, SerbianPIBValidator, SerbianMaticniBrojValidator
)

class BaseForm(FlaskForm):
    """Base form class with common functionality"""
    
    def __init__(self, *args, **kwargs):
        self.language = kwargs.pop('language', 'en')
        super().__init__(*args, **kwargs)
        self.validation_manager = ValidationManager()
    
    def validate_on_submit(self):
        """Enhanced validation with custom validators"""
        if not super().validate_on_submit():
            return False
        
        # Additional custom validation
        return self.custom_validate()
    
    def custom_validate(self) -> bool:
        """Custom validation logic - override in subclasses"""
        return True
    
    def get_validation_errors(self) -> List[Dict]:
        """Get validation errors in a structured format"""
        errors = []
        for field_name, field in self._fields.items():
            if field.errors:
                for error in field.errors:
                    errors.append({
                        'field': field_name,
                        'message': error,
                        'code': 'VALIDATION_ERROR'
                    })
        return errors
    
    def flash_errors(self):
        """Flash validation errors"""
        for field_name, field in self._fields.items():
            if field.errors:
                for error in field.errors:
                    flash(f"{field.label.text}: {error}", 'error')
    
    def get_field_value(self, field_name: str) -> Any:
        """Get field value safely"""
        field = getattr(self, field_name, None)
        if field:
            return field.data
        return None
    
    def set_field_value(self, field_name: str, value: Any):
        """Set field value safely"""
        field = getattr(self, field_name, None)
        if field:
            field.data = value

class SerbianPhoneInput(TextInput):
    """Custom widget for Serbian phone numbers"""
    
    def __call__(self, field, **kwargs):
        kwargs.setdefault('placeholder', '+381 6x xxx xxxx')
        kwargs.setdefault('pattern', r'(\+381|0)6[0-9]\d{6,7}|(\+381|0)1[0-9]\d{6,7}')
        return super().__call__(field, **kwargs)

class SerbianPIBInput(TextInput):
    """Custom widget for Serbian PIB"""
    
    def __call__(self, field, **kwargs):
        kwargs.setdefault('placeholder', '123456789')
        kwargs.setdefault('pattern', r'\d{9}')
        kwargs.setdefault('maxlength', '9')
        return super().__call__(field, **kwargs)

class SerbianMaticniInput(TextInput):
    """Custom widget for Serbian Matični broj"""
    
    def __call__(self, field, **kwargs):
        kwargs.setdefault('placeholder', '1234567890123')
        kwargs.setdefault('pattern', r'\d{13}')
        kwargs.setdefault('maxlength', '13')
        return super().__call__(field, **kwargs)

class CurrencyInput(TextInput):
    """Custom widget for currency input"""
    
    def __call__(self, field, **kwargs):
        kwargs.setdefault('placeholder', '0.00')
        kwargs.setdefault('step', '0.01')
        kwargs.setdefault('min', '0')
        return super().__call__(field, **kwargs)

class PercentageInput(TextInput):
    """Custom widget for percentage input"""
    
    def __call__(self, field, **kwargs):
        kwargs.setdefault('placeholder', '0.00%')
        kwargs.setdefault('step', '0.01')
        kwargs.setdefault('min', '0')
        kwargs.setdefault('max', '100')
        return super().__call__(field, **kwargs)

class CreditCardInput(TextInput):
    """Custom widget for credit card input"""
    
    def __call__(self, field, **kwargs):
        kwargs.setdefault('placeholder', '1234 5678 9012 3456')
        kwargs.setdefault('pattern', r'\d{4}\s?\d{4}\s?\d{4}\s?\d{4}')
        kwargs.setdefault('maxlength', '19')
        return super().__call__(field, **kwargs)

# Custom validators for WTForms

def validate_serbian_phone(form, field):
    """Validate Serbian phone number"""
    if field.data:
        try:
            validator = PhoneValidator(country_code='RS')
            validator.validate(field.data, field.name)
        except ValidationError as e:
            raise WTFormsValidationError(e.message)

def validate_serbian_pib(form, field):
    """Validate Serbian PIB"""
    if field.data:
        try:
            validator = SerbianPIBValidator()
            validator.validate(field.data, field.name)
        except ValidationError as e:
            raise WTFormsValidationError(e.message)

def validate_serbian_maticni(form, field):
    """Validate Serbian Matični broj"""
    if field.data:
        try:
            validator = SerbianMaticniBrojValidator()
            validator.validate(field.data, field.name)
        except ValidationError as e:
            raise WTFormsValidationError(e.message)

def validate_currency(form, field):
    """Validate currency amount"""
    if field.data:
        try:
            validator = CurrencyValidator()
            validator.validate(field.data, field.name)
        except ValidationError as e:
            raise WTFormsValidationError(e.message)

def validate_percentage(form, field):
    """Validate percentage"""
    if field.data:
        try:
            validator = PercentageValidator()
            validator.validate(field.data, field.name)
        except ValidationError as e:
            raise WTFormsValidationError(e.message)

def validate_credit_card(form, field):
    """Validate credit card number"""
    if field.data:
        try:
            validator = CreditCardValidator()
            validator.validate(field.data, field.name)
        except ValidationError as e:
            raise WTFormsValidationError(e.message)

def validate_postal_code(form, field):
    """Validate postal code"""
    if field.data:
        try:
            validator = PostalCodeValidator()
            validator.validate(field.data, field.name)
        except ValidationError as e:
            raise WTFormsValidationError(e.message)

# Form Classes

class UserRegistrationForm(BaseForm):
    """User registration form with comprehensive validation"""
    
    username = StringField('Username', validators=[
        DataRequired(),
        Length(min=3, max=50, message='Username must be between 3 and 50 characters')
    ])
    
    email = EmailField('Email', validators=[
        DataRequired(),
        Email(message='Please enter a valid email address')
    ])
    
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=8, message='Password must be at least 8 characters long')
    ])
    
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired()
    ])
    
    first_name = StringField('First Name', validators=[
        DataRequired(),
        Length(max=50, message='First name must be at most 50 characters')
    ])
    
    last_name = StringField('Last Name', validators=[
        DataRequired(),
        Length(max=50, message='Last name must be at most 50 characters')
    ])
    
    phone = StringField('Phone Number', widget=SerbianPhoneInput(), validators=[
        OptionalValidator(),
        validate_serbian_phone
    ])
    
    submit = SubmitField('Register')
    
    def custom_validate(self):
        """Custom validation for registration form"""
        if self.password.data != self.confirm_password.data:
            self.confirm_password.errors.append('Passwords must match')
            return False
        return True

class UserLoginForm(BaseForm):
    """User login form"""
    
    email = EmailField('Email', validators=[
        DataRequired(),
        Email(message='Please enter a valid email address')
    ])
    
    password = PasswordField('Password', validators=[
        DataRequired()
    ])
    
    remember_me = BooleanField('Remember Me')
    
    submit = SubmitField('Login')

class CompanyRegistrationForm(BaseForm):
    """Company registration form with Serbian-specific fields"""
    
    company_name = StringField('Company Name', validators=[
        DataRequired(),
        Length(max=100, message='Company name must be at most 100 characters')
    ])
    
    pib = StringField('PIB (Poreski identifikacioni broj)', 
                     widget=SerbianPIBInput(), 
                     validators=[
                         DataRequired(),
                         validate_serbian_pib
                     ])
    
    maticni_broj = StringField('Matični broj', 
                              widget=SerbianMaticniInput(), 
                              validators=[
                                  DataRequired(),
                                  validate_serbian_maticni
                              ])
    
    address = TextAreaField('Address', validators=[
        DataRequired(),
        Length(max=200, message='Address must be at most 200 characters')
    ])
    
    postal_code = StringField('Postal Code', validators=[
        DataRequired(),
        validate_postal_code
    ])
    
    city = StringField('City', validators=[
        DataRequired(),
        Length(max=50, message='City must be at most 50 characters')
    ])
    
    phone = StringField('Phone Number', 
                       widget=SerbianPhoneInput(), 
                       validators=[
                           DataRequired(),
                           validate_serbian_phone
                       ])
    
    email = EmailField('Email', validators=[
        DataRequired(),
        Email(message='Please enter a valid email address')
    ])
    
    website = URLField('Website', validators=[
        OptionalValidator(),
        URL(message='Please enter a valid URL')
    ])
    
    submit = SubmitField('Register Company')

class FinancialTransactionForm(BaseForm):
    """Financial transaction form"""
    
    description = StringField('Description', validators=[
        DataRequired(),
        Length(max=200, message='Description must be at most 200 characters')
    ])
    
    amount = DecimalField('Amount', 
                         widget=CurrencyInput(), 
                         validators=[
                             DataRequired(),
                             NumberRange(min=0, message='Amount must be positive')
                         ])
    
    transaction_type = SelectField('Transaction Type', 
                                 choices=[
                                     ('income', 'Income'),
                                     ('expense', 'Expense'),
                                     ('transfer', 'Transfer')
                                 ],
                                 validators=[DataRequired()])
    
    category = SelectField('Category', 
                          choices=[
                              ('salary', 'Salary'),
                              ('freelance', 'Freelance'),
                              ('investment', 'Investment'),
                              ('rent', 'Rent'),
                              ('utilities', 'Utilities'),
                              ('food', 'Food'),
                              ('transport', 'Transport'),
                              ('entertainment', 'Entertainment'),
                              ('other', 'Other')
                          ],
                          validators=[DataRequired()])
    
    date = DateField('Date', validators=[DataRequired()])
    
    notes = TextAreaField('Notes', validators=[
        OptionalValidator(),
        Length(max=500, message='Notes must be at most 500 characters')
    ])
    
    submit = SubmitField('Save Transaction')

class InvoiceForm(BaseForm):
    """Invoice form"""
    
    invoice_number = StringField('Invoice Number', validators=[
        DataRequired(),
        Length(max=20, message='Invoice number must be at most 20 characters')
    ])
    
    client_name = StringField('Client Name', validators=[
        DataRequired(),
        Length(max=100, message='Client name must be at most 100 characters')
    ])
    
    client_pib = StringField('Client PIB', 
                            widget=SerbianPIBInput(), 
                            validators=[
                                OptionalValidator(),
                                validate_serbian_pib
                            ])
    
    issue_date = DateField('Issue Date', validators=[DataRequired()])
    due_date = DateField('Due Date', validators=[DataRequired()])
    
    subtotal = DecimalField('Subtotal', 
                           widget=CurrencyInput(), 
                           validators=[
                               DataRequired(),
                               NumberRange(min=0, message='Subtotal must be positive')
                           ])
    
    tax_rate = DecimalField('Tax Rate (%)', 
                           widget=PercentageInput(), 
                           validators=[
                               DataRequired(),
                               NumberRange(min=0, max=100, message='Tax rate must be between 0 and 100')
                           ])
    
    total = DecimalField('Total', 
                        widget=CurrencyInput(), 
                        validators=[
                            DataRequired(),
                            NumberRange(min=0, message='Total must be positive')
                        ])
    
    description = TextAreaField('Description', validators=[
        OptionalValidator(),
        Length(max=1000, message='Description must be at most 1000 characters')
    ])
    
    submit = SubmitField('Save Invoice')
    
    def custom_validate(self):
        """Custom validation for invoice form"""
        if self.issue_date.data and self.due_date.data:
            if self.due_date.data < self.issue_date.data:
                self.due_date.errors.append('Due date must be after issue date')
                return False
        
        # Calculate total if not provided
        if self.subtotal.data and self.tax_rate.data and not self.total.data:
            tax_amount = self.subtotal.data * (self.tax_rate.data / 100)
            self.total.data = self.subtotal.data + tax_amount
        
        return True

class PaymentForm(BaseForm):
    """Payment form with credit card validation"""
    
    card_holder = StringField('Card Holder Name', validators=[
        DataRequired(),
        Length(max=100, message='Card holder name must be at most 100 characters')
    ])
    
    card_number = StringField('Card Number', 
                             widget=CreditCardInput(), 
                             validators=[
                                 DataRequired(),
                                 validate_credit_card
                             ])
    
    expiry_month = SelectField('Expiry Month', 
                              choices=[(str(i), f'{i:02d}') for i in range(1, 13)],
                              validators=[DataRequired()])
    
    expiry_year = SelectField('Expiry Year', 
                             choices=[(str(i), str(i)) for i in range(datetime.now().year, datetime.now().year + 11)],
                             validators=[DataRequired()])
    
    cvv = StringField('CVV', validators=[
        DataRequired(),
        Length(min=3, max=4, message='CVV must be 3 or 4 digits')
    ])
    
    amount = DecimalField('Amount', 
                         widget=CurrencyInput(), 
                         validators=[
                             DataRequired(),
                             NumberRange(min=0.01, message='Amount must be greater than 0')
                         ])
    
    submit = SubmitField('Process Payment')
    
    def custom_validate(self):
        """Custom validation for payment form"""
        # Check if card is expired
        if self.expiry_month.data and self.expiry_year.data:
            expiry_date = datetime(int(self.expiry_year.data), int(self.expiry_month.data), 1)
            if expiry_date < datetime.now():
                self.expiry_month.errors.append('Card has expired')
                return False
        
        return True

class ContactForm(BaseForm):
    """Contact form"""
    
    name = StringField('Name', validators=[
        DataRequired(),
        Length(max=100, message='Name must be at most 100 characters')
    ])
    
    email = EmailField('Email', validators=[
        DataRequired(),
        Email(message='Please enter a valid email address')
    ])
    
    phone = StringField('Phone Number', 
                       widget=SerbianPhoneInput(), 
                       validators=[
                           OptionalValidator(),
                           validate_serbian_phone
                       ])
    
    subject = StringField('Subject', validators=[
        DataRequired(),
        Length(max=200, message='Subject must be at most 200 characters')
    ])
    
    message = TextAreaField('Message', validators=[
        DataRequired(),
        Length(min=10, max=2000, message='Message must be between 10 and 2000 characters')
    ])
    
    submit = SubmitField('Send Message')

class FileUploadForm(BaseForm):
    """File upload form"""
    
    file = FileField('File', validators=[DataRequired()])
    
    description = StringField('Description', validators=[
        OptionalValidator(),
        Length(max=500, message='Description must be at most 500 characters')
    ])
    
    category = SelectField('Category', 
                          choices=[
                              ('invoice', 'Invoice'),
                              ('receipt', 'Receipt'),
                              ('contract', 'Contract'),
                              ('document', 'Document'),
                              ('image', 'Image'),
                              ('other', 'Other')
                          ],
                          validators=[DataRequired()])
    
    submit = SubmitField('Upload File')

class SearchForm(BaseForm):
    """Search form"""
    
    query = StringField('Search Query', validators=[
        OptionalValidator(),
        Length(max=100, message='Search query must be at most 100 characters')
    ])
    
    category = SelectField('Category', 
                          choices=[
                              ('all', 'All'),
                              ('transactions', 'Transactions'),
                              ('invoices', 'Invoices'),
                              ('clients', 'Clients'),
                              ('reports', 'Reports')
                          ],
                          default='all')
    
    date_from = DateField('From Date', validators=[OptionalValidator()])
    date_to = DateField('To Date', validators=[OptionalValidator()])
    
    amount_min = DecimalField('Min Amount', 
                             widget=CurrencyInput(), 
                             validators=[OptionalValidator()])
    
    amount_max = DecimalField('Max Amount', 
                             widget=CurrencyInput(), 
                             validators=[OptionalValidator()])
    
    submit = SubmitField('Search')
    
    def custom_validate(self):
        """Custom validation for search form"""
        if self.date_from.data and self.date_to.data:
            if self.date_to.data < self.date_from.data:
                self.date_to.errors.append('End date must be after start date')
                return False
        
        if self.amount_min.data and self.amount_max.data:
            if self.amount_max.data < self.amount_min.data:
                self.amount_max.errors.append('Maximum amount must be greater than minimum amount')
                return False
        
        return True

class SettingsForm(BaseForm):
    """User settings form"""
    
    display_name = StringField('Display Name', validators=[
        OptionalValidator(),
        Length(max=100, message='Display name must be at most 100 characters')
    ])
    
    language = SelectField('Language', 
                          choices=[
                              ('en', 'English'),
                              ('sr', 'Serbian')
                          ],
                          validators=[DataRequired()])
    
    timezone = SelectField('Timezone', 
                          choices=[
                              ('Europe/Belgrade', 'Belgrade (UTC+1)'),
                              ('UTC', 'UTC'),
                              ('Europe/London', 'London (UTC+0)'),
                              ('America/New_York', 'New York (UTC-5)')
                          ],
                          validators=[DataRequired()])
    
    currency = SelectField('Currency', 
                          choices=[
                              ('RSD', 'Serbian Dinar (RSD)'),
                              ('EUR', 'Euro (EUR)'),
                              ('USD', 'US Dollar (USD)'),
                              ('GBP', 'British Pound (GBP)')
                          ],
                          validators=[DataRequired()])
    
    notifications_email = BooleanField('Email Notifications', default=True)
    notifications_sms = BooleanField('SMS Notifications', default=False)
    notifications_push = BooleanField('Push Notifications', default=True)
    
    submit = SubmitField('Save Settings')

# Form factory for dynamic form creation

class FormFactory:
    """Factory for creating forms dynamically"""
    
    @staticmethod
    def create_form(form_type: str, **kwargs) -> BaseForm:
        """Create form based on type"""
        form_classes = {
            'user_registration': UserRegistrationForm,
            'user_login': UserLoginForm,
            'company_registration': CompanyRegistrationForm,
            'financial_transaction': FinancialTransactionForm,
            'invoice': InvoiceForm,
            'payment': PaymentForm,
            'contact': ContactForm,
            'file_upload': FileUploadForm,
            'search': SearchForm,
            'settings': SettingsForm
        }
        
        if form_type not in form_classes:
            raise ValueError(f"Unknown form type: {form_type}")
        
        return form_classes[form_type](**kwargs)
    
    @staticmethod
    def create_dynamic_form(fields: List[Dict], **kwargs) -> BaseForm:
        """Create form dynamically from field definitions"""
        class DynamicForm(BaseForm):
            pass
        
        for field_def in fields:
            field_name = field_def['name']
            field_type = field_def['type']
            field_label = field_def.get('label', field_name.title())
            field_validators = field_def.get('validators', [])
            
            # Create field based on type
            if field_type == 'string':
                field = StringField(field_label, validators=field_validators)
            elif field_type == 'email':
                field = EmailField(field_label, validators=field_validators)
            elif field_type == 'password':
                field = PasswordField(field_label, validators=field_validators)
            elif field_type == 'textarea':
                field = TextAreaField(field_label, validators=field_validators)
            elif field_type == 'select':
                choices = field_def.get('choices', [])
                field = SelectField(field_label, choices=choices, validators=field_validators)
            elif field_type == 'date':
                field = DateField(field_label, validators=field_validators)
            elif field_type == 'decimal':
                field = DecimalField(field_label, validators=field_validators)
            elif field_type == 'boolean':
                field = BooleanField(field_label, validators=field_validators)
            elif field_type == 'file':
                field = FileField(field_label, validators=field_validators)
            else:
                field = StringField(field_label, validators=field_validators)
            
            setattr(DynamicForm, field_name, field)
        
        # Add submit field
        DynamicForm.submit = SubmitField('Submit')
        
        return DynamicForm(**kwargs)
