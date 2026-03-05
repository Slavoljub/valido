"""
Integration models for ValidoAI application
Supports banks, eCommerce platforms, financial APIs, and other data sources
"""

from datetime import datetime
from enum import Enum
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON, ForeignKey, Float
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

from ..extensions import db

Base = declarative_base()

class IntegrationType(Enum):
    """Integration types enumeration"""
    BANK = "bank"
    ECOMMERCE = "ecommerce"
    PAYMENT_GATEWAY = "payment_gateway"
    ACCOUNTING = "accounting"
    CRM = "crm"
    ERP = "erp"
    API = "api"
    SOAP = "soap"
    GRPC = "grpc"
    WEBHOOK = "webhook"
    DATABASE = "database"
    FILE_SYSTEM = "file_system"
    CLOUD_STORAGE = "cloud_storage"

class IntegrationStatus(Enum):
    """Integration status"""
    DISCONNECTED = "disconnected"
    CONNECTED = "connected"
    CONFIGURING = "configuring"
    ERROR = "error"
    TESTING = "testing"
    MAINTENANCE = "maintenance"

class IntegrationCategory(Enum):
    """Integration categories"""
    BANKS_SERBIA = "banks_serbia"
    BANKS_EU = "banks_eu"
    ECOMMERCE_PLATFORMS = "ecommerce_platforms"
    PAYMENT_PROCESSORS = "payment_processors"
    ACCOUNTING_SOFTWARE = "accounting_software"
    CRM_SYSTEMS = "crm_systems"
    ERP_SYSTEMS = "erp_systems"
    FINANCIAL_APIS = "financial_apis"
    GOVERNMENT_APIS = "government_apis"
    CLOUD_SERVICES = "cloud_services"

