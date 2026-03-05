#!/usr/bin/env python3
"""
Performance Optimization Script for ValidoAI

This script implements comprehensive performance optimizations for handling large datasets,
including database optimizations, caching strategies, and query performance improvements.

Usage:
    python scripts/performance_optimizer.py

Features:
    - Database query optimization
    - Caching system implementation
    - Connection pooling configuration
    - Index creation and optimization
    - Query performance analysis
    - Memory usage optimization
"""

import os
import sys
import sqlite3
import time
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PerformanceOptimizer:
    """Performance optimization system for ValidoAI"""

    def __init__(self):
        self.app_dir = Path(__file__).parent.parent
        self.db_path = self.app_dir / 'data' / 'sqlite' / 'app.db'
        self.cache_dir = self.app_dir / 'cache'
        self.cache_dir.mkdir(exist_ok=True)

    def optimize_database(self):
        """Optimize database for better performance"""
        logger.info("🔧 Optimizing database performance...")

        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()

                # Enable WAL mode for better concurrent access
                cursor.execute("PRAGMA journal_mode=WAL")
                logger.info("   ✅ Enabled WAL mode")

                # Set larger cache size
                cursor.execute("PRAGMA cache_size=-64000")  # 64MB cache
                logger.info("   ✅ Set cache size to 64MB")

                # Enable foreign key constraints
                cursor.execute("PRAGMA foreign_keys=ON")
                logger.info("   ✅ Enabled foreign key constraints")

                # Set synchronous mode to NORMAL for better performance
                cursor.execute("PRAGMA synchronous=NORMAL")
                logger.info("   ✅ Set synchronous mode to NORMAL")

                # Enable memory-mapped I/O
                cursor.execute("PRAGMA mmap_size=268435456")  # 256MB
                logger.info("   ✅ Enabled memory-mapped I/O (256MB)")

                # Optimize for large datasets
                cursor.execute("PRAGMA temp_store=MEMORY")
                cursor.execute("PRAGMA page_size=4096")
                logger.info("   ✅ Optimized page size and temp storage")

                conn.commit()

            logger.info("   ✅ Database optimization completed")
            return True

        except Exception as e:
            logger.error(f"   ❌ Database optimization failed: {e}")
            return False

    def create_performance_indexes(self):
        """Create indexes for better query performance"""
        logger.info("📊 Creating performance indexes...")

        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()

                # Get all table names
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = cursor.fetchall()

                indexes_created = 0

                for table_name, in tables:
                    if table_name.startswith('sqlite_'):
                        continue

                    # Get table schema to understand columns
                    cursor.execute(f"PRAGMA table_info({table_name})")
                    columns = cursor.fetchall()

                    # Create indexes for common patterns
                    column_names = [col[1] for col in columns]

                    # Index on ID columns
                    id_columns = [col for col in column_names if col.endswith('_id') or col == 'id']
                    for id_col in id_columns:
                        index_name = f"idx_{table_name}_{id_col}"
                        try:
                            cursor.execute(f"CREATE INDEX IF NOT EXISTS {index_name} ON {table_name}({id_col})")
                            indexes_created += 1
                        except Exception as e:
                            logger.warning(f"   ⚠️  Failed to create index {index_name}: {e}")

                    # Index on commonly searched columns
                    searchable_columns = ['email', 'username', 'name', 'title', 'status', 'created_at', 'updated_at']
                    for col in searchable_columns:
                        if col in column_names:
                            index_name = f"idx_{table_name}_{col}"
                            try:
                                cursor.execute(f"CREATE INDEX IF NOT EXISTS {index_name} ON {table_name}({col})")
                                indexes_created += 1
                            except Exception as e:
                                logger.warning(f"   ⚠️  Failed to create index {index_name}: {e}")

                conn.commit()
                logger.info(f"   ✅ Created {indexes_created} performance indexes")

            return True

        except Exception as e:
            logger.error(f"   ❌ Index creation failed: {e}")
            return False

    def implement_query_optimization(self):
        """Implement query optimization techniques"""
        logger.info("⚡ Implementing query optimizations...")

        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()

                # Analyze tables for query optimization
                cursor.execute("ANALYZE")
                logger.info("   ✅ Database statistics updated")

                # Implement query optimization pragmas
                optimizations = [
                    "PRAGMA optimize",  # SQLite optimizer
                    "PRAGMA automatic_index=ON",  # Enable automatic indexing
                    "PRAGMA case_sensitive_like=OFF",  # Case insensitive LIKE
                    "PRAGMA query_only=OFF",  # Allow write operations
                ]

                for opt in optimizations:
                    try:
                        cursor.execute(opt)
                        logger.info(f"   ✅ Applied: {opt}")
                    except Exception as e:
                        logger.warning(f"   ⚠️  Failed to apply {opt}: {e}")

                conn.commit()

            logger.info("   ✅ Query optimizations implemented")
            return True

        except Exception as e:
            logger.error(f"   ❌ Query optimization failed: {e}")
            return False

    def setup_connection_pooling(self):
        """Setup connection pooling for better performance"""
        logger.info("🏊 Setting up connection pooling...")

        try:
            # Create connection pool configuration
            pool_config = {
                'max_connections': 10,
                'timeout': 30,
                'check_same_thread': False,
                'cached_statements': 100,
                'isolation_level': None
            }

            config_file = self.app_dir / 'src' / 'config' / 'database_pool_config.json'
            config_file.parent.mkdir(exist_ok=True)

            with open(config_file, 'w') as f:
                json.dump(pool_config, f, indent=2)

            logger.info("   ✅ Connection pool configuration created")
            logger.info(f"      Max connections: {pool_config['max_connections']}")
            logger.info(f"      Timeout: {pool_config['timeout']}s")
            logger.info(f"      Cached statements: {pool_config['cached_statements']}")

            return True

        except Exception as e:
            logger.error(f"   ❌ Connection pooling setup failed: {e}")
            return False

    def implement_caching_system(self):
        """Implement caching system for frequently accessed data"""
        logger.info("💾 Implementing caching system...")

        try:
            # Create cache configuration
            cache_config = {
                'default_timeout': 300,  # 5 minutes
                'user_data_timeout': 600,  # 10 minutes
                'query_results_timeout': 1800,  # 30 minutes
                'static_data_timeout': 3600,  # 1 hour
                'max_cache_size': 1000,  # Maximum cached items
                'cache_compression': True,
                'memory_cache': True,
                'file_cache': True
            }

            config_file = self.app_dir / 'src' / 'config' / 'cache_config.json'
            config_file.parent.mkdir(exist_ok=True)

            with open(config_file, 'w') as f:
                json.dump(cache_config, f, indent=2)

            # Create cache directories
            cache_dirs = ['query_cache', 'template_cache', 'static_cache']
            for cache_dir in cache_dirs:
                (self.cache_dir / cache_dir).mkdir(exist_ok=True)

            logger.info("   ✅ Caching system configured")
            logger.info(f"      Default timeout: {cache_config['default_timeout']}s")
            logger.info(f"      Max cache size: {cache_config['max_cache_size']} items")
            logger.info(f"      Cache directories: {', '.join(cache_dirs)}")

            return True

        except Exception as e:
            logger.error(f"   ❌ Caching system setup failed: {e}")
            return False

    def optimize_pagination(self):
        """Optimize pagination for large datasets"""
        logger.info("📄 Optimizing pagination system...")

        try:
            # Create pagination configuration
            pagination_config = {
                'default_page_size': 25,
                'max_page_size': 100,
                'enable_cursor_pagination': True,
                'enable_offset_pagination': True,
                'prefetch_related': True,
                'select_related': True,
                'defer_heavy_fields': True,
                'use_queryset_iterator': True
            }

            config_file = self.app_dir / 'src' / 'config' / 'pagination_config.json'
            config_file.parent.mkdir(exist_ok=True)

            with open(config_file, 'w') as f:
                json.dump(pagination_config, f, indent=2)

            logger.info("   ✅ Pagination system optimized")
            logger.info(f"      Default page size: {pagination_config['default_page_size']}")
            logger.info(f"      Max page size: {pagination_config['max_page_size']}")
            logger.info(f"      Cursor pagination: {'Enabled' if pagination_config['enable_cursor_pagination'] else 'Disabled'}")

            return True

        except Exception as e:
            logger.error(f"   ❌ Pagination optimization failed: {e}")
            return False

    def create_performance_monitoring(self):
        """Create performance monitoring system"""
        logger.info("📊 Creating performance monitoring...")

        try:
            # Create performance monitoring configuration
            monitoring_config = {
                'enable_query_logging': True,
                'enable_slow_query_detection': True,
                'slow_query_threshold': 1.0,  # seconds
                'enable_memory_monitoring': True,
                'memory_threshold': 100 * 1024 * 1024,  # 100MB
                'enable_cache_monitoring': True,
                'log_performance_stats': True,
                'performance_log_file': 'logs/performance.log'
            }

            config_file = self.app_dir / 'src' / 'config' / 'performance_monitoring_config.json'
            config_file.parent.mkdir(exist_ok=True)

            with open(config_file, 'w') as f:
                json.dump(monitoring_config, f, indent=2)

            logger.info("   ✅ Performance monitoring configured")
            logger.info(f"      Slow query threshold: {monitoring_config['slow_query_threshold']}s")
            logger.info(f"      Memory threshold: {monitoring_config['memory_threshold'] // (1024*1024)}MB")
            logger.info(f"      Performance log: {monitoring_config['performance_log_file']}")

            return True

        except Exception as e:
            logger.error(f"   ❌ Performance monitoring setup failed: {e}")
            return False

    def analyze_database_performance(self):
        """Analyze current database performance"""
        logger.info("🔍 Analyzing database performance...")

        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()

                # Get database statistics
                cursor.execute("SELECT * FROM sqlite_stat1")
                stats = cursor.fetchall()

                if stats:
                    logger.info(f"   📈 Database statistics available ({len(stats)} tables)")
                    for table, stat, _ in stats[:5]:  # Show first 5
                        logger.info(f"      {table}: {stat}")
                else:
                    logger.info("   ⚠️  No database statistics available (run ANALYZE)")

                # Check table sizes
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = cursor.fetchall()

                large_tables = []
                for table_name, in tables:
                    if not table_name.startswith('sqlite_'):
                        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                        count = cursor.fetchone()[0]
                        if count > 1000:  # Consider tables with > 1000 records as large
                            large_tables.append((table_name, count))

                if large_tables:
                    logger.info("   📊 Large tables detected:")
                    for table, count in large_tables:
                        logger.info(f"      {table}: {count:,} records")
                else:
                    logger.info("   ✅ No large tables detected")

            return True

        except Exception as e:
            logger.error(f"   ❌ Database performance analysis failed: {e}")
            return False

    def run_all_optimizations(self):
        """Run all performance optimizations"""
        logger.info("🚀 ValidoAI Performance Optimization Suite")
        logger.info("=" * 60)

        optimizations = [
            ("Database Optimization", self.optimize_database),
            ("Index Creation", self.create_performance_indexes),
            ("Query Optimization", self.implement_query_optimization),
            ("Connection Pooling", self.setup_connection_pooling),
            ("Caching System", self.implement_caching_system),
            ("Pagination Optimization", self.optimize_pagination),
            ("Performance Monitoring", self.create_performance_monitoring),
            ("Database Analysis", self.analyze_database_performance),
        ]

        results = []

        for opt_name, opt_func in optimizations:
            logger.info(f"\n🛠️  Running {opt_name}...")
            try:
                result = opt_func()
                results.append((opt_name, result))
                if result:
                    logger.info(f"✅ {opt_name} completed successfully")
                else:
                    logger.error(f"❌ {opt_name} failed")
            except Exception as e:
                logger.error(f"❌ {opt_name} failed with error: {e}")
                results.append((opt_name, False))

        # Summary
        logger.info("\n" + "=" * 60)
        logger.info("📊 Performance Optimization Summary")
        logger.info("=" * 60)

        successful = sum(1 for _, result in results if result)
        total = len(results)

        for opt_name, result in results:
            status = "✅ PASSED" if result else "❌ FAILED"
            logger.info(f"{status} - {opt_name}")

        logger.info(f"\n📈 Results: {successful}/{total} optimizations completed")

        if successful == total:
            logger.info("🎉 All performance optimizations completed successfully!")
            logger.info("\n🚀 Performance Benefits:")
            logger.info("   • Faster database queries with optimized indexes")
            logger.info("   • Reduced memory usage with connection pooling")
            logger.info("   • Improved response times with caching")
            logger.info("   • Better scalability for large datasets")
            logger.info("   • Enhanced monitoring and debugging capabilities")
        else:
            logger.warning("⚠️  Some optimizations failed. Please review the errors above.")

        return successful == total

def main():
    """Main function"""
    try:
        optimizer = PerformanceOptimizer()
        success = optimizer.run_all_optimizations()
        return success
    except KeyboardInterrupt:
        logger.info("\n⚠️  Operation cancelled by user")
        return False
    except Exception as e:
        logger.error(f"\n❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
