"""
ValidoAI - Serbian Government Services Integration
===================================================
Comprehensive integration with Serbian government services:
- E-faktura (Electronic Invoicing)
- Poreska Uprava (Tax Authority)
- APR (Business Registry)
- PIO Fond (Social Insurance)
- RFZO (Health Insurance)
- NSZ (Employment Agency)
- NBS (Central Bank)
- Carina (Customs)
- RZS (Statistics Office)
"""

import os
import json
import logging
import requests
import base64
import hashlib
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, field
from enum import Enum
import time
from urllib.parse import urljoin

from .error_handling import error_handler, ErrorSeverity, ErrorCategory, handle_errors

logger = logging.getLogger(__name__)

class ServiceStatus(Enum):
    """Service status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"
    ERROR = "error"

class DocumentType(Enum):
    """Document type enumeration for e-faktura"""
    INVOICE = "380"  # Commercial invoice
    CREDIT_NOTE = "381"  # Credit note
    DEBIT_NOTE = "384"  # Debit note
    ADVANCE_INVOICE = "386"  # Advance invoice
    SELF_INVOICE = "389"  # Self invoice

@dataclass
class ServiceConfig:
    """Configuration for a government service"""
    name: str
    base_url: str
    api_key: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    cert_path: Optional[str] = None
    cert_password: Optional[str] = None
    environment: str = "production"
    timeout: int = 30
    retry_attempts: int = 3
    enabled: bool = False
    status: ServiceStatus = ServiceStatus.ACTIVE

@dataclass
class CompanyInfo:
    """Serbian company information"""
    pib: str  # Tax ID
    matični_broj: str  # Registration number
    company_name: str
    legal_name: str
    address: str
    city: str
    postal_code: str
    phone: Optional[str] = None
    email: Optional[str] = None
    business_entity_type: str = "DOO"
    pdv_registered: bool = True
    pdv_registration_number: Optional[str] = None

@dataclass
class InvoiceData:
    """Invoice data for e-faktura"""
    invoice_number: str
    invoice_date: datetime
    due_date: datetime
    seller: CompanyInfo
    buyer: CompanyInfo
    items: List[Dict[str, Any]] = field(default_factory=list)
    subtotal: float = 0.0
    pdv_amount: float = 0.0
    total_amount: float = 0.0
    currency: str = "RSD"
    document_type: DocumentType = DocumentType.INVOICE
    payment_reference: Optional[str] = None
    qr_code_data: Optional[str] = None

class SerbianGovernmentServices:
    """Main class for Serbian government services integration"""

    def __init__(self):
        self.services = self._initialize_services()
        self.session = requests.Session()
        self.session.timeout = 30

    def _initialize_services(self) -> Dict[str, ServiceConfig]:
        """Initialize all government service configurations"""
        return {
            'e_faktura': ServiceConfig(
                name='E-faktura',
                base_url=os.environ.get('E_FAKTURA_API_URL', 'https://efaktura.mfin.gov.rs'),
                cert_path=os.environ.get('E_FAKTURA_CERT_PATH'),
                cert_password=os.environ.get('E_FAKTURA_CERT_PASSWORD'),
                environment=os.environ.get('E_FAKTURA_ENVIRONMENT', 'production'),
                timeout=int(os.environ.get('E_FAKTURA_TIMEOUT', '30')),
                retry_attempts=int(os.environ.get('E_FAKTURA_RETRY_ATTEMPTS', '3')),
                enabled=os.environ.get('E_FAKTURA_ENABLED', 'false').lower() == 'true'
            ),
            'poreska_uprava': ServiceConfig(
                name='Poreska Uprava',
                base_url=os.environ.get('PORESKA_UPRAVA_API_URL', 'https://api.poreskauprava.rs'),
                api_key=os.environ.get('PORESKA_UPRAVA_API_KEY'),
                cert_path=os.environ.get('PORESKA_UPRAVA_CERT_PATH'),
                timeout=int(os.environ.get('PORESKA_UPRAVA_TIMEOUT', '30')),
                enabled=os.environ.get('PORESKA_UPRAVA_ENABLED', 'false').lower() == 'true'
            ),
            'apr': ServiceConfig(
                name='APR',
                base_url=os.environ.get('APR_API_URL', 'https://api.apr.gov.rs'),
                api_key=os.environ.get('APR_API_KEY'),
                username=os.environ.get('APR_USERNAME'),
                password=os.environ.get('APR_PASSWORD'),
                timeout=int(os.environ.get('APR_TIMEOUT', '30')),
                enabled=os.environ.get('APR_ENABLED', 'false').lower() == 'true'
            ),
            'pio_fond': ServiceConfig(
                name='PIO Fond',
                base_url=os.environ.get('PIO_FOND_API_URL', 'https://api.piofond.rs'),
                cert_path=os.environ.get('PIO_FOND_CERT_PATH'),
                cert_password=os.environ.get('PIO_FOND_CERT_PASSWORD'),
                environment=os.environ.get('PIO_FOND_ENVIRONMENT', 'production'),
                enabled=os.environ.get('PIO_FOND_ENABLED', 'false').lower() == 'true'
            ),
            'rfzo': ServiceConfig(
                name='RFZO',
                base_url=os.environ.get('RFZO_API_URL', 'https://api.rfzo.rs'),
                cert_path=os.environ.get('RFZO_CERT_PATH'),
                username=os.environ.get('RFZO_USERNAME'),
                password=os.environ.get('RFZO_PASSWORD'),
                enabled=os.environ.get('RFZO_ENABLED', 'false').lower() == 'true'
            ),
            'nsz': ServiceConfig(
                name='NSZ',
                base_url=os.environ.get('NSZ_API_URL', 'https://api.nsz.gov.rs'),
                api_key=os.environ.get('NSZ_API_KEY'),
                environment=os.environ.get('NSZ_ENVIRONMENT', 'production'),
                enabled=os.environ.get('NSZ_ENABLED', 'false').lower() == 'true'
            ),
            'nbs': ServiceConfig(
                name='NBS',
                base_url=os.environ.get('NBS_API_URL', 'https://api.nbs.rs'),
                api_key=os.environ.get('NBS_API_KEY'),
                environment=os.environ.get('NBS_ENVIRONMENT', 'production'),
                enabled=os.environ.get('NBS_ENABLED', 'false').lower() == 'true'
            ),
            'carina': ServiceConfig(
                name='Carina',
                base_url=os.environ.get('CARINA_API_URL', 'https://api.carina.gov.rs'),
                cert_path=os.environ.get('CARINA_CERT_PATH'),
                cert_password=os.environ.get('CARINA_CERT_PASSWORD'),
                environment=os.environ.get('CARINA_ENVIRONMENT', 'production'),
                enabled=os.environ.get('CARINA_ENABLED', 'false').lower() == 'true'
            ),
            'rzs': ServiceConfig(
                name='RZS',
                base_url=os.environ.get('RZS_API_URL', 'https://api.stat.gov.rs'),
                api_key=os.environ.get('RZS_API_KEY'),
                environment=os.environ.get('RZS_ENVIRONMENT', 'production'),
                enabled=os.environ.get('RZS_ENABLED', 'false').lower() == 'true'
            )
        }

    def is_service_enabled(self, service_name: str) -> bool:
        """Check if a service is enabled"""
        return self.services.get(service_name, ServiceConfig('')).enabled

    def get_service_config(self, service_name: str) -> ServiceConfig:
        """Get service configuration"""
        return self.services.get(service_name, ServiceConfig(''))

class EFakturaService:
    """E-faktura (Electronic Invoicing) service integration"""

    def __init__(self, config: ServiceConfig):
        self.config = config
        self.session = requests.Session()
        self.session.timeout = config.timeout

        # Set up certificate authentication if provided
        if config.cert_path and config.cert_password:
            self.session.cert = (config.cert_path, config.cert_password)

    @handle_errors(ErrorSeverity.ERROR, ErrorCategory.EXTERNAL_SERVICE)
    def send_invoice(self, invoice_data: InvoiceData) -> Dict[str, Any]:
        """Send invoice to e-faktura system"""
        if not self.config.enabled:
            raise ValueError("E-faktura service is not enabled")

        # Generate XML invoice
        xml_data = self._generate_invoice_xml(invoice_data)

        # Generate QR code data
        qr_data = self._generate_qr_code(invoice_data)

        # Prepare request
        headers = {
            'Content-Type': 'application/xml',
            'X-API-Key': self.config.api_key or ''
        }

        url = urljoin(self.config.base_url, '/api/invoices')

        # Send request with retry logic
        for attempt in range(self.config.retry_attempts):
            try:
                response = self.session.post(url, data=xml_data, headers=headers)

                if response.status_code == 200:
                    result = response.json()
                    return {
                        'success': True,
                        'invoice_id': result.get('invoice_id'),
                        'status': result.get('status'),
                        'qr_code': qr_data,
                        'xml_data': xml_data
                    }
                elif response.status_code in [500, 502, 503, 504]:
                    # Retry on server errors
                    if attempt < self.config.retry_attempts - 1:
                        time.sleep(2 ** attempt)  # Exponential backoff
                        continue

                response.raise_for_status()

            except requests.exceptions.RequestException as e:
                if attempt < self.config.retry_attempts - 1:
                    time.sleep(2 ** attempt)
                    continue
                raise e

        raise Exception("Failed to send invoice after all retry attempts")

    def _generate_invoice_xml(self, invoice_data: InvoiceData) -> str:
        """Generate XML for e-faktura invoice"""
        # Create XML structure according to Serbian e-faktura standard
        root = ET.Element('Invoice')
        root.set('xmlns', 'urn:oasis:names:specification:ubl:schema:xsd:Invoice-2')
        root.set('xmlns:cbc', 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2')
        root.set('xmlns:cac', 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2')

        # Invoice metadata
        ET.SubElement(root, 'cbc:ID').text = invoice_data.invoice_number
        ET.SubElement(root, 'cbc:IssueDate').text = invoice_data.invoice_date.strftime('%Y-%m-%d')

        # Document type
        ET.SubElement(root, 'cbc:InvoiceTypeCode').text = invoice_data.document_type.value

        # Currency
        ET.SubElement(root, 'cbc:DocumentCurrencyCode').text = invoice_data.currency

        # Seller information
        seller_party = ET.SubElement(root, 'cac:AccountingSupplierParty')
        seller = ET.SubElement(seller_party, 'cac:Party')

        seller_pib = ET.SubElement(seller, 'cac:PartyIdentification')
        ET.SubElement(seller_pib, 'cbc:ID', schemeID='PIB').text = invoice_data.seller.pib

        seller_name = ET.SubElement(seller, 'cac:PartyName')
        ET.SubElement(seller_name, 'cbc:Name').text = invoice_data.seller.company_name

        # Buyer information
        buyer_party = ET.SubElement(root, 'cac:AccountingCustomerParty')
        buyer = ET.SubElement(buyer_party, 'cac:Party')

        buyer_pib = ET.SubElement(buyer, 'cac:PartyIdentification')
        ET.SubElement(buyer_pib, 'cbc:ID', schemeID='PIB').text = invoice_data.buyer.pib

        buyer_name = ET.SubElement(buyer, 'cac:PartyName')
        ET.SubElement(buyer_name, 'cbc:Name').text = invoice_data.buyer.company_name

        # Invoice lines
        for item in invoice_data.items:
            invoice_line = ET.SubElement(root, 'cac:InvoiceLine')

            line_id = ET.SubElement(invoice_line, 'cbc:ID')
            line_id.text = str(item.get('line_number', 1))

            quantity = ET.SubElement(invoice_line, 'cbc:InvoicedQuantity', unitCode='C62')
            quantity.text = str(item.get('quantity', 1))

            line_amount = ET.SubElement(invoice_line, 'cbc:LineExtensionAmount', currencyID=invoice_data.currency)
            line_amount.text = str(item.get('line_total', 0))

            # Item details
            item_elem = ET.SubElement(invoice_line, 'cac:Item')
            ET.SubElement(item_elem, 'cbc:Name').text = item.get('name', '')
            ET.SubElement(item_elem, 'cbc:Description').text = item.get('description', '')

            # Price
            price = ET.SubElement(invoice_line, 'cac:Price')
            price_amount = ET.SubElement(price, 'cbc:PriceAmount', currencyID=invoice_data.currency)
            price_amount.text = str(item.get('unit_price', 0))

        # Tax total
        tax_total = ET.SubElement(root, 'cac:TaxTotal')
        tax_amount = ET.SubElement(tax_total, 'cbc:TaxAmount', currencyID=invoice_data.currency)
        tax_amount.text = str(invoice_data.pdv_amount)

        # Legal monetary total
        legal_total = ET.SubElement(root, 'cac:LegalMonetaryTotal')
        ET.SubElement(legal_total, 'cbc:LineExtensionAmount', currencyID=invoice_data.currency).text = str(invoice_data.subtotal)
        ET.SubElement(legal_total, 'cbc:TaxExclusiveAmount', currencyID=invoice_data.currency).text = str(invoice_data.subtotal)
        ET.SubElement(legal_total, 'cbc:TaxInclusiveAmount', currencyID=invoice_data.currency).text = str(invoice_data.total_amount)
        ET.SubElement(legal_total, 'cbc:PayableAmount', currencyID=invoice_data.currency).text = str(invoice_data.total_amount)

        return ET.tostring(root, encoding='unicode', method='xml')

    def _generate_qr_code(self, invoice_data: InvoiceData) -> str:
        """Generate QR code data for Serbian invoice"""
        # Serbian QR code format: K:VAT|I:PIB|V:20|T:total|N:invoice_number|R:reference
        qr_data = (
            f"K:VAT|"
            f"I:{invoice_data.seller.pib}|"
            f"V:{20}|"  # PDV rate
            f"T:{invoice_data.total_amount}|"
            f"N:{invoice_data.invoice_number}|"
            f"R:{invoice_data.payment_reference or ''}"
        )
        return qr_data

    def generate_payment_reference(self, invoice_number: str, amount: float) -> str:
        """Generate Serbian payment reference number (model 97)"""
        # Model 97: Poziv na broj (Call number) format
        # Format: 97 + invoice_number + check digit
        base = f"97{invoice_number}"
        check_digit = self._calculate_check_digit(base)
        return f"{base}{check_digit}"

    def _calculate_check_digit(self, number: str) -> str:
        """Calculate check digit for Serbian payment reference"""
        weights = [3, 1, 7, 3, 1, 7, 3, 1, 7, 3, 1, 7, 3, 1, 7, 3, 1, 7]
        total = 0

        for i, digit in enumerate(number):
            if i < len(weights):
                total += int(digit) * weights[i]

        remainder = total % 10
        check_digit = (10 - remainder) % 10
        return str(check_digit)

class PoreskaUpravaService:
    """Poreska Uprava (Tax Authority) service integration"""

    def __init__(self, config: ServiceConfig):
        self.config = config
        self.session = requests.Session()
        self.session.timeout = config.timeout

        if config.api_key:
            self.session.headers.update({'X-API-Key': config.api_key})

    @handle_errors(ErrorSeverity.ERROR, ErrorCategory.EXTERNAL_SERVICE)
    def get_company_tax_info(self, pib: str) -> Dict[str, Any]:
        """Get company tax information from Poreska Uprava"""
        if not self.config.enabled:
            raise ValueError("Poreska Uprava service is not enabled")

        url = urljoin(self.config.base_url, f'/api/companies/{pib}')

        response = self.session.get(url)
        response.raise_for_status()

        return response.json()

    @handle_errors(ErrorSeverity.ERROR, ErrorCategory.EXTERNAL_SERVICE)
    def get_tax_debt_status(self, pib: str) -> Dict[str, Any]:
        """Get tax debt status for company"""
        if not self.config.enabled:
            raise ValueError("Poreska Uprava service is not enabled")

        url = urljoin(self.config.base_url, f'/api/companies/{pib}/tax-debt')

        response = self.session.get(url)
        response.raise_for_status()

        return response.json()

class APRService:
    """APR (Business Registry) service integration"""

    def __init__(self, config: ServiceConfig):
        self.config = config
        self.session = requests.Session()
        self.session.timeout = config.timeout

        if config.api_key:
            self.session.headers.update({'X-API-Key': config.api_key})

        if config.username and config.password:
            auth_string = base64.b64encode(f"{config.username}:{config.password}".encode()).decode()
            self.session.headers.update({'Authorization': f'Basic {auth_string}'})

    @handle_errors(ErrorSeverity.ERROR, ErrorCategory.EXTERNAL_SERVICE)
    def get_company_info(self, registration_number: str) -> Dict[str, Any]:
        """Get company information from APR"""
        if not self.config.enabled:
            raise ValueError("APR service is not enabled")

        url = urljoin(self.config.base_url, f'/api/companies/{registration_number}')

        response = self.session.get(url)
        response.raise_for_status()

        return response.json()

    @handle_errors(ErrorSeverity.ERROR, ErrorCategory.EXTERNAL_SERVICE)
    def verify_company_status(self, registration_number: str) -> Dict[str, Any]:
        """Verify company status in business registry"""
        if not self.config.enabled:
            raise ValueError("APR service is not enabled")

        url = urljoin(self.config.base_url, f'/api/companies/{registration_number}/status')

        response = self.session.get(url)
        response.raise_for_status()

        return response.json()

class SerbianBusinessService:
    """Unified Serbian business service integration"""

    def __init__(self):
        self.gov_services = SerbianGovernmentServices()
        self.e_faktura = EFakturaService(self.gov_services.services['e_faktura'])
        self.poreska = PoreskaUpravaService(self.gov_services.services['poreska_uprava'])
        self.apr = APRService(self.gov_services.services['apr'])

    def submit_e_invoice(self, invoice_data: InvoiceData) -> Dict[str, Any]:
        """Submit electronic invoice to Serbian system"""
        return self.e_faktura.send_invoice(invoice_data)

    def get_company_tax_status(self, pib: str) -> Dict[str, Any]:
        """Get comprehensive company tax status"""
        result = {
            'pib': pib,
            'tax_info': None,
            'debt_status': None,
            'business_registry_info': None,
            'errors': []
        }

        try:
            if self.gov_services.is_service_enabled('poreska_uprava'):
                result['tax_info'] = self.poreska.get_company_tax_info(pib)
                result['debt_status'] = self.poreska.get_tax_debt_status(pib)
        except Exception as e:
            result['errors'].append(f"Tax service error: {str(e)}")

        try:
            if self.gov_services.is_service_enabled('apr'):
                # Note: This would need the registration number, not PIB
                # For now, we'll skip this part
                pass
        except Exception as e:
            result['errors'].append(f"Business registry error: {str(e)}")

        return result

    def calculate_pdv(self, amount: float, rate: float = 20.0) -> Dict[str, float]:
        """Calculate Serbian PDV (VAT)"""
        pdv_amount = amount * (rate / 100)
        total_amount = amount + pdv_amount

        return {
            'base_amount': amount,
            'pdv_rate': rate,
            'pdv_amount': round(pdv_amount, 2),
            'total_amount': round(total_amount, 2)
        }

    def generate_payment_reference(self, invoice_number: str) -> str:
        """Generate Serbian payment reference"""
        return self.e_faktura.generate_payment_reference(invoice_number, 0)

# Global instance
serbian_business_service = SerbianBusinessService()

# Utility functions
def create_invoice_data(
    invoice_number: str,
    seller_info: CompanyInfo,
    buyer_info: CompanyInfo,
    items: List[Dict[str, Any]],
    invoice_date: Optional[datetime] = None,
    due_date: Optional[datetime] = None
) -> InvoiceData:
    """Create invoice data structure"""

    if invoice_date is None:
        invoice_date = datetime.now()

    if due_date is None:
        due_date = invoice_date + timedelta(days=30)

    # Calculate totals
    subtotal = sum(item.get('quantity', 1) * item.get('unit_price', 0) for item in items)
    pdv_calc = serbian_business_service.calculate_pdv(subtotal)
    total_amount = pdv_calc['total_amount']

    return InvoiceData(
        invoice_number=invoice_number,
        invoice_date=invoice_date,
        due_date=due_date,
        seller=seller_info,
        buyer=buyer_info,
        items=items,
        subtotal=subtotal,
        pdv_amount=pdv_calc['pdv_amount'],
        total_amount=total_amount
    )

# Export key components
__all__ = [
    'SerbianGovernmentServices',
    'EFakturaService',
    'PoreskaUpravaService',
    'APRService',
    'SerbianBusinessService',
    'ServiceConfig',
    'ServiceStatus',
    'DocumentType',
    'CompanyInfo',
    'InvoiceData',
    'serbian_business_service',
    'create_invoice_data'
]
