"""
ValidoAI Core System Info Module
=================================

System information utilities for ValidoAI core.
"""

import platform
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

def get_system_info():
    """Get system information."""
    return {
        "platform": platform.platform(),
        "python_version": sys.version,
        "architecture": platform.architecture(),
        "processor": platform.processor(),
        "hostname": platform.node()
    }

# Export functions
__all__ = ['get_system_info']