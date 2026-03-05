"""
Web Scraping Package for ValidoAI

This package provides comprehensive web scraping functionality including:
- Multiple scraping engines and configurations
- Data extraction templates and tools
- Serbian regulations scraping
- Rate limiting and proxy support
- Error handling and validation
"""

from .scraper import (
    WebScraper, SerbianRegulationsScraper, ScrapingConfig, ScrapingResult,
    DataExtractionTemplate, NEWS_TEMPLATE, PRODUCT_TEMPLATE, CONTACT_TEMPLATE
)

__all__ = [
    'WebScraper',
    'SerbianRegulationsScraper', 
    'ScrapingConfig',
    'ScrapingResult',
    'DataExtractionTemplate',
    'NEWS_TEMPLATE',
    'PRODUCT_TEMPLATE',
    'CONTACT_TEMPLATE'
]
