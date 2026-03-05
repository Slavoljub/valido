"""
ValidoAI N8N Integration Module
===============================

Comprehensive N8N workflow automation integration for ValidoAI.

Features:
- Workflow execution and management
- Webhook handling for N8N workflows
- Real-time workflow status monitoring
- Workflow templates and examples
- Error handling and retry logic
- Security and authentication
- Database integration for workflow data

This module provides a complete bridge between ValidoAI and N8N,
enabling powerful workflow automation capabilities.
"""

import os
import json
import sys
import time
import uuid
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Callable, Union
from dataclasses import dataclass, asdict
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import threading
import queue
from pathlib import Path
import hashlib
import hmac
import base64

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Import global logger if available
try:
    from src.core.global_logger import global_logger, ErrorContext, ErrorSeverity, ErrorCategory
    GLOBAL_LOGGER_AVAILABLE = True
except ImportError:
    GLOBAL_LOGGER_AVAILABLE = False
    logger = logging.getLogger(__name__)

@dataclass
class N8NWorkflow:
    """N8N Workflow configuration"""
    id: str
    name: str
    description: str
    nodes: List[Dict[str, Any]]
    connections: Dict[str, Any]
    settings: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    is_active: bool = True
    tags: List[str] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.metadata is None:
            self.metadata = {}

@dataclass
class N8NExecution:
    """N8N Workflow execution result"""
    id: str
    workflow_id: str
    execution_id: str
    status: str  # 'running', 'success', 'error', 'waiting'
    started_at: datetime
    finished_at: Optional[datetime] = None
    duration: Optional[float] = None
    input_data: Dict[str, Any] = None
    output_data: Dict[str, Any] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    webhook_url: Optional[str] = None

    def __post_init__(self):
        if self.input_data is None:
            self.input_data = {}
        if self.output_data is None:
            self.output_data = {}

