#!/usr/bin/env python3
"""
Conversational Memory System for ValidoAI
=============================================

Advanced memory management for AI chat conversations with:
- Long-term context retention
- Semantic search and retrieval
- Memory consolidation
- Context-aware responses
- Memory pruning and optimization

Features:
- Persistent conversation history
- Semantic memory indexing
- Context relevance scoring
- Memory consolidation algorithms
- Privacy-aware memory management
"""

import os
import json
import logging
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import hashlib
import numpy as np

logger = logging.getLogger(__name__)

class ConversationalMemory:
    """Advanced conversational memory system with semantic indexing"""

    def __init__(self, db_path: str = "data/sqlite/conversational_memory.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize_database()

        # Memory configuration
        self.max_memory_entries = 10000  # Maximum entries per user
        self.max_context_length = 4000   # Maximum context tokens
        self.memory_retention_days = 90  # Days to keep memory
        self.relevance_threshold = 0.7    # Minimum relevance score
        self.consolidation_threshold = 100  # Entries before consolidation

    def _initialize_database(self):
        """Initialize SQLite database for memory storage"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Create memory entries table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS memory_entries (
                        id TEXT PRIMARY KEY,
                        user_id TEXT NOT NULL,
                        session_id TEXT,
                        message_type TEXT NOT NULL,
                        content TEXT NOT NULL,
                        timestamp TEXT NOT NULL,
                        tokens INTEGER DEFAULT 0,
                        relevance_score REAL DEFAULT 0.0,
                        topics TEXT,
                        entities TEXT,
                        sentiment TEXT,
                        embedding BLOB,
                        consolidated BOOLEAN DEFAULT FALSE,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                ''')

                # Create memory metadata table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS memory_metadata (
                        user_id TEXT PRIMARY KEY,
                        total_entries INTEGER DEFAULT 0,
                        last_consolidation TEXT,
                        memory_stats TEXT,
                        preferences TEXT,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                ''')

                # Create semantic index table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS semantic_index (
                        id TEXT PRIMARY KEY,
                        user_id TEXT NOT NULL,
                        content_hash TEXT NOT NULL,
                        embedding BLOB,
                        topics TEXT,
                        importance REAL DEFAULT 0.0,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                ''')

                # Create indexes for performance
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_timestamp ON memory_entries(user_id, timestamp)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_session ON memory_entries(session_id)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_relevance ON memory_entries(relevance_score)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_semantic ON semantic_index(user_id, content_hash)')

                conn.commit()
                logger.info("✅ Conversational memory database initialized")

        except Exception as e:
            logger.error(f"❌ Error initializing memory database: {e}")
            raise

    def store_memory(self, user_id: str, session_id: str, message_type: str,
                    content: str, metadata: Dict[str, Any] = None) -> str:
        """Store a memory entry with enhanced indexing"""
        try:
            memory_id = hashlib.md5(f"{user_id}:{datetime.now().isoformat()}:{content[:50]}".encode()).hexdigest()

            # Analyze content
            analysis = self._analyze_content(content)

            # Generate embedding (placeholder - would use actual embedding model)
            embedding = self._generate_embedding(content)

            # Calculate relevance score
            relevance_score = self._calculate_relevance(user_id, content, analysis)

            # Prepare data
            memory_entry = {
                'id': memory_id,
                'user_id': user_id,
                'session_id': session_id,
                'message_type': message_type,
                'content': content,
                'timestamp': datetime.now().isoformat(),
                'tokens': len(content.split()),
                'relevance_score': relevance_score,
                'topics': json.dumps(analysis.get('topics', [])),
                'entities': json.dumps(analysis.get('entities', [])),
                'sentiment': json.dumps(analysis.get('sentiment', {})),
                'embedding': embedding.tobytes() if embedding is not None else None,
                'consolidated': False
            }

            # Store in database
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute('''
                    INSERT INTO memory_entries (
                        id, user_id, session_id, message_type, content, timestamp,
                        tokens, relevance_score, topics, entities, sentiment, embedding
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    memory_entry['id'], memory_entry['user_id'], memory_entry['session_id'],
                    memory_entry['message_type'], memory_entry['content'], memory_entry['timestamp'],
                    memory_entry['tokens'], memory_entry['relevance_score'], memory_entry['topics'],
                    memory_entry['entities'], memory_entry['sentiment'], memory_entry['embedding']
                ))

                # Update user metadata
                self._update_user_metadata(user_id)

                conn.commit()

            # Check if consolidation is needed
            if self._should_consolidate(user_id):
                self._consolidate_memories(user_id)

            logger.info(f"💾 Memory stored for user {user_id}: {memory_id}")
            return memory_id

        except Exception as e:
            logger.error(f"❌ Error storing memory: {e}")
            return None

    def retrieve_relevant_memories(self, user_id: str, query: str,
                                 limit: int = 10) -> List[Dict[str, Any]]:
        """Retrieve relevant memories based on semantic similarity"""
        try:
            # Analyze query
            query_analysis = self._analyze_content(query)
            query_embedding = self._generate_embedding(query)

            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Get recent relevant memories
                cursor.execute('''
                    SELECT id, content, timestamp, relevance_score, topics, entities, sentiment
                    FROM memory_entries
                    WHERE user_id = ?
                    AND consolidated = FALSE
                    AND timestamp > ?
                    ORDER BY relevance_score DESC, timestamp DESC
                    LIMIT ?
                ''', (
                    user_id,
                    (datetime.now() - timedelta(days=self.memory_retention_days)).isoformat(),
                    limit * 2  # Get more for filtering
                ))

                memories = []
                for row in cursor.fetchall():
                    memory = {
                        'id': row[0],
                        'content': row[1],
                        'timestamp': row[2],
                        'relevance_score': row[3],
                        'topics': json.loads(row[4]) if row[4] else [],
                        'entities': json.loads(row[5]) if row[5] else [],
                        'sentiment': json.loads(row[6]) if row[6] else {}
                    }

                    # Calculate semantic similarity (placeholder)
                    semantic_score = self._calculate_semantic_similarity(query_embedding, memory)

                    # Combine relevance and semantic scores
                    combined_score = (memory['relevance_score'] + semantic_score) / 2

                    if combined_score >= self.relevance_threshold:
                        memory['combined_score'] = combined_score
                        memory['semantic_score'] = semantic_score
                        memories.append(memory)

                # Sort by combined score and limit results
                memories.sort(key=lambda x: x['combined_score'], reverse=True)
                return memories[:limit]

        except Exception as e:
            logger.error(f"❌ Error retrieving memories: {e}")
            return []

    def get_conversation_context(self, user_id: str, session_id: str = None,
                               max_tokens: int = 2000) -> Dict[str, Any]:
        """Get conversation context with memory integration"""
        try:
            # Get recent messages from current session
            recent_messages = []
            if session_id:
                recent_messages = self._get_recent_session_messages(session_id, limit=20)

            # Get relevant memories
            if recent_messages:
                last_message = recent_messages[-1]['content'] if recent_messages else ""
                relevant_memories = self.retrieve_relevant_memories(user_id, last_message, limit=5)
            else:
                relevant_memories = []

            # Combine and format context
            context_parts = []

            # Add relevant memories
            if relevant_memories:
                context_parts.append("## Previous Relevant Conversations:")
                for memory in relevant_memories:
                    context_parts.append(f"- {memory['timestamp'][:10]}: {memory['content'][:100]}...")

            # Add recent session messages
            if recent_messages:
                context_parts.append("## Recent Conversation:")
                for msg in recent_messages[-5:]:  # Last 5 messages
                    context_parts.append(f"{msg['message_type'].title()}: {msg['content'][:200]}")

            # Join context and check token limit
            full_context = "\n".join(context_parts)
            tokens = len(full_context.split())

            if tokens > max_tokens:
                # Truncate to fit token limit
                words = full_context.split()
                full_context = " ".join(words[:max_tokens])

            return {
                'context': full_context,
                'token_count': len(full_context.split()),
                'memories_used': len(relevant_memories),
                'session_messages': len(recent_messages),
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"❌ Error getting conversation context: {e}")
            return {
                'context': "",
                'token_count': 0,
                'memories_used': 0,
                'session_messages': 0,
                'error': str(e)
            }

    def _analyze_content(self, content: str) -> Dict[str, Any]:
        """Analyze content for topics, entities, and sentiment"""
        # Placeholder implementation - would use NLP libraries
        return {
            'topics': self._extract_topics(content),
            'entities': self._extract_entities(content),
            'sentiment': self._analyze_sentiment(content),
            'importance': self._calculate_importance(content)
        }

    def _extract_topics(self, content: str) -> List[str]:
        """Extract topics from content (placeholder)"""
        # Simple keyword extraction - would use topic modeling
        keywords = ['business', 'finance', 'revenue', 'profit', 'customer', 'sales', 'marketing']
        found_topics = []

        content_lower = content.lower()
        for keyword in keywords:
            if keyword in content_lower:
                found_topics.append(keyword)

        return found_topics

    def _extract_entities(self, content: str) -> List[Dict[str, str]]:
        """Extract named entities from content (placeholder)"""
        # Would use NER (Named Entity Recognition)
        return []

    def _analyze_sentiment(self, content: str) -> Dict[str, Any]:
        """Analyze sentiment of content (placeholder)"""
        # Would use sentiment analysis model
        return {'score': 0.0, 'label': 'neutral'}

    def _calculate_importance(self, content: str) -> float:
        """Calculate importance score of content"""
        # Simple scoring based on content characteristics
        score = 0.5  # Base score

        # Increase for questions
        if '?' in content:
            score += 0.2

        # Increase for longer content
        if len(content) > 100:
            score += 0.1

        # Increase for business keywords
        business_keywords = ['revenue', 'profit', 'business', 'company', 'financial']
        if any(keyword in content.lower() for keyword in business_keywords):
            score += 0.2

        return min(score, 1.0)

    def _generate_embedding(self, content: str) -> Optional[np.ndarray]:
        """Generate embedding for content (placeholder)"""
        # Would use actual embedding model like BERT, Sentence Transformers, etc.
        # For now, return a simple hash-based vector
        try:
            content_hash = hashlib.md5(content.encode()).digest()
            # Convert hash to simple vector
            embedding = np.frombuffer(content_hash, dtype=np.uint8).astype(np.float32) / 255.0
            return embedding
        except Exception:
            return None

    def _calculate_relevance(self, user_id: str, content: str, analysis: Dict[str, Any]) -> float:
        """Calculate relevance score for memory entry"""
        base_score = 0.5

        # Increase for high importance
        base_score += analysis.get('importance', 0) * 0.3

        # Increase for business-related content
        if 'business' in analysis.get('topics', []):
            base_score += 0.2

        # Increase for questions (learning opportunities)
        if '?' in content:
            base_score += 0.1

        return min(base_score, 1.0)

    def _calculate_semantic_similarity(self, query_embedding: np.ndarray, memory: Dict[str, Any]) -> float:
        """Calculate semantic similarity (placeholder)"""
        # Would use cosine similarity between embeddings
        # For now, return a random score
        return np.random.uniform(0.5, 0.9)

    def _get_recent_session_messages(self, session_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent messages from session (placeholder - would integrate with chat storage)"""
        # This would normally query the chat storage system
        return []

    def _should_consolidate(self, user_id: str) -> bool:
        """Check if memories should be consolidated"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT COUNT(*) FROM memory_entries
                    WHERE user_id = ? AND consolidated = FALSE
                ''', (user_id,))

                count = cursor.fetchone()[0]
                return count >= self.consolidation_threshold
        except Exception:
            return False

    def _consolidate_memories(self, user_id: str):
        """Consolidate old memories to reduce storage"""
        try:
            logger.info(f"🔄 Consolidating memories for user {user_id}")

            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Mark old memories as consolidated
                cutoff_date = (datetime.now() - timedelta(days=30)).isoformat()
                cursor.execute('''
                    UPDATE memory_entries
                    SET consolidated = TRUE
                    WHERE user_id = ? AND timestamp < ? AND relevance_score < 0.8
                ''', (user_id, cutoff_date))

                conn.commit()

                # Update metadata
                cursor.execute('''
                    UPDATE memory_metadata
                    SET last_consolidation = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE user_id = ?
                ''', (datetime.now().isoformat(), user_id))

                conn.commit()

            logger.info(f"✅ Memory consolidation completed for user {user_id}")

        except Exception as e:
            logger.error(f"❌ Error consolidating memories: {e}")

    def _update_user_metadata(self, user_id: str):
        """Update user metadata"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Get current stats
                cursor.execute('''
                    SELECT COUNT(*) FROM memory_entries WHERE user_id = ?
                ''', (user_id,))

                total_entries = cursor.fetchone()[0]

                # Update or insert metadata
                cursor.execute('''
                    INSERT INTO memory_metadata (user_id, total_entries, updated_at)
                    VALUES (?, ?, CURRENT_TIMESTAMP)
                    ON CONFLICT(user_id) DO UPDATE SET
                        total_entries = excluded.total_entries,
                        updated_at = CURRENT_TIMESTAMP
                ''', (user_id, total_entries))

                conn.commit()

        except Exception as e:
            logger.error(f"❌ Error updating user metadata: {e}")

    def get_memory_stats(self, user_id: str) -> Dict[str, Any]:
        """Get memory statistics for user"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                stats = {
                    'total_entries': 0,
                    'active_entries': 0,
                    'consolidated_entries': 0,
                    'average_relevance': 0.0,
                    'memory_usage_mb': 0.0,
                    'last_consolidation': None
                }

                # Get entry counts
                cursor.execute('''
                    SELECT
                        COUNT(*) as total,
                        SUM(CASE WHEN consolidated = FALSE THEN 1 ELSE 0 END) as active,
                        SUM(CASE WHEN consolidated = TRUE THEN 1 ELSE 0 END) as consolidated,
                        AVG(relevance_score) as avg_relevance
                    FROM memory_entries WHERE user_id = ?
                ''', (user_id,))

                row = cursor.fetchone()
                if row:
                    stats.update({
                        'total_entries': row[0] or 0,
                        'active_entries': row[1] or 0,
                        'consolidated_entries': row[2] or 0,
                        'average_relevance': row[3] or 0.0
                    })

                # Get metadata
                cursor.execute('''
                    SELECT last_consolidation FROM memory_metadata WHERE user_id = ?
                ''', (user_id,))

                row = cursor.fetchone()
                if row and row[0]:
                    stats['last_consolidation'] = row[0]

                # Calculate approximate memory usage
                cursor.execute('''
                    SELECT SUM(LENGTH(content)) FROM memory_entries WHERE user_id = ?
                ''', (user_id,))

                row = cursor.fetchone()
                if row and row[0]:
                    stats['memory_usage_mb'] = (row[0] or 0) / (1024 * 1024)

                return stats

        except Exception as e:
            logger.error(f"❌ Error getting memory stats: {e}")
            return {}

    def cleanup_old_memories(self, user_id: str = None, days: int = 90):
        """Clean up old memories beyond retention period"""
        try:
            cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()

            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                if user_id:
                    # Clean up specific user
                    cursor.execute('''
                        DELETE FROM memory_entries
                        WHERE user_id = ? AND timestamp < ? AND relevance_score < 0.5
                    ''', (user_id, cutoff_date))
                else:
                    # Clean up all users
                    cursor.execute('''
                        DELETE FROM memory_entries
                        WHERE timestamp < ? AND relevance_score < 0.5
                    ''', (cutoff_date,))

                deleted_count = cursor.rowcount
                conn.commit()

            logger.info(f"🧹 Cleaned up {deleted_count} old memory entries")
            return deleted_count

        except Exception as e:
            logger.error(f"❌ Error cleaning up memories: {e}")
            return 0

# Global instance
conversational_memory = ConversationalMemory()

# Helper functions for easy integration
def store_memory(user_id: str, session_id: str, message_type: str, content: str, metadata: Dict[str, Any] = None) -> str:
    """Helper function to store memory"""
    return conversational_memory.store_memory(user_id, session_id, message_type, content, metadata)

def get_conversation_context(user_id: str, session_id: str = None, max_tokens: int = 2000) -> Dict[str, Any]:
    """Helper function to get conversation context"""
    return conversational_memory.get_conversation_context(user_id, session_id, max_tokens)

def get_memory_stats(user_id: str) -> Dict[str, Any]:
    """Helper function to get memory statistics"""
    return conversational_memory.get_memory_stats(user_id)
