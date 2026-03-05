"""
Performance Controller - System Monitoring and Optimization
Handles performance monitoring, system information, and optimization
"""

import os
import psutil
import platform
import logging
from datetime import datetime
from typing import Dict, Any, List
from flask import render_template, jsonify, request

logger = logging.getLogger(__name__)

class PerformanceController:
    """Performance monitoring and system optimization controller"""
    
    def __init__(self):
        self.monitoring_active = False
        self.monitoring_data = []
    
    def show(self):
        """Show performance monitoring dashboard"""
        try:
            system_info = self.get_system_info()
            return render_template('performance/index.html',
                                 system_info=system_info,
                                 monitoring_active=self.monitoring_active)
        except Exception as e:
            logger.error(f"Error showing performance dashboard: {e}")
            return render_template('errors/error.html',
                                 error_code=500,
                                 error_title="Performance Dashboard Error",
                                 error_message="Failed to load performance dashboard.",
                                 stack_trace=str(e),
                                 timestamp=datetime.now().isoformat(),
                                 error_uuid=f"e500_{os.urandom(4).hex()}",
                                 request_id=os.urandom(8).hex()), 500
    
    def start_monitoring(self):
        """Start performance monitoring"""
        try:
            if not self.monitoring_active:
                self.monitoring_active = True
                self.monitoring_data = []
                logger.info("Performance monitoring started")
                return jsonify({
                    'status': 'success',
                    'message': 'Performance monitoring started',
                    'timestamp': datetime.now().isoformat()
                })
            else:
                return jsonify({
                    'status': 'info',
                    'message': 'Performance monitoring already active',
                    'timestamp': datetime.now().isoformat()
                })
        except Exception as e:
            logger.error(f"Error starting performance monitoring: {e}")
            return jsonify({'error': str(e)}), 500
    
    def stop_monitoring(self):
        """Stop performance monitoring"""
        try:
            if self.monitoring_active:
                self.monitoring_active = False
                logger.info("Performance monitoring stopped")
                return jsonify({
                    'status': 'success',
                    'message': 'Performance monitoring stopped',
                    'timestamp': datetime.now().isoformat()
                })
            else:
                return jsonify({
                    'status': 'info',
                    'message': 'Performance monitoring not active',
                    'timestamp': datetime.now().isoformat()
                })
        except Exception as e:
            logger.error(f"Error stopping performance monitoring: {e}")
            return jsonify({'error': str(e)}), 500
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get comprehensive system information"""
        try:
            # CPU information
            cpu_info = {
                'count': psutil.cpu_count(),
                'count_logical': psutil.cpu_count(logical=True),
                'usage_percent': psutil.cpu_percent(interval=1),
                'frequency': psutil.cpu_freq()._asdict() if psutil.cpu_freq() else {}
            }
            
            # Memory information
            memory = psutil.virtual_memory()
            memory_info = {
                'total': memory.total,
                'available': memory.available,
                'used': memory.used,
                'free': memory.free,
                'percent': memory.percent
            }
            
            # Disk information
            disk = psutil.disk_usage('/')
            disk_info = {
                'total': disk.total,
                'used': disk.used,
                'free': disk.free,
                'percent': (disk.used / disk.total) * 100
            }
            
            # Network information
            network = psutil.net_io_counters()
            network_info = {
                'bytes_sent': network.bytes_sent,
                'bytes_recv': network.bytes_recv,
                'packets_sent': network.packets_sent,
                'packets_recv': network.packets_recv
            }
            
            # System information
            system_info = {
                'platform': platform.platform(),
                'system': platform.system(),
                'release': platform.release(),
                'version': platform.version(),
                'machine': platform.machine(),
                'processor': platform.processor(),
                'python_version': platform.python_version()
            }
            
            return {
                'cpu': cpu_info,
                'memory': memory_info,
                'disk': disk_info,
                'network': network_info,
                'system': system_info,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting system info: {e}")
            return {
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def get_process_list(self) -> List[Dict[str, Any]]:
        """Get list of running processes"""
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status']):
                try:
                    proc_info = proc.info
                    processes.append({
                        'pid': proc_info['pid'],
                        'name': proc_info['name'],
                        'cpu_percent': proc_info['cpu_percent'],
                        'memory_percent': proc_info['memory_percent'],
                        'status': proc_info['status']
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
            
            # Sort by CPU usage
            processes.sort(key=lambda x: x['cpu_percent'] or 0, reverse=True)
            return processes[:50]  # Return top 50 processes
            
        except Exception as e:
            logger.error(f"Error getting process list: {e}")
            return []
    
    def optimize_performance(self) -> Dict[str, Any]:
        """Perform basic performance optimization"""
        try:
            optimizations = []
            
            # Check memory usage
            memory = psutil.virtual_memory()
            if memory.percent > 80:
                optimizations.append({
                    'type': 'memory',
                    'message': 'High memory usage detected',
                    'recommendation': 'Consider closing unnecessary applications or increasing RAM'
                })
            
            # Check disk usage
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            if disk_percent > 90:
                optimizations.append({
                    'type': 'disk',
                    'message': 'High disk usage detected',
                    'recommendation': 'Consider cleaning up unnecessary files or increasing disk space'
                })
            
            # Check CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            if cpu_percent > 80:
                optimizations.append({
                    'type': 'cpu',
                    'message': 'High CPU usage detected',
                    'recommendation': 'Consider closing CPU-intensive applications'
                })
            
            if not optimizations:
                optimizations.append({
                    'type': 'status',
                    'message': 'System performance is good',
                    'recommendation': 'No immediate optimizations needed'
                })
            
            return {
                'status': 'success',
                'optimizations': optimizations,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error optimizing performance: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Get comprehensive performance report"""
        try:
            system_info = self.get_system_info()
            process_list = self.get_process_list()
            optimizations = self.optimize_performance()
            
            # Calculate performance score (0-100)
            score = 100
            
            # Deduct points for high resource usage
            if system_info.get('memory', {}).get('percent', 0) > 80:
                score -= 20
            if system_info.get('disk', {}).get('percent', 0) > 90:
                score -= 20
            if system_info.get('cpu', {}).get('usage_percent', 0) > 80:
                score -= 20
            
            score = max(0, score)
            
            return {
                'status': 'success',
                'performance_score': score,
                'system_info': system_info,
                'top_processes': process_list[:10],
                'optimizations': optimizations.get('optimizations', []),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating performance report: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    @staticmethod
    def get_system_info_static() -> Dict[str, Any]:
        """Static method to get system information"""
        controller = PerformanceController()
        return controller.get_system_info()
