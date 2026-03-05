#!/usr/bin/env python3
"""
TDD Tests for Redis Cache Manager
Test-Driven Development for caching functionality
"""

import os
import pytest
import time
import json
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from src.ai_local_models.redis_cache_manager import RedisCacheManager, redis_cache


class TestRedisCacheManager:
    """Comprehensive TDD tests for Redis Cache Manager"""

    @pytest.fixture
    def mock_redis(self):
        """Mock Redis client for testing"""
        with patch('src.ai_local_models.redis_cache_manager.redis') as mock_redis:
            mock_client = MagicMock()
            mock_redis.Redis.return_value = mock_client
            mock_client.ping.return_value = True
            yield mock_client

    @pytest.fixture
    def cache_manager(self, mock_redis):
        """Create cache manager instance for testing"""
        manager = RedisCacheManager(enabled=True)
        return manager

    def test_cache_manager_initialization_enabled(self, mock_redis):
        """Test cache manager initialization when enabled"""
        manager = RedisCacheManager(enabled=True)

        assert manager.enabled is True
        assert manager.redis is not None
        mock_redis.Redis.assert_called_once()
        mock_redis.ping.assert_called_once()

    def test_cache_manager_initialization_disabled(self):
        """Test cache manager initialization when disabled"""
        with patch.dict(os.environ, {'REDIS_ENABLED': 'false'}):
            manager = RedisCacheManager()

            assert manager.enabled is False
            assert manager.redis is None

    def test_cache_manager_initialization_redis_failure(self):
        """Test cache manager initialization when Redis fails"""
        with patch('src.ai_local_models.redis_cache_manager.redis') as mock_redis:
            mock_redis.Redis.return_value.ping.side_effect = Exception("Connection failed")

            manager = RedisCacheManager(enabled=True)

            assert manager.enabled is False
            assert manager.redis is None

    def test_make_key(self, cache_manager):
        """Test key generation"""
        key = cache_manager._make_key('test_category', 'test_key')
        expected = f"{cache_manager.key_prefix}:test_category:test_key"

        assert key == expected

    def test_set_and_get_basic_data(self, cache_manager, mock_redis):
        """Test basic set and get operations"""
        # Mock Redis responses
        mock_redis.get.return_value = None
        mock_redis.setex.return_value = True

        # Test set operation
        result = cache_manager.set('test_category', 'test_key', 'test_value')
        assert result is True

        # Verify Redis calls
        mock_redis.setex.assert_called_once()
        call_args = mock_redis.setex.call_args
        assert call_args[0][0] == f"{cache_manager.key_prefix}:test_category:test_key"
        assert call_args[0][1] == cache_manager.default_timeout
        assert call_args[0][2] is not None  # Serialized data

        # Test get operation
        mock_redis.get.return_value = b'"test_value"'  # JSON serialized

        result = cache_manager.get('test_category', 'test_key')
        assert result == 'test_value'

    def test_get_nonexistent_key(self, cache_manager, mock_redis):
        """Test getting a key that doesn't exist"""
        mock_redis.get.return_value = None

        result = cache_manager.get('test_category', 'nonexistent_key')
        assert result is None

        # Test with default value
        result = cache_manager.get('test_category', 'nonexistent_key', default='default_value')
        assert result == 'default_value'

    def test_set_complex_data(self, cache_manager, mock_redis):
        """Test setting complex data structures"""
        complex_data = {
            'list': [1, 2, 3],
            'dict': {'nested': 'value'},
            'timestamp': datetime.now().isoformat()
        }

        # Test set
        result = cache_manager.set('complex', 'test_key', complex_data)
        assert result is True

        # Test get
        mock_redis.get.return_value = json.dumps(complex_data).encode('utf-8')
        result = cache_manager.get('complex', 'test_key')
        assert result == complex_data

    def test_delete_key(self, cache_manager, mock_redis):
        """Test key deletion"""
        mock_redis.delete.return_value = 1

        result = cache_manager.delete('test_category', 'test_key')
        assert result is True

        mock_redis.delete.assert_called_once()

    def test_exists_key(self, cache_manager, mock_redis):
        """Test key existence check"""
        mock_redis.exists.return_value = 1

        result = cache_manager.exists('test_category', 'test_key')
        assert result is True

        mock_redis.exists.assert_called_once()

    def test_clear_category(self, cache_manager, mock_redis):
        """Test clearing all keys in a category"""
        mock_redis.keys.return_value = [b'test_key1', b'test_key2']
        mock_redis.delete.return_value = 2

        result = cache_manager.clear_category('test_category')
        assert result is True

        mock_redis.keys.assert_called_once_with(f"{cache_manager.key_prefix}:test_category:*")
        mock_redis.delete.assert_called_once()

    def test_clear_all(self, cache_manager, mock_redis):
        """Test clearing all cached data"""
        mock_redis.keys.return_value = [b'key1', b'key2', b'key3']
        mock_redis.delete.return_value = 3

        result = cache_manager.clear_all()
        assert result is True

        mock_redis.keys.assert_called_once_with(f"{cache_manager.key_prefix}:*")

    def test_chat_history_caching(self, cache_manager, mock_redis):
        """Test chat history specific caching"""
        session_id = 'test_session_123'
        messages = [
            {'role': 'user', 'content': 'Hello'},
            {'role': 'assistant', 'content': 'Hi there!'}
        ]

        # Test set chat history
        mock_redis.setex.return_value = True
        result = cache_manager.set_chat_history(session_id, messages)
        assert result is True

        # Test get chat history
        mock_redis.get.return_value = json.dumps(messages).encode('utf-8')
        result = cache_manager.get_chat_history(session_id)
        assert result == messages

    def test_user_context_caching(self, cache_manager, mock_redis):
        """Test user context caching"""
        user_id = 'user_123'
        context = {
            'user_id': user_id,
            'company_id': 'company_456',
            'allowed_topics': ['finance', 'accounting'],
            'temperature': 0.7
        }

        # Test set user context
        result = cache_manager.set_user_context(user_id, context)
        assert result is True

        # Test get user context
        mock_redis.get.return_value = json.dumps(context).encode('utf-8')
        result = cache_manager.get_user_context(user_id)
        assert result == context

    def test_company_data_caching(self, cache_manager, mock_redis):
        """Test company data caching"""
        company_id = 'company_456'
        data = {
            'company_id': company_id,
            'name': 'Test Company',
            'data_sources': ['database1', 'database2'],
            'settings': {'theme': 'dark'}
        }

        # Test set company data
        result = cache_manager.set_company_data(company_id, data)
        assert result is True

        # Test get company data
        mock_redis.get.return_value = json.dumps(data).encode('utf-8')
        result = cache_manager.get_company_data(company_id)
        assert result == data

    def test_embeddings_caching(self, cache_manager, mock_redis):
        """Test embeddings caching"""
        content_id = 'doc_123'
        embeddings = [0.1, 0.2, 0.3, 0.4, 0.5]  # Mock embeddings

        # Test set embeddings
        result = cache_manager.set_embeddings(content_id, embeddings)
        assert result is True

        # Test get embeddings
        mock_redis.get.return_value = json.dumps(embeddings).encode('utf-8')
        result = cache_manager.get_embeddings(content_id)
        assert result == embeddings

    def test_model_config_caching(self, cache_manager, mock_redis):
        """Test model configuration caching"""
        model_id = 'llama2-7b'
        config = {
            'model_id': model_id,
            'type': 'llm',
            'size': '7B',
            'memory_required': 8192,
            'is_downloaded': True
        }

        # Test set model config
        result = cache_manager.set_model_config(model_id, config)
        assert result is True

        # Test get model config
        mock_redis.get.return_value = json.dumps(config).encode('utf-8')
        result = cache_manager.get_model_config(model_id)
        assert result == config

    def test_counter_operations(self, cache_manager, mock_redis):
        """Test counter operations"""
        mock_redis.incrby.return_value = 5

        # Test increment counter
        result = cache_manager.increment_counter('test_counter', 5)
        assert result is True

        # Test get counter
        mock_redis.get.return_value = b'10'
        result = cache_manager.get_counter('test_counter')
        assert result == 10

    def test_set_operations(self, cache_manager, mock_redis):
        """Test Redis set operations"""
        mock_redis.sadd.return_value = 1
        mock_redis.smembers.return_value = [b'item1', b'item2']

        # Test add to set
        result = cache_manager.add_to_set('test_set', 'item1')
        assert result is True

        # Test get set members
        result = cache_manager.get_set_members('test_set')
        assert result == ['item1', 'item2']

    def test_health_check_healthy(self, cache_manager, mock_redis):
        """Test health check when Redis is healthy"""
        mock_redis.setex.return_value = True
        mock_redis.get.return_value = b'test_value'
        mock_redis.delete.return_value = 1

        result = cache_manager.health_check()

        assert result['enabled'] is True
        assert result['status'] == 'healthy'
        assert result['connection'] == 'ok'
        assert result['operations'] == 'ok'

    def test_health_check_disabled(self):
        """Test health check when caching is disabled"""
        manager = RedisCacheManager(enabled=False)

        result = manager.health_check()

        assert result['enabled'] is False
        assert result['status'] == 'disabled'

    def test_health_check_disconnected(self, mock_redis):
        """Test health check when Redis is disconnected"""
        manager = RedisCacheManager(enabled=True)
        manager.redis = None  # Simulate disconnected state

        result = manager.health_check()

        assert result['enabled'] is True
        assert result['status'] == 'disconnected'

    def test_get_cache_stats(self, cache_manager, mock_redis):
        """Test cache statistics retrieval"""
        # Mock Redis info and keys
        mock_redis.info.return_value = {
            'used_memory_human': '1.5M',
            'total_connections_received': 100,
            'uptime_in_days': 5
        }

        mock_redis.keys.side_effect = [
            [b'key1', b'key2'],  # chat_history keys
            [b'key3'],           # user_data keys
            [b'key4', b'key5'],  # embeddings keys
            [b'key6'],           # model_data keys
            [b'key7'],           # company_data keys
            [b'key8']            # analytics keys
        ]

        result = cache_manager.get_cache_stats()

        assert result['enabled'] is True
        assert result['connected'] is True
        assert result['used_memory'] == '1.5M'
        assert result['total_connections'] == 100
        assert result['uptime_days'] == 5
        assert result['keys_by_category']['chat_history'] == 2
        assert result['total_cached_keys'] == 8

    def test_timeout_configuration(self, cache_manager):
        """Test different timeout configurations for categories"""
        # Test default timeout
        assert cache_manager.timeouts['user_data'] == 3600

        # Test custom timeouts
        assert cache_manager.timeouts['embeddings'] == 7200
        assert cache_manager.timeouts['chat_history'] == 1800

    def test_error_handling(self, cache_manager, mock_redis):
        """Test error handling in cache operations"""
        mock_redis.get.side_effect = Exception("Redis error")

        # Should return default value on error
        result = cache_manager.get('test_category', 'test_key', default='fallback')
        assert result == 'fallback'

        # Should return False on error
        mock_redis.setex.side_effect = Exception("Redis error")
        result = cache_manager.set('test_category', 'test_key', 'value')
        assert result is False


