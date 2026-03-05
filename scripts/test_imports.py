#!/usr/bin/env python3
"""
Test Module Imports - Verify all required modules can be imported
"""

import sys
from pathlib import Path

# Add the project root and src to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'src'))

def test_imports():
    """Test all critical module imports"""

    imports_to_test = [
        ('src.assets.asset_manager', 'asset_manager, theme_manager'),
        ('src.components.component_system', 'component_registry'),
        ('src.routes.unified_routes', 'route_manager'),
        ('src.utils.menu_generator', 'main_menu_sidebar, main_menu'),
        ('src.controllers.chat_controller', 'ChatController'),
        ('src.controllers.api_controller', 'APIController'),
        ('src.crud.unified_crud_operations', 'UnifiedCRUDOperations'),
        ('src.crud.unified_crud_config', 'CRUDConfig'),
        ('src.database.unified_db_manager', 'db'),
    ]

    results = []
    for module, objects in imports_to_test:
        try:
            exec(f"from {module} import {objects}")
            print(f"✅ {module} - {objects}")
            results.append((module, True, None))
        except Exception as e:
            print(f"❌ {module} - {objects}: {e}")
            results.append((module, False, str(e)))

    return results

def test_template_functions():
    """Test template function availability"""
    print("\n📄 Testing template function availability...")

    try:
        from src.assets.asset_manager import asset_manager, theme_manager

        # Test asset manager functions
        functions_to_test = [
            ('asset_manager.render_css_links', ['tailwind_css']),
            ('asset_manager.render_js_scripts', ['alpine_js']),
            ('asset_manager.render_font_links', ['inter_font']),
            ('asset_manager.render_favicon_links', []),
            ('theme_manager.render_theme_css', []),
            ('theme_manager.get_theme_css_variables', []),
        ]

        for func_name, args in functions_to_test:
            try:
                parts = func_name.split('.')
                obj = eval(parts[0])
                method = getattr(obj, parts[1])
                if args:
                    result = method(args)
                else:
                    result = method()
                print(f"✅ {func_name}() - {len(str(result))} chars")
            except Exception as e:
                print(f"❌ {func_name}() failed: {e}")

    except Exception as e:
        print(f"❌ Could not test template functions: {e}")

def main():
    """Run all import tests"""
    print("🔍 Module Import Test Suite")
    print("=" * 50)

    results = test_imports()
    test_template_functions()

    # Summary
    print("\n" + "=" * 50)
    print("📊 IMPORT TEST SUMMARY")
    print("=" * 50)

    passed = sum(1 for _, success, _ in results if success)
    failed = len(results) - passed

    for module, success, error in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status} - {module}")
        if error:
            print(f"   Error: {error}")

    print(f"\n📈 Results: {passed} passed, {failed} failed")

    if failed == 0:
        print("🎉 All module imports successful!")
        return 0
    else:
        print("⚠️ Some module imports failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    exit(main())
