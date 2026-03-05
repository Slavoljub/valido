"""
Performance and Load Tests for Webhook System
Tests system performance under various loads and conditions
"""
import pytest
import json
import time
import asyncio
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from unittest.mock import patch, AsyncMock
from datetime import datetime
from flask import Flask
from flask.testing import FlaskClient

from src.models.webhook_models import webhook_manager
from src.controllers.webhook_controller import webhook_controller
from src.services.webhook_service import webhook_service, StandardEventTypes


class TestWebhookPerformance:
    """Performance testing for webhook system"""

    def setup_method(self):
        """Setup test environment"""
        webhook_manager._init_database()
        self._cleanup_test_data()

    def teardown_method(self):
        """Clean up test environment"""
        self._cleanup_test_data()

    def _cleanup_test_data(self):
        """Clean up test data"""
        with webhook_manager.db_path as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM webhook_subscriptions WHERE name LIKE 'perf_%'")
            cursor.execute("DELETE FROM webhook_events WHERE event_type LIKE 'perf_%'")
            conn.commit()

    def test_webhook_creation_performance(self, client: FlaskClient):
        """Test performance of webhook creation"""
        webhook_base = {
            'event_type': StandardEventTypes.CHAT_MESSAGE_SENT,
            'url': 'https://httpbin.org/post',
            'is_active': True
        }

        # Test creating multiple webhooks
        start_time = time.time()
        webhook_ids = []

        for i in range(50):  # Create 50 webhooks
            webhook_data = webhook_base.copy()
            webhook_data['name'] = f'perf_creation_webhook_{i}'

            response = client.post('/api/v1/webhooks',
                                 data=json.dumps(webhook_data),
                                 content_type='application/json')
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            webhook_ids.append(data['data']['id'])

        end_time = time.time()
        creation_time = end_time - start_time

        # Should create 50 webhooks in reasonable time
        assert creation_time < 30, f"Creating 50 webhooks took too long: {creation_time}s"
        print(".2f")

        # Clean up
        for webhook_id in webhook_ids:
            client.delete(f'/api/v1/webhooks/{webhook_id}')

    def test_webhook_retrieval_performance(self, client: FlaskClient):
        """Test performance of webhook retrieval operations"""
        # Create test webhooks
        webhook_ids = []
        for i in range(25):
            webhook_data = {
                'name': f'perf_retrieval_webhook_{i}',
                'event_type': StandardEventTypes.USER_LOGIN,
                'url': 'https://httpbin.org/post',
                'is_active': True
            }

            response = client.post('/api/v1/webhooks',
                                 data=json.dumps(webhook_data),
                                 content_type='application/json')
            webhook_ids.append(json.loads(response.data)['data']['id'])

        # Test listing performance
        start_time = time.time()

        for _ in range(10):  # Multiple retrievals
            response = client.get('/api/v1/webhooks')
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            assert len(data['data']) >= 25

        end_time = time.time()
        retrieval_time = end_time - start_time

        # Should retrieve webhooks quickly
        assert retrieval_time < 5, f"Webhook retrieval took too long: {retrieval_time}s"
        print(".2f")

        # Test individual webhook retrieval
        start_time = time.time()

        for webhook_id in webhook_ids[:10]:  # Test first 10
            response = client.get(f'/api/v1/webhooks/{webhook_id}')
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True

        end_time = time.time()
        individual_time = end_time - start_time

        assert individual_time < 3, f"Individual webhook retrieval took too long: {individual_time}s"
        print(".2f")

        # Clean up
        for webhook_id in webhook_ids:
            client.delete(f'/api/v1/webhooks/{webhook_id}')

    def test_webhook_triggering_performance(self, client: FlaskClient):
        """Test performance of webhook triggering"""
        # Create webhooks for different event types
        webhook_ids = []
        event_types = [
            StandardEventTypes.CHAT_MESSAGE_SENT,
            StandardEventTypes.USER_LOGIN,
            StandardEventTypes.FINANCIAL_TRANSACTION_CREATED,
            StandardEventTypes.SYSTEM_ERROR_OCCURRED,
            StandardEventTypes.NOTIFICATION_SENT
        ]

        for i, event_type in enumerate(event_types):
            webhook_data = {
                'name': f'perf_trigger_webhook_{i}',
                'event_type': event_type,
                'url': 'https://httpbin.org/post',
                'is_active': True
            }

            response = client.post('/api/v1/webhooks',
                                 data=json.dumps(webhook_data),
                                 content_type='application/json')
            webhook_ids.append(json.loads(response.data)['data']['id'])

        # Test triggering performance
        start_time = time.time()

        for i in range(20):  # Trigger 20 events
            event_type = event_types[i % len(event_types)]
            trigger_data = {
                'event_type': event_type,
                'data': {
                    'test_run': i,
                    'timestamp': datetime.now().isoformat(),
                    'message': f'Performance test message {i}'
                }
            }

            response = client.post('/api/v1/webhooks/trigger-event',
                                 data=json.dumps(trigger_data),
                                 content_type='application/json')
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True

        end_time = time.time()
        trigger_time = end_time - start_time

        # Should trigger events reasonably quickly
        assert trigger_time < 15, f"Triggering 20 events took too long: {trigger_time}s"
        print(".2f")

        # Clean up
        for webhook_id in webhook_ids:
            client.delete(f'/api/v1/webhooks/{webhook_id}')

    def test_bulk_operations_performance(self, client: FlaskClient):
        """Test performance of bulk operations"""
        # Create webhooks for bulk testing
        webhook_ids = []
        for i in range(10):
            webhook_data = {
                'name': f'perf_bulk_webhook_{i}',
                'event_type': StandardEventTypes.CHAT_MESSAGE_SENT,
                'url': 'https://httpbin.org/post',
                'is_active': True
            }

            response = client.post('/api/v1/webhooks',
                                 data=json.dumps(webhook_data),
                                 content_type='application/json')
            webhook_ids.append(json.loads(response.data)['data']['id'])

        # Test bulk event triggering
        bulk_events = []
        for i in range(25):
            bulk_events.append({
                'event_type': StandardEventTypes.CHAT_MESSAGE_SENT,
                'data': {
                    'bulk_test': True,
                    'sequence': i,
                    'timestamp': datetime.now().isoformat()
                }
            })

        start_time = time.time()

        response = client.post('/api/v1/webhooks/trigger-bulk',
                             data=json.dumps({'events': bulk_events}),
                             content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['total_events'] == 25

        end_time = time.time()
        bulk_time = end_time - start_time

        # Should handle bulk operations efficiently
        assert bulk_time < 10, f"Bulk operation took too long: {bulk_time}s"
        print(".2f")

        # Clean up
        for webhook_id in webhook_ids:
            client.delete(f'/api/v1/webhooks/{webhook_id}')

    def test_concurrent_webhook_operations(self, client: FlaskClient):
        """Test concurrent webhook operations"""
        webhook_data = {
            'name': 'perf_concurrent_webhook',
            'event_type': StandardEventTypes.USER_LOGIN,
            'url': 'https://httpbin.org/post',
            'is_active': True
        }

        response = client.post('/api/v1/webhooks',
                             data=json.dumps(webhook_data),
                             content_type='application/json')
        webhook_id = json.loads(response.data)['data']['id']

        def perform_concurrent_operation(operation_id):
            """Function to perform operations concurrently"""
            try:
                trigger_data = {
                    'event_type': StandardEventTypes.USER_LOGIN,
                    'data': {
                        'concurrent_test': True,
                        'operation_id': operation_id,
                        'timestamp': datetime.now().isoformat()
                    }
                }

                response = client.post('/api/v1/webhooks/trigger-event',
                                     data=json.dumps(trigger_data),
                                     content_type='application/json')
                return response.status_code == 200
            except Exception as e:
                print(f"Error in concurrent operation {operation_id}: {e}")
                return False

        # Test concurrent operations using ThreadPoolExecutor
        start_time = time.time()

        with ThreadPoolExecutor(max_workers=10) as executor:
            # Submit 50 concurrent operations
            futures = [executor.submit(perform_concurrent_operation, i) for i in range(50)]

            # Wait for all operations to complete
            results = [future.result() for future in as_completed(futures)]

        end_time = time.time()
        concurrent_time = end_time - start_time

        # All operations should succeed
        assert all(results), "Some concurrent operations failed"
        assert concurrent_time < 30, f"Concurrent operations took too long: {concurrent_time}s"
        print(".2f")

        # Verify events were created
        response = client.get('/api/v1/webhooks/events')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['total'] >= 50

        # Clean up
        client.delete(f'/api/v1/webhooks/{webhook_id}')

    def test_database_performance_under_load(self, client: FlaskClient):
        """Test database performance under load"""
        # Create multiple webhooks
        webhook_ids = []
        for i in range(30):
            webhook_data = {
                'name': f'perf_db_webhook_{i}',
                'event_type': StandardEventTypes.FINANCIAL_TRANSACTION_CREATED,
                'url': 'https://httpbin.org/post',
                'is_active': True
            }

            response = client.post('/api/v1/webhooks',
                                 data=json.dumps(webhook_data),
                                 content_type='application/json')
            webhook_ids.append(json.loads(response.data)['data']['id'])

        # Generate many events
        start_time = time.time()

        for i in range(100):
            trigger_data = {
                'event_type': StandardEventTypes.FINANCIAL_TRANSACTION_CREATED,
                'data': {
                    'transaction_id': f'tx_{i}',
                    'amount': 100.00 + i,
                    'timestamp': datetime.now().isoformat()
                }
            }

            response = client.post('/api/v1/webhooks/trigger-event',
                                 data=json.dumps(trigger_data),
                                 content_type='application/json')
            assert response.status_code == 200

        end_time = time.time()
        load_time = end_time - start_time

        # Should handle load reasonably well
        assert load_time < 60, f"Load test took too long: {load_time}s"
        print(".2f")

        # Test database queries under load
        start_time = time.time()

        for _ in range(20):
            response = client.get('/api/v1/webhooks/events')
            assert response.status_code == 200

            response = client.get('/api/v1/webhooks')
            assert response.status_code == 200

            response = client.get('/api/v1/webhooks/stats')
            assert response.status_code == 200

        end_time = time.time()
        query_time = end_time - start_time

        assert query_time < 10, f"Database queries under load took too long: {query_time}s"
        print(".2f")

        # Clean up
        for webhook_id in webhook_ids:
            client.delete(f'/api/v1/webhooks/{webhook_id}')

    def test_memory_usage_monitoring(self, client: FlaskClient):
        """Test memory usage during operations"""
        import psutil
        import os

        # Get initial memory usage
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Create webhooks and generate load
        webhook_ids = []
        for i in range(20):
            webhook_data = {
                'name': f'perf_memory_webhook_{i}',
                'event_type': StandardEventTypes.CHAT_MESSAGE_SENT,
                'url': 'https://httpbin.org/post',
                'is_active': True
            }

            response = client.post('/api/v1/webhooks',
                                 data=json.dumps(webhook_data),
                                 content_type='application/json')
            webhook_ids.append(json.loads(response.data)['data']['id'])

        # Generate events
        for i in range(50):
            trigger_data = {
                'event_type': StandardEventTypes.CHAT_MESSAGE_SENT,
                'data': {'message': f'Memory test {i}'}
            }

            client.post('/api/v1/webhooks/trigger-event',
                       data=json.dumps(trigger_data),
                       content_type='application/json')

        # Check memory usage after operations
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory

        # Memory increase should be reasonable
        assert memory_increase < 100, f"Memory usage increased too much: +{memory_increase:.2f}MB"

        print(".2f")
        print(".2f")
        print("+.2f"
        # Clean up
        for webhook_id in webhook_ids:
            client.delete(f'/api/v1/webhooks/{webhook_id}')

    def test_response_time_distribution(self, client: FlaskClient):
        """Test response time distribution under various loads"""
        webhook_data = {
            'name': 'perf_response_time_webhook',
            'event_type': StandardEventTypes.USER_LOGIN,
            'url': 'https://httpbin.org/post',
            'is_active': True
        }

        response = client.post('/api/v1/webhooks',
                             data=json.dumps(webhook_data),
                             content_type='application/json')
        webhook_id = json.loads(response.data)['data']['id']

        # Measure response times for different operations
        response_times = {
            'trigger_event': [],
            'get_webhooks': [],
            'get_events': [],
            'get_stats': []
        }

        # Perform operations and measure times
        for i in range(30):
            # Trigger event
            start_time = time.time()
            trigger_data = {
                'event_type': StandardEventTypes.USER_LOGIN,
                'data': {'test_id': i}
            }
            client.post('/api/v1/webhooks/trigger-event',
                       data=json.dumps(trigger_data),
                       content_type='application/json')
            response_times['trigger_event'].append(time.time() - start_time)

            # Get webhooks
            start_time = time.time()
            client.get('/api/v1/webhooks')
            response_times['get_webhooks'].append(time.time() - start_time)

            # Get events
            start_time = time.time()
            client.get('/api/v1/webhooks/events')
            response_times['get_events'].append(time.time() - start_time)

            # Get stats
            start_time = time.time()
            client.get('/api/v1/webhooks/stats')
            response_times['get_stats'].append(time.time() - start_time)

        # Calculate statistics for each operation type
        for operation, times in response_times.items():
            avg_time = sum(times) / len(times)
            max_time = max(times)
            min_time = min(times)

            # Response times should be reasonable
            assert avg_time < 1.0, f"Average {operation} time too slow: {avg_time:.3f}s"
            assert max_time < 5.0, f"Max {operation} time too slow: {max_time:.3f}s"

            print("6")

        # Clean up
        client.delete(f'/api/v1/webhooks/{webhook_id}')

    def test_system_resources_monitoring(self, client: FlaskClient):
        """Test system resource monitoring during operations"""
        import psutil
        import os

        process = psutil.Process(os.getpid())

        # Monitor CPU and memory during operations
        webhook_ids = []
        cpu_percentages = []
        memory_percentages = []

        # Create webhooks
        for i in range(15):
            webhook_data = {
                'name': f'perf_resource_webhook_{i}',
                'event_type': StandardEventTypes.NOTIFICATION_SENT,
                'url': 'https://httpbin.org/post',
                'is_active': True
            }

            response = client.post('/api/v1/webhooks',
                                 data=json.dumps(webhook_data),
                                 content_type='application/json')
            webhook_ids.append(json.loads(response.data)['data']['id'])

        # Monitor resources during operations
        for i in range(40):
            # Perform operations
            trigger_data = {
                'event_type': StandardEventTypes.NOTIFICATION_SENT,
                'data': {'resource_test': i}
            }

            client.post('/api/v1/webhooks/trigger-event',
                       data=json.dumps(trigger_data),
                       content_type='application/json')

            # Monitor resources
            cpu_percent = process.cpu_percent(interval=0.1)
            memory_percent = process.memory_percent()

            cpu_percentages.append(cpu_percent)
            memory_percentages.append(memory_percent)

            # Log high resource usage
            if cpu_percent > 50 or memory_percent > 50:
                print(f"High resource usage - CPU: {cpu_percent:.1f}%, Memory: {memory_percent:.1f}%")

        # Calculate averages
        avg_cpu = sum(cpu_percentages) / len(cpu_percentages)
        avg_memory = sum(memory_percentages) / len(memory_percentages)
        max_cpu = max(cpu_percentages)
        max_memory = max(memory_percentages)

        print(".1f")
        print(".1f")
        print(".1f")
        print(".1f")

        # Resource usage should be reasonable
        assert avg_cpu < 30, f"Average CPU usage too high: {avg_cpu:.1f}%"
        assert avg_memory < 30, f"Average memory usage too high: {avg_memory:.1f}%"
        assert max_cpu < 80, f"Peak CPU usage too high: {max_cpu:.1f}%"
        assert max_memory < 80, f"Peak memory usage too high: {max_memory:.1f}%"

        # Clean up
        for webhook_id in webhook_ids:
            client.delete(f'/api/v1/webhooks/{webhook_id}')

    def test_scalability_with_many_webhooks(self, client: FlaskClient):
        """Test system scalability with many webhooks"""
        # Test with increasing number of webhooks
        webhook_counts = [10, 25, 50, 100]
        performance_results = {}

        for count in webhook_counts:
            webhook_ids = []

            # Create webhooks
            start_time = time.time()
            for i in range(count):
                webhook_data = {
                    'name': f'perf_scale_webhook_{count}_{i}',
                    'event_type': StandardEventTypes.CHAT_MESSAGE_SENT,
                    'url': 'https://httpbin.org/post',
                    'is_active': True
                }

                response = client.post('/api/v1/webhooks',
                                     data=json.dumps(webhook_data),
                                     content_type='application/json')
                webhook_ids.append(json.loads(response.data)['data']['id'])

            creation_time = time.time() - start_time

            # Test listing performance
            start_time = time.time()
            response = client.get('/api/v1/webhooks')
            list_time = time.time() - start_time

            # Test triggering with many webhooks
            start_time = time.time()
            trigger_data = {
                'event_type': StandardEventTypes.CHAT_MESSAGE_SENT,
                'data': {'scale_test': count}
            }
            response = client.post('/api/v1/webhooks/trigger-event',
                                 data=json.dumps(trigger_data),
                                 content_type='application/json')
            trigger_time = time.time() - start_time

            performance_results[count] = {
                'creation_time': creation_time,
                'list_time': list_time,
                'trigger_time': trigger_time
            }

            print("3")

            # Clean up for this count
            for webhook_id in webhook_ids:
                client.delete(f'/api/v1/webhooks/{webhook_id}')

        # Performance should scale reasonably
        for count in webhook_counts:
            results = performance_results[count]
            assert results['creation_time'] < count * 0.5, f"Creation time scales poorly for {count} webhooks"
            assert results['list_time'] < 2.0, f"List time too slow for {count} webhooks"
            assert results['trigger_time'] < 5.0, f"Trigger time too slow for {count} webhooks"

    def test_long_running_operations(self, client: FlaskClient):
        """Test system stability during long-running operations"""
        webhook_data = {
            'name': 'perf_long_running_webhook',
            'event_type': StandardEventTypes.SYSTEM_BACKUP_STARTED,
            'url': 'https://httpbin.org/post',
            'is_active': True,
            'timeout': 60  # Longer timeout for stability testing
        }

        response = client.post('/api/v1/webhooks',
                             data=json.dumps(webhook_data),
                             content_type='application/json')
        webhook_id = json.loads(response.data)['data']['id']

        # Perform operations over an extended period
        start_time = time.time()
        operation_count = 0

        while time.time() - start_time < 10:  # Run for 10 seconds
            trigger_data = {
                'event_type': StandardEventTypes.SYSTEM_BACKUP_STARTED,
                'data': {
                    'operation_count': operation_count,
                    'timestamp': datetime.now().isoformat(),
                    'uptime_seconds': time.time() - start_time
                }
            }

            response = client.post('/api/v1/webhooks/trigger-event',
                                 data=json.dumps(trigger_data),
                                 content_type='application/json')
            assert response.status_code == 200

            operation_count += 1

            # Small delay to prevent overwhelming the system
            time.sleep(0.1)

        end_time = time.time()
        duration = end_time - start_time

        print(".1f")
        print(f"Operations performed: {operation_count}")

        # Should maintain stability over time
        assert duration >= 9.5, "Test should run for full duration"
        assert operation_count >= 90, "Should perform reasonable number of operations"

        # System should still be responsive
        response = client.get('/api/v1/webhooks/health')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True

        # Clean up
        client.delete(f'/api/v1/webhooks/{webhook_id}')


# Test configuration
@pytest.fixture(scope="session")
def client():
    """Create test client"""
    from app import app
    app.config['TESTING'] = True
    return app.test_client()


@pytest.fixture(autouse=True)
def cleanup_performance_data(client: FlaskClient):
    """Clean up test data after each test"""
    yield
    try:
        # Clean webhooks
        response = client.get('/api/v1/webhooks')
        if response.status_code == 200:
            data = json.loads(response.data)
            if data['success']:
                for webhook in data['data']:
                    if webhook['name'].startswith('perf_'):
                        client.delete(f'/api/v1/webhooks/{webhook["id"]}')

    except Exception:
        pass  # Ignore cleanup errors
