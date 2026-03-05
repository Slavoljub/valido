"""
UUID Utilities for ValidoAI Application
Provides UUID generation, validation, and formatting utilities
"""

import uuid
import re
from typing import Optional, Union
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class UUIDUtils:
    """Utility class for UUID operations"""
    
    @staticmethod
    def generate_uuid() -> str:
        """Generate a new UUID version 4"""
        return str(uuid.uuid4())
    
    @staticmethod
    def generate_uuid_v1() -> str:
        """Generate a new UUID version 1 (time-based)"""
        return str(uuid.uuid1())
    
    @staticmethod
    def generate_uuid_v3(name: str, namespace: Optional[uuid.UUID] = None) -> str:
        """Generate a new UUID version 3 (name-based with MD5)"""
        if namespace is None:
            namespace = uuid.NAMESPACE_DNS
        return str(uuid.uuid3(namespace, name))
    
    @staticmethod
    def generate_uuid_v5(name: str, namespace: Optional[uuid.UUID] = None) -> str:
        """Generate a new UUID version 5 (name-based with SHA-1)"""
        if namespace is None:
            namespace = uuid.NAMESPACE_DNS
        return str(uuid.uuid5(namespace, name))
    
    @staticmethod
    def is_valid_uuid(uuid_string: str) -> bool:
        """Check if a string is a valid UUID"""
        try:
            uuid.UUID(uuid_string)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def format_uuid(uuid_string: str, format_type: str = 'standard') -> str:
        """Format UUID string in different formats"""
        if not UUIDUtils.is_valid_uuid(uuid_string):
            raise ValueError(f"Invalid UUID: {uuid_string}")
        
        uuid_obj = uuid.UUID(uuid_string)
        
        if format_type == 'standard':
            return str(uuid_obj)
        elif format_type == 'compact':
            return uuid_obj.hex
        elif format_type == 'urn':
            return f"urn:uuid:{uuid_obj}"
        elif format_type == 'braces':
            return f"{{{uuid_obj}}}"
        elif format_type == 'parentheses':
            return f"({uuid_obj})"
        else:
            return str(uuid_obj)
    
    @staticmethod
    def normalize_uuid(uuid_string: str) -> str:
        """Normalize UUID string to standard format"""
        if not UUIDUtils.is_valid_uuid(uuid_string):
            raise ValueError(f"Invalid UUID: {uuid_string}")
        
        return str(uuid.UUID(uuid_string))
    
    @staticmethod
    def extract_uuid_from_string(text: str) -> Optional[str]:
        """Extract UUID from a string containing other text"""
        uuid_pattern = re.compile(
            r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}',
            re.IGNORECASE
        )
        match = uuid_pattern.search(text)
        return match.group() if match else None
    
    @staticmethod
    def generate_short_uuid(length: int = 8) -> str:
        """Generate a short UUID-like string"""
        if length < 1 or length > 32:
            raise ValueError("Length must be between 1 and 32")
        
        full_uuid = uuid.uuid4().hex
        return full_uuid[:length]
    
    @staticmethod
    def generate_uuid_with_prefix(prefix: str) -> str:
        """Generate UUID with a custom prefix"""
        return f"{prefix}_{uuid.uuid4().hex[:8]}"
    
    @staticmethod
    def generate_uuid_with_timestamp() -> str:
        """Generate UUID with embedded timestamp"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{timestamp}_{uuid.uuid4().hex[:8]}"

class UUIDGenerator:
    """Advanced UUID generator with different strategies"""
    
    def __init__(self, strategy: str = 'v4'):
        self.strategy = strategy
    
    def generate(self, **kwargs) -> str:
        """Generate UUID based on strategy"""
        if self.strategy == 'v1':
            return UUIDUtils.generate_uuid_v1()
        elif self.strategy == 'v3':
            name = kwargs.get('name', 'default')
            namespace = kwargs.get('namespace')
            return UUIDUtils.generate_uuid_v3(name, namespace)
        elif self.strategy == 'v4':
            return UUIDUtils.generate_uuid()
        elif self.strategy == 'v5':
            name = kwargs.get('name', 'default')
            namespace = kwargs.get('namespace')
            return UUIDUtils.generate_uuid_v5(name, namespace)
        elif self.strategy == 'short':
            length = kwargs.get('length', 8)
            return UUIDUtils.generate_short_uuid(length)
        elif self.strategy == 'prefixed':
            prefix = kwargs.get('prefix', 'id')
            return UUIDUtils.generate_uuid_with_prefix(prefix)
        elif self.strategy == 'timestamped':
            return UUIDUtils.generate_uuid_with_timestamp()
        else:
            return UUIDUtils.generate_uuid()

class UUIDValidator:
    """UUID validation utilities"""
    
    @staticmethod
    def validate_uuid_list(uuid_list: list) -> tuple[list, list]:
        """Validate a list of UUIDs and return valid and invalid ones"""
        valid_uuids = []
        invalid_uuids = []
        
        for uuid_str in uuid_list:
            if UUIDUtils.is_valid_uuid(uuid_str):
                valid_uuids.append(uuid_str)
            else:
                invalid_uuids.append(uuid_str)
        
        return valid_uuids, invalid_uuids
    
    @staticmethod
    def validate_uuid_format(uuid_string: str, format_type: str = 'standard') -> bool:
        """Validate UUID format"""
        if not UUIDUtils.is_valid_uuid(uuid_string):
            return False
        
        try:
            formatted = UUIDUtils.format_uuid(uuid_string, format_type)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def sanitize_uuid(uuid_string: str) -> Optional[str]:
        """Sanitize and normalize UUID string"""
        try:
            # Remove common prefixes and suffixes
            cleaned = re.sub(r'^(urn:uuid:|uuid:|id:)?', '', uuid_string)
            cleaned = re.sub(r'[{}()\s]', '', cleaned)
            
            # Try to normalize
            return UUIDUtils.normalize_uuid(cleaned)
        except ValueError:
            return None

# Global UUID generator instances
uuid_generator_v4 = UUIDGenerator('v4')
uuid_generator_v1 = UUIDGenerator('v1')
uuid_generator_short = UUIDGenerator('short')
uuid_generator_prefixed = UUIDGenerator('prefixed')
uuid_generator_timestamped = UUIDGenerator('timestamped')

# Convenience functions
def generate_uuid() -> str:
    """Generate a new UUID version 4"""
    return uuid_generator_v4.generate()

def generate_short_uuid(length: int = 8) -> str:
    """Generate a short UUID-like string"""
    return uuid_generator_short.generate(length=length)

def generate_prefixed_uuid(prefix: str) -> str:
    """Generate UUID with a custom prefix"""
    return uuid_generator_prefixed.generate(prefix=prefix)

def generate_timestamped_uuid() -> str:
    """Generate UUID with embedded timestamp"""
    return uuid_generator_timestamped.generate()

def is_valid_uuid(uuid_string: str) -> bool:
    """Check if a string is a valid UUID"""
    return UUIDUtils.is_valid_uuid(uuid_string)

def format_uuid(uuid_string: str, format_type: str = 'standard') -> str:
    """Format UUID string in different formats"""
    return UUIDUtils.format_uuid(uuid_string, format_type)

def normalize_uuid(uuid_string: str) -> str:
    """Normalize UUID string to standard format"""
    return UUIDUtils.normalize_uuid(uuid_string)
