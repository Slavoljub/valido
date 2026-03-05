#!/usr/bin/env python3
"""Test the health endpoint"""

from app import app

def test_health_endpoint():
    print("Testing health endpoint...")
    with app.test_client() as client:
        response = client.get('/health')
        print(f'Status: {response.status_code}')
        if response.status_code == 200:
            data = response.get_json()
            print("✅ Health endpoint working!")
            print(f"Status: {data.get('status')}")
            print(f"Database: {data.get('database', {}).get('status')}")
            print(f"AI/ML: {data.get('ai_ml', {}).get('status')}")
            print(".2f")
        else:
            print("❌ Health endpoint failed!")
            print(f"Response: {response.get_data(as_text=True)}")

if __name__ == "__main__":
    test_health_endpoint()
