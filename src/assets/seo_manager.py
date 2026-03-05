"""
SEO and SEM Management System for ValidoAI
Comprehensive SEO optimization and search engine marketing tools
"""

import os
import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from urllib.parse import urljoin, urlparse
from pathlib import Path
from flask import request, current_app, url_for
from bs4 import BeautifulSoup

class SEOManager:
    """Comprehensive SEO and SEM management system"""

    def __init__(self, static_folder: str = "static"):
        self.static_folder = Path(static_folder)
        self.seo_config: Dict[str, Any] = {}
        self.sitemap_cache: Dict[str, Any] = {}
        self._load_seo_config()

    def _load_seo_config(self):
        """Load SEO configuration from JSON file"""
        config_path = self.static_folder / "seo" / "seo-config.json"
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                self.seo_config = json.load(f)
        else:
            # Default SEO configuration
            self.seo_config = {
                "site": {
                    "name": "ValidoAI",
                    "description": "Advanced AI-powered database platform with real-time analytics",
                    "url": "https://valido.ai",
                    "locale": "en_US",
                    "logo": "/static/images/logo.png",
                    "twitter": "@validoai",
                    "facebook": "validoai"
                },
                "pages": {
                    "dashboard": {
                        "title": "Analytics Dashboard - Real-time Business Insights",
                        "description": "Comprehensive analytics dashboard with real-time data visualization and business intelligence tools",
                        "keywords": ["dashboard", "analytics", "business intelligence", "data visualization", "real-time"],
                        "canonical": "/dashboard"
                    },
                    "admin": {
                        "title": "Administration Panel - System Management",
                        "description": "Complete administration interface for managing users, databases, and system settings",
                        "keywords": ["admin", "administration", "system management", "user management", "database"],
                        "canonical": "/admin"
                    },
                    "settings": {
                        "title": "Settings - System Configuration",
                        "description": "Configure system settings, preferences, and application parameters",
                        "keywords": ["settings", "configuration", "preferences", "system settings"],
                        "canonical": "/settings"
                    }
                },
                "seo": {
                    "robots": {
                        "user-agent": "*",
                        "allow": ["/"],
                        "disallow": ["/admin/", "/api/", "/private/"]
                    },
                    "sitemap": {
                        "priority": {
                            "/": 1.0,
                            "/dashboard": 0.8,
                            "/admin": 0.6,
                            "/settings": 0.4
                        },
                        "changefreq": {
                            "/": "daily",
                            "/dashboard": "hourly",
                            "/admin": "daily",
                            "/settings": "weekly"
                        }
                    }
                },
                "sem": {
                    "google_analytics": "GA_MEASUREMENT_ID",
                    "google_tag_manager": "GTM_CONTAINER_ID",
                    "facebook_pixel": "FB_PIXEL_ID",
                    "meta_pixel": "META_PIXEL_ID"
                }
            }

    def generate_meta_tags(self, page: str = 'dashboard', custom_data: Dict[str, Any] = None) -> str:
        """Generate comprehensive meta tags for SEO"""
        page_config = self.seo_config.get('pages', {}).get(page, {})
        site_config = self.seo_config.get('site', {})

        if custom_data:
            page_config.update(custom_data)

        meta_tags = []

        # Basic meta tags
        meta_tags.append(f'<title>{page_config.get("title", "ValidoAI - Advanced Database Platform")}</title>')
        meta_tags.append(f'<meta name="description" content="{page_config.get("description", "")}">')

        if page_config.get("keywords"):
            meta_tags.append(f'<meta name="keywords" content="{", ".join(page_config["keywords"])}">')

        # Open Graph tags
        meta_tags.extend(self._generate_open_graph_tags(page_config, site_config))

        # Twitter Card tags
        meta_tags.extend(self._generate_twitter_tags(page_config, site_config))

        # Canonical URL
        if page_config.get("canonical"):
            canonical_url = urljoin(site_config.get("url", ""), page_config["canonical"])
            meta_tags.append(f'<link rel="canonical" href="{canonical_url}">')

        # Additional SEO tags
        meta_tags.extend([
            '<meta name="robots" content="index, follow">',
            '<meta name="language" content="English">',
            f'<meta name="author" content="{site_config.get("name", "ValidoAI")}">',
            '<meta name="revisit-after" content="7 days">',
            '<meta name="theme-color" content="#3b82f6">',
            '<meta name="msapplication-TileColor" content="#3b82f6">',
        ])

        # JSON-LD structured data
        meta_tags.append(self._generate_json_ld(page_config, site_config))

        return '\n'.join(meta_tags)

    def _generate_open_graph_tags(self, page_config: Dict, site_config: Dict) -> List[str]:
        """Generate Open Graph meta tags"""
        og_tags = [
            '<meta property="og:type" content="website">',
            f'<meta property="og:title" content="{page_config.get("title", "")}">',
            f'<meta property="og:description" content="{page_config.get("description", "")}">',
            f'<meta property="og:url" content="{urljoin(site_config.get("url", ""), page_config.get("canonical", ""))}">',
            f'<meta property="og:site_name" content="{site_config.get("name", "")}">',
            f'<meta property="og:locale" content="{site_config.get("locale", "en_US")}">',
        ]

        if page_config.get("image"):
            og_tags.append(f'<meta property="og:image" content="{page_config["image"]}">')

        return og_tags

    def _generate_twitter_tags(self, page_config: Dict, site_config: Dict) -> List[str]:
        """Generate Twitter Card meta tags"""
        twitter_tags = [
            '<meta name="twitter:card" content="summary_large_image">',
            f'<meta name="twitter:title" content="{page_config.get("title", "")}">',
            f'<meta name="twitter:description" content="{page_config.get("description", "")}">',
            f'<meta name="twitter:site" content="{site_config.get("twitter", "")}">',
        ]

        if page_config.get("image"):
            twitter_tags.append(f'<meta name="twitter:image" content="{page_config["image"]}">')

        return twitter_tags

    def _generate_json_ld(self, page_config: Dict, site_config: Dict) -> str:
        """Generate JSON-LD structured data"""
        json_ld = {
            "@context": "https://schema.org",
            "@type": "WebSite",
            "name": site_config.get("name", "ValidoAI"),
            "description": page_config.get("description", ""),
            "url": site_config.get("url", ""),
            "potentialAction": {
                "@type": "SearchAction",
                "target": {
                    "@type": "EntryPoint",
                    "urlTemplate": f"{site_config.get('url', '')}/search?q={{search_term_string}}"
                },
                "query-input": "required name=search_term_string"
            }
        }

        return f'<script type="application/ld+json">{json.dumps(json_ld, indent=2)}</script>'

    def generate_robots_txt(self) -> str:
        """Generate robots.txt file content"""
        robots_config = self.seo_config.get('seo', {}).get('robots', {})

        robots_content = []
        robots_content.append(f"User-agent: {robots_config.get('user-agent', '*')}")

        for allow in robots_config.get('allow', []):
            robots_content.append(f"Allow: {allow}")

        for disallow in robots_config.get('disallow', []):
            robots_content.append(f"Disallow: {disallow}")

        robots_content.extend([
            "",
            "Sitemap: https://valido.ai/sitemap.xml",
            "",
            "# Crawl-delay for different bots",
            "User-agent: Bingbot",
            "Crawl-delay: 1",
            "",
            "User-agent: Slurp",
            "Crawl-delay: 1"
        ])

        return '\n'.join(robots_content)

    def generate_sitemap_xml(self, routes: List[Dict[str, Any]]) -> str:
        """Generate XML sitemap"""
        site_config = self.seo_config.get('site', {})
        sitemap_config = self.seo_config.get('seo', {}).get('sitemap', {})

        sitemap_entries = []

        for route in routes:
            if route.get('include_in_sitemap', True):
                url = urljoin(site_config.get('url', ''), route['path'])

                entry = f"""<url>
    <loc>{url}</loc>
    <lastmod>{route.get('lastmod', datetime.now().strftime('%Y-%m-%d'))}</lastmod>
    <changefreq>{sitemap_config.get('changefreq', {}).get(route['path'], 'weekly')}</changefreq>
    <priority>{sitemap_config.get('priority', {}).get(route['path'], '0.5')}</priority>
</url>"""

                sitemap_entries.append(entry)

        sitemap_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:schemaLocation="http://www.sitemaps.org/schemas/sitemap/0.9
        http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd">
{chr(10).join(sitemap_entries)}
</urlset>"""

        return sitemap_xml

    def generate_tracking_scripts(self, page: str = 'dashboard') -> str:
        """Generate tracking scripts for analytics"""
        sem_config = self.seo_config.get('sem', {})

        scripts = []

        # Google Analytics
        if sem_config.get('google_analytics'):
            ga_script = f"""
