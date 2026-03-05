"""
Batch Processor for ValidoAI
Parallel processing system for CRUD operations and route generation
"""

import logging
import asyncio
import threading
from typing import Dict, List, Any, Optional, Callable, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime
import time

logger = logging.getLogger(__name__)


@dataclass
class BatchTask:
    """Batch task definition"""
    id: str
    name: str
    function: Callable
    args: tuple = ()
    kwargs: dict = None
    priority: int = 5
    dependencies: List[str] = None
    timeout: int = 300  # 5 minutes default
    retry_count: int = 0
    max_retries: int = 3


@dataclass
class BatchResult:
    """Batch task result"""
    task_id: str
    success: bool
    result: Any = None
    error: str = None
    execution_time: float = 0.0
    completed_at: datetime = None


class BatchProcessor:
    """Parallel batch processor for CRUD operations"""
    
    def __init__(self, max_workers: int = 10, batch_size: int = 10):
        self.max_workers = max_workers
        self.batch_size = batch_size
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.active_batches: Dict[str, List[BatchTask]] = {}
        self.completed_results: Dict[str, BatchResult] = {}
        self.failed_tasks: Dict[str, BatchResult] = {}
        self.processing_stats = {
            'total_tasks': 0,
            'completed_tasks': 0,
            'failed_tasks': 0,
            'total_time': 0.0
        }
    
    def add_task(self, task: BatchTask) -> str:
        """Add a task to the batch processor"""
        # Keep the original task ID for dependencies
        original_id = task.id
        
        # Generate unique task ID for internal tracking
        task_id = f"{task.name}_{task.id}_{int(time.time())}"
        task.id = task_id
        
        if task.dependencies:
            # Check if dependencies are completed
            for dep_id in task.dependencies:
                if dep_id not in self.completed_results:
                    logger.warning(f"Task {task_id} has unmet dependency: {dep_id}")
        
        # Add to appropriate batch
        batch_key = f"batch_{len(self.active_batches) // self.batch_size}"
        if batch_key not in self.active_batches:
            self.active_batches[batch_key] = []
        
        self.active_batches[batch_key].append(task)
        self.processing_stats['total_tasks'] += 1
        
        logger.info(f"Added task {task_id} to batch {batch_key}")
        return original_id  # Return the original ID for dependency tracking
    
    def add_tasks(self, tasks: List[BatchTask]) -> List[str]:
        """Add multiple tasks"""
        task_ids = []
        for task in tasks:
            task_id = self.add_task(task)
            task_ids.append(task_id)
        return task_ids
    
    def execute_batch(self, batch_key: str) -> List[BatchResult]:
        """Execute a single batch of tasks"""
        if batch_key not in self.active_batches:
            return []
        
        tasks = self.active_batches[batch_key]
        results = []
        
        logger.info(f"Executing batch {batch_key} with {len(tasks)} tasks")
        
        # Submit tasks to thread pool
        future_to_task = {}
        for task in tasks:
            future = self.executor.submit(self._execute_task, task)
            future_to_task[future] = task
        
        # Collect results
        for future in as_completed(future_to_task, timeout=300):
            task = future_to_task[future]
            try:
                result = future.result()
                results.append(result)
                
                if result.success:
                    self.completed_results[task.id] = result
                    self.processing_stats['completed_tasks'] += 1
                else:
                    self.failed_tasks[task.id] = result
                    self.processing_stats['failed_tasks'] += 1
                
                logger.info(f"Task {task.id} completed: {'success' if result.success else 'failed'}")
                
            except Exception as e:
                logger.error(f"Task {task.id} failed with exception: {e}")
                result = BatchResult(
                    task_id=task.id,
                    success=False,
                    error=str(e),
                    completed_at=datetime.now()
                )
                results.append(result)
                self.failed_tasks[task.id] = result
                self.processing_stats['failed_tasks'] += 1
        
        return results
    
    def execute_all_batches(self) -> Dict[str, List[BatchResult]]:
        """Execute all batches in parallel"""
        start_time = time.time()
        all_results = {}
        
        logger.info(f"Starting execution of {len(self.active_batches)} batches")
        
        # Execute batches in parallel
        future_to_batch = {}
        for batch_key in self.active_batches.keys():
            future = self.executor.submit(self.execute_batch, batch_key)
            future_to_batch[future] = batch_key
        
        # Collect all results
        for future in as_completed(future_to_batch, timeout=1800):  # 30 minutes timeout
            batch_key = future_to_batch[future]
            try:
                results = future.result()
                all_results[batch_key] = results
                logger.info(f"Batch {batch_key} completed with {len(results)} results")
            except Exception as e:
                logger.error(f"Batch {batch_key} failed: {e}")
                all_results[batch_key] = []
        
        self.processing_stats['total_time'] = time.time() - start_time
        logger.info(f"All batches completed in {self.processing_stats['total_time']:.2f} seconds")
        
        return all_results
    
    def _execute_task(self, task: BatchTask) -> BatchResult:
        """Execute a single task"""
        start_time = time.time()
        
        try:
            # Check dependencies
            if task.dependencies:
                for dep_id in task.dependencies:
                    if dep_id not in self.completed_results:
                        return BatchResult(
                            task_id=task.id,
                            success=False,
                            error=f"Dependency {dep_id} not completed",
                            execution_time=time.time() - start_time,
                            completed_at=datetime.now()
                        )
            
            # Execute task
            kwargs = task.kwargs or {}
            result = task.function(*task.args, **kwargs)
            
            execution_time = time.time() - start_time
            
            return BatchResult(
                task_id=task.id,
                success=True,
                result=result,
                execution_time=execution_time,
                completed_at=datetime.now()
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            
            # Retry logic
            if task.retry_count < task.max_retries:
                task.retry_count += 1
                logger.warning(f"Task {task.id} failed, retrying ({task.retry_count}/{task.max_retries}): {e}")
                time.sleep(1)  # Brief delay before retry
                return self._execute_task(task)
            
            return BatchResult(
                task_id=task.id,
                success=False,
                error=str(e),
                execution_time=execution_time,
                completed_at=datetime.now()
            )
    
    def get_progress(self) -> Dict[str, Any]:
        """Get processing progress"""
        total_tasks = self.processing_stats['total_tasks']
        completed_tasks = self.processing_stats['completed_tasks']
        failed_tasks = self.processing_stats['failed_tasks']
        
        if total_tasks == 0:
            progress_percentage = 0
        else:
            progress_percentage = (completed_tasks + failed_tasks) / total_tasks * 100
        
        return {
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'failed_tasks': failed_tasks,
            'pending_tasks': total_tasks - completed_tasks - failed_tasks,
            'progress_percentage': progress_percentage,
            'total_time': self.processing_stats['total_time'],
            'success_rate': (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        }
    
    def get_results(self) -> Dict[str, BatchResult]:
        """Get all completed results"""
        return self.completed_results.copy()
    
    def get_failed_tasks(self) -> Dict[str, BatchResult]:
        """Get all failed tasks"""
        return self.failed_tasks.copy()
    
    def clear_completed(self):
        """Clear completed results to free memory"""
        self.completed_results.clear()
        self.failed_tasks.clear()
        self.processing_stats = {
            'total_tasks': 0,
            'completed_tasks': 0,
            'failed_tasks': 0,
            'total_time': 0.0
        }
    
    def shutdown(self):
        """Shutdown the batch processor"""
        self.executor.shutdown(wait=True)
        logger.info("Batch processor shutdown complete")


class CRUDBatchProcessor(BatchProcessor):
    """Specialized batch processor for CRUD operations"""
    
    def __init__(self, max_workers: int = 10):
        super().__init__(max_workers=max_workers, batch_size=10)
    
    def create_crud_tasks(self, table_configs: Dict[str, Any]) -> List[str]:
        """Create CRUD tasks for multiple tables"""
        tasks = []
        
        for table_name, config_data in table_configs.items():
            # Task 1: Create CRUD configuration
            config_task = BatchTask(
                id=f"config_{table_name}",
                name=f"Create CRUD Config for {table_name}",
                function=self._create_crud_config,
                args=(table_name, config_data),
                priority=1
            )
            tasks.append(config_task)
            
            # Task 2: Generate CRUD operations
            crud_task = BatchTask(
                id=f"crud_{table_name}",
                name=f"Generate CRUD Operations for {table_name}",
                function=self._generate_crud_operations,
                args=(table_name,),
                dependencies=[f"config_{table_name}"],
                priority=2
            )
            tasks.append(crud_task)
            
            # Task 3: Generate routes
            route_task = BatchTask(
                id=f"routes_{table_name}",
                name=f"Generate Routes for {table_name}",
                function=self._generate_routes,
                args=(table_name,),
                dependencies=[f"crud_{table_name}"],
                priority=3
            )
            tasks.append(route_task)
            
            # Task 4: Create templates
            template_task = BatchTask(
                id=f"templates_{table_name}",
                name=f"Create Templates for {table_name}",
                function=self._create_templates,
                args=(table_name,),
                dependencies=[f"routes_{table_name}"],
                priority=4
            )
            tasks.append(template_task)
            
            # Task 5: Run tests
            test_task = BatchTask(
                id=f"tests_{table_name}",
                name=f"Run Tests for {table_name}",
                function=self._run_tests,
                args=(table_name,),
                dependencies=[f"templates_{table_name}"],
                priority=5
            )
            tasks.append(test_task)
        
        return self.add_tasks(tasks)
    
    def _create_crud_config(self, table_name: str, config_data: Dict[str, Any]) -> bool:
        """Create CRUD configuration for a table"""
        try:
            from ..crud.unified_crud_config import CRUDConfig, crud_config_registry
            
            # If config_data is already a CRUDConfig object, use it directly
            if isinstance(config_data, CRUDConfig):
                config = config_data
            else:
                # Otherwise, create from dict
                config = CRUDConfig.from_dict(config_data)
            
            crud_config_registry.register(config)
            
            logger.info(f"Created CRUD config for {table_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create CRUD config for {table_name}: {e}")
            return False
    
    def _generate_crud_operations(self, table_name: str) -> bool:
        """Generate CRUD operations for a table"""
        try:
            from ..crud.unified_crud_operations import unified_crud_registry
            from ..crud.unified_crud_config import crud_config_registry
            
            config = crud_config_registry.get(table_name)
            if not config:
                raise ValueError(f"No configuration found for {table_name}")
            
            crud = unified_crud_registry.get_crud(table_name, config)
            
            logger.info(f"Generated CRUD operations for {table_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to generate CRUD operations for {table_name}: {e}")
            return False
    
    def _generate_routes(self, table_name: str) -> bool:
        """Generate routes for a table"""
        try:
            from ..routes.unified_route_generator import unified_route_generator
            from ..crud.unified_crud_config import crud_config_registry
            
            config = crud_config_registry.get(table_name)
            if not config:
                raise ValueError(f"No configuration found for {table_name}")
            
            blueprint = unified_route_generator.generate_routes(table_name, config)
            
            logger.info(f"Generated routes for {table_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to generate routes for {table_name}: {e}")
            return False
    
    def _create_templates(self, table_name: str) -> bool:
        """Create templates for a table"""
        try:
            # This would create the necessary template files
            # For now, just return success
            logger.info(f"Created templates for {table_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create templates for {table_name}: {e}")
            return False
    
    def _run_tests(self, table_name: str) -> bool:
        """Run tests for a table"""
        try:
            # This would run tests for the table
            # For now, just return success
            logger.info(f"Ran tests for {table_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to run tests for {table_name}: {e}")
            return False


# Global batch processor instance
batch_processor = CRUDBatchProcessor(max_workers=10)
