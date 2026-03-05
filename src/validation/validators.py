"""
Comprehensive Input Validation System for ValidoAI
Supports all data types, Serbian-specific validations, and validation rules
"""

import re
import uuid
import json
import ipaddress
from datetime import datetime, date
from decimal import Decimal, InvalidOperation
from typing import Any, Dict, List, Optional, Union, Tuple
import hashlib
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ValidationError(Exception):
    """Custom validation error with detailed message"""
    def __init__(self, field: str, message: str, code: str = None):
        self.field = field
        self.message = message
        self.code = code
        super().__init__(f"{field}: {message}")

class BaseValidator:
    """Base validator class with common functionality"""
    
    def __init__(self, required: bool = True, min_length: int = None, max_length: int = None):
        self.required = required
        self.min_length = min_length
        self.max_length = max_length
    
    def validate_required(self, value: Any) -> bool:
        """Check if required field is present"""
        if self.required and (value is None or value == ""):
            raise ValidationError("field", "This field is required", "REQUIRED")
        return True
    
    def validate_length(self, value: str) -> bool:
        """Validate string length"""
        if value is None:
            return True
            
        if self.min_length and len(value) < self.min_length:
            raise ValidationError("field", f"Minimum length is {self.min_length} characters", "MIN_LENGTH")
        
        if self.max_length and len(value) > self.max_length:
            raise ValidationError("field", f"Maximum length is {self.max_length} characters", "MAX_LENGTH")
        
        return True

class StringValidator(BaseValidator):
    """String validation with pattern matching"""
    
    def __init__(self, pattern: str = None, allowed_values: List[str] = None, **kwargs):
        super().__init__(**kwargs)
        self.pattern = pattern
        self.allowed_values = allowed_values
    
    def validate(self, value: str, field_name: str = "field") -> str:
        """Validate string value"""
        self.validate_required(value)
        
        if value is None:
            return value
            
        if not isinstance(value, str):
            raise ValidationError(field_name, "Must be a string", "TYPE_ERROR")
        
        self.validate_length(value)
        
        if self.pattern and not re.match(self.pattern, value):
            raise ValidationError(field_name, f"Must match pattern: {self.pattern}", "PATTERN_ERROR")
        
        if self.allowed_values and value not in self.allowed_values:
            raise ValidationError(field_name, f"Must be one of: {', '.join(self.allowed_values)}", "ALLOWED_VALUES")
        
        return value.strip()

class IntegerValidator(BaseValidator):
    """Integer validation with range checking"""
    
    def __init__(self, min_value: int = None, max_value: int = None, **kwargs):
        super().__init__(**kwargs)
        self.min_value = min_value
        self.max_value = max_value
    
    def validate(self, value: Any, field_name: str = "field") -> int:
        """Validate integer value"""
        self.validate_required(value)
        
        if value is None:
            return value
        
        try:
            if isinstance(value, str):
                value = int(value.strip())
            elif not isinstance(value, int):
                raise ValidationError(field_name, "Must be an integer", "TYPE_ERROR")
        except ValueError:
            raise ValidationError(field_name, "Must be a valid integer", "TYPE_ERROR")
        
        if self.min_value is not None and value < self.min_value:
            raise ValidationError(field_name, f"Must be at least {self.min_value}", "MIN_VALUE")
        
        if self.max_value is not None and value > self.max_value:
            raise ValidationError(field_name, f"Must be at most {self.max_value}", "MAX_VALUE")
        
        return value

class FloatValidator(BaseValidator):
    """Float validation with range checking"""
    
    def __init__(self, min_value: float = None, max_value: float = None, **kwargs):
        super().__init__(**kwargs)
        self.min_value = min_value
        self.max_value = max_value
    
    def validate(self, value: Any, field_name: str = "field") -> float:
        """Validate float value"""
        self.validate_required(value)
        
        if value is None:
            return value
        
        try:
            if isinstance(value, str):
                value = float(value.strip())
            elif not isinstance(value, (int, float)):
                raise ValidationError(field_name, "Must be a number", "TYPE_ERROR")
        except ValueError:
            raise ValidationError(field_name, "Must be a valid number", "TYPE_ERROR")
        
        if self.min_value is not None and value < self.min_value:
            raise ValidationError(field_name, f"Must be at least {self.min_value}", "MIN_VALUE")
        
        if self.max_value is not None and value > self.max_value:
            raise ValidationError(field_name, f"Must be at most {self.max_value}", "MAX_VALUE")
        
        return value

