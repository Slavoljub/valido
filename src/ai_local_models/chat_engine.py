"""
Advanced Chat Engine - Consolidated
Handles communication with local AI models with ML capabilities and modern features
"""

import logging
import sqlite3
import json
import uuid
import asyncio
import numpy as np
from datetime import datetime
from typing import Tuple, Optional, Dict, List, Any
from pathlib import Path
import re

logger = logging.getLogger(__name__)

class AdvancedChatEngine:
    """Advanced chat engine with ML capabilities, embeddings, and modern features"""
    
    def __init__(self, db_path: str = "data/sqlite/sample.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        # Initialize core components
        self._init_database()
        self._init_ml_components()
        self._init_vector_database()

        # Chat state management
        self.active_sessions = {}
        self.pending_requests = {}
        self.generation_tasks = {}

        # ML Configuration
        self.embedding_model_name = 'all-MiniLM-L6-v2'
        self.similarity_threshold = 0.7
        self.max_embedding_results = 10

        # Financial analysis capabilities
        self.financial_keywords = {
            'revenue': ['revenue', 'income', 'sales', 'earnings'],
            'costs': ['cost', 'expense', 'spending', 'expenditure'],
            'clients': ['client', 'customer', 'buyer', 'purchaser'],
            'products': ['product', 'item', 'service', 'offering'],
            'cashflow': ['cash flow', 'cashflow', 'liquidity', 'cash'],
            'inventory': ['inventory', 'stock', 'warehouse', 'supply'],
            'profit': ['profit', 'margin', 'earnings', 'gain']
        }

    def _init_ml_components(self):
        """Initialize ML components for embeddings and analysis"""
        try:
            # Try to import sentence transformers for embeddings
            try:
                from sentence_transformers import SentenceTransformer
                self.embedding_model = SentenceTransformer(self.embedding_model_name)
                logger.info(f"✅ Embedding model loaded: {self.embedding_model_name}")
            except ImportError:
                logger.warning("⚠️ SentenceTransformers not available, embeddings disabled")
                self.embedding_model = None

            # Initialize clustering components
            try:
                from sklearn.cluster import KMeans
                from sklearn.preprocessing import StandardScaler
                self.kmeans = KMeans
                self.scaler = StandardScaler
                logger.info("✅ ML clustering components loaded")
            except ImportError:
                logger.warning("⚠️ Scikit-learn not available, clustering disabled")
                self.kmeans = None
                self.scaler = None

        except Exception as e:
            logger.error(f"❌ Error initializing ML components: {e}")
            self.embedding_model = None
            self.kmeans = None
            self.scaler = None

    def _init_vector_database(self):
        """Initialize vector database for embeddings storage"""
        try:
            # Try PostgreSQL with pgvector first
            try:
                import psycopg2
                self.vector_db_type = 'postgresql'
                self._init_postgresql_vector_db()
                logger.info("✅ PostgreSQL vector database initialized")
            except (ImportError, Exception) as e:
                logger.warning(f"⚠️ PostgreSQL not available: {e}")
                # Fallback to SQLite-based vector storage
                self.vector_db_type = 'sqlite'
                self._init_sqlite_vector_db()
                logger.info("✅ SQLite vector database initialized")

        except Exception as e:
            logger.error(f"❌ Error initializing vector database: {e}")
            self.vector_db_type = None

    def _init_postgresql_vector_db(self):
        """Initialize PostgreSQL with pgvector extension"""
        try:
            import psycopg2
            # Note: In production, these would come from environment variables
            self.pg_connection = psycopg2.connect(
                database="ai_embeddings",
                user="ai_user",
                password="secure_password",
                host="localhost",
                port="5432"
            )

            # Create vector extension and tables
            with self.pg_connection.cursor() as cursor:
                # Enable pgvector extension
                cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")

                # Create embeddings table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS embeddings (
                        id SERIAL PRIMARY KEY,
                        content_id VARCHAR(255) UNIQUE,
                        content_type VARCHAR(50),
                        content TEXT,
                        embedding vector(384),  -- all-MiniLM-L6-v2 produces 384-dim embeddings
                        metadata JSONB,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """)

                # Create index for vector similarity search
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS embeddings_vector_idx
                    ON embeddings USING ivfflat (embedding vector_cosine_ops)
                    WITH (lists = 100);
                """)

                self.pg_connection.commit()

        except Exception as e:
            logger.error(f"❌ PostgreSQL vector DB initialization failed: {e}")
            raise

    def _init_sqlite_vector_db(self):
        """Initialize SQLite-based vector storage as fallback"""
        try:
            # Create SQLite tables for vector storage
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Create vector storage table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS vector_embeddings (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        content_id TEXT UNIQUE,
                        content_type TEXT,
                        content TEXT,
                        embedding BLOB,  -- Store numpy array as blob
                        metadata TEXT,    -- JSON string
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """)

                # Create index for content type searches
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_vector_content_type
                    ON vector_embeddings(content_type);
                """)

                conn.commit()

        except Exception as e:
            logger.error(f"❌ SQLite vector DB initialization failed: {e}")
            raise

    # ==========================================
    # ML-POWERED METHODS
    # ==========================================

    def generate_embeddings(self, text: str) -> Optional[np.ndarray]:
        """Generate text embeddings using sentence transformers"""
        if not self.embedding_model or not text.strip():
            return None

        try:
            embeddings = self.embedding_model.encode([text])[0]
            return np.array(embeddings, dtype=np.float32)
        except Exception as e:
            logger.error(f"❌ Error generating embeddings: {e}")
            return None

    def store_embeddings(self, content_id: str, content: str, content_type: str, metadata: Dict[str, Any] = None) -> bool:
        """Store content embeddings in vector database"""
        if not self.embedding_model:
            return False

        try:
            embeddings = self.generate_embeddings(content)
            if embeddings is None:
                return False

            if self.vector_db_type == 'postgresql':
                return self._store_embeddings_postgresql(content_id, content, content_type, embeddings, metadata)
            elif self.vector_db_type == 'sqlite':
                return self._store_embeddings_sqlite(content_id, content, content_type, embeddings, metadata)
            else:
                return False

        except Exception as e:
            logger.error(f"❌ Error storing embeddings: {e}")
            return False

    def _store_embeddings_postgresql(self, content_id: str, content: str, content_type: str,
                                   embeddings: np.ndarray, metadata: Dict[str, Any] = None) -> bool:
        """Store embeddings in PostgreSQL"""
        try:
            with self.pg_connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO embeddings (content_id, content_type, content, embedding, metadata)
                    VALUES (%s, %s, %s, %s::vector, %s)
                    ON CONFLICT (content_id) DO UPDATE SET
                        content = EXCLUDED.content,
                        embedding = EXCLUDED.embedding,
                        metadata = EXCLUDED.metadata,
                        created_at = CURRENT_TIMESTAMP;
                """, (
                    content_id, content_type, content,
                    embeddings.tolist(), json.dumps(metadata or {})
                ))
                self.pg_connection.commit()
            return True
        except Exception as e:
            logger.error(f"❌ PostgreSQL embedding storage failed: {e}")
            return False

    def _store_embeddings_sqlite(self, content_id: str, content: str, content_type: str,
                               embeddings: np.ndarray, metadata: Dict[str, Any] = None) -> bool:
        """Store embeddings in SQLite"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO vector_embeddings
                    (content_id, content_type, content, embedding, metadata)
                    VALUES (?, ?, ?, ?, ?);
                """, (
                    content_id, content_type, content,
                    embeddings.tobytes(), json.dumps(metadata or {})
                ))
                conn.commit()
            return True
        except Exception as e:
            logger.error(f"❌ SQLite embedding storage failed: {e}")
            return False

    def search_similar_content(self, query: str, content_type: str = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Search for similar content using embeddings"""
        if not self.embedding_model:
            return []

        try:
            query_embedding = self.generate_embeddings(query)
            if query_embedding is None:
                return []

            if self.vector_db_type == 'postgresql':
                return self._search_similar_postgresql(query_embedding, content_type, limit)
            elif self.vector_db_type == 'sqlite':
                return self._search_similar_sqlite(query_embedding, content_type, limit)
            else:
                return []

        except Exception as e:
            logger.error(f"❌ Error searching similar content: {e}")
            return []

    def _search_similar_postgresql(self, query_embedding: np.ndarray, content_type: str = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Search similar content in PostgreSQL"""
        try:
            with self.pg_connection.cursor() as cursor:
                if content_type:
                    cursor.execute("""
                        SELECT content_id, content_type, content, metadata,
                               1 - (embedding <=> %s::vector) as similarity
                        FROM embeddings
                        WHERE content_type = %s
                        ORDER BY embedding <=> %s::vector
                        LIMIT %s;
                    """, (query_embedding.tolist(), content_type, query_embedding.tolist(), limit))
                else:
                    cursor.execute("""
                        SELECT content_id, content_type, content, metadata,
                               1 - (embedding <=> %s::vector) as similarity
                        FROM embeddings
                        ORDER BY embedding <=> %s::vector
                        LIMIT %s;
                    """, (query_embedding.tolist(), query_embedding.tolist(), limit))

                results = []
                for row in cursor.fetchall():
                    results.append({
                        'content_id': row[0],
                        'content_type': row[1],
                        'content': row[2],
                        'metadata': json.loads(row[3]) if row[3] else {},
                        'similarity': float(row[4])
                    })

                return results

        except Exception as e:
            logger.error(f"❌ PostgreSQL similarity search failed: {e}")
            return []

    def _search_similar_sqlite(self, query_embedding: np.ndarray, content_type: str = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Search similar content in SQLite (using cosine similarity approximation)"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                if content_type:
                    cursor.execute("""
                        SELECT content_id, content_type, content, embedding, metadata
                        FROM vector_embeddings
                        WHERE content_type = ?
                        ORDER BY id
                        LIMIT ?;
                    """, (content_type, limit * 2))  # Get more for better similarity calculation
                else:
                    cursor.execute("""
                        SELECT content_id, content_type, content, embedding, metadata
                        FROM vector_embeddings
                        ORDER BY id
                        LIMIT ?;
                    """, (limit * 2,))

                rows = cursor.fetchall()
                if not rows:
                    return []

                # Calculate cosine similarity
                similarities = []
                for row in rows:
                    try:
                        embedding_bytes = row[3]
                        embedding = np.frombuffer(embedding_bytes, dtype=np.float32)

                        # Cosine similarity
                        dot_product = np.dot(query_embedding, embedding)
                        norm_query = np.linalg.norm(query_embedding)
                        norm_embedding = np.linalg.norm(embedding)

                        if norm_query > 0 and norm_embedding > 0:
                            similarity = dot_product / (norm_query * norm_embedding)
                        else:
                            similarity = 0.0

                        similarities.append({
                            'content_id': row[0],
                            'content_type': row[1],
                            'content': row[2],
                            'metadata': json.loads(row[4]) if row[4] else {},
                            'similarity': float(similarity)
                        })
                    except Exception as e:
                        logger.warning(f"Error calculating similarity for {row[0]}: {e}")
                        continue

                # Sort by similarity and return top results
                similarities.sort(key=lambda x: x['similarity'], reverse=True)
                return similarities[:limit]

        except Exception as e:
            logger.error(f"❌ SQLite similarity search failed: {e}")
            return []

    # ==========================================
    # FINANCIAL ANALYSIS METHODS
    # ==========================================

    def find_best_clients_and_products(self, data_source: str = "sample.db", analysis_type: str = "comprehensive") -> Dict[str, Any]:
        """Find best clients and selling products using ML and database analysis"""
        try:
            analysis_result = {
                'success': True,
                'analysis_type': analysis_type,
                'timestamp': datetime.now().isoformat(),
                'best_clients': [],
                'best_products': [],
                'insights': [],
                'recommendations': []
            }

            # Analyze clients
            clients_data = self._analyze_client_performance(data_source)
            if clients_data:
                analysis_result['best_clients'] = clients_data[:10]  # Top 10 clients

            # Analyze products
            products_data = self._analyze_product_performance(data_source)
            if products_data:
                analysis_result['best_products'] = products_data[:10]  # Top 10 products

            # Generate insights
            analysis_result['insights'] = self._generate_business_insights(
                analysis_result['best_clients'],
                analysis_result['best_products']
            )

            # Generate recommendations
            analysis_result['recommendations'] = self._generate_business_recommendations(
                analysis_result['best_clients'],
                analysis_result['best_products']
            )

            return analysis_result

        except Exception as e:
            logger.error(f"❌ Error in financial analysis: {e}")
            return {
                'success': False,
                'error': str(e),
                'analysis_type': analysis_type,
                'timestamp': datetime.now().isoformat()
            }

    def _analyze_client_performance(self, data_source: str) -> List[Dict[str, Any]]:
        """Analyze client performance from database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Get client performance data
                cursor.execute("""
                    SELECT
                        c.id,
                        c.name,
                        c.email,
                        COUNT(i.id) as total_invoices,
                        SUM(i.total_amount) as total_revenue,
                        AVG(i.total_amount) as avg_invoice_value,
                        MAX(i.issue_date) as last_invoice_date,
                        c.created_at
                    FROM clients c
                    LEFT JOIN invoices i ON c.id = i.client_id
                    WHERE i.status = 'paid'
                    GROUP BY c.id, c.name, c.email, c.created_at
                    ORDER BY total_revenue DESC;
                """)

                clients = []
                for row in cursor.fetchall():
                    clients.append({
                        'id': row[0],
                        'name': row[1],
                        'email': row[2],
                        'total_invoices': row[3],
                        'total_revenue': float(row[4] or 0),
                        'avg_invoice_value': float(row[5] or 0),
                        'last_invoice_date': row[6],
                        'client_since': row[7],
                        'performance_score': self._calculate_client_score(row)
                    })

                return clients

        except Exception as e:
            logger.error(f"❌ Error analyzing client performance: {e}")
            return []

    def _analyze_product_performance(self, data_source: str) -> List[Dict[str, Any]]:
        """Analyze product performance from database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Get product performance data
                cursor.execute("""
                    SELECT
                        p.id,
                        p.name,
                        p.description,
                        p.price,
                        COUNT(ii.id) as total_sold,
                        SUM(ii.quantity * ii.unit_price) as total_revenue,
                        AVG(ii.unit_price) as avg_selling_price,
                        SUM(ii.quantity) as total_quantity_sold,
                        p.stock_quantity,
                        p.created_at
                    FROM products p
                    LEFT JOIN invoice_items ii ON p.id = ii.product_id
                    GROUP BY p.id, p.name, p.description, p.price, p.stock_quantity, p.created_at
                    ORDER BY total_revenue DESC;
                """)

                products = []
                for row in cursor.fetchall():
                    products.append({
                        'id': row[0],
                        'name': row[1],
                        'description': row[2],
                        'price': float(row[3] or 0),
                        'total_sold': row[4],
                        'total_revenue': float(row[5] or 0),
                        'avg_selling_price': float(row[6] or 0),
                        'total_quantity_sold': row[7],
                        'stock_quantity': row[8],
                        'created_at': row[9],
                        'performance_score': self._calculate_product_score(row)
                    })

                return products

        except Exception as e:
            logger.error(f"❌ Error analyzing product performance: {e}")
            return []

    def _calculate_client_score(self, client_data) -> float:
        """Calculate client performance score"""
        try:
            revenue_score = min(float(client_data[4] or 0) / 10000, 1.0)  # Normalize to 0-1
            invoice_count_score = min(int(client_data[3] or 0) / 50, 1.0)   # Normalize to 0-1
            avg_value_score = min(float(client_data[5] or 0) / 1000, 1.0)  # Normalize to 0-1

            return (revenue_score * 0.5 + invoice_count_score * 0.3 + avg_value_score * 0.2)
        except:
            return 0.0

    def _calculate_product_score(self, product_data) -> float:
        """Calculate product performance score"""
        try:
            revenue_score = min(float(product_data[5] or 0) / 5000, 1.0)   # Normalize to 0-1
            quantity_score = min(int(product_data[7] or 0) / 100, 1.0)     # Normalize to 0-1
            price_score = min(float(product_data[3] or 0) / 500, 1.0)      # Normalize to 0-1

            return (revenue_score * 0.5 + quantity_score * 0.3 + price_score * 0.2)
        except:
            return 0.0

    def _generate_business_insights(self, clients: List[Dict], products: List[Dict]) -> List[str]:
        """Generate business insights from analysis"""
        insights = []

        try:
            if clients:
                top_client = clients[0]
                insights.append(f"🏆 Top client '{top_client['name']}' generates €{top_client['total_revenue']:,.2f} in revenue")

            if products:
                top_product = products[0]
                insights.append(f"📈 Best selling product '{top_product['name']}' with {top_product['total_sold']} units sold")

            # Calculate revenue concentration
            if len(clients) >= 5:
                top_5_revenue = sum(c['total_revenue'] for c in clients[:5])
                total_revenue = sum(c['total_revenue'] for c in clients)
                concentration = (top_5_revenue / total_revenue) * 100 if total_revenue > 0 else 0
                insights.append(f"🎯 Top 5 clients account for {concentration:.1f}% of total revenue")

            # Analyze product diversity
            if len(products) >= 10:
                top_3_revenue = sum(p['total_revenue'] for p in products[:3])
                total_revenue = sum(p['total_revenue'] for p in products)
                diversity = (top_3_revenue / total_revenue) * 100 if total_revenue > 0 else 0
                insights.append(f"📊 Top 3 products account for {diversity:.1f}% of product revenue")

        except Exception as e:
            logger.error(f"❌ Error generating insights: {e}")

        return insights

    def _generate_business_recommendations(self, clients: List[Dict], products: List[Dict]) -> List[str]:
        """Generate business recommendations"""
        recommendations = []

        try:
            # Client-based recommendations
            if clients:
                low_performing_clients = [c for c in clients if c['performance_score'] < 0.3]
                if low_performing_clients:
                    recommendations.append(f"📞 Follow up with {len(low_performing_clients)} underperforming clients")

            # Product-based recommendations
            if products:
                low_stock_products = [p for p in products if (p['stock_quantity'] or 0) < 10]
                if low_stock_products:
                    recommendations.append(f"📦 Restock {len(low_stock_products)} products with low inventory")

                high_performing_products = [p for p in products if p['performance_score'] > 0.7]
                if high_performing_products:
                    recommendations.append(f"🚀 Focus marketing on {len(high_performing_products)} high-performing products")

            # General recommendations
            recommendations.extend([
                "💡 Consider loyalty programs for top 10% of clients",
                "📊 Implement automated inventory tracking",
                "🎯 Develop targeted marketing campaigns for best-selling products"
            ])

        except Exception as e:
            logger.error(f"❌ Error generating recommendations: {e}")

        return recommendations

    # ==========================================
    # MODERN CHAT FEATURES
    # ==========================================

    async def process_message_with_ml(self, message: str, session_id: str,
                                    progress_callback: Optional[callable] = None) -> Dict[str, Any]:
        """Process message with ML capabilities and streaming support"""
        try:
            # Create task for tracking
            task_id = f"msg_{int(asyncio.get_event_loop().time() * 1000)}"
            task = self.start_task(task_id, f"Processing: {message[:50]}...", 'process')
            self.generation_tasks[task_id] = task

            # Update progress
            if progress_callback:
                await progress_callback(task_id, 10, "Analyzing message...")

            # Generate embeddings for the message
            embeddings = self.generate_embeddings(message)

            # Search for similar content
            similar_content = []
            if embeddings is not None:
                similar_content = self.search_similar_content(message, limit=5)

            if progress_callback:
                await progress_callback(task_id, 30, "Searching knowledge base...")

            # Analyze message for financial keywords
            financial_analysis = self._analyze_financial_query(message)

            if progress_callback:
                await progress_callback(task_id, 50, "Generating response...")

            # Generate response based on analysis
            if financial_analysis['type'] == 'best_clients_products':
                # Special handling for the user's specific request
                analysis_result = self.find_best_clients_and_products()
                response = self._format_financial_analysis_response(analysis_result)
            else:
                response = self._generate_normal_response(message, similar_content, financial_analysis)

            if progress_callback:
                await progress_callback(task_id, 80, "Formatting response...")

            # Store message and response for future similarity search
            message_id = f"{session_id}_{int(asyncio.get_event_loop().time() * 1000)}"
            self.store_embeddings(message_id, message, 'user_message', {
                'session_id': session_id,
                'timestamp': datetime.now().isoformat()
            })

            response_id = f"{session_id}_resp_{int(asyncio.get_event_loop().time() * 1000)}"
            self.store_embeddings(response_id, response, 'ai_response', {
                'session_id': session_id,
                'timestamp': datetime.now().isoformat()
            })

            if progress_callback:
                await progress_callback(task_id, 100, "Complete!")

            # Complete task
            self.complete_task(task_id)

            return {
                'success': True,
                'response': response,
                'similar_content': similar_content,
                'financial_analysis': financial_analysis,
                'embeddings_generated': embeddings is not None
            }

        except Exception as e:
            logger.error(f"❌ Error processing message with ML: {e}")
            if task_id in self.generation_tasks:
                self.fail_task(task_id, str(e))
            return {
                'success': False,
                'error': str(e),
                'response': 'I apologize, but I encountered an error processing your message. Please try again.'
            }

    def _analyze_financial_query(self, message: str) -> Dict[str, Any]:
        """Analyze message for financial keywords and intent"""
        message_lower = message.lower()

        analysis = {
            'type': 'general',
            'keywords_found': [],
            'financial_categories': [],
            'intent': 'general_query'
        }

        # Check for specific query patterns
        if any(word in message_lower for word in ['best clients', 'best customers', 'top clients', 'top customers']):
            if any(word in message_lower for word in ['best products', 'best selling', 'top products', 'selling products']):
                analysis['type'] = 'best_clients_products'
                analysis['intent'] = 'comprehensive_analysis'

        # Check financial categories
        for category, keywords in self.financial_keywords.items():
            if any(keyword in message_lower for keyword in keywords):
                analysis['financial_categories'].append(category)
                analysis['keywords_found'].extend([k for k in keywords if k in message_lower])

        # Determine intent
        if 'analyze' in message_lower or 'analysis' in message_lower:
            analysis['intent'] = 'analysis_request'
        elif 'report' in message_lower:
            analysis['intent'] = 'report_request'
        elif 'recommend' in message_lower or 'suggest' in message_lower:
            analysis['intent'] = 'recommendation_request'

        return analysis

    def _format_financial_analysis_response(self, analysis_result: Dict[str, Any]) -> str:
        """Format financial analysis response"""
        if not analysis_result['success']:
            return f"❌ Error performing analysis: {analysis_result.get('error', 'Unknown error')}"

        response = "🎯 **Comprehensive Business Analysis Report**\n\n"

        # Best Clients
        if analysis_result['best_clients']:
            response += "🏆 **Top Performing Clients:**\n"
            for i, client in enumerate(analysis_result['best_clients'][:5], 1):
                response += f"{i}. **{client['name']}** - €{client['total_revenue']:,.2f} revenue ({client['total_invoices']} invoices)\n"
            response += "\n"

        # Best Products
        if analysis_result['best_products']:
            response += "📈 **Best Selling Products:**\n"
            for i, product in enumerate(analysis_result['best_products'][:5], 1):
                response += f"{i}. **{product['name']}** - €{product['total_revenue']:,.2f} revenue ({product['total_sold']} units)\n"
            response += "\n"

        # Insights
        if analysis_result['insights']:
            response += "💡 **Key Insights:**\n"
            for insight in analysis_result['insights']:
                response += f"• {insight}\n"
            response += "\n"

        # Recommendations
        if analysis_result['recommendations']:
            response += "🎯 **Business Recommendations:**\n"
            for recommendation in analysis_result['recommendations']:
                response += f"• {recommendation}\n"

        return response

    def _generate_normal_response(self, message: str, similar_content: List[Dict], financial_analysis: Dict) -> str:
        """Generate normal response with ML insights"""
        response = f"I understand your message: '{message}'\n\n"

        if similar_content:
            response += "📚 **Related Information Found:**\n"
            for content in similar_content[:3]:
                similarity = content['similarity'] * 100
                if similarity > 70:
                    response += f"• {content['content'][:100]}... (similarity: {similarity:.1f}%)\n"
            response += "\n"

        if financial_analysis['financial_categories']:
            response += f"💼 **Financial Categories Detected:** {', '.join(financial_analysis['financial_categories'])}\n\n"

        response += "How can I assist you further with this analysis?"

        return response

    def stop_generation(self, task_id: str) -> bool:
        """Stop message generation"""
        if task_id in self.generation_tasks:
            task = self.generation_tasks[task_id]
            self.fail_task(task_id, "Generation stopped by user")
            return True
        return False

    def get_active_generations(self) -> List[str]:
        """Get list of active generation tasks"""
        return list(self.generation_tasks.keys())

    def cleanup_completed_tasks(self):
        """Clean up completed generation tasks"""
        completed_tasks = [tid for tid, task in self.generation_tasks.items()
                          if task.status in ['completed', 'failed']]
        for task_id in completed_tasks:
            del self.generation_tasks[task_id]
    
    def _init_database(self):
        """Initialize the chat database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create chat sessions table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS chat_sessions (
                        id TEXT PRIMARY KEY,
                        model_path TEXT,
                        gpu_id TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Create chat messages table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS chat_messages (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        session_id TEXT,
                        sender TEXT,
                        message TEXT,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (session_id) REFERENCES chat_sessions (id)
                    )
                """)
                
                conn.commit()
                logger.info("Chat database initialized successfully")
                
        except Exception as e:
            logger.error(f"Failed to initialize chat database: {e}")
    
    def send_message(self, message: str, model_path: str, gpu_id: str = 'auto', 
                    session_id: Optional[str] = None) -> Tuple[str, str]:
        """
        Send a message to the AI model and get a response
        
        Args:
            message: The user's message
            model_path: Path to the model file or Ollama model name
            gpu_id: GPU configuration to use
            session_id: Existing session ID or None for new session
            
        Returns:
            Tuple of (response, session_id)
        """
        try:
            # Create or get session
            if not session_id:
                session_id = str(uuid.uuid4())
                self._create_session(session_id, model_path, gpu_id)
            
            # Save user message
            self._save_message(session_id, 'user', message)
            
            # Generate AI response
            response = self._generate_response(message, model_path, gpu_id)
            
            # Save AI response
            self._save_message(session_id, 'ai', response)
            
            # Update session timestamp
            self._update_session(session_id)
            
            return response, session_id
            
        except Exception as e:
            logger.error(f"Error in send_message: {e}")
            error_response = f"I apologize, but I encountered an error: {str(e)}"
            return error_response, session_id or str(uuid.uuid4())
    
    def _create_session(self, session_id: str, model_path: str, gpu_id: str):
        """Create a new chat session"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO chat_sessions (id, model_path, gpu_id)
                    VALUES (?, ?, ?)
                """, (session_id, model_path, gpu_id))
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to create session: {e}")
    
    def _save_message(self, session_id: str, sender: str, message: str):
        """Save a message to the database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO chat_messages (session_id, sender, message)
                    VALUES (?, ?, ?)
                """, (session_id, sender, message))
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to save message: {e}")
    
    def _update_session(self, session_id: str):
        """Update session timestamp"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE chat_sessions 
                    SET updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (session_id,))
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to update session: {e}")
    
    def _generate_response(self, message: str, model_path: str, gpu_id: str) -> str:
        """
        Generate a response using the local AI model
        
        This is a placeholder implementation. In a real implementation,
        you would load the model and generate actual responses.
        """
        try:
            # Check if it's an Ollama model
            if model_path.startswith('ollama://'):
                return self._generate_ollama_response(message, model_path)
            
            # For now, return a mock response based on the message content
            # In a real implementation, you would load the GGUF model and generate responses
            return self._generate_mock_response(message, model_path)
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return f"I apologize, but I encountered an error while processing your request: {str(e)}"
    
    def _generate_ollama_response(self, message: str, model_path: str) -> str:
        """Generate response using Ollama"""
        import subprocess
        
        try:
            # Extract model name from ollama://model_name
            model_name = model_path.replace('ollama://', '')
            
            # Call Ollama API
            result = subprocess.run([
                'ollama', 'run', model_name, message
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                logger.error(f"Ollama error: {result.stderr}")
                return "I apologize, but I encountered an error with the Ollama model."
                
        except subprocess.TimeoutExpired:
            return "I apologize, but the model took too long to respond."
        except Exception as e:
            logger.error(f"Error with Ollama: {e}")
            return f"I apologize, but I encountered an error: {str(e)}"
    
    def _generate_mock_response(self, message: str, model_path: str) -> str:
        """Generate a mock response for testing purposes"""
        message_lower = message.lower()
        
        # Financial analysis responses
        if any(word in message_lower for word in ['revenue', 'income', 'sales']):
            return """📊 **Revenue Analysis Report**

Based on your financial data, here's what I found:

**Total Revenue:** €45,000
**Net Revenue:** €38,250 (after deductions)
**Growth Rate:** +12% compared to previous period
**Top Revenue Sources:**
- Product Sales: 62% (€27,900)
- Services: 28% (€12,600)
- Other: 10% (€4,500)

**Key Insights:**
- Revenue is growing steadily month-over-month
- Product sales remain your primary income source
- Consider expanding service offerings to diversify revenue

Would you like me to analyze any specific aspect of your revenue data?"""
        
        elif any(word in message_lower for word in ['cash', 'flow', 'cashflow']):
            return """💰 **Cash Flow Analysis**

**Current Cash Flow Status:**

**Inflows:**
- Operating Activities: €42,000
- Investing Activities: €5,000
- Financing Activities: €2,000

**Outflows:**
- Operating Expenses: €38,000
- Capital Expenditures: €8,000
- Debt Payments: €1,500

**Net Cash Flow:** €1,500 (positive)

**Recommendations:**
- Monitor operating expenses closely
- Consider optimizing payment terms with suppliers
- Maintain healthy cash reserves for unexpected expenses

Your cash flow is currently positive, which is good for business sustainability."""
        
        elif any(word in message_lower for word in ['invoice', 'billing']):
            return """📄 **Invoice Status Overview**

**Current Invoice Status:**

**Outstanding Invoices:** €12,500
- 30+ days overdue: €3,200 (2 invoices)
- 15-30 days overdue: €5,800 (4 invoices)
- 0-15 days overdue: €3,500 (3 invoices)

**Recent Invoices:**
- Invoice #2024-001: €2,500 (Due: 5 days)
- Invoice #2024-002: €1,800 (Due: 12 days)
- Invoice #2024-003: €3,200 (Due: 18 days)

**Recommendations:**
- Follow up on overdue invoices immediately
- Consider implementing automated payment reminders
- Review payment terms with clients

Would you like me to generate payment reminder templates?"""
        
        elif any(word in message_lower for word in ['vat', 'tax']):
            return """🧾 **VAT Analysis Report**

**VAT Summary for Current Period:**

**VAT Collected (Output VAT):** €8,100
**VAT Paid (Input VAT):** €5,400
**Net VAT Due:** €2,700

**Breakdown by Category:**
- Sales VAT: €8,100
- Purchase VAT: €5,400
- Import VAT: €0
- Export VAT: €0

**Important Dates:**
- VAT Return Due: 25th of next month
- Payment Due: 25th of next month

**Recommendations:**
- Ensure all VAT receipts are properly documented
- Consider VAT optimization strategies
- Prepare for quarterly VAT return

Your VAT position looks healthy with proper documentation."""
        
        elif any(word in message_lower for word in ['client', 'customer']):
            return """👥 **Client Performance Review**

**Top Clients by Revenue:**

1. **TechCorp Solutions** - €8,500 (18.9%)
   - Projects: 3 active
   - Payment History: Excellent
   - Growth: +15% this quarter

2. **Global Industries** - €6,200 (13.8%)
   - Projects: 2 active
   - Payment History: Good
   - Growth: +8% this quarter

3. **StartupXYZ** - €4,800 (10.7%)
   - Projects: 1 active
   - Payment History: Average
   - Growth: +25% this quarter

**Client Satisfaction Score:** 4.6/5
**Retention Rate:** 87%

**Recommendations:**
- Focus on expanding relationships with top clients
- Address payment issues with clients showing delays
- Develop retention strategies for at-risk clients"""
        
        elif any(word in message_lower for word in ['warehouse', 'inventory', 'stock']):
            return """📦 **Warehouse Inventory Status**

**Current Inventory Overview:**

**Total Items:** 1,247
**Total Value:** €67,500
**Low Stock Items:** 23 (need reordering)

**Top Categories:**
- Electronics: €25,000 (37%)
- Office Supplies: €18,000 (27%)
- Furniture: €15,000 (22%)
- Other: €9,500 (14%)

**Stock Alerts:**
- Laptops: 5 units remaining (reorder point: 10)
- Office Chairs: 3 units remaining (reorder point: 8)
- Printers: 2 units remaining (reorder point: 5)

**Recommendations:**
- Place orders for low stock items immediately
- Review reorder points based on demand patterns
- Consider bulk purchasing for high-demand items

Would you like me to generate purchase orders for low stock items?"""
        
        else:
            return f"""Hello! I'm your AI financial assistant. I can help you analyze:

📊 **Financial Data** - Revenue, expenses, cash flow
📄 **Invoices & Billing** - Payment status, overdue amounts  
🧾 **VAT & Taxes** - Tax calculations and compliance
👥 **Client Analysis** - Customer performance and relationships
📦 **Inventory Management** - Stock levels and warehouse status

You asked: "{message}"

Try asking me about specific financial metrics, or use the quick question buttons above for common analyses. I'm here to help you make informed business decisions!"""

    def get_chat_history(self, session_id: str, limit: int = 50) -> list:
        """Get chat history for a session"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT sender, message, timestamp
                    FROM chat_messages
                    WHERE session_id = ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                """, (session_id, limit))
                
                messages = []
                for row in cursor.fetchall():
                    messages.append({
                        'sender': row[0],
                        'message': row[1],
                        'timestamp': row[2]
                    })
                
                return list(reversed(messages))  # Return in chronological order
                
        except Exception as e:
            logger.error(f"Failed to get chat history: {e}")
            return []
    
    def get_sessions(self, limit: int = 20) -> list:
        """Get recent chat sessions"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, model_path, gpu_id, created_at, updated_at
                    FROM chat_sessions
                    ORDER BY updated_at DESC
                    LIMIT ?
                """, (limit,))
                
                sessions = []
                for row in cursor.fetchall():
                    sessions.append({
                        'id': row[0],
                        'model_path': row[1],
                        'gpu_id': row[2],
                        'created_at': row[3],
                        'updated_at': row[4]
                    })
                
                return sessions
                
        except Exception as e:
            logger.error(f"Failed to get sessions: {e}")
            return []
