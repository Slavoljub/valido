#!/usr/bin/env python3
"""
Demo script for AI Chat Testing System
Demonstrates all the testing and monitoring capabilities
"""

import os
import sys
import json
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from ai_local_models.chat_tester import chat_tester, AIChatTester
from ai_local_models.route_tester import route_tester, RouteTester
from controllers.chat_controller import chat_controller


def demo_chat_question_testing():
    """Demonstrate AI chat question testing"""
    print("🤖 AI Chat Question Testing Demo")
    print("=" * 50)

    try:
        # Test a few sample questions
        test_questions = [
            {
                "id": "revenue_trends",
                "text": "📊 Analyze my revenue trends and provide insights",
                "category": "financial",
                "expected_type": "analysis"
            },
            {
                "id": "best_clients",
                "text": "🏆 What are the best clients and selling products?",
                "category": "business",
                "expected_type": "analysis"
            },
            {
                "id": "database_health",
                "text": "🗄️ Check database connection health",
                "category": "database",
                "expected_type": "status"
            }
        ]

        print(f"Testing {len(test_questions)} sample questions...")

        for question in test_questions:
            print(f"\n📝 Testing: {question['text'][:50]}...")

            # Load database context
            contexts = {}
            for db_name in ['main', 'sqlite']:
                try:
                    context = chat_tester.load_database_context(db_name)
                    contexts[db_name] = context
                    print(f"   ✅ Loaded context for {db_name}: {context['connection_status']}")
                except Exception as e:
                    print(f"   ❌ Failed to load context for {db_name}: {e}")

            # Generate AI response
            try:
                response = chat_tester.generate_ai_response(question, contexts)
                print(f"   🤖 Response: {response[:100]}...")
            except Exception as e:
                print(f"   ❌ Failed to generate response: {e}")

        print("\n✅ Chat question testing demo completed!")

    except Exception as e:
        print(f"❌ Chat testing demo failed: {e}")