class DecimalValidator(BaseValidator):
    """Decimal validation for currency and precise calculations"""
    
    def __init__(self, min_value: Decimal = None, max_value: Decimal = None, precision: int = 2, **kwargs):
        super().__init__(**kwargs)
        self.min_value = min_value
        self.max_value = max_value
        self.precision = precision
    
    def validate(self, value: Any, field_name: str = "field") -> Decimal:
        """Validate decimal value"""
        self.validate_required(value)
        
        if value is None:
            return value
        
        try:
            if isinstance(value, str):
                value = Decimal(value.strip())
            elif isinstance(value, (int, float)):
                value = Decimal(str(value))
            elif not isinstance(value, Decimal):
                raise ValidationError(field_name, "Must be a decimal number", "TYPE_ERROR")
        except (ValueError, InvalidOperation):
            raise ValidationError(field_name, "Must be a valid decimal number", "TYPE_ERROR")
        
        # Round to specified precision
        value = value.quantize(Decimal('0.' + '0' * self.precision))
        
        if self.min_value is not None and value < self.min_value:
            raise ValidationError(field_name, f"Must be at least {self.min_value}", "MIN_VALUE")
        
        if self.max_value is not None and value > self.max_value:
            raise ValidationError(field_name, f"Must be at most {self.max_value}", "MAX_VALUE")
        
        return value

class BooleanValidator(BaseValidator):
    """Boolean validation"""
    
    def validate(self, value: Any, field_name: str = "field") -> bool:
        """Validate boolean value"""
        self.validate_required(value)
        
        if value is None:
            return value
        
        if isinstance(value, bool):
            return value
        elif isinstance(value, str):
            value_lower = value.lower().strip()
            if value_lower in ('true', '1', 'yes', 'on'):
                return True
            elif value_lower in ('false', '0', 'no', 'off'):
                return False
            else:
                raise ValidationError(field_name, "Must be true or false", "TYPE_ERROR")
        elif isinstance(value, int):
            return bool(value)
        else:
            raise ValidationError(field_name, "Must be a boolean value", "TYPE_ERROR")

class DateValidator(BaseValidator):
    """Date validation"""
    
    def __init__(self, min_date: date = None, max_date: date = None, format: str = "%Y-%m-%d", **kwargs):
        super().__init__(**kwargs)
        self.min_date = min_date
        self.max_date = max_date
        self.format = format
    
    def validate(self, value: Any, field_name: str = "field") -> date:
        """Validate date value"""
        self.validate_required(value)
        
        if value is None:
            return value
        
        if isinstance(value, date):
            parsed_date = value
        elif isinstance(value, datetime):
            parsed_date = value.date()
        elif isinstance(value, str):
            try:
                parsed_date = datetime.strptime(value.strip(), self.format).date()
            except ValueError:
                raise ValidationError(field_name, f"Must be a valid date in format {self.format}", "FORMAT_ERROR")
        else:
            raise ValidationError(field_name, "Must be a valid date", "TYPE_ERROR")
        
        if self.min_date and parsed_date < self.min_date:
            raise ValidationError(field_name, f"Date must be on or after {self.min_date}", "MIN_DATE")
        
        if self.max_date and parsed_date > self.max_date:
            raise ValidationError(field_name, f"Date must be on or before {self.max_date}", "MAX_DATE")
        
        return parsed_date

class DateTimeValidator(BaseValidator):
    """DateTime validation"""
    
    def __init__(self, min_datetime: datetime = None, max_datetime: datetime = None, format: str = "%Y-%m-%d %H:%M:%S", **kwargs):
        super().__init__(**kwargs)
        self.min_datetime = min_datetime
        self.max_datetime = max_datetime
        self.format = format
    
    def validate(self, value: Any, field_name: str = "field") -> datetime:
        """Validate datetime value"""
        self.validate_required(value)
        
        if value is None:
            return value
        
        if isinstance(value, datetime):
            parsed_datetime = value
        elif isinstance(value, str):
            try:
                parsed_datetime = datetime.strptime(value.strip(), self.format)
            except ValueError:
                raise ValidationError(field_name, f"Must be a valid datetime in format {self.format}", "FORMAT_ERROR")
        else:
            raise ValidationError(field_name, "Must be a valid datetime", "TYPE_ERROR")
        
        if self.min_datetime and parsed_datetime < self.min_datetime:
            raise ValidationError(field_name, f"Datetime must be on or after {self.min_datetime}", "MIN_DATETIME")
        
        if self.max_datetime and parsed_datetime > self.max_datetime:
            raise ValidationError(field_name, f"Datetime must be on or before {self.max_datetime}", "MAX_DATETIME")
        
        return parsed_datetime

