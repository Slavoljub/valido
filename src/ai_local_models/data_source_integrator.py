#!/usr/bin/env python3
"""
Data Source Integration System
Integrates various external data sources including WordPress, WooCommerce, and other popular services
"""

import os
import json
import requests
import logging
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
from urllib.parse import urljoin, urlparse
import base64
import hashlib
import hmac
import time


logger = logging.getLogger(__name__)


class DataSourceIntegrator:
    """Main data source integration manager"""

    def __init__(self):
        """Initialize data source integrator"""
        self.sources = {}
        self.cache = {}
        self._load_configurations()

    def _load_configurations(self):
        """Load data source configurations from environment"""
        # WordPress & WooCommerce
        if os.environ.get('WORDPRESS_ENABLED', 'false').lower() == 'true':
            self.sources['wordpress'] = WordPressIntegration()
        if os.environ.get('WOOCOMMERCE_ENABLED', 'false').lower() == 'true':
            self.sources['woocommerce'] = WooCommerceIntegration()

        # E-commerce Platforms
        if os.environ.get('SHOPIFY_ENABLED', 'false').lower() == 'true':
            self.sources['shopify'] = ShopifyIntegration()
        if os.environ.get('MAGENTO_ENABLED', 'false').lower() == 'true':
            self.sources['magento'] = MagentoIntegration()
        if os.environ.get('BIGCOMMERCE_ENABLED', 'false').lower() == 'true':
            self.sources['bigcommerce'] = BigCommerceIntegration()

        # Analytics & Marketing
        if os.environ.get('GOOGLE_ANALYTICS_ENABLED', 'false').lower() == 'true':
            self.sources['google_analytics'] = GoogleAnalyticsIntegration()
        if os.environ.get('FACEBOOK_ADS_ENABLED', 'false').lower() == 'true':
            self.sources['facebook_ads'] = FacebookAdsIntegration()

        # Payment Processors
        if os.environ.get('STRIPE_ENABLED', 'false').lower() == 'true':
            self.sources['stripe'] = StripeIntegration()
        if os.environ.get('PAYPAL_ENABLED', 'false').lower() == 'true':
            self.sources['paypal'] = PayPalIntegration()

        # Accounting Software
        if os.environ.get('QUICKBOOKS_ENABLED', 'false').lower() == 'true':
            self.sources['quickbooks'] = QuickBooksIntegration()
        if os.environ.get('XERO_ENABLED', 'false').lower() == 'true':
            self.sources['xero'] = XeroIntegration()
        if os.environ.get('FRESHBOOKS_ENABLED', 'false').lower() == 'true':
            self.sources['freshbooks'] = FreshBooksIntegration()
        if os.environ.get('ZOHO_BOOKS_ENABLED', 'false').lower() == 'true':
            self.sources['zoho_books'] = ZohoBooksIntegration()
        if os.environ.get('WAVE_ENABLED', 'false').lower() == 'true':
            self.sources['wave'] = WaveIntegration()

        # CRM Systems
        if os.environ.get('SALESFORCE_ENABLED', 'false').lower() == 'true':
            self.sources['salesforce'] = SalesforceIntegration()
        if os.environ.get('HUBSPOT_ENABLED', 'false').lower() == 'true':
            self.sources['hubspot'] = HubSpotIntegration()
        if os.environ.get('PIPEDRIVE_ENABLED', 'false').lower() == 'true':
            self.sources['pipedrive'] = PipedriveIntegration()

    def get_available_sources(self) -> List[str]:
        """Get list of available data sources"""
        return list(self.sources.keys())

    def get_data_from_source(self, source_name: str, endpoint: str = '',
                           params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get data from a specific source"""
        if source_name not in self.sources:
            return {
                'success': False,
                'error': f'Data source {source_name} not available'
            }

        try:
            source = self.sources[source_name]
            return source.get_data(endpoint, params)
        except Exception as e:
            logger.error(f"Error getting data from {source_name}: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def get_all_data_summary(self) -> Dict[str, Any]:
        """Get summary of data from all available sources"""
        summary = {
            'timestamp': datetime.now().isoformat(),
            'sources': {},
            'total_records': 0,
            'errors': []
        }

        for source_name, source in self.sources.items():
            try:
                if hasattr(source, 'get_summary'):
                    source_summary = source.get_summary()
                    summary['sources'][source_name] = source_summary
                    summary['total_records'] += source_summary.get('record_count', 0)
                else:
                    summary['sources'][source_name] = {'status': 'available', 'record_count': 0}
            except Exception as e:
                summary['errors'].append(f"{source_name}: {str(e)}")
                summary['sources'][source_name] = {'status': 'error', 'error': str(e)}

        return summary


class BaseDataSource:
    """Base class for data source integrations"""

    def __init__(self, source_name: str):
        """Initialize base data source"""
        self.source_name = source_name
        self.base_url = ""
        self.api_key = ""
        self.auth_headers = {}
        self.timeout = int(os.environ.get('DATA_SOURCE_TIMEOUT', '30'))
        self.max_retries = int(os.environ.get('DATA_SOURCE_MAX_RETRIES', '3'))
        self.cache_enabled = os.environ.get('DATA_SOURCE_CACHE_ENABLED', 'true').lower() == 'true'
        self.cache_timeout = int(os.environ.get('DATA_SOURCE_CACHE_TIMEOUT', '3600'))

    def _make_request(self, method: str, endpoint: str, params: Dict[str, Any] = None,
                     data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Make HTTP request with retry logic"""
        url = urljoin(self.base_url, endpoint)
        headers = self.auth_headers.copy()

        for attempt in range(self.max_retries):
            try:
                response = requests.request(
                    method=method,
                    url=url,
                    params=params,
                    json=data,
                    headers=headers,
                    timeout=self.timeout
                )

                if response.status_code == 200:
                    return {'success': True, 'data': response.json()}
                elif response.status_code == 401:
                    return {'success': False, 'error': 'Authentication failed'}
                elif response.status_code == 403:
                    return {'success': False, 'error': 'Access forbidden'}
                elif response.status_code == 404:
                    return {'success': False, 'error': 'Resource not found'}
                else:
                    return {'success': False, 'error': f'HTTP {response.status_code}: {response.text}'}

            except requests.exceptions.RequestException as e:
                if attempt == self.max_retries - 1:
                    return {'success': False, 'error': str(e)}
                time.sleep(2 ** attempt)  # Exponential backoff

        return {'success': False, 'error': 'Max retries exceeded'}

    def get_data(self, endpoint: str = '', params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get data from the source"""
        cache_key = f"{self.source_name}:{endpoint}:{json.dumps(params or {})}"

        if self.cache_enabled and cache_key in self._cache:
            cached_data = self._cache[cache_key]
            if datetime.now() - cached_data['timestamp'] < timedelta(seconds=self.cache_timeout):
                return cached_data['data']

        result = self._make_request('GET', endpoint, params)

        if self.cache_enabled and result['success']:
            self._cache[cache_key] = {
                'data': result,
                'timestamp': datetime.now()
            }

        return result

    def post_data(self, endpoint: str = '', data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Post data to the source"""
        return self._make_request('POST', endpoint, data=data)


class WordPressIntegration(BaseDataSource):
    """WordPress REST API integration"""

    def __init__(self):
        super().__init__('wordpress')
        self.base_url = os.environ.get('WORDPRESS_URL', '')
        self.username = os.environ.get('WORDPRESS_USERNAME', '')
        self.password = os.environ.get('WORDPRESS_PASSWORD', '')
        self.rest_base = os.environ.get('WORDPRESS_REST_BASE', '/wp-json/wp/v2')

        if self.username and self.password:
            credentials = f"{self.username}:{self.password}"
            token = base64.b64encode(credentials.encode()).decode()
            self.auth_headers = {
                'Authorization': f'Basic {token}',
                'Content-Type': 'application/json'
            }

    def get_posts(self, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get WordPress posts"""
        return self.get_data(f"{self.rest_base}/posts", params)

    def get_pages(self, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get WordPress pages"""
        return self.get_data(f"{self.rest_base}/pages", params)

    def get_users(self, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get WordPress users"""
        return self.get_data(f"{self.rest_base}/users", params)

    def get_summary(self) -> Dict[str, Any]:
        """Get WordPress summary"""
        posts_result = self.get_posts({'per_page': 1})
        pages_result = self.get_pages({'per_page': 1})

        return {
            'status': 'connected',
            'posts_count': posts_result.get('data', {}).get('found', 0) if posts_result['success'] else 0,
            'pages_count': pages_result.get('data', {}).get('found', 0) if pages_result['success'] else 0,
            'record_count': posts_result.get('data', {}).get('found', 0) + pages_result.get('data', {}).get('found', 0)
        }


class WooCommerceIntegration(BaseDataSource):
    """WooCommerce REST API integration"""

    def __init__(self):
        super().__init__('woocommerce')
        self.base_url = os.environ.get('WOOCOMMERCE_URL', '')
        self.consumer_key = os.environ.get('WOOCOMMERCE_CONSUMER_KEY', '')
        self.consumer_secret = os.environ.get('WOOCOMMERCE_CONSUMER_SECRET', '')
        self.api_version = os.environ.get('WOOCOMMERCE_API_VERSION', 'wc/v3')

        self.auth_headers = {
            'Content-Type': 'application/json'
        }

    def _make_request(self, method: str, endpoint: str, params: Dict[str, Any] = None,
                     data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Override to add WooCommerce authentication"""
        if params is None:
            params = {}

        # Add authentication parameters
        params['consumer_key'] = self.consumer_key
        params['consumer_secret'] = self.consumer_secret

        return super()._make_request(method, f"{self.api_version}/{endpoint}", params, data)

    def get_orders(self, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get WooCommerce orders"""
        return self.get_data("orders", params)

    def get_products(self, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get WooCommerce products"""
        return self.get_data("products", params)

    def get_customers(self, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get WooCommerce customers"""
        return self.get_data("customers", params)

    def get_summary(self) -> Dict[str, Any]:
        """Get WooCommerce summary"""
        orders_result = self.get_orders({'per_page': 1})
        products_result = self.get_products({'per_page': 1})
        customers_result = self.get_customers({'per_page': 1})

        return {
            'status': 'connected',
            'orders_count': len(orders_result.get('data', [])) if orders_result['success'] else 0,
            'products_count': len(products_result.get('data', [])) if products_result['success'] else 0,
            'customers_count': len(customers_result.get('data', [])) if customers_result['success'] else 0,
            'record_count': (len(orders_result.get('data', [])) + len(products_result.get('data', [])) +
                           len(customers_result.get('data', [])))
        }


class ShopifyIntegration(BaseDataSource):
    """Shopify REST API integration"""

    def __init__(self):
        super().__init__('shopify')
        store_url = os.environ.get('SHOPIFY_STORE_URL', '')
        access_token = os.environ.get('SHOPIFY_ACCESS_TOKEN', '')
        api_version = os.environ.get('SHOPIFY_API_VERSION', '2024-01')

        self.base_url = f"https://{store_url}/admin/api/{api_version}"
        self.auth_headers = {
            'X-Shopify-Access-Token': access_token,
            'Content-Type': 'application/json'
        }

    def get_orders(self, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get Shopify orders"""
        return self.get_data("orders.json", params)

    def get_products(self, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get Shopify products"""
        return self.get_data("products.json", params)

    def get_customers(self, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get Shopify customers"""
        return self.get_data("customers.json", params)

    def get_summary(self) -> Dict[str, Any]:
        """Get Shopify summary"""
        orders_result = self.get_orders({'limit': 1})
        products_result = self.get_products({'limit': 1})
        customers_result = self.get_customers({'limit': 1})

        return {
            'status': 'connected',
            'orders_count': len(orders_result.get('data', {}).get('orders', [])) if orders_result['success'] else 0,
            'products_count': len(products_result.get('data', {}).get('products', [])) if products_result['success'] else 0,
            'customers_count': len(customers_result.get('data', {}).get('customers', [])) if customers_result['success'] else 0,
            'record_count': (len(orders_result.get('data', {}).get('orders', [])) +
                           len(products_result.get('data', {}).get('products', [])) +
                           len(customers_result.get('data', {}).get('customers', [])))
        }


class StripeIntegration(BaseDataSource):
    """Stripe API integration"""

    def __init__(self):
        super().__init__('stripe')
        self.api_key = os.environ.get('STRIPE_SECRET_KEY', '')
        self.auth_headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        self.base_url = "https://api.stripe.com/v1"

    def get_balance(self) -> Dict[str, Any]:
        """Get Stripe balance"""
        return self.get_data("balance")

    def get_charges(self, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get Stripe charges"""
        return self.get_data("charges", params)

    def get_customers(self, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get Stripe customers"""
        return self.get_data("customers", params)

    def get_subscriptions(self, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get Stripe subscriptions"""
        return self.get_data("subscriptions", params)

    def get_summary(self) -> Dict[str, Any]:
        """Get Stripe summary"""
        balance_result = self.get_balance()
        charges_result = self.get_charges({'limit': 1})
        customers_result = self.get_customers({'limit': 1})

        balance = balance_result.get('data', {})
        available_balance = sum(b.get('amount', 0) for b in balance.get('available', [])) if balance_result['success'] else 0

        return {
            'status': 'connected',
            'balance_available': available_balance,
            'charges_count': len(charges_result.get('data', {}).get('data', [])) if charges_result['success'] else 0,
            'customers_count': len(customers_result.get('data', {}).get('data', [])) if customers_result['success'] else 0,
            'record_count': (len(charges_result.get('data', {}).get('data', [])) +
                           len(customers_result.get('data', {}).get('data', [])))
        }


class GoogleAnalyticsIntegration(BaseDataSource):
    """Google Analytics API integration"""

    def __init__(self):
        super().__init__('google_analytics')
        self.property_id = os.environ.get('GOOGLE_ANALYTICS_PROPERTY_ID', '')
        # Note: This would need proper OAuth2 setup for real implementation
        self.base_url = "https://analyticsdata.googleapis.com/v1beta"

    def get_report(self, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get Google Analytics report"""
        if not params:
            params = {
                "property": f"properties/{self.property_id}",
                "dateRanges": [{"startDate": "7daysAgo", "endDate": "today"}],
                "metrics": [{"name": "activeUsers"}, {"name": "sessions"}],
                "dimensions": [{"name": "date"}]
            }
        return self.post_data("properties:batchRunReports", params)

    def get_summary(self) -> Dict[str, Any]:
        """Get Google Analytics summary"""
        report_result = self.get_report()

        return {
            'status': 'connected' if report_result['success'] else 'error',
            'has_data': report_result['success'] and bool(report_result.get('data', {}).get('reports')),
            'record_count': 1 if report_result['success'] else 0
        }


class QuickBooksIntegration(BaseDataSource):
    """QuickBooks API integration"""

    def __init__(self):
        super().__init__('quickbooks')
        self.client_id = os.environ.get('QUICKBOOKS_CLIENT_ID', '')
        self.client_secret = os.environ.get('QUICKBOOKS_CLIENT_SECRET', '')
        self.redirect_uri = os.environ.get('QUICKBOOKS_REDIRECT_URI', '')
        self.base_url = "https://quickbooks.api.intuit.com/v3/company"

        # This would need proper OAuth2 token management
        self.auth_headers = {
            'Authorization': 'Bearer YOUR_ACCESS_TOKEN',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

    def get_company_info(self) -> Dict[str, Any]:
        """Get QuickBooks company info"""
        return self.get_data("companyinfo/1")

    def get_customers(self, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get QuickBooks customers"""
        return self.get_data("query?query=SELECT * FROM Customer", params)

    def get_invoices(self, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get QuickBooks invoices"""
        return self.get_data("query?query=SELECT * FROM Invoice", params)

    def get_summary(self) -> Dict[str, Any]:
        """Get QuickBooks summary"""
        company_result = self.get_company_info()
        customers_result = self.get_customers()
        invoices_result = self.get_invoices()

        return {
            'status': 'connected' if company_result['success'] else 'error',
            'company_name': company_result.get('data', {}).get('CompanyInfo', {}).get('CompanyName'),
            'customers_count': len(customers_result.get('data', {}).get('QueryResponse', {}).get('Customer', [])) if customers_result['success'] else 0,
            'invoices_count': len(invoices_result.get('data', {}).get('QueryResponse', {}).get('Invoice', [])) if invoices_result['success'] else 0,
            'record_count': (len(customers_result.get('data', {}).get('QueryResponse', {}).get('Customer', [])) +
                           len(invoices_result.get('data', {}).get('QueryResponse', {}).get('Invoice', [])))
        }


class SalesforceIntegration(BaseDataSource):
    """Salesforce API integration"""

    def __init__(self):
        super().__init__('salesforce')
        self.username = os.environ.get('SALESFORCE_USERNAME', '')
        self.password = os.environ.get('SALESFORCE_PASSWORD', '')
        self.security_token = os.environ.get('SALESFORCE_SECURITY_TOKEN', '')
        self.domain = os.environ.get('SALESFORCE_DOMAIN', 'login')

        # This would need proper OAuth2 or SOAP login
        self.base_url = f"https://{self.domain}.salesforce.com/services/data/v57.0"
        self.auth_headers = {
            'Authorization': 'Bearer YOUR_ACCESS_TOKEN',
            'Content-Type': 'application/json'
        }

    def get_accounts(self, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get Salesforce accounts"""
        return self.get_data("sobjects/Account", params)

    def get_contacts(self, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get Salesforce contacts"""
        return self.get_data("sobjects/Contact", params)

    def get_opportunities(self, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get Salesforce opportunities"""
        return self.get_data("sobjects/Opportunity", params)

    def get_summary(self) -> Dict[str, Any]:
        """Get Salesforce summary"""
        accounts_result = self.get_accounts()
        contacts_result = self.get_contacts()
        opportunities_result = self.get_opportunities()

        return {
            'status': 'connected' if accounts_result['success'] else 'error',
            'accounts_count': accounts_result.get('data', {}).get('totalSize', 0) if accounts_result['success'] else 0,
            'contacts_count': contacts_result.get('data', {}).get('totalSize', 0) if contacts_result['success'] else 0,
            'opportunities_count': opportunities_result.get('data', {}).get('totalSize', 0) if opportunities_result['success'] else 0,
            'record_count': (accounts_result.get('data', {}).get('totalSize', 0) +
                           contacts_result.get('data', {}).get('totalSize', 0) +
                           opportunities_result.get('data', {}).get('totalSize', 0))
        }


class MagentoIntegration(BaseDataSource):
    """Magento REST API integration"""

    def __init__(self):
        super().__init__('magento')
        self.base_url = os.environ.get('MAGENTO_URL', '')
        self.username = os.environ.get('MAGENTO_USERNAME', '')
        self.password = os.environ.get('MAGENTO_PASSWORD', '')
        self.api_base = os.environ.get('MAGENTO_API_BASE', '/rest/V1')

        # This would need proper OAuth2 token management
        self.auth_headers = {
            'Authorization': 'Bearer YOUR_ACCESS_TOKEN',
            'Content-Type': 'application/json'
        }

    def get_orders(self, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get Magento orders"""
        return self.get_data("orders", params)

    def get_products(self, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get Magento products"""
        return self.get_data("products", params)

    def get_customers(self, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get Magento customers"""
        return self.get_data("customers", params)

    def get_summary(self) -> Dict[str, Any]:
        """Get Magento summary"""
        orders_result = self.get_orders()
        products_result = self.get_products()
        customers_result = self.get_customers()

        return {
            'status': 'connected' if orders_result['success'] else 'error',
            'orders_count': len(orders_result.get('data', {}).get('items', [])) if orders_result['success'] else 0,
            'products_count': len(products_result.get('data', {}).get('items', [])) if products_result['success'] else 0,
            'customers_count': len(customers_result.get('data', {}).get('items', [])) if customers_result['success'] else 0,
            'record_count': (len(orders_result.get('data', {}).get('items', [])) +
                           len(products_result.get('data', {}).get('items', [])) +
                           len(customers_result.get('data', {}).get('items', [])))
        }


class BigCommerceIntegration(BaseDataSource):
    """BigCommerce REST API integration"""

    def __init__(self):
        super().__init__('bigcommerce')
        store_hash = os.environ.get('BIGCOMMERCE_STORE_HASH', '')
        client_id = os.environ.get('BIGCOMMERCE_CLIENT_ID', '')
        access_token = os.environ.get('BIGCOMMERCE_ACCESS_TOKEN', '')
        api_version = os.environ.get('BIGCOMMERCE_API_VERSION', 'v3')

        self.base_url = f"https://api.bigcommerce.com/stores/{store_hash}/{api_version}"
        self.auth_headers = {
            'X-Auth-Client': client_id,
            'X-Auth-Token': access_token,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

    def get_orders(self, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get BigCommerce orders"""
        return self.get_data("orders", params)

    def get_products(self, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get BigCommerce products"""
        return self.get_data("catalog/products", params)

    def get_customers(self, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get BigCommerce customers"""
        return self.get_data("customers", params)

    def get_summary(self) -> Dict[str, Any]:
        """Get BigCommerce summary"""
        orders_result = self.get_orders()
        products_result = self.get_products()
        customers_result = self.get_customers()

        return {
            'status': 'connected' if orders_result['success'] else 'error',
            'orders_count': len(orders_result.get('data', {}).get('data', [])) if orders_result['success'] else 0,
            'products_count': len(products_result.get('data', {}).get('data', [])) if products_result['success'] else 0,
            'customers_count': len(customers_result.get('data', {}).get('data', [])) if customers_result['success'] else 0,
            'record_count': (len(orders_result.get('data', {}).get('data', [])) +
                           len(products_result.get('data', {}).get('data', [])) +
                           len(customers_result.get('data', {}).get('data', [])))
        }


class FacebookAdsIntegration(BaseDataSource):
    """Facebook Ads API integration"""

    def __init__(self):
        super().__init__('facebook_ads')
        self.access_token = os.environ.get('FACEBOOK_ADS_ACCESS_TOKEN', '')
        self.account_id = os.environ.get('FACEBOOK_ADS_ACCOUNT_ID', '')
        self.base_url = "https://graph.facebook.com/v18.0"

        self.auth_headers = {
            'Content-Type': 'application/json'
        }

    def get_campaigns(self, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get Facebook campaigns"""
        if not params:
            params = {}
        params['access_token'] = self.access_token
        return self.get_data(f"act_{self.account_id}/campaigns", params)

    def get_ads(self, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get Facebook ads"""
        if not params:
            params = {}
        params['access_token'] = self.access_token
        return self.get_data(f"act_{self.account_id}/ads", params)

    def get_insights(self, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get Facebook ads insights"""
        if not params:
            params = {}
        params['access_token'] = self.access_token
        return self.get_data(f"act_{self.account_id}/insights", params)

    def get_summary(self) -> Dict[str, Any]:
        """Get Facebook Ads summary"""
        campaigns_result = self.get_campaigns()
        ads_result = self.get_ads()

        return {
            'status': 'connected' if campaigns_result['success'] else 'error',
            'campaigns_count': len(campaigns_result.get('data', {}).get('data', [])) if campaigns_result['success'] else 0,
            'ads_count': len(ads_result.get('data', {}).get('data', [])) if ads_result['success'] else 0,
            'record_count': (len(campaigns_result.get('data', {}).get('data', [])) +
                           len(ads_result.get('data', {}).get('data', [])))
        }


class PayPalIntegration(BaseDataSource):
    """PayPal REST API integration"""

    def __init__(self):
        super().__init__('paypal')
        self.client_id = os.environ.get('PAYPAL_CLIENT_ID', '')
        self.client_secret = os.environ.get('PAYPAL_CLIENT_SECRET', '')
        self.base_url = "https://api.paypal.com/v1"

        # This would need proper OAuth2 token management
        self.auth_headers = {
            'Authorization': 'Bearer YOUR_ACCESS_TOKEN',
            'Content-Type': 'application/json'
        }

    def get_payments(self, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get PayPal payments"""
        return self.get_data("payments/payment", params)

    def get_orders(self, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get PayPal orders"""
        return self.get_data("orders", params)

    def get_invoices(self, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get PayPal invoices"""
        return self.get_data("invoicing/invoices", params)

    def get_summary(self) -> Dict[str, Any]:
        """Get PayPal summary"""
        payments_result = self.get_payments()
        orders_result = self.get_orders()

        return {
            'status': 'connected' if payments_result['success'] else 'error',
            'payments_count': len(payments_result.get('data', [])) if payments_result['success'] else 0,
            'orders_count': len(orders_result.get('data', [])) if orders_result['success'] else 0,
            'record_count': (len(payments_result.get('data', [])) +
                           len(orders_result.get('data', [])))
        }


class XeroIntegration(BaseDataSource):
    """Xero API integration"""

    def __init__(self):
        super().__init__('xero')
        self.client_id = os.environ.get('XERO_CLIENT_ID', '')
        self.client_secret = os.environ.get('XERO_CLIENT_SECRET', '')
        self.base_url = "https://api.xero.com/api.xro/2.0"

        # This would need proper OAuth2 token management
        self.auth_headers = {
            'Authorization': 'Bearer YOUR_ACCESS_TOKEN',
            'Xero-tenant-id': 'YOUR_TENANT_ID',
            'Content-Type': 'application/json'
        }

    def get_invoices(self, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get Xero invoices"""
        return self.get_data("Invoices", params)

    def get_contacts(self, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get Xero contacts"""
        return self.get_data("Contacts", params)

    def get_accounts(self, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get Xero accounts"""
        return self.get_data("Accounts", params)

    def get_summary(self) -> Dict[str, Any]:
        """Get Xero summary"""
        invoices_result = self.get_invoices()
        contacts_result = self.get_contacts()

        return {
            'status': 'connected' if invoices_result['success'] else 'error',
            'invoices_count': len(invoices_result.get('data', {}).get('Invoices', [])) if invoices_result['success'] else 0,
            'contacts_count': len(contacts_result.get('data', {}).get('Contacts', [])) if contacts_result['success'] else 0,
            'record_count': (len(invoices_result.get('data', {}).get('Invoices', [])) +
                           len(contacts_result.get('data', {}).get('Contacts', [])))
        }


class FreshBooksIntegration(BaseDataSource):
    """FreshBooks API integration"""

    def __init__(self):
        super().__init__('freshbooks')
        self.access_token = os.environ.get('FRESHBOOKS_ACCESS_TOKEN', '')
        self.business_id = os.environ.get('FRESHBOOKS_BUSINESS_ID', '')
        self.base_url = f"https://api.freshbooks.com/accounting/account/{self.business_id}"

        self.auth_headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }

    def get_invoices(self, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get FreshBooks invoices"""
        return self.get_data("invoices/invoices", params)

    def get_clients(self, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get FreshBooks clients"""
        return self.get_data("users/clients", params)

    def get_expenses(self, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get FreshBooks expenses"""
        return self.get_data("expenses/expenses", params)

    def get_summary(self) -> Dict[str, Any]:
        """Get FreshBooks summary"""
        invoices_result = self.get_invoices()
        clients_result = self.get_clients()

        return {
            'status': 'connected' if invoices_result['success'] else 'error',
            'invoices_count': len(invoices_result.get('data', {}).get('invoices', [])) if invoices_result['success'] else 0,
            'clients_count': len(clients_result.get('data', {}).get('clients', [])) if clients_result['success'] else 0,
            'record_count': (len(invoices_result.get('data', {}).get('invoices', [])) +
                           len(clients_result.get('data', {}).get('clients', [])))
        }


class ZohoBooksIntegration(BaseDataSource):
    """Zoho Books API integration"""

    def __init__(self):
        super().__init__('zoho_books')
        self.client_id = os.environ.get('ZOHO_BOOKS_CLIENT_ID', '')
        self.client_secret = os.environ.get('ZOHO_BOOKS_CLIENT_SECRET', '')
        self.base_url = "https://www.zohoapis.com/books/v3"

        # This would need proper OAuth2 token management
        self.auth_headers = {
            'Authorization': 'Bearer YOUR_ACCESS_TOKEN',
            'Content-Type': 'application/json'
        }

    def get_invoices(self, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get Zoho Books invoices"""
        return self.get_data("invoices", params)

    def get_customers(self, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get Zoho Books customers"""
        return self.get_data("contacts", params)

    def get_items(self, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get Zoho Books items"""
        return self.get_data("items", params)

    def get_summary(self) -> Dict[str, Any]:
        """Get Zoho Books summary"""
        invoices_result = self.get_invoices()
        customers_result = self.get_customers()

        return {
            'status': 'connected' if invoices_result['success'] else 'error',
            'invoices_count': len(invoices_result.get('data', [])) if invoices_result['success'] else 0,
            'customers_count': len(customers_result.get('data', [])) if customers_result['success'] else 0,
            'record_count': (len(invoices_result.get('data', [])) +
                           len(customers_result.get('data', [])))
        }


class WaveIntegration(BaseDataSource):
    """Wave Accounting API integration"""

    def __init__(self):
        super().__init__('wave')
        self.access_token = os.environ.get('WAVE_ACCESS_TOKEN', '')
        self.business_id = os.environ.get('WAVE_BUSINESS_ID', '')
        self.base_url = "https://api.waveapps.com/v1"

        self.auth_headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }

    def get_invoices(self, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get Wave invoices"""
        return self.get_data(f"businesses/{self.business_id}/invoices", params)

    def get_customers(self, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get Wave customers"""
        return self.get_data(f"businesses/{self.business_id}/customers", params)

    def get_products(self, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get Wave products"""
        return self.get_data(f"businesses/{self.business_id}/products", params)

    def get_summary(self) -> Dict[str, Any]:
        """Get Wave summary"""
        invoices_result = self.get_invoices()
        customers_result = self.get_customers()

        return {
            'status': 'connected' if invoices_result['success'] else 'error',
            'invoices_count': len(invoices_result.get('data', [])) if invoices_result['success'] else 0,
            'customers_count': len(customers_result.get('data', [])) if customers_result['success'] else 0,
            'record_count': (len(invoices_result.get('data', [])) +
                           len(customers_result.get('data', [])))
        }


class HubSpotIntegration(BaseDataSource):
    """HubSpot CRM API integration"""

    def __init__(self):
        super().__init__('hubspot')
        self.access_token = os.environ.get('HUBSPOT_ACCESS_TOKEN', '')
        self.client_id = os.environ.get('HUBSPOT_CLIENT_ID', '')
        self.client_secret = os.environ.get('HUBSPOT_CLIENT_SECRET', '')
        self.base_url = "https://api.hubapi.com/crm/v3"

        self.auth_headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }

    def get_contacts(self, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get HubSpot contacts"""
        return self.get_data("objects/contacts", params)

    def get_deals(self, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get HubSpot deals"""
        return self.get_data("objects/deals", params)

    def get_companies(self, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get HubSpot companies"""
        return self.get_data("objects/companies", params)

    def get_summary(self) -> Dict[str, Any]:
        """Get HubSpot summary"""
        contacts_result = self.get_contacts()
        deals_result = self.get_deals()
        companies_result = self.get_companies()

        return {
            'status': 'connected' if contacts_result['success'] else 'error',
            'contacts_count': len(contacts_result.get('data', {}).get('results', [])) if contacts_result['success'] else 0,
            'deals_count': len(deals_result.get('data', {}).get('results', [])) if deals_result['success'] else 0,
            'companies_count': len(companies_result.get('data', {}).get('results', [])) if companies_result['success'] else 0,
            'record_count': (len(contacts_result.get('data', {}).get('results', [])) +
                           len(deals_result.get('data', {}).get('results', [])) +
                           len(companies_result.get('data', {}).get('results', [])))
        }


class PipedriveIntegration(BaseDataSource):
    """Pipedrive CRM API integration"""

    def __init__(self):
        super().__init__('pipedrive')
        self.api_token = os.environ.get('PIPEDRIVE_API_TOKEN', '')
        self.company_domain = os.environ.get('PIPEDRIVE_COMPANY_DOMAIN', '')
        self.base_url = f"https://{self.company_domain}.pipedrive.com/api/v1"

    def _make_request(self, method: str, endpoint: str, params: Dict[str, Any] = None,
                     data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Override to add Pipedrive authentication"""
        if params is None:
            params = {}
        params['api_token'] = self.api_token

        return super()._make_request(method, endpoint, params, data)

    def get_deals(self, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get Pipedrive deals"""
        return self.get_data("deals", params)

    def get_persons(self, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get Pipedrive persons"""
        return self.get_data("persons", params)

    def get_organizations(self, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get Pipedrive organizations"""
        return self.get_data("organizations", params)

    def get_summary(self) -> Dict[str, Any]:
        """Get Pipedrive summary"""
        deals_result = self.get_deals()
        persons_result = self.get_persons()
        organizations_result = self.get_organizations()

        return {
            'status': 'connected' if deals_result['success'] else 'error',
            'deals_count': len(deals_result.get('data', {}).get('data', [])) if deals_result['success'] else 0,
            'persons_count': len(persons_result.get('data', {}).get('data', [])) if persons_result['success'] else 0,
            'organizations_count': len(organizations_result.get('data', {}).get('data', [])) if organizations_result['success'] else 0,
            'record_count': (len(deals_result.get('data', {}).get('data', [])) +
                           len(persons_result.get('data', {}).get('data', [])) +
                           len(organizations_result.get('data', {}).get('data', [])))
        }


# Global instance
data_source_integrator = DataSourceIntegrator()