def demo_route_testing():
    """Demonstrate route status testing"""
    print("\n🛣️ Route Status Testing Demo")
    print("=" * 50)

    try:
        # Test a few key routes
        test_routes = [
            {"path": "/", "method": "GET", "expected_status": 200},
            {"path": "/chat-local", "method": "GET", "expected_status": 200},
            {"path": "/database-example", "method": "GET", "expected_status": 200},
        ]

        print(f"Testing {len(test_routes)} routes...")

        for route in test_routes:
            print(f"\n🔗 Testing: {route['method']} {route['path']}")
            result = route_tester.test_single_route(route)

            if result.is_success:
                print(".2f"            else:
                print(f"   ❌ Failed: {result.error_message}")

        # Generate comprehensive report
        print("\n📊 Generating comprehensive route status report...")
        try:
            report = route_tester.generate_comprehensive_report()

            print("   ✅ Report generated successfully!"            print(f"   📈 Overall success rate: {report['overall_status']['routes_success_rate']:.1f}%")
            print(f"   ⏱️ Average response time: {report['overall_status']['average_response_time']:.2f}s")

            if report['database_status']['success']:
                print("   🗄️ Database: Connected"            else:
                print("   🗄️ Database: Disconnected"
            if report['chat_status']['success']:
                print("   💬 Chat: Functional"            else:
                print("   💬 Chat: Issues detected"
        except Exception as e:
            print(f"   ❌ Failed to generate report: {e}")

        print("\n✅ Route testing demo completed!")

    except Exception as e:
        print(f"❌ Route testing demo failed: {e}")


def demo_chat_controller_features():
    """Demonstrate chat controller features"""
    print("\n🎮 Chat Controller Features Demo")
    print("=" * 50)

    try:
        # Test session creation
        print("Creating chat session...")
        session_result = chat_controller.create_session(user_id='demo_user')
        print(f"   ✅ Session created: {session_result.get('success', False)}")

        # Test question suggestions
        print("\nGetting question suggestions...")
        suggestions = chat_controller.get_question_suggestions('financial')
        print(f"   ✅ Found {suggestions.get('total', 0)} financial questions")

        # Show sample questions
        if suggestions.get('questions'):
            print("   📝 Sample questions:")
            for i, question in enumerate(suggestions['questions'][:3], 1):
                print(f"      {i}. {question['text'][:60]}...")

        print("\n✅ Chat controller demo completed!")

    except Exception as e:
        print(f"❌ Chat controller demo failed: {e}")


def demo_question_test_suite():
    """Demonstrate full question test suite"""
    print("\n🧪 Complete Question Test Suite Demo")
    print("=" * 50)

    try:
        print("Running complete AI chat question test suite...")
        print("This will test all sample questions against database data...")

        # Run the test suite (this would be comprehensive in real scenario)
        # For demo, we'll show what would happen
        test_suite = chat_tester.run_complete_test_suite(['main', 'sqlite'])

        print("
📊 Test Suite Results:"        print(".2f"        print(f"   📝 Total questions: {test_suite.total_questions}")
        print(f"   ✅ Passed: {test_suite.passed_tests}")
        print(f"   ❌ Failed: {test_suite.failed_tests}")
        print(".2f"
        # Show some results
        if test_suite.test_results:
            print("
📝 Sample Test Results:"            for i, result in enumerate(test_suite.test_results[:3], 1):
                status = "✅" if result.ai_processing_success and result.data_found else "❌"
                print(".2f"                if result.actual_response:
                    print(f"         Response: {result.actual_response[:80]}...")

        print("\n✅ Question test suite demo completed!")

    except Exception as e:
        print(f"❌ Question test suite demo failed: {e}")


def demo_comprehensive_system_check():
    """Demonstrate comprehensive system health check"""
    print("\n🔍 Comprehensive System Health Check Demo")
    print("=" * 50)

    try:
        print("Performing comprehensive system health check...")

        # Check database connections
        print("\n🗄️ Database Health Check:")
        try:
            db_health = route_tester.test_database_connectivity()
            if db_health['success']:
                print(".2f"            else:
                print(f"   ❌ Database issues: {db_health.get('error', 'Unknown')}")
        except Exception as e:
            print(f"   ❌ Database check failed: {e}")

        # Check chat functionality
        print("\n💬 Chat Functionality Check:")
        try:
            chat_health = route_tester.test_chat_functionality()
            if chat_health['success']:
                print(f"   ✅ Chat system functional (page load: {chat_health.get('page_load_time', 0):.2f}s)")
            else:
                print(f"   ❌ Chat issues: {chat_health.get('error', 'Unknown')}")
        except Exception as e:
            print(f"   ❌ Chat check failed: {e}")

        # Check API endpoints
        print("\n🔗 API Endpoints Check:")
        try:
            api_results = route_tester.test_api_endpoints_with_data()
            passed_apis = sum(1 for r in api_results if r.is_success)
            print(f"   ✅ API endpoints: {passed_apis}/{len(api_results)} passed")
        except Exception as e:
            print(f"   ❌ API check failed: {e}")

        print("\n✅ Comprehensive system check completed!")

    except Exception as e:
        print(f"❌ Comprehensive system check failed: {e}")


def main():
    """Main demo function"""
    print("🚀 AI Chat Testing System - Comprehensive Demo")
    print("=" * 60)
    print("This demo will showcase all the AI chat testing and monitoring features:")
    print("• AI chat question testing with database integration")
    print("• Route status monitoring and health checks")
    print("• Chat controller functionality")
    print("• Complete question test suites")
    print("• Comprehensive system health monitoring")
    print("=" * 60)

    # Run all demos
    demo_chat_question_testing()
    demo_route_testing()
    demo_chat_controller_features()
    demo_question_test_suite()
    demo_comprehensive_system_check()

    print("\n🎉 All demos completed!")
    print("\n📋 Summary of features demonstrated:")
    print("✅ AI-powered question testing with database context")
    print("✅ Real-time route status monitoring")
    print("✅ Chat session management with safety features")
    print("✅ Comprehensive test reporting (JSON + HTML)")
    print("✅ Database connectivity testing")
    print("✅ System health monitoring")
    print("✅ API endpoint validation")
    print("✅ Performance metrics tracking")

    print("\n🔧 Available API endpoints for testing:")
    print("• POST /api/chat/test-questions - Test all questions")
    print("• GET /api/chat/question-suggestions - Get question suggestions")
    print("• POST /api/routes/test-all - Test all routes")
    print("• POST /api/routes/test-single - Test single route")
    print("• GET /api/routes/status-report - Get comprehensive status report")

    print("\n📊 Test reports are saved to: data/test_reports/")
    print("• JSON reports for programmatic access")
    print("• HTML reports for human-readable results")
    print("• Comprehensive metrics and performance data")


if __name__ == '__main__':
    main()