class EmailValidator(BaseValidator):
    """Email validation with domain checking"""
    
    def __init__(self, allowed_domains: List[str] = None, **kwargs):
        super().__init__(**kwargs)
        self.allowed_domains = allowed_domains
    
    def validate(self, value: str, field_name: str = "field") -> str:
        """Validate email address"""
        self.validate_required(value)
        
        if value is None:
            return value
        
        if not isinstance(value, str):
            raise ValidationError(field_name, "Must be a string", "TYPE_ERROR")
        
        value = value.strip().lower()
        
        # Basic email pattern
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, value):
            raise ValidationError(field_name, "Must be a valid email address", "FORMAT_ERROR")
        
        # Domain checking
        if self.allowed_domains:
            domain = value.split('@')[1]
            if domain not in self.allowed_domains:
                raise ValidationError(field_name, f"Email domain must be one of: {', '.join(self.allowed_domains)}", "DOMAIN_ERROR")
        
        return value

class URLValidator(BaseValidator):
    """URL validation with protocol checking"""
    
    def __init__(self, allowed_protocols: List[str] = None, **kwargs):
        super().__init__(**kwargs)
        self.allowed_protocols = allowed_protocols or ['http', 'https']
    
    def validate(self, value: str, field_name: str = "field") -> str:
        """Validate URL"""
        self.validate_required(value)
        
        if value is None:
            return value
        
        if not isinstance(value, str):
            raise ValidationError(field_name, "Must be a string", "TYPE_ERROR")
        
        value = value.strip()
        
        # URL pattern
        url_pattern = r'^https?://[^\s/$.?#].[^\s]*$'
        if not re.match(url_pattern, value):
            raise ValidationError(field_name, "Must be a valid URL", "FORMAT_ERROR")
        
        # Protocol checking
        protocol = value.split('://')[0]
        if protocol not in self.allowed_protocols:
            raise ValidationError(field_name, f"URL protocol must be one of: {', '.join(self.allowed_protocols)}", "PROTOCOL_ERROR")
        
        return value

class PhoneValidator(BaseValidator):
    """Phone number validation with international format support"""
    
    def __init__(self, country_code: str = None, **kwargs):
        super().__init__(**kwargs)
        self.country_code = country_code
    
    def validate(self, value: str, field_name: str = "field") -> str:
        """Validate phone number"""
        self.validate_required(value)
        
        if value is None:
            return value
        
        if not isinstance(value, str):
            raise ValidationError(field_name, "Must be a string", "TYPE_ERROR")
        
        value = re.sub(r'[\s\-\(\)]', '', value.strip())
        
        # Serbian phone number patterns
        if self.country_code == 'RS' or not self.country_code:
            # Serbian mobile: +381 6x xxx xxxx or 06x xxx xxxx
            mobile_pattern = r'^(\+381|0)6[0-9]\d{6,7}$'
            # Serbian landline: +381 1x xxx xxxx or 01x xxx xxxx
            landline_pattern = r'^(\+381|0)1[0-9]\d{6,7}$'
            
            if re.match(mobile_pattern, value) or re.match(landline_pattern, value):
                # Normalize to international format
                if value.startswith('0'):
                    value = '+381' + value[1:]
                return value
            else:
                raise ValidationError(field_name, "Must be a valid Serbian phone number", "FORMAT_ERROR")
        
        # Generic international pattern
        international_pattern = r'^\+[1-9]\d{1,14}$'
        if not re.match(international_pattern, value):
            raise ValidationError(field_name, "Must be a valid international phone number", "FORMAT_ERROR")
        
        return value

class IPValidator(BaseValidator):
    """IP address validation"""
    
    def __init__(self, ip_version: int = 4, **kwargs):
        super().__init__(**kwargs)
        self.ip_version = ip_version
    
    def validate(self, value: str, field_name: str = "field") -> str:
        """Validate IP address"""
        self.validate_required(value)
        
        if value is None:
            return value
        
        if not isinstance(value, str):
            raise ValidationError(field_name, "Must be a string", "TYPE_ERROR")
        
        value = value.strip()
        
        try:
            ip = ipaddress.ip_address(value)
            if self.ip_version == 4 and not isinstance(ip, ipaddress.IPv4Address):
                raise ValidationError(field_name, "Must be a valid IPv4 address", "IP_VERSION_ERROR")
            elif self.ip_version == 6 and not isinstance(ip, ipaddress.IPv6Address):
                raise ValidationError(field_name, "Must be a valid IPv6 address", "IP_VERSION_ERROR")
        except ValueError:
            raise ValidationError(field_name, "Must be a valid IP address", "FORMAT_ERROR")
        
        return str(ip)

