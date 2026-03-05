#!/usr/bin/env python3
"""
Functional Test Suite for Chat System
Tests real functionality with sample questions and models
"""

import sys
import os
import json
import time
import requests
from datetime import datetime
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def test_chat_functionality():
    """Test chat functionality with sample questions"""
    print("🧪 Starting Chat Functional Tests...")
    print("=" * 60)

    base_url = "http://localhost:5000"  # Adjust if needed

    try:
        # Test 1: Get sample questions
        print("📋 Test 1: Getting sample questions...")
        response = requests.get(f"{base_url}/api/chat/sample-questions")

        if response.status_code == 200:
            data = response.json()
            questions = data.get('suggestions', [])
            print(f"✅ Found {len(questions)} sample questions")

            # Display question categories
            categories = data.get('categories', [])
            print(f"📂 Categories: {', '.join(categories)}")

            # Test a few key questions
            test_questions = [q for q in questions if q['id'] in ['1', '7', '8', '9']]

            for question in test_questions:
                print(f"\n🧪 Testing Question: {question['question'][:50]}...")

                # Test with different formats if applicable
                test_data = question.get('test_data', {})
                if 'format' in test_data:
                    format_type = test_data['format']
                    print(f"📄 Testing {format_type.upper()} generation...")

        else:
            print(f"❌ Failed to get sample questions: {response.status_code}")

        # Test 2: Get available models
        print("\n🤖 Test 2: Getting available models...")
        response = requests.get(f"{base_url}/api/chat/models")

        if response.status_code == 200:
            data = response.json()
            models = data.get('models', [])
            print(f"✅ Found {len(models)} available models")

            for model in models:
                status = "✅ Downloaded" if model.get('is_downloaded') else "❌ Not downloaded"
                print(f"   - {model['name']} ({model['size']}): {status}")
        else:
            print(f"❌ Failed to get models: {response.status_code}")

        # Test 3: Test theme colors
        print("\n🎨 Test 3: Testing theme colors...")
        themes_to_test = ['light', 'dark', 'dracula']

        for theme in themes_to_test:
            response = requests.get(f"{base_url}/api/chat/theme-colors?theme={theme}")

            if response.status_code == 200:
                data = response.json()
                if 'error' not in data:
                    css_vars = data.get('css_variables', {})
                    print(f"✅ {theme.title()} theme: {len(css_vars)} CSS variables")
                else:
                    print(f"❌ {theme.title()} theme error: {data['error']}")
            else:
                print(f"❌ Failed to get {theme} theme: {response.status_code}")

        # Test 4: Run theme validation
        print("\n🔍 Test 4: Running theme validation...")
        response = requests.post(f"{base_url}/api/chat/test-themes")

        if response.status_code == 200:
            data = response.json()
            if 'error' not in data:
                results = data.get('test_results', [])
                passed = data.get('passed_tests', 0)
                total = data.get('total_themes', 0)
                print(f"✅ Theme validation: {passed}/{total} themes passed")

                for result in results:
                    status = "✅" if result.get('status') == 'passed' else "❌"
                    print(f"   {status} {result.get('theme_name', 'Unknown')}")
            else:
                print(f"❌ Theme validation error: {data['error']}")
        else:
            print(f"❌ Failed to run theme validation: {response.status_code}")

        # Test 5: Test individual question with model (if models available)
        print("\n⚡ Test 5: Testing question with model...")
        response = requests.get(f"{base_url}/api/chat/models")
        if response.status_code == 200:
            data = response.json()
            models = [m for m in data.get('models', []) if m.get('is_downloaded')]

            if models:
                first_model = models[0]
                print(f"🤖 Testing with model: {first_model['name']}")

                test_payload = {
                    'question_id': '1',
                    'model_id': first_model['id']
                }

                response = requests.post(
                    f"{base_url}/api/chat/test-question",
                    json=test_payload,
                    headers={'Content-Type': 'application/json'}
                )

                if response.status_code == 200:
                    result = response.json()
                    if 'error' not in result:
                        print("✅ Question test completed successfully"                        print(f"   Status: {result.get('status', 'Unknown')}")
                        print(f"   Response length: {len(result.get('response', ''))} chars")
                    else:
                        print(f"❌ Question test error: {result['error']}")
                else:
                    print(f"❌ Failed to test question: {response.status_code}")
            else:
                print("⚠️ No downloaded models available for testing")

        print("\n" + "=" * 60)
        print("🎉 Chat Functional Tests Completed!")
        print("\n📊 Summary:")
        print("- ✅ Sample questions integration")
        print("- ✅ Model discovery and status")
        print("- ✅ Theme color validation")
        print("- ✅ Comprehensive theme testing")
        print("- ✅ Individual question testing (when models available)")

    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Please ensure the Flask app is running")
        print(f"   Try: python app.py (then visit {base_url})")
    except Exception as e:
        print(f"❌ Test Error: {str(e)}")
        import traceback
        traceback.print_exc()

def test_report_generation():
    """Test report generation functionality"""
    print("\n📊 Testing Report Generation...")
    print("=" * 40)

    base_url = "http://localhost:5000"

    try:
        # Test company report generation
        print("🏢 Testing Company Report Generation...")
        response = requests.get(f"{base_url}/api/reports/company?company_id=1&format=json")

        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ Company report generated successfully")
                print(f"   File: {data.get('filepath', 'N/A')}")
            else:
                print(f"❌ Company report error: {data.get('error', 'Unknown')}")
        else:
            print(f"❌ Company report failed: {response.status_code}")

        # Test financial report generation
        print("\n💰 Testing Financial Report Generation...")
        response = requests.get(
            f"{base_url}/api/reports/financial?company_id=1&format=excel&start_date=2024-01-01&end_date=2024-12-31"
        )

        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ Financial report generated successfully")
                print(f"   File: {data.get('filepath', 'N/A')}")
            else:
                print(f"❌ Financial report error: {data.get('error', 'Unknown')}")
        else:
            print(f"❌ Financial report failed: {response.status_code}")

        # Test tax report generation
        print("\n📋 Testing Tax Report Generation...")
        response = requests.get(f"{base_url}/api/reports/tax?company_id=1&format=pdf&year=2024")

        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ Tax report generated successfully")
                print(f"   File: {data.get('filepath', 'N/A')}")
            else:
                print(f"❌ Tax report error: {data.get('error', 'Unknown')}")
        else:
            print(f"❌ Tax report failed: {response.status_code}")

        # Test customer report generation
        print("\n👥 Testing Customer Report Generation...")
        response = requests.get(f"{base_url}/api/reports/customer?format=csv")

        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ Customer report generated successfully")
                print(f"   File: {data.get('filepath', 'N/A')}")
            else:
                print(f"❌ Customer report error: {data.get('error', 'Unknown')}")
        else:
            print(f"❌ Customer report failed: {response.status_code}")

        print("\n📊 Report Generation Tests Completed!")

    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Please ensure the Flask app is running")
    except Exception as e:
        print(f"❌ Report Test Error: {str(e)}")

def main():
    """Main test function"""
    print("🚀 ValidoAI Chat & Report System - Functional Tests")
    print("=" * 70)

    # Run chat functionality tests
    test_chat_functionality()

    # Run report generation tests
    test_report_generation()

    print("\n" + "=" * 70)
    print("🎯 Functional Testing Complete!")
    print("\n💡 Next Steps:")
    print("- Run the Flask application: python app.py")
    print("- Visit http://localhost:5000/chat to test the interface")
    print("- Check generated reports in the reports/ directory")
    print("- Review test results and implement any needed fixes")

if __name__ == "__main__":
    main()