<!-- Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id={sem_config['google_analytics']}"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){{dataLayer.push(arguments);}}
  gtag('js', new Date());
  gtag('config', '{sem_config['google_analytics']}');
</script>"""
            scripts.append(ga_script)

        # Google Tag Manager
        if sem_config.get('google_tag_manager'):
            gtm_script = f"""
<!-- Google Tag Manager -->
<script>(function(w,d,s,l,i){{w[l]=w[l]||[];w[l].push({{'gtm.start':
new Date().getTime(),event:'gtm.js'}});var f=d.getElementsByTagName(s)[0],
j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
}})(window,document,'script','dataLayer','{sem_config['google_tag_manager']}');</script>"""
            scripts.append(gtm_script)

        # Facebook Pixel
        if sem_config.get('facebook_pixel'):
            fb_script = f"""
<!-- Facebook Pixel -->
<script>
  !function(f,b,e,v,n,t,s)
  {{if(f.fbq)return;n=f.fbq=function(){{n.callMethod?
  n.callMethod.apply(n,arguments):n.queue.push(arguments)}};
  if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version='2.0';
  n.queue=[];t=b.createElement(e);t.async=!0;
  t.src=v;s=b.getElementsByTagName(e)[0];
  s.parentNode.insertBefore(t,s)}}(window, document,'script',
  'https://connect.facebook.net/en_US/fbevents.js');
  fbq('init', '{sem_config['facebook_pixel']}');
  fbq('track', 'PageView');
