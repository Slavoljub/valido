#!/usr/bin/env python3
"""
Test script to isolate import issues in app.py
"""

print("🔍 Testing imports step by step...")

# Test 1: Standard library imports
try:
    import os, sys, json, logging, uuid, asyncio
    from datetime import datetime, timedelta
    from functools import wraps
    from pathlib import Path
    from typing import Dict, List, Any, Optional, Callable, Union, Tuple
    from dataclasses import dataclass, asdict
    from enum import Enum
    print("✅ Standard library imports OK")
except Exception as e:
    print(f"❌ Standard library imports failed: {e}")

# Test 2: Flask core imports
try:
    from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, g, session, current_app, send_file, make_response
    from flask_login import LoginManager, login_required, current_user, login_user, logout_user, UserMixin
    from werkzeug.security import generate_password_hash, check_password_hash
    from werkzeug.utils import secure_filename
    print("✅ Flask core imports OK")
except Exception as e:
    print(f"❌ Flask core imports failed: {e}")

# Test 3: Database imports
try:
    from flask_sqlalchemy import SQLAlchemy
    from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, ForeignKey, UUID, JSON, Index, create_engine
    from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
    from sqlalchemy.orm import relationship, sessionmaker
    from sqlalchemy.ext.declarative import declarative_base
    print("✅ Database imports OK")
except Exception as e:
    print(f"❌ Database imports failed: {e}")

# Test 4: Optional Flask extensions
print("\n🔍 Testing optional Flask extensions...")

optional_imports = [
    ('flask_socketio', 'SocketIO'),
    ('flask_wtf', 'FlaskForm'),
    ('flask_migrate', 'Migrate'),
    ('flask_session', 'Session'),
    ('flask_cors', 'CORS'),
    ('dotenv', 'load_dotenv'),
]

for module_name, class_name in optional_imports:
    try:
        module = __import__(module_name)
        if hasattr(module, class_name):
            getattr(module, class_name)
        print(f"✅ {module_name}.{class_name} available")
    except Exception as e:
        print(f"⚠️ {module_name}.{class_name} not available: {e}")

# Test 5: ASGI imports
try:
    from asgiref.wsgi import WsgiToAsgi
    from hypercorn.config import Config as HypercornConfig
    from hypercorn.asyncio import serve as hypercorn_serve
    print("✅ ASGI imports OK")
except Exception as e:
    print(f"⚠️ ASGI imports failed: {e}")

print("\n🎉 Import testing completed!")
