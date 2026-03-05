"""
ValidoAI Core Logging Module
============================

Logging functionality for ValidoAI core.
"""

import logging
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

class LoggerFactory:
    """Factory for creating logger instances."""

    @staticmethod
    def get_logger(name: str) -> logging.Logger:
        """Get a logger instance."""
        return logging.getLogger(name)

    @staticmethod
    def initialize():
        """Initialize logging configuration."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

# Export classes
__all__ = ['LoggerFactory']