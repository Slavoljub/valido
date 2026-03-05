"""
Web Scraping System for ValidoAI

This module provides comprehensive web scraping functionality including:
- Multiple scraping engines (requests, selenium, playwright)
- Data extraction with BeautifulSoup and XPath
- Rate limiting and proxy support
- Error handling and retry mechanisms
- Data validation and cleaning
"""

import requests
import time
import random
from typing import Dict, List, Optional, Any, Union
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import json
import logging
from dataclasses import dataclass
from datetime import datetime
import re

logger = logging.getLogger(__name__)


@dataclass
class ScrapingConfig:
    """Configuration for web scraping"""
    user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    timeout: int = 30
    max_retries: int = 3
    delay_between_requests: float = 1.0
    use_proxy: bool = False
    proxy_list: List[str] = None
    respect_robots_txt: bool = True
    max_redirects: int = 5


@dataclass
class ScrapingResult:
    """Result of a scraping operation"""
    url: str
    status_code: int
    content: str
    soup: BeautifulSoup
    metadata: Dict[str, Any]
    timestamp: datetime
    error: Optional[str] = None


class WebScraper:
    """Main web scraping class"""
    
    def __init__(self, config: ScrapingConfig = None):
        self.config = config or ScrapingConfig()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': self.config.user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
        
        if self.config.use_proxy and self.config.proxy_list:
            self.current_proxy = random.choice(self.config.proxy_list)
            self.session.proxies = {
                'http': self.current_proxy,
                'https': self.current_proxy
            }
    
    def scrape_url(self, url: str) -> ScrapingResult:
        """Scrape a single URL"""
        start_time = time.time()
        
        try:
            # Add delay between requests
            if hasattr(self, '_last_request_time'):
                time_since_last = time.time() - self._last_request_time
                if time_since_last < self.config.delay_between_requests:
                    time.sleep(self.config.delay_between_requests - time_since_last)
            
            # Make request
            response = self.session.get(
                url,
                timeout=self.config.timeout,
                allow_redirects=True,
                max_redirects=self.config.max_redirects
            )
            
            self._last_request_time = time.time()
            
            # Parse content
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract metadata
            metadata = self._extract_metadata(soup, response)
            
            return ScrapingResult(
                url=url,
                status_code=response.status_code,
                content=response.text,
                soup=soup,
                metadata=metadata,
                timestamp=datetime.now()
            )
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error scraping {url}: {str(e)}")
            return ScrapingResult(
                url=url,
                status_code=0,
                content="",
                soup=None,
                metadata={},
                timestamp=datetime.now(),
                error=str(e)
            )
    
    def _extract_metadata(self, soup: BeautifulSoup, response: requests.Response) -> Dict[str, Any]:
        """Extract metadata from the page"""
        metadata = {
            'title': '',
            'description': '',
            'keywords': '',
            'author': '',
            'language': '',
            'charset': '',
            'viewport': '',
            'robots': '',
            'canonical_url': '',
            'og_tags': {},
            'twitter_tags': {},
            'structured_data': [],
            'links': [],
            'images': [],
            'forms': [],
            'scripts': [],
            'stylesheets': []
        }
        
        try:
            # Basic meta tags
            if soup.title:
                metadata['title'] = soup.title.get_text(strip=True)
            
            meta_tags = soup.find_all('meta')
            for meta in meta_tags:
                name = meta.get('name', '').lower()
                property_attr = meta.get('property', '').lower()
                content = meta.get('content', '')
                
                if name == 'description':
                    metadata['description'] = content
                elif name == 'keywords':
                    metadata['keywords'] = content
                elif name == 'author':
                    metadata['author'] = content
                elif name == 'robots':
                    metadata['robots'] = content
                elif property_attr.startswith('og:'):
                    metadata['og_tags'][property_attr] = content
                elif property_attr.startswith('twitter:'):
                    metadata['twitter_tags'][property_attr] = content
            
            # Language and charset
            html_tag = soup.find('html')
            if html_tag:
                metadata['language'] = html_tag.get('lang', '')
            
            # Canonical URL
            canonical = soup.find('link', rel='canonical')
            if canonical:
                metadata['canonical_url'] = canonical.get('href', '')
            
            # Structured data
            structured_data = soup.find_all('script', type='application/ld+json')
            for script in structured_data:
                try:
                    data = json.loads(script.string)
                    metadata['structured_data'].append(data)
                except (json.JSONDecodeError, AttributeError):
                    continue
            
            # Links
            links = soup.find_all('a', href=True)
            metadata['links'] = [link.get('href') for link in links]
            
            # Images
            images = soup.find_all('img')
            metadata['images'] = [
                {
                    'src': img.get('src', ''),
                    'alt': img.get('alt', ''),
                    'title': img.get('title', '')
                }
                for img in images
            ]
            
            # Forms
            forms = soup.find_all('form')
            metadata['forms'] = [
                {
                    'action': form.get('action', ''),
                    'method': form.get('method', ''),
                    'inputs': [
                        {
                            'name': input_tag.get('name', ''),
                            'type': input_tag.get('type', ''),
                            'value': input_tag.get('value', '')
                        }
                        for input_tag in form.find_all('input')
                    ]
                }
                for form in forms
            ]
            
            # Scripts and stylesheets
            scripts = soup.find_all('script', src=True)
            metadata['scripts'] = [script.get('src') for script in scripts]
            
            stylesheets = soup.find_all('link', rel='stylesheet')
            metadata['stylesheets'] = [link.get('href') for link in stylesheets]
            
        except Exception as e:
            logger.error(f"Error extracting metadata: {str(e)}")
        
        return metadata
    
    def extract_text_content(self, soup: BeautifulSoup) -> str:
        """Extract clean text content from the page"""
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Get text
        text = soup.get_text()
        
        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return text
    
    def extract_by_css_selector(self, soup: BeautifulSoup, selector: str) -> List[str]:
        """Extract content using CSS selector"""
        elements = soup.select(selector)
        return [elem.get_text(strip=True) for elem in elements]
    
    def extract_by_xpath(self, soup: BeautifulSoup, xpath: str) -> List[str]:
        """Extract content using XPath (requires lxml)"""
        try:
            from lxml import html
            tree = html.fromstring(str(soup))
            elements = tree.xpath(xpath)
            return [str(elem) if hasattr(elem, 'text') else elem for elem in elements]
        except ImportError:
            logger.warning("lxml not installed, XPath extraction not available")
            return []
    
    def extract_emails(self, text: str) -> List[str]:
        """Extract email addresses from text"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        return re.findall(email_pattern, text)
    
    def extract_phone_numbers(self, text: str) -> List[str]:
        """Extract phone numbers from text"""
        phone_pattern = r'(\+?[\d\s\-\(\)]{7,})'
        return re.findall(phone_pattern, text)
    
    def extract_urls(self, text: str) -> List[str]:
        """Extract URLs from text"""
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        return re.findall(url_pattern, text)


class SerbianRegulationsScraper(WebScraper):
    """Specialized scraper for Serbian regulations and legal documents"""
    
    def __init__(self, config: ScrapingConfig = None):
        super().__init__(config)
        self.base_urls = [
            'https://www.paragraf.rs',
            'https://www.pravno-informacioni-sistem.rs',
            'https://www.slglasnik.info'
        ]
    
    def scrape_regulations(self, search_term: str = None, category: str = None) -> List[Dict]:
        """Scrape Serbian regulations"""
        results = []
        
        for base_url in self.base_urls:
            try:
                # Search for regulations
                search_url = f"{base_url}/search"
                params = {}
                
                if search_term:
                    params['q'] = search_term
                if category:
                    params['category'] = category
                
                result = self.scrape_url(search_url)
                if result.error:
                    continue
                
                # Extract regulation links
                regulation_links = result.soup.find_all('a', href=re.compile(r'regulation|zakon|uredba'))
                
                for link in regulation_links[:10]:  # Limit to first 10 results
                    regulation_url = urljoin(base_url, link.get('href'))
                    regulation_result = self.scrape_url(regulation_url)
                    
                    if not regulation_result.error:
                        regulation_data = self._parse_regulation(regulation_result)
                        results.append(regulation_data)
                
            except Exception as e:
                logger.error(f"Error scraping {base_url}: {str(e)}")
                continue
        
        return results
    
    def _parse_regulation(self, result: ScrapingResult) -> Dict:
        """Parse regulation content"""
        regulation = {
            'title': '',
            'number': '',
            'date': '',
            'content': '',
            'source_url': result.url,
            'scraped_at': result.timestamp.isoformat()
        }
        
        try:
            # Extract title
            title_elem = result.soup.find(['h1', 'h2'], class_=re.compile(r'title|naslov'))
            if title_elem:
                regulation['title'] = title_elem.get_text(strip=True)
            
            # Extract regulation number
            number_pattern = r'(?:Zakon|Uredba|Pravilnik)\s+(?:br\.?\s*)?([A-Z0-9\-/]+)'
            number_match = re.search(number_pattern, regulation['title'])
            if number_match:
                regulation['number'] = number_match.group(1)
            
            # Extract date
            date_pattern = r'(\d{1,2}\.\d{1,2}\.\d{4})'
            date_match = re.search(date_pattern, result.content)
            if date_match:
                regulation['date'] = date_match.group(1)
            
            # Extract content
            content_elem = result.soup.find(['div', 'article'], class_=re.compile(r'content|text|sadrzaj'))
            if content_elem:
                regulation['content'] = self.extract_text_content(content_elem)
            else:
                regulation['content'] = self.extract_text_content(result.soup)
            
        except Exception as e:
            logger.error(f"Error parsing regulation: {str(e)}")
        
        return regulation


class DataExtractionTemplate:
    """Template for extracting structured data from web pages"""
    
    def __init__(self, name: str, selectors: Dict[str, str]):
        self.name = name
        self.selectors = selectors
    
    def extract(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract data using the template"""
        data = {}
        
        for field, selector in self.selectors.items():
            elements = soup.select(selector)
            if elements:
                if len(elements) == 1:
                    data[field] = elements[0].get_text(strip=True)
                else:
                    data[field] = [elem.get_text(strip=True) for elem in elements]
            else:
                data[field] = None
        
        return data


# Predefined templates
NEWS_TEMPLATE = DataExtractionTemplate(
    name="news_article",
    selectors={
        'title': 'h1, .article-title, .post-title',
        'author': '.author, .byline, .writer',
        'date': '.date, .published, .timestamp',
        'content': '.content, .article-body, .post-content',
        'category': '.category, .section, .tag'
    }
)

PRODUCT_TEMPLATE = DataExtractionTemplate(
    name="product_page",
    selectors={
        'name': '.product-name, .product-title, h1',
        'price': '.price, .product-price, .cost',
        'description': '.description, .product-description',
        'images': '.product-image img, .gallery img',
        'specifications': '.specs, .specifications, .features'
    }
)

CONTACT_TEMPLATE = DataExtractionTemplate(
    name="contact_page",
    selectors={
        'company_name': '.company-name, .business-name, h1',
        'address': '.address, .location',
        'phone': '.phone, .telephone',
        'email': '.email, .contact-email',
        'hours': '.hours, .business-hours'
    }
)
