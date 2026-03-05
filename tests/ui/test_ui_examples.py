#!/usr/bin/env python3
"""Test UI Examples functionality"""

from app import app
import json

def test_ui_examples():
    with app.test_client() as client:
        # Test main route
        print("Testing /ui-examples route...")
        response = client.get('/ui-examples/')
        print(f"Main route status: {response.status_code}")

        if response.status_code == 200:
            print("✅ Main route working correctly")
        else:
            print(f"❌ Main route error: {response.data.decode()}")

        # Test API endpoint
        print("\nTesting /ui-examples/api/components endpoint...")
        response = client.get('/ui-examples/api/components')
        print(f"API route status: {response.status_code}")

        if response.status_code == 200:
            try:
                data = json.loads(response.data.decode())
                components_count = len(data.get("data", {}))
                print(f"✅ API endpoint working correctly - {components_count} components returned")
                print(f"Available components: {list(data.get('data', {}).keys())}")
            except json.JSONDecodeError as e:
                print(f"❌ JSON decode error: {e}")
        else:
            print(f"❌ API Error: {response.data.decode()}")

if __name__ == "__main__":
    test_ui_examples()