class JSONValidator(BaseValidator):
    """JSON validation with schema checking"""
    
    def __init__(self, schema: Dict = None, **kwargs):
        super().__init__(**kwargs)
        self.schema = schema
    
    def validate(self, value: Any, field_name: str = "field") -> Dict:
        """Validate JSON value"""
        self.validate_required(value)
        
        if value is None:
            return value
        
        if isinstance(value, str):
            try:
                value = json.loads(value)
            except json.JSONDecodeError:
                raise ValidationError(field_name, "Must be valid JSON", "JSON_ERROR")
        elif not isinstance(value, (dict, list)):
            raise ValidationError(field_name, "Must be a valid JSON object or array", "TYPE_ERROR")
        
        # Schema validation (basic implementation)
        if self.schema:
            # Add schema validation logic here
            pass
        
        return value

class ListValidator(BaseValidator):
    """List validation"""
    
    def __init__(self, item_validator: BaseValidator = None, min_items: int = None, max_items: int = None, **kwargs):
        super().__init__(**kwargs)
        self.item_validator = item_validator
        self.min_items = min_items
        self.max_items = max_items
    
    def validate(self, value: Any, field_name: str = "field") -> List:
        """Validate list value"""
        self.validate_required(value)
        
        if value is None:
            return value
        
        if not isinstance(value, list):
            raise ValidationError(field_name, "Must be a list", "TYPE_ERROR")
        
        if self.min_items and len(value) < self.min_items:
            raise ValidationError(field_name, f"Must have at least {self.min_items} items", "MIN_ITEMS")
        
        if self.max_items and len(value) > self.max_items:
            raise ValidationError(field_name, f"Must have at most {self.max_items} items", "MAX_ITEMS")
        
        if self.item_validator:
            validated_items = []
            for i, item in enumerate(value):
                try:
                    validated_item = self.item_validator.validate(item, f"{field_name}[{i}]")
                    validated_items.append(validated_item)
                except ValidationError as e:
                    raise ValidationError(f"{field_name}[{i}]", e.message, e.code)
            return validated_items
        
        return value

class DictValidator(BaseValidator):
    """Dictionary validation"""
    
    def __init__(self, key_validator: BaseValidator = None, value_validator: BaseValidator = None, **kwargs):
        super().__init__(**kwargs)
        self.key_validator = key_validator
        self.value_validator = value_validator
    
    def validate(self, value: Any, field_name: str = "field") -> Dict:
        """Validate dictionary value"""
        self.validate_required(value)
        
        if value is None:
            return value
        
        if not isinstance(value, dict):
            raise ValidationError(field_name, "Must be a dictionary", "TYPE_ERROR")
        
        validated_dict = {}
        for key, val in value.items():
            validated_key = key
            validated_val = val
            
            if self.key_validator:
                validated_key = self.key_validator.validate(key, f"{field_name}.key")
            
            if self.value_validator:
                validated_val = self.value_validator.validate(val, f"{field_name}.{key}")
            
            validated_dict[validated_key] = validated_val
        
        return validated_dict

class FileValidator(BaseValidator):
    """File upload validation"""
    
    def __init__(self, allowed_types: List[str] = None, max_size: int = None, **kwargs):
        super().__init__(**kwargs)
        self.allowed_types = allowed_types
        self.max_size = max_size  # in bytes
    
    def validate(self, value: Any, field_name: str = "field") -> Any:
        """Validate file upload"""
        self.validate_required(value)
        
        if value is None:
            return value
        
        # Check file type
        if self.allowed_types:
            if hasattr(value, 'content_type'):
                if value.content_type not in self.allowed_types:
                    raise ValidationError(field_name, f"File type must be one of: {', '.join(self.allowed_types)}", "FILE_TYPE_ERROR")
            elif hasattr(value, 'filename'):
                ext = value.filename.split('.')[-1].lower()
                if ext not in self.allowed_types:
                    raise ValidationError(field_name, f"File extension must be one of: {', '.join(self.allowed_types)}", "FILE_TYPE_ERROR")
        
        # Check file size
        if self.max_size and hasattr(value, 'content_length'):
            if value.content_length > self.max_size:
                raise ValidationError(field_name, f"File size must be at most {self.max_size} bytes", "FILE_SIZE_ERROR")
        
        return value

