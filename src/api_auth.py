"""
API Authentication and Key Management System
Handles API keys, tokens, versioning, and authentication for RESTful endpoints
"""

import os
import secrets
import hashlib
import time
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from pathlib import Path
from functools import wraps
from flask import request, jsonify, current_app, g
# Try to import JWT, but provide fallback if not available
try:
    import jwt
    JWT_AVAILABLE = True
except ImportError:
    JWT_AVAILABLE = False
    jwt = None
    logging.warning("PyJWT not available - JWT authentication features will be disabled")

from src.config.unified_config import config

logger = logging.getLogger(__name__)

@dataclass
class APIKey:
    """API Key data structure"""
    key_id: str
    key_hash: str
    name: str
    description: str
    user_id: Optional[str]
    permissions: List[str]
    version: str
    is_active: bool
    created_at: datetime
    expires_at: Optional[datetime]
    last_used: Optional[datetime]
    usage_count: int

@dataclass
class APIToken:
    """API Token data structure"""
    token_id: str
    token_hash: str
    key_id: str
    user_id: Optional[str]
    permissions: List[str]
    version: str
    is_active: bool
    created_at: datetime
    expires_at: datetime
    last_used: Optional[datetime]

class APIKeyManager:
    """
    Manages API keys and tokens for authentication
    """
    
    def __init__(self, storage_file: str = "api_keys.json"):
        self.storage_file = Path(storage_file)
        self.keys: Dict[str, APIKey] = {}
        self.tokens: Dict[str, APIToken] = {}
        self.load_keys()
    
    def load_keys(self):
        """Load API keys from storage"""
        if self.storage_file.exists():
            try:
                with open(self.storage_file, 'r') as f:
                    data = json.load(f)
                    
                # Load API keys
                for key_data in data.get('keys', []):
                    key = APIKey(
                        key_id=key_data['key_id'],
                        key_hash=key_data['key_hash'],
                        name=key_data['name'],
                        description=key_data['description'],
                        user_id=key_data.get('user_id'),
                        permissions=key_data['permissions'],
                        version=key_data['version'],
                        is_active=key_data['is_active'],
                        created_at=datetime.fromisoformat(key_data['created_at']),
                        expires_at=datetime.fromisoformat(key_data['expires_at']) if key_data.get('expires_at') else None,
                        last_used=datetime.fromisoformat(key_data['last_used']) if key_data.get('last_used') else None,
                        usage_count=key_data['usage_count']
                    )
                    self.keys[key.key_id] = key
                
                # Load API tokens
                for token_data in data.get('tokens', []):
                    token = APIToken(
                        token_id=token_data['token_id'],
                        token_hash=token_data['token_hash'],
                        key_id=token_data['key_id'],
                        user_id=token_data.get('user_id'),
                        permissions=token_data['permissions'],
                        version=token_data['version'],
                        is_active=token_data['is_active'],
                        created_at=datetime.fromisoformat(token_data['created_at']),
                        expires_at=datetime.fromisoformat(token_data['expires_at']),
                        last_used=datetime.fromisoformat(token_data['last_used']) if token_data.get('last_used') else None
                    )
                    self.tokens[token.token_id] = token
                    
            except Exception as e:
                logger.error(f"Error loading API keys: {e}")
    
    def save_keys(self):
        """Save API keys to storage"""
        try:
            data = {
                'keys': [asdict(key) for key in self.keys.values()],
                'tokens': [asdict(token) for token in self.tokens.values()]
            }
            
            # Convert datetime objects to ISO format
            for key_data in data['keys']:
                key_data['created_at'] = key_data['created_at'].isoformat()
                if key_data.get('expires_at'):
                    key_data['expires_at'] = key_data['expires_at'].isoformat()
                if key_data.get('last_used'):
                    key_data['last_used'] = key_data['last_used'].isoformat()
            
            for token_data in data['tokens']:
                token_data['created_at'] = token_data['created_at'].isoformat()
                token_data['expires_at'] = token_data['expires_at'].isoformat()
                if token_data.get('last_used'):
                    token_data['last_used'] = token_data['last_used'].isoformat()
            
            with open(self.storage_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error saving API keys: {e}")
    
    def generate_api_key(self, name: str, description: str = "", user_id: Optional[str] = None, 
                        permissions: List[str] = None, version: str = "v1") -> Tuple[str, APIKey]:
        """Generate a new API key"""
        if permissions is None:
            permissions = ["read", "write"]
        
        # Generate key ID and secret
        key_id = secrets.token_urlsafe(16)
        key_secret = secrets.token_urlsafe(config.api.key_length)
        key_hash = hashlib.sha256(key_secret.encode()).hexdigest()
        
        # Calculate expiration
        expires_at = datetime.now() + timedelta(days=config.api.key_expires_days)
        
        # Create API key object
        api_key = APIKey(
            key_id=key_id,
            key_hash=key_hash,
            name=name,
            description=description,
            user_id=user_id,
            permissions=permissions,
            version=version,
            is_active=True,
            created_at=datetime.now(),
            expires_at=expires_at,
            last_used=None,
            usage_count=0
        )
        
        self.keys[key_id] = api_key
        self.save_keys()
        
        # Return the full key (key_id:key_secret) and the API key object
        full_key = f"{key_id}:{key_secret}"
        return full_key, api_key
    
    def generate_api_token(self, key_id: str, user_id: Optional[str] = None, 
                          permissions: List[str] = None, version: str = "v1") -> Tuple[str, APIToken]:
        """Generate a new API token"""
        if key_id not in self.keys:
            raise ValueError(f"API key {key_id} not found")
        
        if permissions is None:
            permissions = self.keys[key_id].permissions
        
        # Generate token ID and secret
        token_id = secrets.token_urlsafe(16)
        token_secret = secrets.token_urlsafe(config.api.token_length)
        token_hash = hashlib.sha256(token_secret.encode()).hexdigest()
        
        # Calculate expiration
        expires_at = datetime.now() + timedelta(hours=config.api.token_expires_hours)
        
        # Create API token object
        api_token = APIToken(
            token_id=token_id,
            token_hash=token_hash,
            key_id=key_id,
            user_id=user_id,
            permissions=permissions,
            version=version,
            is_active=True,
            created_at=datetime.now(),
            expires_at=expires_at,
            last_used=None
        )
        
        self.tokens[token_id] = api_token
        self.save_keys()
        
        # Return the full token (token_id:token_secret) and the API token object
        full_token = f"{token_id}:{token_secret}"
        return full_token, api_token
    
    def validate_api_key(self, api_key: str) -> Optional[APIKey]:
        """Validate an API key"""
        try:
            key_id, key_secret = api_key.split(':', 1)
        except ValueError:
            return None
        
        if key_id not in self.keys:
            return None
        
        stored_key = self.keys[key_id]
        
        # Check if key is active
        if not stored_key.is_active:
            return None
        
        # Check if key has expired
        if stored_key.expires_at and datetime.now() > stored_key.expires_at:
            return None
        
        # Validate key secret
        key_hash = hashlib.sha256(key_secret.encode()).hexdigest()
        if key_hash != stored_key.key_hash:
            return None
        
        # Update usage statistics
        stored_key.last_used = datetime.now()
        stored_key.usage_count += 1
        self.save_keys()
        
        return stored_key
    
    def validate_api_token(self, api_token: str) -> Optional[APIToken]:
        """Validate an API token"""
        try:
            token_id, token_secret = api_token.split(':', 1)
        except ValueError:
            return None
        
        if token_id not in self.tokens:
            return None
        
        stored_token = self.tokens[token_id]
        
        # Check if token is active
        if not stored_token.is_active:
            return None
        
        # Check if token has expired
        if datetime.now() > stored_token.expires_at:
            return None
        
        # Validate token secret
        token_hash = hashlib.sha256(token_secret.encode()).hexdigest()
        if token_hash != stored_token.token_hash:
            return None
        
        # Update usage statistics
        stored_token.last_used = datetime.now()
        self.save_keys()
        
        return stored_token
    
    def revoke_api_key(self, key_id: str) -> bool:
        """Revoke an API key"""
        if key_id in self.keys:
            self.keys[key_id].is_active = False
            self.save_keys()
            return True
        return False
    
    def revoke_api_token(self, token_id: str) -> bool:
        """Revoke an API token"""
        if token_id in self.tokens:
            self.tokens[token_id].is_active = False
            self.save_keys()
            return True
        return False
    
    def get_api_keys(self, user_id: Optional[str] = None) -> List[APIKey]:
        """Get API keys for a user"""
        if user_id:
            return [key for key in self.keys.values() if key.user_id == user_id]
        return list(self.keys.values())
    
    def get_api_tokens(self, key_id: Optional[str] = None) -> List[APIToken]:
        """Get API tokens for a key"""
        if key_id:
            return [token for token in self.tokens.values() if token.key_id == key_id]
        return list(self.tokens.values())

# Global API key manager instance
api_key_manager = APIKeyManager()

def get_api_key_manager() -> APIKeyManager:
    """Get the global API key manager instance"""
    return api_key_manager

def require_api_auth(f):
    """Decorator to require API authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not config.api.require_authentication:
            return f(*args, **kwargs)
        
        # Get API key from header
        api_key = request.headers.get('X-API-Key')
        api_token = request.headers.get('X-API-Token')
        api_version = request.headers.get('X-API-Version', config.api.default_version)
        
        # Validate API version
        if api_version not in config.api.supported_versions:
            return jsonify({
                'error': 'Unsupported API version',
                'supported_versions': config.api.supported_versions
            }), 400
        
        # Validate API key or token
        authenticated_key = None
        authenticated_token = None
        
        if api_key:
            authenticated_key = api_key_manager.validate_api_key(api_key)
        
        if api_token:
            authenticated_token = api_key_manager.validate_api_token(api_token)
        
        if not authenticated_key and not authenticated_token:
            return jsonify({
                'error': 'Invalid or missing API authentication',
                'message': 'Please provide a valid API key or token'
            }), 401
        
        # Store authentication info in Flask g
        g.api_key = authenticated_key
        g.api_token = authenticated_token
        g.api_version = api_version
        
        return f(*args, **kwargs)
    
    return decorated_function

def require_permission(permission: str):
    """Decorator to require specific permission"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not config.api.require_authentication:
                return f(*args, **kwargs)
            
            # Check if user has required permission
            has_permission = False
            
            if hasattr(g, 'api_key') and g.api_key:
                has_permission = permission in g.api_key.permissions
            
            if hasattr(g, 'api_token') and g.api_token:
                has_permission = permission in g.api_token.permissions
            
            if not has_permission:
                return jsonify({
                    'error': 'Insufficient permissions',
                    'required_permission': permission
                }), 403
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator

def rate_limit(f):
    """Decorator to implement rate limiting"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not config.api.enable_rate_limiting:
            return f(*args, **kwargs)
        
        # Get client identifier
        client_id = None
        if hasattr(g, 'api_key') and g.api_key:
            client_id = g.api_key.key_id
        elif hasattr(g, 'api_token') and g.api_token:
            client_id = g.api_token.token_id
        else:
            client_id = request.remote_addr
        
        # TODO: Implement rate limiting logic with Redis
        # For now, just pass through
        return f(*args, **kwargs)
    
    return decorated_function

def api_response(data: Any = None, message: str = "Success", status_code: int = 200, 
                version: str = None) -> Tuple[Any, int]:
    """Generate standardized API response"""
    if version is None:
        version = getattr(g, 'api_version', config.api.default_version)
    
    response = {
        'success': 200 <= status_code < 300,
        'message': message,
        'version': version,
        'timestamp': datetime.now().isoformat(),
        'data': data
    }
    
    return jsonify(response), status_code

def api_error(message: str, status_code: int = 400, error_code: str = None, 
              version: str = None) -> Tuple[Any, int]:
    """Generate standardized API error response"""
    if version is None:
        version = getattr(g, 'api_version', config.api.default_version)
    
    response = {
        'success': False,
        'error': {
            'message': message,
            'code': error_code,
            'status_code': status_code
        },
        'version': version,
        'timestamp': datetime.now().isoformat()
    }
    
    return jsonify(response), status_code
