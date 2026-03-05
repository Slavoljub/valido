"""
ValidoAI Integrations Package
============================

External service integrations for ValidoAI.

This package handles:
- Third-party API integrations
- Payment processing
- Email services
- Cloud storage
- Social media
- Analytics platforms
- Government services
- N8N workflow automation
"""

# Import integration modules conditionally to avoid circular imports
try:
    from . import n8n_integration
    _n8n_available = True
except ImportError:
    _n8n_available = False

# Other integrations can be imported as needed
__all__ = ['n8n_integration'] if '_n8n_available' in locals() and _n8n_available else []