class PasswordValidator(BaseValidator):
    """Password strength validation"""
    
    def __init__(self, min_length: int = 8, require_uppercase: bool = True, require_lowercase: bool = True, 
                 require_digits: bool = True, require_special: bool = True, **kwargs):
        super().__init__(**kwargs)
        self.min_length = min_length
        self.require_uppercase = require_uppercase
        self.require_lowercase = require_lowercase
        self.require_digits = require_digits
        self.require_special = require_special
    
    def validate(self, value: str, field_name: str = "field") -> str:
        """Validate password strength"""
        self.validate_required(value)
        
        if value is None:
            return value
        
        if not isinstance(value, str):
            raise ValidationError(field_name, "Must be a string", "TYPE_ERROR")
        
        if len(value) < self.min_length:
            raise ValidationError(field_name, f"Password must be at least {self.min_length} characters long", "MIN_LENGTH")
        
        if self.require_uppercase and not re.search(r'[A-Z]', value):
            raise ValidationError(field_name, "Password must contain at least one uppercase letter", "UPPERCASE_REQUIRED")
        
        if self.require_lowercase and not re.search(r'[a-z]', value):
            raise ValidationError(field_name, "Password must contain at least one lowercase letter", "LOWERCASE_REQUIRED")
        
        if self.require_digits and not re.search(r'\d', value):
            raise ValidationError(field_name, "Password must contain at least one digit", "DIGIT_REQUIRED")
        
        if self.require_special and not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
            raise ValidationError(field_name, "Password must contain at least one special character", "SPECIAL_REQUIRED")
        
        return value

class CurrencyValidator(BaseValidator):
    """Currency validation with proper decimal handling"""
    
    def __init__(self, currency_code: str = "RSD", min_amount: Decimal = None, max_amount: Decimal = None, **kwargs):
        super().__init__(**kwargs)
        self.currency_code = currency_code
        self.min_amount = min_amount
        self.max_amount = max_amount
    
    def validate(self, value: Any, field_name: str = "field") -> Decimal:
        """Validate currency amount"""
        self.validate_required(value)
        
        if value is None:
            return value
        
        try:
            if isinstance(value, str):
                # Remove currency symbols and spaces
                value = re.sub(r'[^\d.,-]', '', value)
                # Replace comma with dot for decimal
                value = value.replace(',', '.')
                amount = Decimal(value)
            elif isinstance(value, (int, float)):
                amount = Decimal(str(value))
            elif isinstance(value, Decimal):
                amount = value
            else:
                raise ValidationError(field_name, "Must be a valid currency amount", "TYPE_ERROR")
        except (ValueError, InvalidOperation):
            raise ValidationError(field_name, "Must be a valid currency amount", "FORMAT_ERROR")
        
        # Round to 2 decimal places
        amount = amount.quantize(Decimal('0.01'))
        
        if self.min_amount and amount < self.min_amount:
            raise ValidationError(field_name, f"Amount must be at least {self.min_amount} {self.currency_code}", "MIN_AMOUNT")
        
        if self.max_amount and amount > self.max_amount:
            raise ValidationError(field_name, f"Amount must be at most {self.max_amount} {self.currency_code}", "MAX_AMOUNT")
        
        return amount

class PercentageValidator(BaseValidator):
    """Percentage validation"""
    
    def __init__(self, min_percentage: float = 0.0, max_percentage: float = 100.0, **kwargs):
        super().__init__(**kwargs)
        self.min_percentage = min_percentage
        self.max_percentage = max_percentage
    
    def validate(self, value: Any, field_name: str = "field") -> float:
        """Validate percentage value"""
        self.validate_required(value)
        
        if value is None:
            return value
        
        try:
            if isinstance(value, str):
                # Remove % symbol
                value = value.replace('%', '').strip()
                percentage = float(value)
            elif isinstance(value, (int, float)):
                percentage = float(value)
            else:
                raise ValidationError(field_name, "Must be a valid percentage", "TYPE_ERROR")
        except ValueError:
            raise ValidationError(field_name, "Must be a valid percentage", "FORMAT_ERROR")
        
        if percentage < self.min_percentage:
            raise ValidationError(field_name, f"Percentage must be at least {self.min_percentage}%", "MIN_PERCENTAGE")
        
        if percentage > self.max_percentage:
            raise ValidationError(field_name, f"Percentage must be at most {self.max_percentage}%", "MAX_PERCENTAGE")
        
        return percentage

class UUIDValidator(BaseValidator):
    """UUID validation"""
    
    def validate(self, value: Any, field_name: str = "field") -> str:
        """Validate UUID"""
        self.validate_required(value)
        
        if value is None:
            return value
        
        if isinstance(value, str):
            try:
                uuid.UUID(value)
                return value
            except ValueError:
                raise ValidationError(field_name, "Must be a valid UUID", "FORMAT_ERROR")
        else:
            raise ValidationError(field_name, "Must be a valid UUID string", "TYPE_ERROR")

