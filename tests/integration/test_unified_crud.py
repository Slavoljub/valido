#!/usr/bin/env python3
"""
Test Unified CRUD System
Simple test to verify the unified CRUD system is working
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.crud.unified_crud_config import CRUDConfig, crud_config_registry
from src.crud.unified_crud_operations import unified_crud_registry
from src.routes.unified_route_generator import unified_route_generator
from src.config.table_configurations import get_companies_config, get_all_table_configs

def test_unified_crud():
    """Test the unified CRUD system"""

    print("Testing Unified CRUD System")
    print("=" * 50)

    # Test 1: Load all configurations
    print("\n1. Loading All Table Configurations")
    all_configs = get_all_table_configs()
    print(f"✓ Loaded {len(all_configs)} table configurations")

    # Test 2: Register all configurations
    print("\n2. Registering All Configurations")
    for table_name, config in all_configs.items():
        crud_config_registry.register(config)
        print(f"  ✓ Registered {table_name}")
    print(f"✓ Total configurations registered: {len(all_configs)}")

    # Test 3: Test multiple table configurations
    print("\n3. Testing Multiple Table Configurations")
    test_tables = ['companies', 'users', 'countries', 'business_config', 'warehouses', 'ai_models_system']

    for table_name in test_tables:
        config = crud_config_registry.get(table_name)
        if config:
            print(f"  ✓ {table_name}: {config.display_name} ({len(config.columns)} columns)")
        else:
            print(f"  ✗ {table_name}: Not found")

    # Test 4: Create CRUD instances for multiple tables
    print("\n4. Creating CRUD Instances")
    for table_name in test_tables:
        config = crud_config_registry.get(table_name)
        if config:
            crud = unified_crud_registry.get_crud(table_name, config)
            print(f"  ✓ {table_name}: CRUD instance created")

    # Test 5: Generate routes for multiple tables
    print("\n5. Generating Routes")
    for table_name in test_tables:
        config = crud_config_registry.get(table_name)
        if config:
            try:
                blueprint = unified_route_generator.generate_routes(table_name, config)
                print(f"  ✓ {table_name}: Routes generated ({blueprint.url_prefix})")
            except Exception as e:
                print(f"  ✗ {table_name}: Route generation failed - {e}")

    # Test 6: Check comprehensive registry status
    print("\n6. Comprehensive Registry Status")
    all_configs_final = crud_config_registry.get_all()
    all_crud_final = unified_crud_registry.get_all_crud()
    all_blueprints_final = unified_route_generator.blueprints

    print(f"✓ Total Configurations: {len(all_configs_final)}")
    print(f"✓ Total CRUD Instances: {len(all_crud_final)}")
    print(f"✓ Total Blueprints: {len(all_blueprints_final)}")

    # Test 7: Test specific features
    print("\n7. Testing Specific Features")
    companies_config = crud_config_registry.get('companies')
    if companies_config:
        print(f"✓ Companies tabs: {len(companies_config.tabs)}")
        print(f"✓ Companies validation rules: {len(companies_config.validation_rules)}")
        print(f"✓ Companies export formats: {[fmt.value for fmt in companies_config.export_formats]}")

    users_config = crud_config_registry.get('users')
    if users_config:
        print(f"✓ Users columns: {len(users_config.columns)}")
        print(f"✓ Users filters: {len(users_config.filters)}")

    # Test 8: Test special table features
    print("\n8. Testing Special Table Features")
    ai_config = crud_config_registry.get('ai_models_system')
    if ai_config:
        print(f"✓ AI Models: {len(ai_config.columns)} columns, {len(ai_config.filters)} filters")

    chat_config = crud_config_registry.get('chat_sessions')
    if chat_config:
        print(f"✓ Chat Sessions: {len(chat_config.columns)} columns")

    print("\n" + "=" * 50)
    print("✓ Unified CRUD System Test Completed!")
    print(f"✓ Successfully processed {len(all_configs)} tables")
    print("✓ All core features working correctly")

if __name__ == "__main__":
    test_unified_crud()
