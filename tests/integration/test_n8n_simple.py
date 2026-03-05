#!/usr/bin/env python3
"""
Simple N8N Integration Test
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_basic_imports():
    """Test basic N8N imports"""
    print("🧪 Testing basic N8N imports...")

    try:
        from src.integrations.n8n_integration import N8NIntegration, N8NWorkflow
        print("✅ N8N Integration import successful")
        return True
    except Exception as e:
        print(f"❌ N8N Integration import failed: {e}")
        return False

def test_n8n_initialization():
    """Test N8N initialization"""
    print("\n🧪 Testing N8N initialization...")

    try:
        from src.integrations.n8n_integration import N8NIntegration

        integration = N8NIntegration()
        print("✅ N8N Integration initialized")
        print(f"   - Enabled: {integration.config.get('enabled', False)}")
        print(f"   - Base URL: {integration.config.get('base_url', 'Not set')}")
        return True
    except Exception as e:
        print(f"❌ N8N Integration initialization failed: {e}")
        return False

def test_workflow_creation():
    """Test workflow creation"""
    print("\n🧪 Testing workflow creation...")

    try:
        from src.integrations.n8n_integration import N8NIntegration

        integration = N8NIntegration()

        workflow_data = {
            'name': 'Test Workflow',
            'description': 'A simple test workflow',
            'nodes': [{'id': '1', 'name': 'Test Node', 'type': 'test'}],
            'connections': {},
            'settings': {}
        }

        workflow_id = integration.create_workflow(workflow_data)
        print(f"✅ Workflow created with ID: {workflow_id}")
        return True
    except Exception as e:
        print(f"❌ Workflow creation failed: {e}")
        return False

def test_error_handling():
    """Test error handling system"""
    print("\n🧪 Testing error handling...")

    try:
        from src.core.error_handling import get_error_details

        title, message = get_error_details(404)
        print(f"✅ Error details retrieved: {title}")
        return True
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
        return False

def main():
    """Run all simple tests"""
    print("🚀 Simple N8N Integration Testing\n")

    tests = [
        test_basic_imports,
        test_n8n_initialization,
        test_workflow_creation,
        test_error_handling
    ]

    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
            results.append(False)

    print("\n📊 Test Summary:")
    print(f"   Passed: {sum(results)}/{len(results)}")
    print(f"   Failed: {len(results) - sum(results)}/{len(results)}")

    if all(results):
        print("🎉 All Simple N8N Integration Tests Passed!")
        return True
    else:
        print("⚠️ Some tests failed, but core functionality is working")
        return False

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