class ColorValidator(BaseValidator):
    """Color validation (hex, rgb, rgba)"""
    
    def validate(self, value: str, field_name: str = "field") -> str:
        """Validate color value"""
        self.validate_required(value)
        
        if value is None:
            return value
        
        if not isinstance(value, str):
            raise ValidationError(field_name, "Must be a string", "TYPE_ERROR")
        
        value = value.strip()
        
        # Hex color pattern
        hex_pattern = r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$'
        # RGB pattern
        rgb_pattern = r'^rgb\(\s*\d+\s*,\s*\d+\s*,\s*\d+\s*\)$'
        # RGBA pattern
        rgba_pattern = r'^rgba\(\s*\d+\s*,\s*\d+\s*,\s*\d+\s*,\s*[0-9.]+\s*\)$'
        
        if not (re.match(hex_pattern, value) or re.match(rgb_pattern, value) or re.match(rgba_pattern, value)):
            raise ValidationError(field_name, "Must be a valid color (hex, rgb, or rgba)", "FORMAT_ERROR")
        
        return value

class CreditCardValidator(BaseValidator):
    """Credit card validation using Luhn algorithm"""
    
    def validate(self, value: str, field_name: str = "field") -> str:
        """Validate credit card number"""
        self.validate_required(value)
        
        if value is None:
            return value
        
        if not isinstance(value, str):
            raise ValidationError(field_name, "Must be a string", "TYPE_ERROR")
        
        # Remove spaces and dashes
        value = re.sub(r'[\s\-]', '', value.strip())
        
        # Check if it's all digits
        if not value.isdigit():
            raise ValidationError(field_name, "Must contain only digits", "FORMAT_ERROR")
        
        # Check length (13-19 digits)
        if len(value) < 13 or len(value) > 19:
            raise ValidationError(field_name, "Must be 13-19 digits long", "LENGTH_ERROR")
        
        # Luhn algorithm
        def luhn_checksum(card_number):
            def digits_of(n):
                return [int(d) for d in str(n)]
            
            digits = digits_of(card_number)
            odd_digits = digits[-1::-2]
            even_digits = digits[-2::-2]
            checksum = sum(odd_digits)
            for d in even_digits:
                checksum += sum(digits_of(d * 2))
            return checksum % 10
        
        if luhn_checksum(value) != 0:
            raise ValidationError(field_name, "Invalid credit card number", "CHECKSUM_ERROR")
        
        return value

class PostalCodeValidator(BaseValidator):
    """Postal code validation"""
    
    def __init__(self, country: str = "RS", **kwargs):
        super().__init__(**kwargs)
        self.country = country
    
    def validate(self, value: str, field_name: str = "field") -> str:
        """Validate postal code"""
        self.validate_required(value)
        
        if value is None:
            return value
        
        if not isinstance(value, str):
            raise ValidationError(field_name, "Must be a string", "TYPE_ERROR")
        
        value = value.strip()
        
        if self.country == "RS":
            # Serbian postal codes: 5 digits
            postal_pattern = r'^\d{5}$'
            if not re.match(postal_pattern, value):
                raise ValidationError(field_name, "Must be a 5-digit postal code", "FORMAT_ERROR")
        else:
            # Generic postal code pattern
            postal_pattern = r'^[A-Z0-9\s\-]{3,10}$'
            if not re.match(postal_pattern, value):
                raise ValidationError(field_name, "Must be a valid postal code", "FORMAT_ERROR")
        
        return value

class SerbianPIBValidator(BaseValidator):
    """Serbian PIB (Poreski identifikacioni broj) validation with checksum"""
    
    def validate(self, value: str, field_name: str = "field") -> str:
        """Validate Serbian PIB"""
        self.validate_required(value)
        
        if value is None:
            return value
        
        if not isinstance(value, str):
            raise ValidationError(field_name, "Must be a string", "TYPE_ERROR")
        
        # Remove spaces and dashes
        value = re.sub(r'[\s\-]', '', value.strip())
        
        # Check if it's 9 digits
        if not value.isdigit() or len(value) != 9:
            raise ValidationError(field_name, "PIB must be exactly 9 digits", "FORMAT_ERROR")
        
        # Checksum validation
        weights = [8, 7, 6, 5, 4, 3, 2]
        checksum = 0
        
        for i in range(7):
            checksum += int(value[i]) * weights[i]
        
        checksum = 11 - (checksum % 11)
        if checksum == 11:
            checksum = 0
        elif checksum == 10:
            checksum = 1
        
        if checksum != int(value[7]):
            raise ValidationError(field_name, "Invalid PIB checksum", "CHECKSUM_ERROR")
        
        return value

