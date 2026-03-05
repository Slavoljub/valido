"""
ValidoAI Extensions Package
===========================

Extensions and plugins for the ValidoAI application.
This package contains various extensions like themes, plugins, etc.
"""

__version__ = "1.0.0"

# Flask extensions
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_caching import Cache
from flask_babel import Babel
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager
from flask_mail import Mail

# Initialize extensions (will be configured in app factory)
db = SQLAlchemy()
migrate = Migrate()
cache = Cache()
babel = Babel()
csrf = CSRFProtect()
login_manager = LoginManager()
mail = Mail()
