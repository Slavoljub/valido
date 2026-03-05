"""
ValidoAI Content Management Package
==================================

Content management and file processing for ValidoAI.

This package provides:
- File upload and validation
- Content processing and analysis
- Metadata extraction
- File storage and organization
- Search and retrieval
- Access control and permissions
"""

from .manager import ContentManager, content_manager

__all__ = ['ContentManager', 'content_manager']