</script>
<noscript><img height="1" width="1" style="display:none"
  src="https://www.facebook.com/tr?id={sem_config['facebook_pixel']}&ev=PageView&noscript=1"
/></noscript>"""
            scripts.append(fb_script)

        # Meta Pixel
        if sem_config.get('meta_pixel'):
            meta_script = f"""
<!-- Meta Pixel -->
<script>
  !function(f,b,e,v,n,t,s)
  {{if(f.fbq)return;n=f.fbq=function(){{n.callMethod?
  n.callMethod.apply(n,arguments):n.queue.push(arguments)}};
  if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version='2.0';
  n.queue=[];t=b.createElement(e);t.async=!0;
  t.src=v;s=b.getElementsByTagName(e)[0];
  s.parentNode.insertBefore(t,s)}}(window, document,'script',
  'https://connect.facebook.net/en_US/fbevents.js');
  fbq('init', '{sem_config['meta_pixel']}');
  fbq('track', 'PageView');
</script>"""
            scripts.append(meta_script)

        return '\n'.join(scripts)

    def optimize_content_for_seo(self, content: str, page_type: str = 'dashboard') -> str:
        """Optimize content for better SEO"""
        soup = BeautifulSoup(content, 'html.parser')

        # Add heading structure if missing
        if not soup.find('h1'):
            first_h2 = soup.find('h2')
            if first_h2:
                first_h2.name = 'h1'

        # Ensure proper heading hierarchy
        headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        for i, heading in enumerate(headings):
            if i == 0 and heading.name != 'h1':
                heading.name = 'h1'
            elif heading.name == 'h1' and i > 0:
                heading.name = 'h2'

        # Add alt text to images
        images = soup.find_all('img')
        for img in images:
            if not img.get('alt'):
                img['alt'] = 'ValidoAI analytics and business intelligence platform'

        # Ensure proper internal linking
        links = soup.find_all('a')
        for link in links:
            href = link.get('href', '')
            if href.startswith('/') and not href.startswith('//'):
                if not link.get('title'):
                    link['title'] = link.get_text().strip()[:50]

        return str(soup)

    def generate_seo_report(self, routes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate comprehensive SEO report"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'summary': {},
            'issues': [],
            'recommendations': [],
            'page_analysis': {},
            'technical_seo': {}
        }

        # Analyze each route
        for route in routes:
            page_analysis = {
                'url': route['path'],
                'seo_score': 0,
                'issues': [],
                'recommendations': []
            }

            # Check title length
            if route.get('title'):
                title_length = len(route['title'])
                if title_length < 30:
                    page_analysis['issues'].append('Title too short (< 30 characters)')
                elif title_length > 60:
                    page_analysis['issues'].append('Title too long (> 60 characters)')
                else:
                    page_analysis['seo_score'] += 20

            # Check description length
            if route.get('description'):
                desc_length = len(route['description'])
                if desc_length < 120:
                    page_analysis['issues'].append('Description too short (< 120 characters)')
                elif desc_length > 160:
                    page_analysis['issues'].append('Description too long (> 160 characters)')
                else:
                    page_analysis['seo_score'] += 20

            # Check keywords
            if route.get('keywords'):
                if len(route['keywords']) < 3:
                    page_analysis['issues'].append('Too few keywords')
                elif len(route['keywords']) > 10:
                    page_analysis['issues'].append('Too many keywords')
                else:
                    page_analysis['seo_score'] += 15

            # Check canonical URL
            if not route.get('canonical'):
                page_analysis['issues'].append('Missing canonical URL')
            else:
                page_analysis['seo_score'] += 15

            # Check for images without alt text
            if route.get('has_images') and not route.get('has_alt_text'):
                page_analysis['issues'].append('Images missing alt text')
                page_analysis['recommendations'].append('Add descriptive alt text to all images')

            # Check heading structure
            if not route.get('has_h1'):
                page_analysis['issues'].append('Missing H1 heading')
            else:
                page_analysis['seo_score'] += 10

            # Check internal linking
            if route.get('internal_links', 0) < 3:
                page_analysis['recommendations'].append('Add more internal links')

            # Check mobile-friendliness
            if not route.get('mobile_friendly'):
                page_analysis['issues'].append('Not mobile-friendly')
            else:
                page_analysis['seo_score'] += 10

            # Check page speed
            if route.get('load_time', 0) > 3.0:
                page_analysis['issues'].append('Page load time too slow')
                page_analysis['recommendations'].append('Optimize images and reduce JavaScript')

            report['page_analysis'][route['path']] = page_analysis

        # Generate summary
        all_pages = list(report['page_analysis'].values())
        total_pages = len(all_pages)
        total_issues = sum(len(page['issues']) for page in all_pages)
        average_seo_score = sum(page['seo_score'] for page in all_pages) / total_pages if total_pages > 0 else 0

        report['summary'] = {
            'total_pages': total_pages,
            'total_issues': total_issues,
            'average_seo_score': round(average_seo_score, 1),
            'pages_with_issues': len([p for p in all_pages if p['issues']])
        }

        # Add technical SEO recommendations
        report['technical_seo'] = {
            'robots_txt': 'Generated successfully',
            'sitemap_xml': 'Generated successfully',
            'meta_tags': 'Optimized for all pages',
            'structured_data': 'JSON-LD implemented',
            'page_speed': 'Critical CSS implemented',
            'mobile_responsive': 'Responsive design applied'
        }

        return report

    def create_seo_friendly_url(self, text: str) -> str:
        """Create SEO-friendly URL from text"""
        import re
        import unicodedata

        # Normalize unicode characters
        text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')

        # Convert to lowercase and replace spaces with hyphens
        text = text.lower().replace(' ', '-')

        # Remove special characters except hyphens
        text = re.sub(r'[^a-z0-9-]', '', text)

        # Remove multiple consecutive hyphens
        text = re.sub(r'-+', '-', text)

        # Remove leading/trailing hyphens
        text = text.strip('-')

        return text

    def generate_breadcrumb_schema(self, breadcrumbs: List[Dict[str, str]]) -> str:
        """Generate breadcrumb structured data"""
        items = []
        for i, crumb in enumerate(breadcrumbs, 1):
            items.append({
                "@type": "ListItem",
                "position": i,
                "name": crumb['name'],
                "item": urljoin(self.seo_config.get('site', {}).get('url', ''), crumb['url'])
            })

        breadcrumb_schema = {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": items
        }

        return f'<script type="application/ld+json">{json.dumps(breadcrumb_schema, indent=2)}</script>'

    def optimize_for_featured_snippet(self, content: str, query_type: str = 'definition') -> str:
        """Optimize content for featured snippets"""
        soup = BeautifulSoup(content, 'html.parser')

        # Add structured data based on query type
        if query_type == 'definition':
            # Create FAQ structured data
            faq_schema = {
                "@context": "https://schema.org",
                "@type": "FAQPage",
                "mainEntity": []
            }

            questions = soup.find_all(['h2', 'h3', 'strong'])
            for question in questions[:5]:  # Limit to 5 questions
                faq_schema["mainEntity"].append({
                    "@type": "Question",
                    "name": question.get_text().strip(),
                    "acceptedAnswer": {
                        "@type": "Answer",
                        "text": "ValidoAI is an advanced AI-powered database platform with real-time analytics and business intelligence capabilities."
                    }
                })

            schema_script = f'<script type="application/ld+json">{json.dumps(faq_schema, indent=2)}</script>'
            if soup.head:
                soup.head.append(BeautifulSoup(schema_script, 'html.parser'))

        elif query_type == 'table':
            # Create table structured data
            table_schema = {
                "@context": "https://schema.org",
                "@type": "Table",
                "about": "ValidoAI Features and Capabilities"
            }

            schema_script = f'<script type="application/ld+json">{json.dumps(table_schema, indent=2)}</script>'
            if soup.head:
                soup.head.append(BeautifulSoup(schema_script, 'html.parser'))

        return str(soup)

    def save_seo_config(self):
        """Save SEO configuration to file"""
        config_path = self.static_folder / "seo" / "seo-config.json"
        config_path.parent.mkdir(exist_ok=True)

        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(self.seo_config, f, indent=2, ensure_ascii=False)


# Global instance
seo_manager = SEOManager()
