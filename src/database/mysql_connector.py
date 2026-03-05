"""
MySQL database connector for ValidoAI application
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
from flask import current_app

Base = declarative_base()

def get_mysql_connection_string():
    """Get MySQL connection string from environment variables or config"""
    # Try to get from environment variables first
    host = os.getenv('MYSQL_HOST', 'localhost')
    port = os.getenv('MYSQL_PORT', '3306')
    user = os.getenv('MYSQL_USER', 'root')
    password = os.getenv('MYSQL_PASSWORD', 'root')
    database = os.getenv('MYSQL_DATABASE', 'valido')
    
    # If in Flask context, try to get from app config
    if current_app:
        host = current_app.config.get('MYSQL_HOST', host)
        port = current_app.config.get('MYSQL_PORT', port)
        user = current_app.config.get('MYSQL_USER', user)
        password = current_app.config.get('MYSQL_PASSWORD', password)
        database = current_app.config.get('MYSQL_DATABASE', database)
    
    return f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"

def get_mysql_engine():
    """Create SQLAlchemy engine for MySQL"""
    connection_string = get_mysql_connection_string()
    return create_engine(connection_string, pool_pre_ping=True, pool_recycle=3600)

def get_mysql_session():
    """Create SQLAlchemy session for MySQL"""
    engine = get_mysql_engine()
    session_factory = sessionmaker(bind=engine)
    return scoped_session(session_factory)

def init_mysql_tables():
    """Initialize MySQL tables if they don't exist"""
    engine = get_mysql_engine()
    
    # Import all models that need to be created
    from src.models.company import Company
    
    # Create tables
    Base.metadata.create_all(engine)
    
    return engine