class N8NIntegration:
    """Main N8N Integration class"""

    def __init__(self, config: Dict[str, Any] = None):
        """Initialize N8N integration with configuration"""
        self.config = config or self._load_config()
        self.session = self._create_session()
        self.workflows: Dict[str, N8NWorkflow] = {}
        self.executions: Dict[str, N8NExecution] = {}
        self.webhook_handlers: Dict[str, Callable] = {}
        self.execution_queue = queue.Queue()
        self.is_running = False
        self._setup_logging()

        # Start execution processor if enabled
        if self.config.get('enabled', False):
            self._start_execution_processor()

    def _load_config(self) -> Dict[str, Any]:
        """Load N8N configuration from environment variables"""
        return {
            'enabled': os.getenv('N8N_ENABLED', 'false').lower() == 'true',
            'base_url': os.getenv('N8N_BASE_URL', 'http://localhost:5678'),
            'api_url': os.getenv('N8N_API_URL', ''),
            'api_key': os.getenv('N8N_API_KEY', ''),
            'webhook_url': os.getenv('N8N_WEBHOOK_URL', ''),
            'webhook_timeout': int(os.getenv('N8N_WEBHOOK_TIMEOUT', '30')),
            'retry_attempts': int(os.getenv('N8N_RETRY_ATTEMPTS', '3')),
            'connection_timeout': int(os.getenv('N8N_CONNECTION_TIMEOUT', '10')),
            'max_connections': int(os.getenv('N8N_MAX_CONNECTIONS', '10')),
            'workflow_timeout': int(os.getenv('N8N_WORKFLOW_TIMEOUT', '300')),
            'workflow_execution_timeout': int(os.getenv('N8N_WORKFLOW_EXECUTION_TIMEOUT', '600')),
            'workflow_max_executions': int(os.getenv('N8N_WORKFLOW_MAX_EXECUTIONS', '100')),
            'workflow_concurrency': int(os.getenv('N8N_WORKFLOW_CONCURRENCY', '5')),
            'username': os.getenv('N8N_USERNAME', ''),
            'password': os.getenv('N8N_PASSWORD', ''),
            'jwt_secret': os.getenv('N8N_JWT_SECRET', ''),
            'encryption_key': os.getenv('N8N_ENCRYPTION_KEY', ''),
            'cors_enabled': os.getenv('N8N_CORS_ENABLED', 'true').lower() == 'true',
            'cors_origins': os.getenv('N8N_CORS_ORIGINS', '').split(','),
            'csrf_enabled': os.getenv('N8N_CSRF_ENABLED', 'true').lower() == 'true',
            'session_secret': os.getenv('N8N_SESSION_SECRET', ''),
            'rate_limit_enabled': os.getenv('N8N_RATE_LIMIT_ENABLED', 'true').lower() == 'true',
            'rate_limit_requests': int(os.getenv('N8N_RATE_LIMIT_REQUESTS', '100')),
            'rate_limit_window': int(os.getenv('N8N_RATE_LIMIT_WINDOW', '3600')),
            'metrics_enabled': os.getenv('N8N_METRICS_ENABLED', 'true').lower() == 'true',
            'metrics_port': int(os.getenv('N8N_METRICS_PORT', '9090')),
            'log_level': os.getenv('N8N_LOG_LEVEL', 'info'),
            'log_file': os.getenv('N8N_LOG_FILE', 'logs/n8n.log'),
            'audit_log_enabled': os.getenv('N8N_AUDIT_LOG_ENABLED', 'true').lower() == 'true',
            'audit_log_file': os.getenv('N8N_AUDIT_LOG_FILE', 'logs/n8n_audit.log'),
            'workflow_storage_path': os.getenv('N8N_WORKFLOW_STORAGE_PATH', 'data/n8n/workflows'),
            'workflow_backup_enabled': os.getenv('N8N_WORKFLOW_BACKUP_ENABLED', 'true').lower() == 'true',
            'workflow_backup_path': os.getenv('N8N_WORKFLOW_BACKUP_PATH', 'data/n8n/backups'),
            'workflow_backup_retention_days': int(os.getenv('N8N_WORKFLOW_BACKUP_RETENTION_DAYS', '30')),
            'community_packages_enabled': os.getenv('N8N_COMMUNITY_PACKAGES_ENABLED', 'true').lower() == 'true',
            'community_packages_path': os.getenv('N8N_COMMUNITY_PACKAGES_PATH', 'data/n8n/packages'),
            'custom_nodes_enabled': os.getenv('N8N_CUSTOM_NODES_ENABLED', 'true').lower() == 'true',
            'custom_nodes_path': os.getenv('N8N_CUSTOM_NODES_PATH', 'data/n8n/custom_nodes'),
            'execution_mode': os.getenv('N8N_EXECUTION_MODE', 'regular'),
            'execution_save_data_enabled': os.getenv('N8N_EXECUTION_SAVE_DATA_ENABLED', 'true').lower() == 'true',
            'execution_save_data_success': int(os.getenv('N8N_EXECUTION_SAVE_DATA_SUCCESS', '1')),
            'execution_save_data_error': int(os.getenv('N8N_EXECUTION_SAVE_DATA_ERROR', '1')),
            'execution_save_execution_progress': os.getenv('N8N_EXECUTION_SAVE_EXECUTION_PROGRESS', 'false').lower() == 'true',
            'execution_report_item_records_limit': int(os.getenv('N8N_EXECUTION_REPORT_ITEM_RECORDS_LIMIT', '10000')),
            'queue_mode': os.getenv('N8N_QUEUE_MODE', 'internal'),
            'queue_bull_redis_host': os.getenv('N8N_QUEUE_BULL_REDIS_HOST', 'localhost'),
            'queue_bull_redis_port': int(os.getenv('N8N_QUEUE_BULL_REDIS_PORT', '6379')),
            'queue_bull_redis_db': int(os.getenv('N8N_QUEUE_BULL_REDIS_DB', '1')),
            'queue_bull_redis_password': os.getenv('N8N_QUEUE_BULL_REDIS_PASSWORD', ''),
            'queue_bull_redis_username': os.getenv('N8N_QUEUE_BULL_REDIS_USERNAME', ''),
            'binary_data_mode': os.getenv('N8N_BINARY_DATA_MODE', 'filesystem'),
            'binary_data_path': os.getenv('N8N_BINARY_DATA_PATH', 'data/n8n/binary-data'),
            'binary_data_max_size': int(os.getenv('N8N_BINARY_DATA_MAX_SIZE', '16')),
            'binary_data_ttl': int(os.getenv('N8N_BINARY_DATA_TTL', '1')),
            'external_hooks_enabled': os.getenv('N8N_EXTERNAL_HOOKS_ENABLED', 'false').lower() == 'true',
            'external_hooks_url': os.getenv('N8N_EXTERNAL_HOOKS_URL', ''),
            'external_hooks_method': os.getenv('N8N_EXTERNAL_HOOKS_METHOD', 'POST'),
            'external_hooks_blocking': os.getenv('N8N_EXTERNAL_HOOKS_BLOCKING', 'false').lower() == 'true',
        }

    def _create_session(self) -> requests.Session:
        """Create requests session with retry strategy"""
        session = requests.Session()

        # Configure retry strategy
        retry_strategy = Retry(
            total=self.config['retry_attempts'],
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "POST", "PUT", "DELETE", "OPTIONS", "TRACE"],
            backoff_factor=1
        )

        # Configure HTTP adapter
        adapter = HTTPAdapter(
            max_retries=retry_strategy,
            pool_connections=self.config['max_connections'],
            pool_maxsize=self.config['max_connections']
        )

        session.mount("http://", adapter)
        session.mount("https://", adapter)

        # Set default headers
        if self.config['api_key']:
            session.headers.update({
                'X-N8N-API-KEY': self.config['api_key'],
                'Authorization': f'Bearer {self.config["api_key"]}',
                'Content-Type': 'application/json'
            })

        return session

    def _setup_logging(self):
        """Setup logging for N8N integration"""
        if GLOBAL_LOGGER_AVAILABLE:
            self.logger = lambda msg, severity=ErrorSeverity.INFO, category=ErrorCategory.EXTERNAL_SERVICE: \
                global_logger.log_error(msg, severity, category, context=ErrorContext(component="n8n"))
        else:
            self.logger = lambda msg, **kwargs: logger.info(f"[N8N] {msg}")

    def _start_execution_processor(self):
        """Start the execution processor thread"""
        self.is_running = True
        processor_thread = threading.Thread(target=self._process_execution_queue, daemon=True)
        processor_thread.start()

    def _process_execution_queue(self):
        """Process workflow executions from queue"""
        while self.is_running:
            try:
                execution_data = self.execution_queue.get(timeout=1)
                self._execute_workflow(execution_data)
            except queue.Empty:
                continue
            except Exception as e:
                self.logger(f"Error processing execution queue: {e}", ErrorSeverity.ERROR)

    def create_workflow(self, workflow_data: Dict[str, Any]) -> str:
        """Create a new N8N workflow"""
        try:
            workflow_id = str(uuid.uuid4())

            workflow = N8NWorkflow(
                id=workflow_id,
                name=workflow_data.get('name', 'Untitled Workflow'),
                description=workflow_data.get('description', ''),
                nodes=workflow_data.get('nodes', []),
                connections=workflow_data.get('connections', {}),
                settings=workflow_data.get('settings', {}),
                created_at=datetime.now(),
                updated_at=datetime.now(),
                is_active=workflow_data.get('is_active', True),
                tags=workflow_data.get('tags', []),
                metadata=workflow_data.get('metadata', {})
            )

            self.workflows[workflow_id] = workflow

            # Save workflow to storage if configured
            if self.config.get('workflow_storage_path'):
                self._save_workflow_to_file(workflow)

            self.logger(f"Workflow '{workflow.name}' created with ID: {workflow_id}")
            return workflow_id

        except Exception as e:
            self.logger(f"Error creating workflow: {e}", ErrorSeverity.ERROR)
            raise

    def execute_workflow(self, workflow_id: str, input_data: Dict[str, Any] = None,
                        webhook_url: str = None) -> str:
        """Execute a workflow"""
        try:
            if workflow_id not in self.workflows:
                raise ValueError(f"Workflow {workflow_id} not found")

            execution_id = str(uuid.uuid4())

            execution = N8NExecution(
                id=execution_id,
                workflow_id=workflow_id,
                execution_id=f"exec_{execution_id}",
                status='waiting',
                started_at=datetime.now(),
                input_data=input_data or {},
                webhook_url=webhook_url
            )

            self.executions[execution_id] = execution

            # Queue execution
            execution_data = {
                'execution_id': execution_id,
                'workflow_id': workflow_id,
                'input_data': input_data,
                'webhook_url': webhook_url
            }

            self.execution_queue.put(execution_data)

            self.logger(f"Workflow execution queued: {execution_id}")
            return execution_id

        except Exception as e:
            self.logger(f"Error executing workflow: {e}", ErrorSeverity.ERROR)
            raise

    def _execute_workflow(self, execution_data: Dict[str, Any]):
        """Execute workflow via N8N API or local execution"""
        execution_id = execution_data['execution_id']
        workflow_id = execution_data['workflow_id']
        input_data = execution_data.get('input_data', {})
        webhook_url = execution_data.get('webhook_url')

        try:
            execution = self.executions.get(execution_id)
            if not execution:
                return

            execution.status = 'running'

            # If N8N API is configured, use it
            if self.config.get('api_url'):
                result = self._execute_via_api(workflow_id, input_data, webhook_url)
            else:
                # Otherwise, simulate execution (for development)
                result = self._simulate_execution(workflow_id, input_data)

            execution.status = result.get('status', 'success')
            execution.output_data = result.get('output_data', {})
            execution.finished_at = datetime.now()
            execution.duration = (execution.finished_at - execution.started_at).total_seconds()

            if execution.status == 'error':
                execution.error_message = result.get('error_message', 'Unknown error')

            self.logger(f"Workflow execution completed: {execution_id} - Status: {execution.status}")

        except Exception as e:
            execution = self.executions.get(execution_id)
            if execution:
                execution.status = 'error'
                execution.error_message = str(e)
                execution.finished_at = datetime.now()
                execution.duration = (execution.finished_at - execution.started_at).total_seconds()

            self.logger(f"Workflow execution failed: {execution_id} - Error: {e}", ErrorSeverity.ERROR)

    def _execute_via_api(self, workflow_id: str, input_data: Dict[str, Any],
                        webhook_url: str = None) -> Dict[str, Any]:
        """Execute workflow via N8N API"""
        try:
            workflow = self.workflows.get(workflow_id)
            if not workflow:
                raise ValueError(f"Workflow {workflow_id} not found")

            # Prepare API request
            api_url = f"{self.config['api_url']}/webhook/{workflow_id}"

            headers = {
                'Content-Type': 'application/json',
                'User-Agent': 'ValidoAI-N8N-Integration/1.0'
            }

            # Add authentication if configured
            if self.config.get('api_key'):
                headers['X-N8N-API-KEY'] = self.config['api_key']

            payload = {
                'workflow_id': workflow_id,
                'input_data': input_data,
                'webhook_url': webhook_url,
                'timestamp': datetime.now().isoformat(),
                'source': 'validoai'
            }

            # Make API request
            response = self.session.post(
                api_url,
                json=payload,
                headers=headers,
                timeout=self.config['workflow_timeout']
            )

            if response.status_code == 200:
                return {
                    'status': 'success',
                    'output_data': response.json(),
                    'execution_time': response.elapsed.total_seconds()
                }
            else:
                return {
                    'status': 'error',
                    'error_message': f"API request failed with status {response.status_code}: {response.text}"
                }

        except Exception as e:
            return {
                'status': 'error',
                'error_message': str(e)
            }

    def _simulate_execution(self, workflow_id: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate workflow execution for development/testing"""
        try:
            # Simulate processing time
            import time
            time.sleep(2)

            return {
                'status': 'success',
                'output_data': {
                    'workflow_id': workflow_id,
                    'input_processed': input_data,
                    'result': 'Workflow executed successfully (simulated)',
                    'timestamp': datetime.now().isoformat()
                },
                'execution_time': 2.0
            }

        except Exception as e:
            return {
                'status': 'error',
                'error_message': f"Simulation error: {e}"
            }

    def get_workflow_status(self, execution_id: str) -> Optional[N8NExecution]:
        """Get workflow execution status"""
        return self.executions.get(execution_id)

    def list_workflows(self) -> List[N8NWorkflow]:
        """List all workflows"""
        return list(self.workflows.values())

    def list_executions(self, workflow_id: str = None) -> List[N8NExecution]:
        """List workflow executions"""
        if workflow_id:
            return [exec for exec in self.executions.values() if exec.workflow_id == workflow_id]
        return list(self.executions.values())

    def delete_workflow(self, workflow_id: str) -> bool:
        """Delete a workflow"""
        if workflow_id in self.workflows:
            del self.workflows[workflow_id]
            self.logger(f"Workflow {workflow_id} deleted")
            return True
        return False

    def update_workflow(self, workflow_id: str, updates: Dict[str, Any]) -> bool:
        """Update workflow configuration"""
        if workflow_id not in self.workflows:
            return False

        workflow = self.workflows[workflow_id]
        for key, value in updates.items():
            if hasattr(workflow, key):
                setattr(workflow, key, value)

        workflow.updated_at = datetime.now()
        self.logger(f"Workflow {workflow_id} updated")
        return True

    def register_webhook_handler(self, workflow_id: str, handler: Callable):
        """Register webhook handler for workflow results"""
        self.webhook_handlers[workflow_id] = handler
        self.logger(f"Webhook handler registered for workflow {workflow_id}")

    def handle_webhook(self, workflow_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming webhook from N8N"""
        try:
            # Find execution by workflow_id
            execution = None
            for exec_obj in self.executions.values():
                if exec_obj.workflow_id == workflow_id and exec_obj.status == 'running':
                    execution = exec_obj
                    break

            if execution:
                execution.status = data.get('status', 'completed')
                execution.output_data = data.get('output_data', {})
                execution.finished_at = datetime.now()
                if execution.started_at:
                    execution.duration = (execution.finished_at - execution.started_at).total_seconds()

            # Call registered handler if available
            if workflow_id in self.webhook_handlers:
                return self.webhook_handlers[workflow_id](data)
            else:
                return {'status': 'received', 'message': 'No handler registered'}

        except Exception as e:
            self.logger(f"Error handling webhook for workflow {workflow_id}: {e}", ErrorSeverity.ERROR)
            return {'status': 'error', 'message': str(e)}

    def create_validoai_workflow_templates(self) -> Dict[str, N8NWorkflow]:
        """Create pre-built workflow templates for ValidoAI integration"""
        templates = {}

        # Template 1: Data Processing Workflow
        data_processing_workflow = {
            'name': 'ValidoAI Data Processing',
            'description': 'Process and analyze financial data from various sources',
            'nodes': [
                {
                    'id': '1',
                    'name': 'HTTP Request',
                    'type': 'n8n-nodes-base.httpRequest',
                    'parameters': {
                        'url': 'https://api.validoai.com/data',
                        'method': 'GET',
                        'sendHeaders': True,
                        'headerParameters': {
                            'Authorization': '={{$credentials.apiKey}}',
                            'Content-Type': 'application/json'
                        }
                    }
                },
                {
                    'id': '2',
                    'name': 'Data Transformation',
                    'type': 'n8n-nodes-base.function',
                    'parameters': {
                        'functionCode': '''
                        const data = $json;
                        return {
                            processed_data: data.map(item => ({
                                id: item.id,
                                value: parseFloat(item.value),
                                category: item.category,
                                processed_at: new Date().toISOString()
                            }))
                        };
                        '''
                    }
                }
            ],
            'connections': {
                '1': {'main': [[{'node': '2', 'type': 'main', 'index': 0}]]}
            },
            'settings': {
                'saveExecutionProgress': False,
                'saveManualExecutions': True,
                'saveDataSuccessExecution': '1',
                'saveDataErrorExecution': '1'
            },
            'tags': ['validoai', 'data-processing', 'automation']
        }

        templates['data_processing'] = self.create_workflow(data_processing_workflow)

        # Template 2: AI Analysis Workflow
        ai_analysis_workflow = {
            'name': 'ValidoAI AI Analysis',
            'description': 'Perform AI-powered analysis on processed data',
            'nodes': [
                {
                    'id': '1',
                    'name': 'Schedule Trigger',
                    'type': 'n8n-nodes-base.scheduleTrigger',
                    'parameters': {
                        'rule': {
                            'interval': [{'type': 'hours', 'hours': 1}]
                        }
                    }
                },
                {
                    'id': '2',
                    'name': 'AI Analysis',
                    'type': 'n8n-nodes-base.httpRequest',
                    'parameters': {
                        'url': 'https://api.validoai.com/analyze',
                        'method': 'POST',
                        'sendBody': True,
                        'bodyContentType': 'application/json',
                        'bodyParameters': {
                            'data': '={{$json.processed_data}}',
                            'analysis_type': 'financial_trends'
                        }
                    }
                }
            ],
            'connections': {
                '1': {'main': [[{'node': '2', 'type': 'main', 'index': 0}]]}
            },
            'settings': {
                'timezone': 'Europe/Belgrade',
                'saveExecutionProgress': False,
                'saveManualExecutions': True
            },
            'tags': ['validoai', 'ai-analysis', 'scheduled']
        }

        templates['ai_analysis'] = self.create_workflow(ai_analysis_workflow)

        # Template 3: Report Generation Workflow
        report_workflow = {
            'name': 'ValidoAI Report Generation',
            'description': 'Generate automated financial reports',
            'nodes': [
                {
                    'id': '1',
                    'name': 'Report Trigger',
                    'type': 'n8n-nodes-base.webhook',
                    'parameters': {
                        'httpMethod': 'POST',
                        'path': 'generate-report',
                        'responseMode': 'response',
                        'responseBody': '{"status": "Report generation started"}'
                    }
                },
                {
                    'id': '2',
                    'name': 'Generate Report',
                    'type': 'n8n-nodes-base.httpRequest',
                    'parameters': {
                        'url': 'https://api.validoai.com/reports/generate',
                        'method': 'POST',
                        'sendBody': True,
                        'bodyParameters': {
                            'report_type': '={{$json.report_type}}',
                            'date_range': '={{$json.date_range}}'
                        }
                    }
                },
                {
                    'id': '3',
                    'name': 'Email Report',
                    'type': 'n8n-nodes-base.emailSend',
                    'parameters': {
                        'to': '={{$json.recipient_email}}',
                        'subject': 'ValidoAI Financial Report',
                        'body': 'Please find your financial report attached.',
                        'attachments': {
                            'report.pdf': '={{$json.report_data}}'
                        }
                    }
                }
            ],
            'connections': {
                '1': {'main': [[{'node': '2', 'type': 'main', 'index': 0}]]},
                '2': {'main': [[{'node': '3', 'type': 'main', 'index': 0}]]}
            },
            'settings': {
                'saveExecutionProgress': True,
                'saveManualExecutions': True
            },
            'tags': ['validoai', 'reporting', 'email']
        }

        templates['report_generation'] = self.create_workflow(report_workflow)

        self.logger(f"Created {len(templates)} workflow templates")
        return templates

    def get_workflow_templates(self) -> Dict[str, Dict[str, Any]]:
        """Get available workflow templates"""
        return {
            'data_processing': {
                'name': 'Data Processing',
                'description': 'Process and transform financial data',
                'category': 'data'
            },
            'ai_analysis': {
                'name': 'AI Analysis',
                'description': 'AI-powered data analysis and insights',
                'category': 'ai'
            },
            'report_generation': {
                'name': 'Report Generation',
                'description': 'Automated financial report generation',
                'category': 'reporting'
            }
        }

    def export_workflow(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Export workflow configuration"""
        workflow = self.workflows.get(workflow_id)
        if not workflow:
            return None

        return {
            'id': workflow.id,
            'name': workflow.name,
            'description': workflow.description,
            'nodes': workflow.nodes,
            'connections': workflow.connections,
            'settings': workflow.settings,
            'tags': workflow.tags,
            'metadata': workflow.metadata,
            'exported_at': datetime.now().isoformat()
        }

    def import_workflow(self, workflow_data: Dict[str, Any]) -> str:
        """Import workflow configuration"""
        return self.create_workflow(workflow_data)

    def get_statistics(self) -> Dict[str, Any]:
        """Get N8N integration statistics"""
        total_workflows = len(self.workflows)
        active_workflows = len([w for w in self.workflows.values() if w.is_active])
        total_executions = len(self.executions)
        successful_executions = len([e for e in self.executions.values() if e.status == 'success'])
        failed_executions = len([e for e in self.executions.values() if e.status == 'error'])

        return {
            'workflows': {
                'total': total_workflows,
                'active': active_workflows,
                'inactive': total_workflows - active_workflows
            },
            'executions': {
                'total': total_executions,
                'successful': successful_executions,
                'failed': failed_executions,
                'running': len([e for e in self.executions.values() if e.status == 'running'])
            },
            'webhook_handlers': len(self.webhook_handlers),
            'queue_size': self.execution_queue.qsize(),
            'is_running': self.is_running
        }

    def health_check(self) -> Dict[str, Any]:
        """Perform health check on N8N integration"""
        try:
            if self.config.get('api_url'):
                response = self.session.get(f"{self.config['api_url']}/health",
                                          timeout=10)
                api_status = response.status_code == 200
            else:
                api_status = False

            return {
                'status': 'healthy' if api_status else 'degraded',
                'api_connection': api_status,
                'workflows_loaded': len(self.workflows),
                'executions_queued': self.execution_queue.qsize(),
                'webhook_handlers': len(self.webhook_handlers),
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

    def cleanup_old_executions(self, days: int = 30):
        """Clean up old execution records"""
        cutoff_date = datetime.now() - timedelta(days=days)
        old_executions = []

        for exec_id, execution in self.executions.items():
            if execution.finished_at and execution.finished_at < cutoff_date:
                old_executions.append(exec_id)

        for exec_id in old_executions:
            del self.executions[exec_id]

        if old_executions:
            self.logger(f"Cleaned up {len(old_executions)} old executions")

    def _save_workflow_to_file(self, workflow: N8NWorkflow):
        """Save workflow to file system"""
        try:
            storage_path = Path(self.config.get('workflow_storage_path', 'data/n8n/workflows'))
            storage_path.mkdir(parents=True, exist_ok=True)

            workflow_file = storage_path / f"{workflow.id}.json"

            with open(workflow_file, 'w', encoding='utf-8') as f:
                json.dump(asdict(workflow), f, indent=2, default=str)

        except Exception as e:
            self.logger(f"Error saving workflow to file: {e}", ErrorSeverity.WARNING)

# Global N8N integration instance
n8n_integration = N8NIntegration()

# Convenience functions
def get_n8n_integration():
    """Get the global N8N integration instance"""
    return n8n_integration

def create_n8n_workflow(workflow_data: Dict[str, Any]) -> str:
    """Create a new N8N workflow"""
    return n8n_integration.create_workflow(workflow_data)

def execute_n8n_workflow(workflow_id: str, input_data: Dict[str, Any] = None) -> str:
    """Execute an N8N workflow"""
    return n8n_integration.execute_workflow(workflow_id, input_data)

def get_n8n_workflow_status(execution_id: str) -> Optional[N8NExecution]:
    """Get workflow execution status"""
    return n8n_integration.get_workflow_status(execution_id)

# Export key components
__all__ = [
    'N8NIntegration',
    'N8NWorkflow',
    'N8NExecution',
    'n8n_integration',
    'get_n8n_integration',
    'create_n8n_workflow',
    'execute_n8n_workflow',
    'get_n8n_workflow_status'
]
