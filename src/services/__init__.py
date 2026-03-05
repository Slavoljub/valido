"""
ValidoAI Services Package
========================

Business services layer for ValidoAI.

This package provides:
- Business logic separation
- Service-oriented architecture
- Reusable business components
- Transaction management
- Data processing services
"""

# Import service modules conditionally to avoid circular imports
_available_services = []

try:
    from . import user_service
    _available_services.append('user_service')
except ImportError:
    pass

try:
    from . import content_service
    _available_services.append('content_service')
except ImportError:
    pass

try:
    from . import analytics_service
    _available_services.append('analytics_service')
except ImportError:
    pass

try:
    from . import notification_service
    _available_services.append('notification_service')
except ImportError:
    pass

try:
    from . import report_service
    _available_services.append('report_service')
except ImportError:
    pass

__all__ = _available_services