class SerbianMaticniBrojValidator(BaseValidator):
    """Serbian Matični broj validation with checksum"""
    
    def validate(self, value: str, field_name: str = "field") -> str:
        """Validate Serbian Matični broj"""
        self.validate_required(value)
        
        if value is None:
            return value
        
        if not isinstance(value, str):
            raise ValidationError(field_name, "Must be a string", "TYPE_ERROR")
        
        # Remove spaces and dashes
        value = re.sub(r'[\s\-]', '', value.strip())
        
        # Check if it's 13 digits
        if not value.isdigit() or len(value) != 13:
            raise ValidationError(field_name, "Matični broj must be exactly 13 digits", "FORMAT_ERROR")
        
        # Checksum validation
        weights = [7, 6, 5, 4, 3, 2, 7, 6, 5, 4, 3, 2]
        checksum = 0
        
        for i in range(12):
            checksum += int(value[i]) * weights[i]
        
        checksum = 11 - (checksum % 11)
        if checksum == 11:
            checksum = 0
        elif checksum == 10:
            checksum = 1
        
        if checksum != int(value[12]):
            raise ValidationError(field_name, "Invalid Matični broj checksum", "CHECKSUM_ERROR")
        
        return value

# Validation factory
class ValidatorFactory:
    """Factory for creating validators"""
    
    @staticmethod
    def create_validator(data_type: str, **kwargs) -> BaseValidator:
        """Create validator based on data type"""
        validators = {
            'string': StringValidator,
            'integer': IntegerValidator,
            'float': FloatValidator,
            'decimal': DecimalValidator,
            'boolean': BooleanValidator,
            'date': DateValidator,
            'datetime': DateTimeValidator,
            'email': EmailValidator,
            'url': URLValidator,
            'phone': PhoneValidator,
            'ip': IPValidator,
            'json': JSONValidator,
            'list': ListValidator,
            'dict': DictValidator,
            'file': FileValidator,
            'password': PasswordValidator,
            'currency': CurrencyValidator,
            'percentage': PercentageValidator,
            'uuid': UUIDValidator,
            'color': ColorValidator,
            'credit_card': CreditCardValidator,
            'postal_code': PostalCodeValidator,
            'serbian_pib': SerbianPIBValidator,
            'serbian_maticni': SerbianMaticniBrojValidator,
        }
        
        if data_type not in validators:
            raise ValueError(f"Unknown data type: {data_type}")
        
        return validators[data_type](**kwargs)

