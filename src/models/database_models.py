"""
Database Models
SQLAlchemy models for the ValidoAI application
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from flask_login import UserMixin

from ..extensions import db

Base = declarative_base()


class OpenAILog(db.Model):
    """OpenAI API request logging"""
    __tablename__ = 'openai_logs'
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    endpoint = Column(String(100), nullable=False)
    model = Column(String(50), nullable=False)
    user_message = Column(Text)
    ai_response = Column(Text)
    tokens_used = Column(Integer)
    response_time = Column(Float)
    status = Column(String(20), default='success')
    error_message = Column(Text)
    ip_address = Column(String(45))
    user_agent = Column(String(500))
    
    def __repr__(self):
        return f'<OpenAILog {self.id}: {self.endpoint} - {self.status}>'


class User(db.Model, UserMixin):
    """User model for authentication and preferences"""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)
    preferences = Column(JSON)
    
    # Flask-Login required methods
    def is_authenticated(self):
        return True
    
    def is_anonymous(self):
        return False
    
    def get_id(self):
        return str(self.id)
    
    # Additional properties for templates
    @property
    def name(self):
        return self.username
    
    @property
    def avatar(self):
        return self.preferences.get('avatar') if self.preferences else None
    
    @property
    def role(self):
        return self.preferences.get('role', 'Korisnik') if self.preferences else 'Korisnik'
    
    # Relationships
    analysis_logs = relationship('AnalysisLog', back_populates='user')
    
    def __repr__(self):
        return f'<User {self.username}>'


class AnalysisLog(db.Model):
    """Analysis execution logging"""
    __tablename__ = 'analysis_logs'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, db.ForeignKey('users.id'))
    analysis_type = Column(String(50), nullable=False)
    input_data = Column(JSON)
    output_data = Column(JSON)
    execution_time = Column(Float)
    status = Column(String(20), default='success')
    error_message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship('User', back_populates='analysis_logs')
    
    def __repr__(self):
        return f'<AnalysisLog {self.id}: {self.analysis_type} - {self.status}>'


class TwoFactorAuth(db.Model):
    """Two-Factor Authentication model"""
    __tablename__ = 'two_factor_auth'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, db.ForeignKey('users.id'), nullable=False)
    secret = Column(String(32), nullable=False)  # TOTP secret key
    backup_codes = Column(Text)  # Comma-separated backup codes
    is_enabled = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_used = Column(DateTime)
    
    # Relationships
    user = relationship('User', backref='two_factor_auth')
    
    def __repr__(self):
        return f'<TwoFactorAuth {self.user_id}: {"enabled" if self.is_enabled else "disabled"}>'


def init_database_models(app):
    """Initialize database models with the Flask app"""
    with app.app_context():
        db.create_all()
