"""
Unified Models System for ValidoAI
==================================
Consolidated database models, AI models, and business logic models
Following Cursor Rules: separation of concerns, modularity, no code duplication

CONSOLIDATED FROM:
- src/models.py (main SQLAlchemy models)
- src/ai/models.py (AI model management)
- src/emailing/models.py (email models)
- src/models/models.py (duplicate models)
"""

from typing import Dict, List, Any, Optional
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, ForeignKey, UUID, JSON, Index
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import relationship, declared_attr
from datetime import datetime
import uuid
import os
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Initialize SQLAlchemy
db = SQLAlchemy()

# ============================================================================
# BASE MODEL CLASS
# ============================================================================

class BaseModel:
    """Base model with common functionality"""

    id = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @declared_attr
    def created_by_id(cls):
        return db.Column(db.UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=True)

    @declared_attr
    def updated_by_id(cls):
        return db.Column(db.UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=True)

    @declared_attr
    def created_by(cls):
        return db.relationship("User", foreign_keys=[cls.created_by_id])

    @declared_attr
    def updated_by(cls):
        return db.relationship("User", foreign_keys=[cls.updated_by_id])

    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary"""
        result = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            if isinstance(value, datetime):
                result[column.name] = value.isoformat()
            elif isinstance(value, uuid.UUID):
                result[column.name] = str(value)
            else:
                result[column.name] = value
        return result

    def update_from_dict(self, data: Dict[str, Any]) -> None:
        """Update model from dictionary"""
        for key, value in data.items():
            if hasattr(self, key) and key not in ['id', 'created_at']:
                setattr(self, key, value)
        self.updated_at = datetime.utcnow()

# ============================================================================
# DATABASE MODELS (from src/models.py)
# ============================================================================

class Company(db.Model):
    """Company model for Serbian businesses"""
    __tablename__ = 'companies'

    companies_id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_name = Column(String(255), nullable=False)
    legal_name = Column(String(255), nullable=False)
    tax_id = Column(String(20), unique=True, nullable=False)  # PIB
    registration_number = Column(String(20), unique=True, nullable=False)  # Matični broj
    business_entity_type_id = Column(PostgresUUID(as_uuid=True), nullable=True)
    industry = Column(String(100))
    company_type = Column(String(50))  # DOO, AD, Preduzetnik

    # Serbian-specific fields
    pdv_registration = Column(String(20))
    statistical_number = Column(String(20))
    bank_account = Column(String(50))
    bank_name = Column(String(100))
    address_line1 = Column(String(255))
    city = Column(String(100))
    postal_code = Column(String(20))
    phone = Column(String(50))
    email = Column(String(255))
    is_pdv_registered = Column(Boolean, default=False)
    is_e_invoice_enabled = Column(Boolean, default=False)

    # Metadata
    status = Column(String(20), default='active')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    invoices = relationship("Invoice", back_populates="company", cascade="all, delete-orphan")
    users = relationship("User", back_populates="company", cascade="all, delete-orphan")

class User(db.Model):
    """User model with Serbian business compliance"""
    __tablename__ = 'users'

    users_id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False)
    username = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100))
    last_name = Column(String(100))
    phone = Column(String(20))
    role = Column(String(50), default='user')
    status = Column(String(20), default='active')
    email_verified_at = Column(DateTime)
    is_active = Column(Boolean, default=True)
    company_id = Column(PostgresUUID(as_uuid=True), ForeignKey('companies.companies_id'))
    department = Column(String(100))
    job_title = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login_at = Column(DateTime)

    # Relationships
    company = relationship("Company", back_populates="users")

class Invoice(db.Model):
    """Invoice model for Serbian e-invoicing compliance"""
    __tablename__ = 'invoices'

    invoices_id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    invoice_number = Column(String(50), unique=True, nullable=False)
    company_id = Column(PostgresUUID(as_uuid=True), ForeignKey('companies.companies_id'), nullable=False)
    customer_name = Column(String(255), nullable=False)
    customer_tax_id = Column(String(20))  # Customer PIB
    invoice_date = Column(DateTime, default=datetime.utcnow)
    due_date = Column(DateTime)
    total_amount = Column(Float, nullable=False)
    tax_amount = Column(Float, default=0)
    currency = Column(String(3), default='RSD')
    status = Column(String(20), default='draft')
    payment_status = Column(String(20), default='unpaid')

    # Serbian-specific fields
    is_e_invoice = Column(Boolean, default=False)
    e_invoice_id = Column(String(100))
    fiskal_trust_id = Column(String(100))

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    company = relationship("Company", back_populates="invoices")
    items = relationship("InvoiceItem", back_populates="invoice", cascade="all, delete-orphan")

class InvoiceItem(db.Model):
    """Invoice item model"""
    __tablename__ = 'invoice_items'

    invoice_items_id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    invoice_id = Column(PostgresUUID(as_uuid=True), ForeignKey('invoices.invoices_id'), nullable=False)
    product_name = Column(String(255), nullable=False)
    quantity = Column(Float, nullable=False)
    unit_price = Column(Float, nullable=False)
    tax_rate = Column(Float, default=20.0)  # Serbian PDV rate
    discount = Column(Float, default=0)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    invoice = relationship("Invoice", back_populates="items")

# ============================================================================
# EMAIL MODELS (from src/emailing/models.py)
# ============================================================================

class EmailTemplate(db.Model):
    """Email template model"""
    __tablename__ = 'email_templates'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    subject = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    category = Column(String(100), nullable=False, default='business')
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    campaigns = relationship("EmailCampaign", back_populates="template")

class EmailCampaign(db.Model):
    """Email campaign model"""
    __tablename__ = 'email_campaigns'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    template_id = Column(Integer, ForeignKey('email_templates.id'))
    status = Column(String(50), default='draft')  # draft, scheduled, sending, completed, paused
    scheduled_at = Column(DateTime)
    sent_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Campaign statistics
    total_recipients = Column(Integer, default=0)
    sent_count = Column(Integer, default=0)
    opened_count = Column(Integer, default=0)
    clicked_count = Column(Integer, default=0)
    bounce_count = Column(Integer, default=0)

    # Relationships
    template = relationship("EmailTemplate", back_populates="campaigns")
    recipients = relationship("EmailRecipient", back_populates="campaign")

class EmailRecipient(db.Model):
    """Email recipient model"""
    __tablename__ = 'email_recipients'

    id = Column(Integer, primary_key=True)
    campaign_id = Column(Integer, ForeignKey('email_campaigns.id'))
    email = Column(String(255), nullable=False)
    first_name = Column(String(100))
    last_name = Column(String(100))
    status = Column(String(50), default='pending')  # pending, sent, opened, clicked, bounced
    sent_at = Column(DateTime)
    opened_at = Column(DateTime)
    clicked_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    campaign = relationship("EmailCampaign", back_populates="recipients")

# ============================================================================
# AI MODELS MANAGEMENT (from src/ai/models.py)
# ============================================================================

class LocalModelManager:
    """Manages local AI models"""

    def __init__(self, config_path: str = None):
        self.config_path = config_path or "src/ai_local_models/local_models_config.json"
        self.models_config = {}
        self.loaded_models = {}
        self._load_config()

    def _load_config(self):
        """Load model configuration"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self.models_config = json.load(f)
                logger.info(f"✅ Loaded {len(self.models_config)} model configurations")
            else:
                logger.warning(f"⚠️  Model config not found: {self.config_path}")
        except Exception as e:
            logger.error(f"❌ Error loading model config: {e}")

    def list_available_models(self) -> List[Dict[str, Any]]:
        """List all available models"""
        return list(self.models_config.values()) if self.models_config else []

    def get_model_info(self, model_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific model"""
        return self.models_config.get(model_name)

    def download_model(self, model_name: str) -> Dict[str, Any]:
        """Download a specific model"""
        try:
            from src.ai_local_models.downloader import ModelDownloader
            downloader = ModelDownloader()
            return downloader.download_model(model_name)
        except Exception as e:
            logger.error(f"❌ Error downloading model {model_name}: {e}")
            return {'success': False, 'error': str(e)}

    def load_model(self, model_name: str) -> bool:
        """Load a model into memory"""
        try:
            model_info = self.get_model_info(model_name)
            if not model_info:
                return False

            # Model loading logic here
            self.loaded_models[model_name] = model_info
            logger.info(f"✅ Model {model_name} loaded successfully")
            return True
        except Exception as e:
            logger.error(f"❌ Error loading model {model_name}: {e}")
            return False

    def unload_model(self, model_name: str) -> bool:
        """Unload a model from memory"""
        if model_name in self.loaded_models:
            del self.loaded_models[model_name]
            logger.info(f"✅ Model {model_name} unloaded successfully")
            return True
        return False

    def generate_response(self, model_name: str, prompt: str) -> Optional[str]:
        """Generate response using specified model"""
        try:
            if model_name not in self.loaded_models:
                if not self.load_model(model_name):
                    return None

            # AI generation logic here
            return f"AI Response from {model_name}: {prompt[:50]}..."
        except Exception as e:
            logger.error(f"❌ Error generating response with {model_name}: {e}")
            return None

class AIModel(db.Model):
    """AI Model configuration in database"""
    __tablename__ = 'ai_models'

    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    model_type = Column(String(50), nullable=False)  # local, external, api
    provider = Column(String(100))  # openai, anthropic, local
    model_path = Column(String(500))
    config = Column(JSON)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class AIInsight(db.Model):
    """AI-generated insights and analytics"""
    __tablename__ = 'ai_insights'

    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(PostgresUUID(as_uuid=True), ForeignKey('companies.companies_id'))
    insight_type = Column(String(100), nullable=False)  # financial, operational, market
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    confidence = Column(Float)  # AI confidence score
    generated_at = Column(DateTime, default=datetime.utcnow)
    is_read = Column(Boolean, default=False)

# ============================================================================
# MODEL MANAGEMENT SYSTEM
# ============================================================================

class UnifiedModelManager:
    """Unified model management system"""

    def __init__(self):
        self.database_models = {}
        self.ai_models = {}
        self._register_models()

    def _register_models(self):
        """Register all models in the system"""
        # Database models
        self.database_models = {
            'Company': Company,
            'User': User,
            'Invoice': Invoice,
            'InvoiceItem': InvoiceItem,
            'EmailTemplate': EmailTemplate,
            'EmailCampaign': EmailCampaign,
            'EmailRecipient': EmailRecipient,
            'AIModel': AIModel,
            'AIInsight': AIInsight
        }

        # AI models
        self.ai_models = {
            'local_manager': LocalModelManager()
        }

    def get_database_model(self, model_name: str):
        """Get database model by name"""
        return self.database_models.get(model_name)

    def get_ai_model(self, model_name: str):
        """Get AI model manager by name"""
        return self.ai_models.get(model_name)

    def list_all_models(self) -> Dict[str, List[str]]:
        """List all available models"""
        return {
            'database_models': list(self.database_models.keys()),
            'ai_models': list(self.ai_models.keys())
        }

    def create_all_tables(self):
        """Create all database tables"""
        try:
            with db.app.app_context():
                db.create_all()
                logger.info("✅ All database tables created successfully")
                return True
        except Exception as e:
            logger.error(f"❌ Error creating database tables: {e}")
            return False

    def get_model_stats(self) -> Dict[str, Any]:
        """Get statistics about all models"""
        stats = {
            'database_models_count': len(self.database_models),
            'ai_models_count': len(self.ai_models),
            'timestamp': datetime.utcnow().isoformat()
        }

        return stats

# ============================================================================
# POSTGRESQL MODELS (from master structure)
# ============================================================================

class Country(db.Model, BaseModel):
    """Countries table with Unicode support"""
    __tablename__ = 'countries'

    country_code = db.Column(db.String(3), unique=True, nullable=False)
    country_name = db.Column(db.String(100), nullable=False)
    country_name_sr = db.Column(db.String(100))  # Serbian name
    currency_code = db.Column(db.String(3))
    phone_code = db.Column(db.String(5))
    region = db.Column(db.String(50))
    subregion = db.Column(db.String(50))
    population = db.Column(db.Integer)
    capital = db.Column(db.String(100))
    description = db.Column(db.Text)

    # Relationships
    companies = db.relationship("Company", back_populates="country")

class Currency(db.Model, BaseModel):
    """Currencies table"""
    __tablename__ = 'currencies'

    currency_code = db.Column(db.String(3), unique=True, nullable=False)
    currency_name = db.Column(db.String(100), nullable=False)
    currency_name_sr = db.Column(db.String(100))  # Serbian name
    symbol = db.Column(db.String(10))
    decimal_places = db.Column(db.Integer, default=2)
    exchange_rate = db.Column(db.DECIMAL(10, 4))
    description = db.Column(db.Text)

    # Relationships
    companies = db.relationship("Company", back_populates="currency")

class BusinessEntityType(db.Model, BaseModel):
    """Business entity types"""
    __tablename__ = 'business_entity_types'

    entity_code = db.Column(db.String(20), unique=True, nullable=False)
    entity_name = db.Column(db.String(100), nullable=False)
    entity_name_sr = db.Column(db.String(100))  # Serbian name
    description = db.Column(db.Text)

    # Relationships
    companies = db.relationship("Company", back_populates="business_entity_type")

class BusinessArea(db.Model, BaseModel):
    """Business areas/sectors"""
    __tablename__ = 'business_areas'

    area_code = db.Column(db.String(20), unique=True, nullable=False)
    area_name = db.Column(db.String(100), nullable=False)
    area_name_sr = db.Column(db.String(100))  # Serbian name
    description = db.Column(db.Text)
    tax_rates = db.Column(db.JSON)

    # Relationships
    companies = db.relationship("Company", back_populates="business_area")

class CustomerFeedback(db.Model, BaseModel):
    """Customer feedback and reviews"""
    __tablename__ = 'customer_feedback'

    # Foreign Keys
    company_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('companies.id'))
    user_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('users.id'))

    # Feedback Details
    feedback_type = db.Column(db.String(50), nullable=False)  # review, complaint, suggestion, etc.
    rating = db.Column(db.Integer)  # 1-5 stars
    title = db.Column(db.String(255))
    content = db.Column(db.Text, nullable=False)

    # Contact Information
    customer_name = db.Column(db.String(255))
    customer_email = db.Column(db.String(255))
    customer_phone = db.Column(db.String(20))

    # Status and Management
    status = db.Column(db.String(20), default='pending')  # pending, reviewed, responded, resolved
    priority = db.Column(db.String(10), default='medium')  # low, medium, high, urgent

    # AI Analysis
    sentiment_score = db.Column(db.DECIMAL(3, 2))  # -1 to 1
    sentiment_label = db.Column(db.String(20))  # positive, negative, neutral
    keywords = db.Column(db.JSON)
    embedding_vector = db.Column(db.Text)

    # Response
    response_content = db.Column(db.Text)
    response_date = db.Column(db.DateTime)
    response_by_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('users.id'))

    # Relationships
    company = db.relationship("Company", back_populates="customer_feedback")
    user = db.relationship("User", back_populates="feedback_given")
    response_by = db.relationship("User", foreign_keys=[response_by_id])

# Update existing Company model to add missing relationships
Company.country = db.relationship("Country", back_populates="companies")
Company.currency = db.relationship("Currency", back_populates="companies")
Company.business_entity_type = db.relationship("BusinessEntityType", back_populates="companies")
Company.business_area = db.relationship("BusinessArea", back_populates="companies")
Company.customer_feedback = db.relationship("CustomerFeedback", back_populates="company")

# Update existing User model to add missing relationships
User.feedback_given = db.relationship("CustomerFeedback", back_populates="user")

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_model_class(table_name: str):
    """Get model class by table name"""
    model_map = {
        'countries': Country,
        'currencies': Currency,
        'business_entity_types': BusinessEntityType,
        'business_areas': BusinessArea,
        'companies': Company,
        'users': User,
        'customer_feedback': CustomerFeedback
    }
    return model_map.get(table_name)

def get_all_postgres_models() -> List:
    """Get all PostgreSQL model classes"""
    return [
        Country, Currency, BusinessEntityType, BusinessArea,
        Company, User, CustomerFeedback
    ]

# ============================================================================
# GLOBAL INSTANCES
# ============================================================================

# Global instances
model_manager = UnifiedModelManager()
local_model_manager = LocalModelManager()

# Export commonly used models for backward compatibility
__all__ = [
    'db', 'BaseModel',
    'Country', 'Currency', 'BusinessEntityType', 'BusinessArea',
    'Company', 'User', 'CustomerFeedback',
    'Invoice', 'InvoiceItem',
    'EmailTemplate', 'EmailCampaign', 'EmailRecipient',
    'AIModel', 'AIInsight',
    'LocalModelManager', 'UnifiedModelManager',
    'model_manager', 'local_model_manager',
    'get_model_class', 'get_all_postgres_models'
]

logger.info("✅ Unified models system initialized successfully")
logger.info(f"📊 Registered {len(model_manager.database_models)} database models")
logger.info(f"🤖 Registered {len(model_manager.ai_models)} AI model managers")