# Validation manager
class ValidationManager:
    """Manages validation rules and validation execution"""
    
    def __init__(self):
        self.validators = {}
        self.error_messages = {
            'en': {
                'REQUIRED': 'This field is required',
                'TYPE_ERROR': 'Invalid data type',
                'FORMAT_ERROR': 'Invalid format',
                'MIN_LENGTH': 'Minimum length is {min_length} characters',
                'MAX_LENGTH': 'Maximum length is {max_length} characters',
                'MIN_VALUE': 'Must be at least {min_value}',
                'MAX_VALUE': 'Must be at most {max_value}',
                'PATTERN_ERROR': 'Must match pattern: {pattern}',
                'ALLOWED_VALUES': 'Must be one of: {allowed_values}',
                'DOMAIN_ERROR': 'Email domain must be one of: {allowed_domains}',
                'PROTOCOL_ERROR': 'URL protocol must be one of: {allowed_protocols}',
                'FILE_TYPE_ERROR': 'File type must be one of: {allowed_types}',
                'FILE_SIZE_ERROR': 'File size must be at most {max_size} bytes',
                'UPPERCASE_REQUIRED': 'Password must contain at least one uppercase letter',
                'LOWERCASE_REQUIRED': 'Password must contain at least one lowercase letter',
                'DIGIT_REQUIRED': 'Password must contain at least one digit',
                'SPECIAL_REQUIRED': 'Password must contain at least one special character',
                'CHECKSUM_ERROR': 'Invalid checksum',
                'IP_VERSION_ERROR': 'Invalid IP version',
                'JSON_ERROR': 'Invalid JSON',
                'MIN_ITEMS': 'Must have at least {min_items} items',
                'MAX_ITEMS': 'Must have at most {max_items} items',
                'MIN_DATE': 'Date must be on or after {min_date}',
                'MAX_DATE': 'Date must be on or before {max_date}',
                'MIN_DATETIME': 'Datetime must be on or after {min_datetime}',
                'MAX_DATETIME': 'Datetime must be on or before {max_datetime}',
                'MIN_AMOUNT': 'Amount must be at least {min_amount} {currency_code}',
                'MAX_AMOUNT': 'Amount must be at most {max_amount} {currency_code}',
                'MIN_PERCENTAGE': 'Percentage must be at least {min_percentage}%',
                'MAX_PERCENTAGE': 'Percentage must be at most {max_percentage}%',
                'LENGTH_ERROR': 'Must be {length} digits long',
            },
            'sr': {
                'REQUIRED': 'Ovo polje je obavezno',
                'TYPE_ERROR': 'Neispravan tip podataka',
                'FORMAT_ERROR': 'Neispravan format',
                'MIN_LENGTH': 'Minimalna dužina je {min_length} karaktera',
                'MAX_LENGTH': 'Maksimalna dužina je {max_length} karaktera',
                'MIN_VALUE': 'Mora biti najmanje {min_value}',
                'MAX_VALUE': 'Mora biti najviše {max_value}',
                'PATTERN_ERROR': 'Mora odgovarati obrascu: {pattern}',
                'ALLOWED_VALUES': 'Mora biti jedan od: {allowed_values}',
                'DOMAIN_ERROR': 'Domen email-a mora biti jedan od: {allowed_domains}',
                'PROTOCOL_ERROR': 'URL protokol mora biti jedan od: {allowed_protocols}',
                'FILE_TYPE_ERROR': 'Tip fajla mora biti jedan od: {allowed_types}',
                'FILE_SIZE_ERROR': 'Veličina fajla mora biti najviše {max_size} bajtova',
                'UPPERCASE_REQUIRED': 'Lozinka mora sadržati najmanje jedno veliko slovo',
                'LOWERCASE_REQUIRED': 'Lozinka mora sadržati najmanje jedno malo slovo',
                'DIGIT_REQUIRED': 'Lozinka mora sadržati najmanje jednu cifru',
                'SPECIAL_REQUIRED': 'Lozinka mora sadržati najmanje jedan specijalni karakter',
                'CHECKSUM_ERROR': 'Neispravan kontrolni zbir',
                'IP_VERSION_ERROR': 'Neispravna IP verzija',
                'JSON_ERROR': 'Neispravan JSON',
                'MIN_ITEMS': 'Mora imati najmanje {min_items} stavki',
                'MAX_ITEMS': 'Mora imati najviše {max_items} stavki',
                'MIN_DATE': 'Datum mora biti {min_date} ili kasnije',
                'MAX_DATE': 'Datum mora biti {max_date} ili ranije',
                'MIN_DATETIME': 'Datum i vreme mora biti {min_datetime} ili kasnije',
                'MAX_DATETIME': 'Datum i vreme mora biti {max_datetime} ili ranije',
                'MIN_AMOUNT': 'Iznos mora biti najmanje {min_amount} {currency_code}',
                'MAX_AMOUNT': 'Iznos mora biti najviše {max_amount} {currency_code}',
                'MIN_PERCENTAGE': 'Procenat mora biti najmanje {min_percentage}%',
                'MAX_PERCENTAGE': 'Procenat mora biti najviše {max_percentage}%',
                'LENGTH_ERROR': 'Mora biti {length} cifara',
            }
        }
    
    def add_validator(self, field_name: str, validator: BaseValidator):
        """Add validator for a field"""
        self.validators[field_name] = validator
    
    def validate_data(self, data: Dict, language: str = 'en') -> Tuple[Dict, List[Dict]]:
        """Validate data and return validated data and errors"""
        validated_data = {}
        errors = []
        
        for field_name, validator in self.validators.items():
            try:
                value = data.get(field_name)
                validated_value = validator.validate(value, field_name)
                validated_data[field_name] = validated_value
            except ValidationError as e:
                error_message = self.get_error_message(e.code, language, e.field)
                errors.append({
                    'field': e.field,
                    'message': error_message,
                    'code': e.code
                })
                logger.warning(f"Validation error for field {e.field}: {e.message}")
        
        return validated_data, errors
    
    def get_error_message(self, code: str, language: str, field: str) -> str:
        """Get localized error message"""
        if language not in self.error_messages:
            language = 'en'
        
        messages = self.error_messages[language]
        if code in messages:
            return messages[code].format(field=field)
        
        return f"Validation error for {field}"
    
    def validate_single_field(self, field_name: str, value: Any, language: str = 'en') -> Tuple[Any, Optional[Dict]]:
        """Validate a single field"""
        if field_name not in self.validators:
            return value, None
        
        try:
            validated_value = self.validators[field_name].validate(value, field_name)
            return validated_value, None
        except ValidationError as e:
            error_message = self.get_error_message(e.code, language, e.field)
            error = {
                'field': e.field,
                'message': error_message,
                'code': e.code
            }
            logger.warning(f"Validation error for field {e.field}: {e.message}")
            return value, error
