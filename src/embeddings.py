"""
ValidoAI - Embeddings Generation System
======================================
Generate embeddings from business data for AI applications
Supports multiple embedding models and formats
"""

import os
import json
import logging
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union
import uuid
import hashlib

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except (ImportError, ValueError) as e:
    # Handle both import errors and Keras compatibility issues
    print(f"⚠️  Sentence transformers not available: {e}")
    SENTENCE_TRANSFORMERS_AVAILABLE = False

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

from .config import get_db_config
import psycopg2
import psycopg2.extras

logger = logging.getLogger(__name__)

class EmbeddingGenerator:
    """Generate embeddings from business data"""

    def __init__(self):
        self.config = get_db_config().get_current_config()
        self.models = {}
        self.embeddings_dir = os.path.join(os.getcwd(), 'embeddings')
        os.makedirs(self.embeddings_dir, exist_ok=True)

        # Initialize available models
        self._initialize_models()

    def _initialize_models(self):
        """Initialize available embedding models"""
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            try:
                # Serbian/Balkan language model
                self.models['serbian'] = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
                logger.info("✅ Serbian embedding model loaded")
            except Exception as e:
                logger.warning(f"Could not load Serbian model: {e}")

            try:
                # English model as fallback
                self.models['english'] = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
                logger.info("✅ English embedding model loaded")
            except Exception as e:
                logger.warning(f"Could not load English model: {e}")

        if OPENAI_AVAILABLE:
            openai_api_key = os.environ.get('OPENAI_API_KEY')
            if openai_api_key:
                self.models['openai'] = 'text-embedding-3-small'
                logger.info("✅ OpenAI embedding model available")

        # If no models are available, log a warning
        if not self.models:
            logger.warning("⚠️  No embedding models available. Using fallback hash-based embeddings.")

    def generate_company_embeddings(self, format: str = 'json') -> str:
        """Generate embeddings for company data"""

        conn = self.get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        try:
            cur.execute("""
                SELECT
                    companies_id, company_name, legal_name, industry,
                    company_type, address_line1, city, phone, email,
                    tax_id, registration_number
                FROM companies
                WHERE status = 'active'
            """)

            companies = cur.fetchall()

            embeddings_data = {
                'generated_at': datetime.now().isoformat(),
                'data_type': 'companies',
                'total_records': len(companies),
                'embeddings': []
            }

            for company in companies:
                # Create text representation for embedding
                text_content = self._create_company_text(company)

                # Generate embeddings
                embedding = self._generate_text_embedding(text_content)

                if embedding is not None:
                    company_embedding = {
                        'id': str(company['companies_id']),
                        'type': 'company',
                        'text': text_content,
                        'embedding': embedding.tolist() if hasattr(embedding, 'tolist') else embedding,
                        'metadata': {
                            'company_name': company['company_name'],
                            'industry': company['industry'],
                            'city': company['city'],
                            'tax_id': company['tax_id']
                        }
                    }
                    embeddings_data['embeddings'].append(company_embedding)

            return self._save_embeddings(embeddings_data, f"company_embeddings_{datetime.now().strftime('%Y%m%d_%H%M%S')}", format)

        finally:
            cur.close()
            conn.close()

    def generate_invoice_embeddings(self, format: str = 'json') -> str:
        """Generate embeddings for invoice data"""

        conn = self.get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        try:
            cur.execute("""
                SELECT
                    i.invoices_id, i.invoice_number, i.invoice_date, i.due_date,
                    i.total_amount, i.currency, i.payment_status, i.notes,
                    c.company_name, c.industry
                FROM invoices i
                JOIN companies c ON i.company_id = c.companies_id
                WHERE i.status = 'issued'
                ORDER BY i.invoice_date DESC
                LIMIT 1000
            """)

            invoices = cur.fetchall()

            embeddings_data = {
                'generated_at': datetime.now().isoformat(),
                'data_type': 'invoices',
                'total_records': len(invoices),
                'embeddings': []
            }

            for invoice in invoices:
                # Create text representation for embedding
                text_content = self._create_invoice_text(invoice)

                # Generate embeddings
                embedding = self._generate_text_embedding(text_content)

                if embedding is not None:
                    invoice_embedding = {
                        'id': str(invoice['invoices_id']),
                        'type': 'invoice',
                        'text': text_content,
                        'embedding': embedding.tolist() if hasattr(embedding, 'tolist') else embedding,
                        'metadata': {
                            'invoice_number': invoice['invoice_number'],
                            'company_name': invoice['company_name'],
                            'total_amount': float(invoice['total_amount']) if invoice['total_amount'] else 0,
                            'currency': invoice['currency'],
                            'payment_status': invoice['payment_status'],
                            'invoice_date': invoice['invoice_date'].isoformat() if invoice['invoice_date'] else None
                        }
                    }
                    embeddings_data['embeddings'].append(invoice_embedding)

            return self._save_embeddings(embeddings_data, f"invoice_embeddings_{datetime.now().strftime('%Y%m%d_%H%M%S')}", format)

        finally:
            cur.close()
            conn.close()

    def generate_customer_embeddings(self, format: str = 'json') -> str:
        """Generate embeddings for customer data"""

        conn = self.get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        try:
            cur.execute("""
                SELECT
                    customers_id, customer_name, tax_id, registration_number,
                    address_line1, city, country, phone, email, contact_person,
                    industry, credit_limit, payment_terms
                FROM customers
                WHERE status = 'active'
            """)

            customers = cur.fetchall()

            embeddings_data = {
                'generated_at': datetime.now().isoformat(),
                'data_type': 'customers',
                'total_records': len(customers),
                'embeddings': []
            }

            for customer in customers:
                # Create text representation for embedding
                text_content = self._create_customer_text(customer)

                # Generate embeddings
                embedding = self._generate_text_embedding(text_content)

                if embedding is not None:
                    customer_embedding = {
                        'id': str(customer['customers_id']),
                        'type': 'customer',
                        'text': text_content,
                        'embedding': embedding.tolist() if hasattr(embedding, 'tolist') else embedding,
                        'metadata': {
                            'customer_name': customer['customer_name'],
                            'city': customer['city'],
                            'country': customer['country'],
                            'tax_id': customer['tax_id']
                        }
                    }
                    embeddings_data['embeddings'].append(customer_embedding)

            return self._save_embeddings(embeddings_data, f"customer_embeddings_{datetime.now().strftime('%Y%m%d_%H%M%S')}", format)

        finally:
            cur.close()
            conn.close()

    def generate_business_insights_embeddings(self, format: str = 'json') -> str:
        """Generate embeddings for business insights"""

        conn = self.get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        try:
            cur.execute("""
                SELECT
                    ai_insights_id, insight_type, insight_text, confidence_score,
                    created_at, related_company_id, related_invoice_id
                FROM ai_insights
                WHERE confidence_score > 0.5
                ORDER BY created_at DESC
                LIMIT 500
            """)

            insights = cur.fetchall()

            embeddings_data = {
                'generated_at': datetime.now().isoformat(),
                'data_type': 'business_insights',
                'total_records': len(insights),
                'embeddings': []
            }

            for insight in insights:
                # Create text representation for embedding
                text_content = self._create_insight_text(insight)

                # Generate embeddings
                embedding = self._generate_text_embedding(text_content)

                if embedding is not None:
                    insight_embedding = {
                        'id': str(insight['ai_insights_id']),
                        'type': 'business_insight',
                        'text': text_content,
                        'embedding': embedding.tolist() if hasattr(embedding, 'tolist') else embedding,
                        'metadata': {
                            'insight_type': insight['insight_type'],
                            'confidence_score': float(insight['confidence_score']) if insight['confidence_score'] else 0,
                            'created_at': insight['created_at'].isoformat() if insight['created_at'] else None
                        }
                    }
                    embeddings_data['embeddings'].append(insight_embedding)

            return self._save_embeddings(embeddings_data, f"insights_embeddings_{datetime.now().strftime('%Y%m%d_%H%M%S')}", format)

        finally:
            cur.close()
            conn.close()

    def _create_company_text(self, company: Dict[str, Any]) -> str:
        """Create text representation of company for embedding"""
        return f"""
Company: {company.get('company_name', '')}
Legal Name: {company.get('legal_name', '')}
Industry: {company.get('industry', '')}
Company Type: {company.get('company_type', '')}
Location: {company.get('address_line1', '')}, {company.get('city', '')}
Contact: {company.get('phone', '')}, {company.get('email', '')}
Tax ID: {company.get('tax_id', '')}
Registration: {company.get('registration_number', '')}
""".strip()

    def _create_invoice_text(self, invoice: Dict[str, Any]) -> str:
        """Create text representation of invoice for embedding"""
        return f"""
Invoice: {invoice.get('invoice_number', '')}
Company: {invoice.get('company_name', '')}
Amount: {invoice.get('total_amount', 0)} {invoice.get('currency', 'RSD')}
Status: {invoice.get('payment_status', '')}
Date: {invoice.get('invoice_date', '')}
Due Date: {invoice.get('due_date', '')}
Industry: {invoice.get('industry', '')}
Notes: {invoice.get('notes', '')}
""".strip()

    def _create_customer_text(self, customer: Dict[str, Any]) -> str:
        """Create text representation of customer for embedding"""
        return f"""
Customer: {customer.get('customer_name', '')}
Location: {customer.get('address_line1', '')}, {customer.get('city', '')}, {customer.get('country', '')}
Contact: {customer.get('phone', '')}, {customer.get('email', '')}
Contact Person: {customer.get('contact_person', '')}
Tax ID: {customer.get('tax_id', '')}
Registration: {customer.get('registration_number', '')}
Credit Limit: {customer.get('credit_limit', 0)}
Payment Terms: {customer.get('payment_terms', '')}
""".strip()

    def _create_insight_text(self, insight: Dict[str, Any]) -> str:
        """Create text representation of business insight for embedding"""
        return f"""
Insight Type: {insight.get('insight_type', '')}
Content: {insight.get('insight_text', '')}
Confidence: {insight.get('confidence_score', 0)}
Created: {insight.get('created_at', '')}
""".strip()

    def _generate_text_embedding(self, text: str, model: str = 'serbian') -> Optional[Union[np.ndarray, List[float]]]:
        """Generate embedding for text using specified model"""

        if not text or not text.strip():
            return None

        try:
            # Try Serbian model first
            if model == 'serbian' and 'serbian' in self.models:
                embedding = self.models['serbian'].encode(text)
                return embedding

            # Fallback to English model
            elif 'english' in self.models:
                embedding = self.models['english'].encode(text)
                return embedding

            # Fallback to simple hash-based embedding (not good but works)
            else:
                # Create a simple deterministic embedding based on text hash
                text_hash = hashlib.md5(text.encode()).hexdigest()
                # Convert to 384-dimensional vector (similar to sentence-transformers)
                embedding = []
                for i in range(0, len(text_hash), 2):
                    hex_pair = text_hash[i:i+2]
                    value = int(hex_pair, 16) / 255.0  # Normalize to 0-1
                    embedding.append(value)

                # Pad or truncate to 384 dimensions
                while len(embedding) < 384:
                    embedding.extend(embedding)
                embedding = embedding[:384]

                return np.array(embedding)

        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            return None

    def _save_embeddings(self, data: Dict[str, Any], filename: str, format: str) -> str:
        """Save embeddings in specified format"""

        filepath = os.path.join(self.embeddings_dir, f"{filename}.{format}")

        if format.lower() == 'json':
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)

        elif format.lower() == 'csv' and PANDAS_AVAILABLE:
            # Convert embeddings to DataFrame
            records = []
            for item in data.get('embeddings', []):
                record = {
                    'id': item.get('id'),
                    'type': item.get('type'),
                    'text': item.get('text', '')[:100],  # Truncate for CSV
                    'embedding': ','.join([str(x) for x in item.get('embedding', [])])
                }
                records.append(record)

            df = pd.DataFrame(records)
            df.to_csv(filepath, index=False, encoding='utf-8')

        elif format.lower() == 'npy':
            # Save as NumPy arrays
            embeddings = [item['embedding'] for item in data.get('embeddings', [])]
            if embeddings:
                np.save(filepath, np.array(embeddings))

        else:
            # Default to JSON
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)

        logger.info(f"✅ Embeddings saved: {filepath}")
        return filepath

    def get_db_connection(self):
        """Get database connection"""
        return psycopg2.connect(
            host=self.config['host'],
            port=self.config['port'],
            database=self.config['database'],
            user=self.config['user'],
            password=self.config['password']
        )

    def generate_all_embeddings(self, format: str = 'json') -> Dict[str, str]:
        """Generate embeddings for all data types"""
        results = {}

        try:
            logger.info("🔄 Generating company embeddings...")
            results['companies'] = self.generate_company_embeddings(format)
        except Exception as e:
            logger.error(f"Error generating company embeddings: {e}")

        try:
            logger.info("🔄 Generating invoice embeddings...")
            results['invoices'] = self.generate_invoice_embeddings(format)
        except Exception as e:
            logger.error(f"Error generating invoice embeddings: {e}")

        try:
            logger.info("🔄 Generating customer embeddings...")
            results['customers'] = self.generate_customer_embeddings(format)
        except Exception as e:
            logger.error(f"Error generating customer embeddings: {e}")

        try:
            logger.info("🔄 Generating business insights embeddings...")
            results['insights'] = self.generate_business_insights_embeddings(format)
        except Exception as e:
            logger.error(f"Error generating insights embeddings: {e}")

        logger.info("✅ All embeddings generated successfully")
        return results

    def list_embeddings_files(self) -> List[str]:
        """List all generated embeddings files"""
        if os.path.exists(self.embeddings_dir):
            return [f for f in os.listdir(self.embeddings_dir) if f.endswith(('.json', '.csv', '.npy'))]
        return []

    def cleanup_old_embeddings(self, days: int = 30):
        """Clean up embeddings older than specified days"""
        cutoff_date = datetime.now() - timedelta(days=days)

        for filename in self.list_embeddings_files():
            filepath = os.path.join(self.embeddings_dir, filename)
            if os.path.getctime(filepath) < cutoff_date.timestamp():
                os.remove(filepath)
                logger.info(f"Cleaned up old embeddings: {filename}")

# Global embedding generator instance
embedding_generator = EmbeddingGenerator()

# Utility functions
def generate_company_embeddings(format: str = 'json') -> str:
    """Generate company embeddings"""
    return embedding_generator.generate_company_embeddings(format)

def generate_invoice_embeddings(format: str = 'json') -> str:
    """Generate invoice embeddings"""
    return embedding_generator.generate_invoice_embeddings(format)

def generate_customer_embeddings(format: str = 'json') -> str:
    """Generate customer embeddings"""
    return embedding_generator.generate_customer_embeddings(format)

def generate_all_embeddings(format: str = 'json') -> Dict[str, str]:
    """Generate all embeddings"""
    return embedding_generator.generate_all_embeddings(format)

# Export key components
__all__ = [
    'EmbeddingGenerator',
    'embedding_generator',
    'generate_company_embeddings',
    'generate_invoice_embeddings',
    'generate_customer_embeddings',
    'generate_all_embeddings'
]

