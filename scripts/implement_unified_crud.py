#!/usr/bin/env python3
"""
Implement Unified CRUD System
Script to implement the unified CRUD system with parallel batch processing
"""

import sys
import os
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.core.batch_processor import batch_processor
from src.config.table_configurations import get_batch_configs, get_all_table_configs
from src.crud.unified_crud_config import crud_config_registry
from src.crud.unified_crud_operations import unified_crud_registry
from src.routes.unified_route_generator import unified_route_generator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def implement_unified_crud():
    """Implement the unified CRUD system"""
    
    logger.info("Starting Unified CRUD System Implementation")
    
    try:
        # Step 1: Get all table configurations
        logger.info("Step 1: Loading table configurations")
        all_configs = get_all_table_configs()
        batch_configs = get_batch_configs()
        
        logger.info(f"Loaded {len(all_configs)} table configurations")
        
        # Step 2: Register configurations
        logger.info("Step 2: Registering CRUD configurations")
        for table_name, config in all_configs.items():
            crud_config_registry.register(config)
            logger.info(f"Registered configuration for {table_name}")
        
        # Step 3: Create CRUD tasks for parallel processing
        logger.info("Step 3: Creating batch tasks for parallel processing")
        
        # Process each batch
        for batch_name, batch_tables in batch_configs.items():
            logger.info(f"Processing {batch_name} with {len(batch_tables)} tables")
            
            # Convert table names to config objects
            batch_configs_dict = {}
            for table_name in batch_tables.keys():
                if table_name in all_configs:
                    batch_configs_dict[table_name] = all_configs[table_name]
            
            # Create tasks for this batch
            task_ids = batch_processor.create_crud_tasks(batch_configs_dict)
            logger.info(f"Created {len(task_ids)} tasks for {batch_name}")
        
        # Step 4: Execute all batches in parallel
        logger.info("Step 4: Executing all batches in parallel")
        results = batch_processor.execute_all_batches()
        
        # Step 5: Process results
        logger.info("Step 5: Processing results")
        
        total_success = 0
        total_failed = 0
        
        for batch_name, batch_results in results.items():
            batch_success = sum(1 for result in batch_results if result.success)
            batch_failed = len(batch_results) - batch_success
            
            total_success += batch_success
            total_failed += batch_failed
            
            logger.info(f"{batch_name}: {batch_success} successful, {batch_failed} failed")
        
        # Step 6: Generate routes for successful configurations
        logger.info("Step 6: Generating routes for successful configurations")
        
        successful_tables = []
        for table_name, config in all_configs.items():
            if crud_config_registry.exists(table_name):
                successful_tables.append(table_name)
        
        logger.info(f"Generating routes for {len(successful_tables)} successful tables")
        
        for table_name in successful_tables:
            config = crud_config_registry.get(table_name)
            if config:
                try:
                    blueprint = unified_route_generator.generate_routes(table_name, config)
                    logger.info(f"Generated routes for {table_name}")
                except Exception as e:
                    logger.error(f"Failed to generate routes for {table_name}: {e}")
        
        # Step 7: Final summary
        logger.info("Step 7: Implementation Summary")
        
        progress = batch_processor.get_progress()
        
        summary = {
            "total_tables": len(all_configs),
            "successful_tables": total_success,
            "failed_tables": total_failed,
            "success_rate": progress.get('success_rate', 0),
            "total_time": progress.get('total_time', 0),
            "batches_processed": len(results)
        }
        
        logger.info("=== IMPLEMENTATION SUMMARY ===")
        logger.info(f"Total Tables: {summary['total_tables']}")
        logger.info(f"Successful: {summary['successful_tables']}")
        logger.info(f"Failed: {summary['failed_tables']}")
        logger.info(f"Success Rate: {summary['success_rate']:.1f}%")
        logger.info(f"Total Time: {summary['total_time']:.2f} seconds")
        logger.info(f"Batches Processed: {summary['batches_processed']}")
        
        # Step 8: Save results
        logger.info("Step 8: Saving implementation results")
        
        import json
        from datetime import datetime
        
        results_data = {
            "implementation_date": datetime.now().isoformat(),
            "summary": summary,
            "successful_tables": successful_tables,
            "failed_tasks": batch_processor.get_failed_tasks(),
            "progress": progress
        }
        
        results_file = project_root / "logs" / "unified_crud_implementation.json"
        results_file.parent.mkdir(exist_ok=True)
        
        with open(results_file, 'w') as f:
            json.dump(results_data, f, indent=2, default=str)
        
        logger.info(f"Results saved to {results_file}")
        
        # Step 9: Cleanup
        logger.info("Step 9: Cleaning up")
        batch_processor.clear_completed()
        
        logger.info("Unified CRUD System Implementation Completed Successfully!")
        
        return summary
        
    except Exception as e:
        logger.error(f"Implementation failed: {e}")
        raise


def check_implementation_status():
    """Check the status of the implementation"""
    
    logger.info("Checking Implementation Status")
    
    try:
        # Check configurations
        all_configs = get_all_table_configs()
        registered_configs = crud_config_registry.get_all()
        
        # Check CRUD instances
        crud_instances = unified_crud_registry.get_all_crud()
        
        # Check routes
        route_blueprints = unified_route_generator.blueprints
        
        status = {
            "configurations": {
                "total": len(all_configs),
                "registered": len(registered_configs),
                "missing": len(all_configs) - len(registered_configs)
            },
            "crud_instances": {
                "total": len(crud_instances),
                "tables": list(crud_instances.keys())
            },
            "routes": {
                "total": len(route_blueprints),
                "tables": list(route_blueprints.keys())
            }
        }
        
        logger.info("=== IMPLEMENTATION STATUS ===")
        logger.info(f"Configurations: {status['configurations']['registered']}/{status['configurations']['total']}")
        logger.info(f"CRUD Instances: {status['crud_instances']['total']}")
        logger.info(f"Routes Generated: {status['routes']['total']}")
        
        return status
        
    except Exception as e:
        logger.error(f"Status check failed: {e}")
        return None


def main():
    """Main function"""
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "implement":
            implement_unified_crud()
        elif command == "status":
            check_implementation_status()
        elif command == "test":
            # Test individual components
            logger.info("Testing individual components")
            
            # Test configuration
            configs = get_all_table_configs()
            logger.info(f"Loaded {len(configs)} configurations")
            
            # Test batch processor
            progress = batch_processor.get_progress()
            logger.info(f"Batch processor status: {progress}")
            
        else:
            logger.error(f"Unknown command: {command}")
            logger.info("Available commands: implement, status, test")
    else:
        # Default: implement
        implement_unified_crud()


if __name__ == "__main__":
    main()
