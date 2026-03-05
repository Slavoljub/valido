#!/usr/bin/env python3
"""
Redis Cache Manager
Provides Redis-based caching for AI chat, embeddings, and system data
"""

import os
import json
import pickle
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
import threading

logger = logging.getLogger(__name__)

class RedisCacheManager:
    """Redis-based caching system for AI applications"""

    def __init__(self, enabled: bool = None, **redis_config):
        self.enabled = enabled if enabled is not None else os.getenv('REDIS_ENABLED', 'true').lower() == 'true'
        self._lock = threading.Lock()

        if not self.enabled:
            logger.info("Redis caching is disabled")
            self.redis = None
            return

        try:
            import redis
            self.redis = redis.Redis(**redis_config)

            # Test connection
            self.redis.ping()
            logger.info("✅ Redis connection established")

        except ImportError:
            logger.warning("Redis library not available, caching disabled")
            self.redis = None
            self.enabled = False
        except Exception as e:
            logger.error(f"Redis connection failed: {e}")
            self.redis = None
            self.enabled = False

        # Configuration
        self.key_prefix = os.getenv('REDIS_CACHE_KEY_PREFIX', 'validoai')
        self.default_timeout = int(os.getenv('REDIS_CACHE_DEFAULT_TIMEOUT', '3600'))

        # Cache timeouts for different data types
        self.timeouts = {
            'embeddings': int(os.getenv('REDIS_CACHE_EMBEDDINGS_TIMEOUT', '7200')),
            'chat_history': int(os.getenv('REDIS_CACHE_CHAT_HISTORY_TIMEOUT', '1800')),
            'model_data': int(os.getenv('REDIS_CACHE_MODEL_DATA_TIMEOUT', '3600')),
            'user_data': int(os.getenv('REDIS_SESSION_TIMEOUT', '3600')),
            'company_data': 3600,
            'analytics': 3600
        }

    def _make_key(self, category: str, key: str) -> str:
        """Create a Redis key with prefix"""
        return f"{self.key_prefix}:{category}:{key}"

    def get(self, category: str, key: str, default: Any = None) -> Any:
        """Get cached data"""
        if not self.enabled or not self.redis:
            return default

        try:
            redis_key = self._make_key(category, key)
            data = self.redis.get(redis_key)

            if data is None:
                return default

            # Try to decode JSON first, then pickle
            try:
                return json.loads(data.decode('utf-8'))
            except (json.JSONDecodeError, UnicodeDecodeError):
                return pickle.loads(data)

        except Exception as e:
            logger.warning(f"Error getting cache data: {e}")
            return default

    def set(self, category: str, key: str, value: Any, timeout: int = None) -> bool:
        """Set cached data"""
        if not self.enabled or not self.redis:
            return False

        try:
            redis_key = self._make_key(category, key)

            # Use JSON for serializable data, pickle for complex objects
            try:
                data = json.dumps(value, ensure_ascii=False).encode('utf-8')
            except (TypeError, ValueError):
                data = pickle.dumps(value)

            timeout = timeout or self.timeouts.get(category, self.default_timeout)

            return bool(self.redis.setex(redis_key, timeout, data))

        except Exception as e:
            logger.warning(f"Error setting cache data: {e}")
            return False

    def delete(self, category: str, key: str) -> bool:
        """Delete cached data"""
        if not self.enabled or not self.redis:
            return False

        try:
            redis_key = self._make_key(category, key)
            return bool(self.redis.delete(redis_key))
        except Exception as e:
            logger.warning(f"Error deleting cache data: {e}")
            return False

    def exists(self, category: str, key: str) -> bool:
        """Check if key exists in cache"""
        if not self.enabled or not self.redis:
            return False

        try:
            redis_key = self._make_key(category, key)
            return bool(self.redis.exists(redis_key))
        except Exception as e:
            logger.warning(f"Error checking cache existence: {e}")
            return False

    def clear_category(self, category: str) -> bool:
        """Clear all keys in a category"""
        if not self.enabled or not self.redis:
            return False

        try:
            pattern = self._make_key(category, "*")
            keys = self.redis.keys(pattern)

            if keys:
                return bool(self.redis.delete(*keys))
            return True

        except Exception as e:
            logger.warning(f"Error clearing category cache: {e}")
            return False

    def clear_all(self) -> bool:
        """Clear all cached data"""
        if not self.enabled or not self.redis:
            return False

        try:
            pattern = f"{self.key_prefix}:*"
            keys = self.redis.keys(pattern)

            if keys:
                return bool(self.redis.delete(*keys))
            return True

        except Exception as e:
            logger.warning(f"Error clearing all cache: {e}")
            return False

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        if not self.enabled or not self.redis:
            return {"enabled": False}

        try:
            info = self.redis.info()

            # Count keys by category
            category_counts = {}
            for category in self.timeouts.keys():
                pattern = self._make_key(category, "*")
                keys = self.redis.keys(pattern)
                category_counts[category] = len(keys) if keys else 0

            return {
                "enabled": True,
                "connected": True,
                "used_memory": info.get('used_memory_human', 'N/A'),
                "total_connections": info.get('total_connections_received', 0),
                "uptime_days": info.get('uptime_in_days', 0),
                "keys_by_category": category_counts,
                "total_cached_keys": sum(category_counts.values())
            }

        except Exception as e:
            return {
                "enabled": True,
                "connected": False,
                "error": str(e)
            }

    # ==========================================
    # CHAT-SPECIFIC CACHE METHODS
    # ==========================================

    def get_chat_history(self, session_id: str) -> Optional[List[Dict]]:
        """Get cached chat history for a session"""
        return self.get('chat_history', f"session:{session_id}")

    def set_chat_history(self, session_id: str, messages: List[Dict]) -> bool:
        """Cache chat history for a session"""
        return self.set('chat_history', f"session:{session_id}", messages)

    def get_user_context(self, user_id: str) -> Optional[Dict]:
        """Get cached user context"""
        return self.get('user_data', f"context:{user_id}")

    def set_user_context(self, user_id: str, context: Dict) -> bool:
        """Cache user context"""
        return self.set('user_data', f"context:{user_id}", context)

    def get_company_data(self, company_id: str) -> Optional[Dict]:
        """Get cached company data"""
        return self.get('company_data', f"data:{company_id}")

    def set_company_data(self, company_id: str, data: Dict) -> bool:
        """Cache company data"""
        return self.set('company_data', f"data:{company_id}", data)

    # ==========================================
    # EMBEDDINGS CACHE METHODS
    # ==========================================

    def get_embeddings(self, content_id: str) -> Optional[Any]:
        """Get cached embeddings for content"""
        return self.get('embeddings', f"content:{content_id}")

    def set_embeddings(self, content_id: str, embeddings: Any) -> bool:
        """Cache embeddings for content"""
        return self.set('embeddings', f"content:{content_id}", embeddings)

    def get_similar_content_cache(self, query_hash: str) -> Optional[List[Dict]]:
        """Get cached similar content results"""
        return self.get('embeddings', f"similar:{query_hash}")

    def set_similar_content_cache(self, query_hash: str, results: List[Dict]) -> bool:
        """Cache similar content results"""
        return self.set('embeddings', f"similar:{query_hash}", results)

    # ==========================================
    # MODEL DATA CACHE METHODS
    # ==========================================

    def get_model_config(self, model_id: str) -> Optional[Dict]:
        """Get cached model configuration"""
        return self.get('model_data', f"config:{model_id}")

    def set_model_config(self, model_id: str, config: Dict) -> bool:
        """Cache model configuration"""
        return self.set('model_data', f"config:{model_id}", config)

    def get_model_status(self, model_id: str) -> Optional[Dict]:
        """Get cached model status"""
        return self.get('model_data', f"status:{model_id}")

    def set_model_status(self, model_id: str, status: Dict) -> bool:
        """Cache model status"""
        return self.set('model_data', f"status:{model_id}", status)

    # ==========================================
    # ANALYTICS CACHE METHODS
    # ==========================================

    def get_analytics_data(self, metric: str, time_range: str) -> Optional[Dict]:
        """Get cached analytics data"""
        return self.get('analytics', f"metric:{metric}:{time_range}")

    def set_analytics_data(self, metric: str, time_range: str, data: Dict) -> bool:
        """Cache analytics data"""
        return self.set('analytics', f"metric:{metric}:{time_range}", data)

    def increment_counter(self, counter_name: str, amount: int = 1) -> bool:
        """Increment a counter in Redis"""
        if not self.enabled or not self.redis:
            return False

        try:
            key = self._make_key('counters', counter_name)
            return bool(self.redis.incrby(key, amount))
        except Exception as e:
            logger.warning(f"Error incrementing counter: {e}")
            return False

    def get_counter(self, counter_name: str) -> int:
        """Get counter value"""
        if not self.enabled or not self.redis:
            return 0

        try:
            key = self._make_key('counters', counter_name)
            value = self.redis.get(key)
            return int(value) if value else 0
        except Exception as e:
            logger.warning(f"Error getting counter: {e}")
            return 0

    def add_to_set(self, set_name: str, value: str) -> bool:
        """Add value to a Redis set"""
        if not self.enabled or not self.redis:
            return False

        try:
            key = self._make_key('sets', set_name)
            return bool(self.redis.sadd(key, value))
        except Exception as e:
            logger.warning(f"Error adding to set: {e}")
            return False

    def get_set_members(self, set_name: str) -> List[str]:
        """Get all members of a Redis set"""
        if not self.enabled or not self.redis:
            return []

        try:
            key = self._make_key('sets', set_name)
            members = self.redis.smembers(key)
            return [member.decode('utf-8') for member in members] if members else []
        except Exception as e:
            logger.warning(f"Error getting set members: {e}")
            return []

    def health_check(self) -> Dict[str, Any]:
        """Perform health check on Redis"""
        if not self.enabled:
            return {"enabled": False, "status": "disabled"}

        if not self.redis:
            return {"enabled": True, "status": "disconnected"}

        try:
            # Test basic operations
            test_key = self._make_key('health', 'test')
            self.redis.setex(test_key, 10, 'test_value')
            value = self.redis.get(test_key)
            self.redis.delete(test_key)

            if value and value.decode('utf-8') == 'test_value':
                return {
                    "enabled": True,
                    "status": "healthy",
                    "connection": "ok",
                    "operations": "ok"
                }
            else:
                return {
                    "enabled": True,
                    "status": "unhealthy",
                    "connection": "ok",
                    "operations": "failed"
                }

        except Exception as e:
            return {
                "enabled": True,
                "status": "unhealthy",
                "connection": "failed",
                "error": str(e)
            }

# Global instance
redis_cache = RedisCacheManager(
    host=os.getenv('REDIS_HOST', 'localhost'),
    port=int(os.getenv('REDIS_PORT', 6379)),
    db=int(os.getenv('REDIS_DB', 0)),
    password=os.getenv('REDIS_PASSWORD', None),
    decode_responses=False,
    socket_timeout=int(os.getenv('REDIS_SOCKET_TIMEOUT', 5)),
    socket_connect_timeout=int(os.getenv('REDIS_SOCKET_CONNECT_TIMEOUT', 5)),
    max_connections=int(os.getenv('REDIS_MAX_CONNECTIONS', 20))
)