class Integration(db.Model):
    """Integration model for storing integration configurations"""
    __tablename__ = 'integrations'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    name = Column(String(255), nullable=False)
    display_name = Column(String(255), nullable=False)
    integration_type = Column(String(50), nullable=False)
    category = Column(String(50), nullable=False)
    status = Column(String(20), nullable=False, default=IntegrationStatus.DISCONNECTED.value)
    
    # Configuration
    config = Column(JSON)  # API keys, endpoints, credentials, etc.
    settings = Column(JSON)  # User-specific settings
    
    # Connection details
    api_endpoint = Column(String(500))
    api_version = Column(String(20))
    authentication_type = Column(String(50))  # oauth, api_key, basic, etc.
    
    # Metadata
    description = Column(Text)
    logo_url = Column(String(500))
    website_url = Column(String(500))
    documentation_url = Column(String(500))
    
    # Performance metrics
    last_sync = Column(DateTime)
    sync_frequency = Column(String(20), default='daily')  # realtime, hourly, daily, weekly
    success_rate = Column(Float, default=0.0)
    response_time_avg = Column(Float)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_used = Column(DateTime)
    
    # Relationships
    user = relationship('User', back_populates='integrations')
    sync_logs = relationship('IntegrationSyncLog', back_populates='integration')
    
    def __repr__(self):
        return f'<Integration {self.id}: {self.name} - {self.status}>'
    
    def to_dict(self):
        """Convert integration to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'display_name': self.display_name,
            'type': self.integration_type,
            'category': self.category,
            'status': self.status,
            'config': self.config,
            'settings': self.settings,
            'api_endpoint': self.api_endpoint,
            'api_version': self.api_version,
            'authentication_type': self.authentication_type,
            'description': self.description,
            'logo_url': self.logo_url,
            'website_url': self.website_url,
            'documentation_url': self.documentation_url,
            'last_sync': self.last_sync.isoformat() if self.last_sync else None,
            'sync_frequency': self.sync_frequency,
            'success_rate': self.success_rate,
            'response_time_avg': self.response_time_avg,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'last_used': self.last_used.isoformat() if self.last_used else None
        }
    
    def update_status(self, status):
        """Update integration status"""
        self.status = status
        self.updated_at = datetime.utcnow()
        db.session.commit()
    
    def update_sync_info(self, success=True, response_time=None):
        """Update sync information"""
        self.last_sync = datetime.utcnow()
        if response_time:
            if self.response_time_avg:
                self.response_time_avg = (self.response_time_avg + response_time) / 2
            else:
                self.response_time_avg = response_time
        
        # Update success rate
        if hasattr(self, '_sync_count'):
            self._sync_count += 1
        else:
            self._sync_count = 1
        
        if success:
            if hasattr(self, '_success_count'):
                self._success_count += 1
            else:
                self._success_count = 1
        
        self.success_rate = (self._success_count / self._sync_count) * 100
        db.session.commit()

class IntegrationTemplate(db.Model):
    """Template for available integrations"""
    __tablename__ = 'integration_templates'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, unique=True)
    display_name = Column(String(255), nullable=False)
    integration_type = Column(String(50), nullable=False)
    category = Column(String(50), nullable=False)
    
    # Configuration template
    config_schema = Column(JSON)  # JSON schema for configuration
    required_fields = Column(JSON)  # List of required configuration fields
    optional_fields = Column(JSON)  # List of optional configuration fields
    
    # API information
    api_endpoint = Column(String(500))
    api_version = Column(String(20))
    authentication_type = Column(String(50))
    supported_operations = Column(JSON)  # List of supported operations
    
    # Metadata
    description = Column(Text)
    logo_url = Column(String(500))
    website_url = Column(String(500))
    documentation_url = Column(String(500))
    pricing_info = Column(Text)
    
    # Features
    features = Column(JSON)  # List of features
    limitations = Column(JSON)  # List of limitations
    supported_countries = Column(JSON)  # List of supported countries
    
    # Status
    is_active = Column(Boolean, default=True)
    is_beta = Column(Boolean, default=False)
    is_premium = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<IntegrationTemplate {self.id}: {self.name}>'
    
    def to_dict(self):
        """Convert template to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'display_name': self.display_name,
            'type': self.integration_type,
            'category': self.category,
            'config_schema': self.config_schema,
            'required_fields': self.required_fields,
            'optional_fields': self.optional_fields,
            'api_endpoint': self.api_endpoint,
            'api_version': self.api_version,
            'authentication_type': self.authentication_type,
            'supported_operations': self.supported_operations,
            'description': self.description,
            'logo_url': self.logo_url,
            'website_url': self.website_url,
            'documentation_url': self.documentation_url,
            'pricing_info': self.pricing_info,
            'features': self.features,
            'limitations': self.limitations,
            'supported_countries': self.supported_countries,
            'is_active': self.is_active,
            'is_beta': self.is_beta,
            'is_premium': self.is_premium,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class IntegrationSyncLog(db.Model):
    """Log for integration sync operations"""
    __tablename__ = 'integration_sync_logs'
    
    id = Column(Integer, primary_key=True)
    integration_id = Column(Integer, ForeignKey('integrations.id'), nullable=False)
    operation = Column(String(100), nullable=False)  # sync, test, auth, etc.
    status = Column(String(20), nullable=False)  # success, error, warning
    message = Column(Text)
    
    # Performance metrics
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime)
    duration = Column(Float)  # Duration in seconds
    records_processed = Column(Integer, default=0)
    records_success = Column(Integer, default=0)
    records_failed = Column(Integer, default=0)
    
    # Error details
    error_code = Column(String(50))
    error_details = Column(JSON)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    integration = relationship('Integration', back_populates='sync_logs')
    
    def __repr__(self):
        return f'<IntegrationSyncLog {self.id}: {self.operation} - {self.status}>'
    
    def complete(self, status, message=None, records_processed=0, records_success=0, records_failed=0, error_code=None, error_details=None):
        """Complete the sync operation"""
        self.end_time = datetime.utcnow()
        self.duration = (self.end_time - self.start_time).total_seconds()
        self.status = status
        self.message = message
        self.records_processed = records_processed
        self.records_success = records_success
        self.records_failed = records_failed
        self.error_code = error_code
        self.error_details = error_details
        db.session.commit()

class IntegrationData(db.Model):
    """Stored data from integrations"""
    __tablename__ = 'integration_data'
    
    id = Column(Integer, primary_key=True)
    integration_id = Column(Integer, ForeignKey('integrations.id'), nullable=False)
    data_type = Column(String(100), nullable=False)  # transactions, accounts, customers, etc.
    external_id = Column(String(255))  # ID from external system
    data = Column(JSON, nullable=False)  # The actual data
    metadata = Column(JSON)  # Additional metadata
    
    # Sync information
    last_synced = Column(DateTime, default=datetime.utcnow)
    sync_version = Column(String(20))
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    integration = relationship('Integration')
    
    def __repr__(self):
        return f'<IntegrationData {self.id}: {self.data_type} - {self.external_id}>'
