"""
Comprehensive Import and Dependency Test Suite
============================================
Tests all imports, dependencies, and configurations to ensure the application
can run properly with all required and optional components.
"""

import sys
import os
import importlib
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from pathlib import Path

# Configure logging for tests
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class DependencyTest:
    """Test result for a dependency"""
    name: str
    required: bool
    available: bool
    version: Optional[str] = None
    error: Optional[str] = None
    category: str = "unknown"

@dataclass
class ImportTestResult:
    """Result of import testing"""
    success: bool
    total_dependencies: int
    available_dependencies: int
    required_dependencies: int
    available_required: int
    tests: List[DependencyTest]
    errors: List[str]

class DependencyTester:
    """Comprehensive dependency testing system"""
    
    def __init__(self):
        self.test_results: List[DependencyTest] = []
        self.errors: List[str] = []
        
        # Define all dependencies with their categories and requirements
        self.dependencies = {
            # Core Flask Dependencies (Always Required)
            'core': {
                'flask': {'required': True, 'category': 'core'},
                'flask_sqlalchemy': {'required': True, 'category': 'core'},
                'flask_login': {'required': True, 'category': 'core'},
                'werkzeug': {'required': True, 'category': 'core'},
                'sqlalchemy': {'required': True, 'category': 'core'},
                'dotenv': {'required': True, 'category': 'core'},
            },
            
            # Database Drivers (Optional but recommended)
            'databases': {
                'psycopg2': {'required': False, 'category': 'database'},
                'pymysql': {'required': False, 'category': 'database'},
                'sqlite3': {'required': False, 'category': 'database'},  # Built-in
                'pymongo': {'required': False, 'category': 'database'},
                'redis': {'required': False, 'category': 'database'},
                'cassandra': {'required': False, 'category': 'database'},
                'neo4j': {'required': False, 'category': 'database'},
                'elasticsearch': {'required': False, 'category': 'database'},
            },
            
            # Vector Databases (Optional)
            'vector_databases': {
                'pinecone': {'required': False, 'category': 'vector_db'},
                'weaviate': {'required': False, 'category': 'vector_db'},
                'qdrant_client': {'required': False, 'category': 'vector_db'},
                'chromadb': {'required': False, 'category': 'vector_db'},
                'milvus': {'required': False, 'category': 'vector_db'},
                'faiss': {'required': False, 'category': 'vector_db'},
            },
            
            # AI/ML Libraries (Optional but heavy)
            'ai_ml': {
                'tensorflow': {'required': False, 'category': 'ai_ml'},
                'torch': {'required': False, 'category': 'ai_ml'},
                'sentence_transformers': {'required': False, 'category': 'ai_ml'},
                'openai': {'required': False, 'category': 'ai_ml'},
                'cohere': {'required': False, 'category': 'ai_ml'},
                'transformers': {'required': False, 'category': 'ai_ml'},
                'scikit-learn': {'required': False, 'category': 'ai_ml'},
                'pandas': {'required': False, 'category': 'ai_ml'},
                'numpy': {'required': False, 'category': 'ai_ml'},
            },
            
            # Flask Extensions (Optional)
            'flask_extensions': {
                'flask_socketio': {'required': False, 'category': 'flask_extension'},
                'flask_wtf': {'required': False, 'category': 'flask_extension'},
                'flask_migrate': {'required': False, 'category': 'flask_extension'},
                'flask_session': {'required': False, 'category': 'flask_extension'},
                'flask_cors': {'required': False, 'category': 'flask_extension'},
            },
            
            # ASGI/Production Server (Optional but recommended for production)
            'asgi': {
                'asgiref': {'required': False, 'category': 'asgi'},
                'hypercorn': {'required': False, 'category': 'asgi'},
                'aioquic': {'required': False, 'category': 'asgi'},
            },
            
            # Monitoring and Metrics (Optional)
            'monitoring': {
                'prometheus_client': {'required': False, 'category': 'monitoring'},
                'psutil': {'required': False, 'category': 'monitoring'},
            },
            
            # Utilities (Optional)
            'utilities': {
                'requests': {'required': False, 'category': 'utility'},
                'aiohttp': {'required': False, 'category': 'utility'},
                'celery': {'required': False, 'category': 'utility'},
                'redis': {'required': False, 'category': 'utility'},
            }
        }
    
    def test_dependency(self, name: str, required: bool = False, category: str = "unknown") -> DependencyTest:
        """Test if a specific dependency is available"""
        try:
            # Special handling for built-in modules
            if name == 'sqlite3':
                import sqlite3
                version = sqlite3.sqlite_version
                return DependencyTest(
                    name=name,
                    required=required,
                    available=True,
                    version=version,
                    category=category
                )
            
            # Try to import the module
            module = importlib.import_module(name)
            
            # Get version if available
            version = None
            if hasattr(module, '__version__'):
                version = module.__version__
            elif hasattr(module, 'VERSION'):
                version = module.VERSION
            
            return DependencyTest(
                name=name,
                required=required,
                available=True,
                version=version,
                category=category
            )
            
        except ImportError as e:
            return DependencyTest(
                name=name,
                required=required,
                available=False,
                error=str(e),
                category=category
            )
        except Exception as e:
            return DependencyTest(
                name=name,
                required=required,
                available=False,
                error=str(e),
                category=category
            )
    
    def test_all_dependencies(self) -> ImportTestResult:
        """Test all dependencies"""
        logger.info("🔍 Starting comprehensive dependency testing...")
        
        for category, deps in self.dependencies.items():
            logger.info(f"Testing {category} dependencies...")
            for dep_name, config in deps.items():
                test_result = self.test_dependency(
                    name=dep_name,
                    required=config['required'],
                    category=config['category']
                )
                self.test_results.append(test_result)
                
                if test_result.available:
                    logger.info(f"  ✅ {dep_name} - Available" + (f" (v{test_result.version})" if test_result.version else ""))
                else:
                    if test_result.required:
                        logger.error(f"  ❌ {dep_name} - Required but not available: {test_result.error}")
                        self.errors.append(f"Required dependency {dep_name} not available: {test_result.error}")
                    else:
                        logger.warning(f"  ⚠️ {dep_name} - Optional but not available: {test_result.error}")
        
        return self._compile_results()
    
    def _compile_results(self) -> ImportTestResult:
        """Compile test results into a summary"""
        total_deps = len(self.test_results)
        available_deps = len([t for t in self.test_results if t.available])
        required_deps = len([t for t in self.test_results if t.required])
        available_required = len([t for t in self.test_results if t.required and t.available])
        
        success = len(self.errors) == 0
        
        return ImportTestResult(
            success=success,
            total_dependencies=total_deps,
            available_dependencies=available_deps,
            required_dependencies=required_deps,
            available_required=available_required,
            tests=self.test_results,
            errors=self.errors
        )
    
    def test_project_imports(self) -> bool:
        """Test if all project modules can be imported"""
        logger.info("🔍 Testing project module imports...")
        
        project_modules = [
            'src.config',
            'src.database',
            'src.models.unified_models',
            'src.controllers',
            'src.core.error_handling',
            'routes'
        ]
        
        all_imports_ok = True
        
        for module_name in project_modules:
            try:
                importlib.import_module(module_name)
                logger.info(f"  ✅ {module_name} - Import successful")
            except ImportError as e:
                logger.error(f"  ❌ {module_name} - Import failed: {e}")
                self.errors.append(f"Project module {module_name} import failed: {e}")
                all_imports_ok = False
            except Exception as e:
                logger.error(f"  ❌ {module_name} - Unexpected error: {e}")
                self.errors.append(f"Project module {module_name} unexpected error: {e}")
                all_imports_ok = False
        
        return all_imports_ok
    
    def test_controller_imports(self) -> bool:
        """Test if all controllers can be imported and instantiated"""
        logger.info("🔍 Testing controller imports...")
        
        controllers = [
            'src.controllers.example_controller.ExampleController',
            'src.controllers.settings_controller.SettingsController',
            'src.controllers.chat_controller.ChatController',
            'src.controllers.companies_controller.CompaniesController',
            'src.controllers.api_controller.ApiController',
        ]
        
        all_controllers_ok = True
        
        for controller_path in controllers:
            try:
                module_name, class_name = controller_path.rsplit('.', 1)
                module = importlib.import_module(module_name)
                controller_class = getattr(module, class_name)
                
                # Try to instantiate if it has __init__
                if hasattr(controller_class, '__init__'):
                    try:
                        instance = controller_class()
                        logger.info(f"  ✅ {controller_path} - Import and instantiation successful")
                    except Exception as e:
                        logger.warning(f"  ⚠️ {controller_path} - Import successful but instantiation failed: {e}")
                else:
                    logger.info(f"  ✅ {controller_path} - Import successful (static class)")
                    
            except ImportError as e:
                logger.error(f"  ❌ {controller_path} - Import failed: {e}")
                self.errors.append(f"Controller {controller_path} import failed: {e}")
                all_controllers_ok = False
            except Exception as e:
                logger.error(f"  ❌ {controller_path} - Unexpected error: {e}")
                self.errors.append(f"Controller {controller_path} unexpected error: {e}")
                all_controllers_ok = False
        
        return all_controllers_ok
    
    def test_database_connections(self) -> bool:
        """Test database connectivity"""
        logger.info("🔍 Testing database connections...")
        
        try:
            from src.database import database_manager
            if hasattr(database_manager, 'test_connections'):
                result = database_manager.test_connections()
                if result:
                    logger.info("  ✅ Database connections test successful")
                    return True
                else:
                    logger.error("  ❌ Database connections test failed")
                    self.errors.append("Database connections test failed")
                    return False
            else:
                logger.warning("  ⚠️ Database manager doesn't have test_connections method")
                return True
        except Exception as e:
            logger.error(f"  ❌ Database connection test error: {e}")
            self.errors.append(f"Database connection test error: {e}")
            return False
    
    def generate_report(self, result: ImportTestResult) -> str:
        """Generate a comprehensive test report"""
        report = []
        report.append("=" * 80)
        report.append("COMPREHENSIVE DEPENDENCY TEST REPORT")
        report.append("=" * 80)
        report.append("")
        
        # Summary
        report.append("SUMMARY:")
        report.append(f"  Total Dependencies: {result.total_dependencies}")
        report.append(f"  Available Dependencies: {result.available_dependencies}")
        report.append(f"  Required Dependencies: {result.required_dependencies}")
        report.append(f"  Available Required: {result.available_required}")
        report.append(f"  Overall Status: {'✅ PASS' if result.success else '❌ FAIL'}")
        report.append("")
        
        # Group by category
        categories = {}
        for test in result.tests:
            if test.category not in categories:
                categories[test.category] = []
            categories[test.category].append(test)
        
        for category, tests in categories.items():
            report.append(f"{category.upper()} DEPENDENCIES:")
            for test in tests:
                status = "✅" if test.available else "❌"
                required = " (REQUIRED)" if test.required else " (OPTIONAL)"
                version_info = f" v{test.version}" if test.version else ""
                report.append(f"  {status} {test.name}{required}{version_info}")
                if test.error:
                    report.append(f"      Error: {test.error}")
            report.append("")
        
        # Errors
        if result.errors:
            report.append("ERRORS:")
            for error in result.errors:
                report.append(f"  ❌ {error}")
            report.append("")
        
        # Recommendations
        report.append("RECOMMENDATIONS:")
        missing_required = [t for t in result.tests if t.required and not t.available]
        if missing_required:
            report.append("  Required dependencies to install:")
            for test in missing_required:
                report.append(f"    pip install {test.name}")
        else:
            report.append("  ✅ All required dependencies are available")
        
        missing_optional = [t for t in result.tests if not t.required and not t.available]
        if missing_optional:
            report.append("  Optional dependencies to consider:")
            for test in missing_optional:
                report.append(f"    pip install {test.name}")
        
        report.append("")
        report.append("=" * 80)
        
        return "\n".join(report)

def run_comprehensive_tests() -> ImportTestResult:
    """Run all comprehensive tests"""
    tester = DependencyTester()
    
    # Test external dependencies
    result = tester.test_all_dependencies()
    
    # Test project imports
    project_imports_ok = tester.test_project_imports()
    
    # Test controller imports
    controller_imports_ok = tester.test_controller_imports()
    
    # Test database connections
    database_ok = tester.test_database_connections()
    
    # Update result
    result.success = result.success and project_imports_ok and controller_imports_ok and database_ok
    
    # Generate and print report
    report = tester.generate_report(result)
    print(report)
    
    return result

if __name__ == "__main__":
    result = run_comprehensive_tests()
    sys.exit(0 if result.success else 1)