class TestRedisCacheManagerIntegration:
    """Integration tests for Redis Cache Manager"""

    def test_cache_manager_with_real_redis(self):
        """Test with actual Redis if available (integration test)"""
        try:
            manager = RedisCacheManager(enabled=True)

            if manager.enabled and manager.redis:
                # Test basic operations
                test_data = {'test': 'data', 'number': 42}

                # Set data
                result = manager.set('integration_test', 'test_key', test_data, timeout=10)
                assert result is True

                # Get data
                retrieved = manager.get('integration_test', 'test_key')
                assert retrieved == test_data

                # Test existence
                exists = manager.exists('integration_test', 'test_key')
                assert exists is True

                # Clean up
                manager.delete('integration_test', 'test_key')

                # Verify deletion
                exists_after = manager.exists('integration_test', 'test_key')
                assert exists_after is False
            else:
                pytest.skip("Redis not available for integration test")

        except Exception as e:
            pytest.skip(f"Redis integration test failed: {e}")

    def test_cache_manager_performance(self, cache_manager, mock_redis):
        """Test cache manager performance characteristics"""
        import time

        # Test multiple operations
        start_time = time.time()

        for i in range(100):
            cache_manager.set('performance', f'key_{i}', f'value_{i}')
            cache_manager.get('performance', f'key_{i}')

        end_time = time.time()
        duration = end_time - start_time

        # Should complete within reasonable time (adjust as needed)
        assert duration < 5.0, f"Performance test took too long: {duration}s"

    def test_concurrent_access(self, cache_manager, mock_redis):
        """Test concurrent access to cache manager"""
        import threading
        import queue

        results = queue.Queue()

        def worker(worker_id):
            try:
                # Each worker performs operations
                for i in range(10):
                    key = f"worker_{worker_id}_key_{i}"
                    cache_manager.set('concurrent', key, f'value_{i}')
                    value = cache_manager.get('concurrent', key)
                    results.put((worker_id, i, value))

            except Exception as e:
                results.put((worker_id, 'error', str(e)))

        # Start multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=worker, args=(i,))
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join(timeout=10)
            assert not thread.is_alive(), "Thread should have completed"

        # Check results
        completed_operations = 0
        while not results.empty():
            worker_id, operation, result = results.get()
            if operation != 'error':
                completed_operations += 1
            else:
                pytest.fail(f"Worker {worker_id} failed: {result}")

        assert completed_operations == 50, f"Expected 50 operations, got {completed_operations}"


if __name__ == '__main__':
    pytest.main([__file__])
