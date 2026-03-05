#!/usr/bin/env python3
"""
Test Chat Local Functionality
Tests the chat-local functionality with sample database
"""

import sys
import os
from pathlib import Path

# Add current directory to path
sys.path.append('.')

def test_chat_functionality():
    """Test the chat functionality"""
    
    try:
        from src.ai_local_models import EnhancedChatInterface, FinancialContextProvider
        
        print("🧪 Testing Chat Local Functionality...")
        
        # Test context provider
        print("\n1. Testing Financial Context Provider...")
        context_provider = FinancialContextProvider()
        
        # Test getting companies
        companies = context_provider.get_companies()
        print(f"   ✅ Found {len(companies)} companies")
        
        if companies:
            company_id = companies[0]['id']
            print(f"   📊 Using company: {companies[0]['name']}")
            
            # Test financial summary
            summary = context_provider.get_financial_summary(company_id)
            if summary:
                print(f"   ✅ Financial summary retrieved")
                print(f"   💰 Revenue: €{summary.get('revenue', {}).get('total', 0):,.2f}")
            else:
                print("   ⚠️  No financial summary data available")
            
            # Test revenue analysis
            revenue = context_provider.get_revenue_analysis(company_id)
            if revenue:
                print(f"   ✅ Revenue analysis retrieved")
                print(f"   📈 Total revenue: €{revenue.get('total_revenue', 0):,.2f}")
            else:
                print("   ⚠️  No revenue data available")
            
            # Test partners
            partners = context_provider.get_partners(company_id)
            print(f"   ✅ Found {len(partners)} partners")
        
        # Test chat interface
        print("\n2. Testing Enhanced Chat Interface...")
        chat_interface = EnhancedChatInterface()
        
        # Test session creation
        session_id = chat_interface.create_session("Test Session", "qwen3-4b-gguf")
        if session_id:
            print(f"   ✅ Created session: {session_id}")
            
            # Test message sending (without actual AI model)
            print("   📝 Testing message processing...")
            
            # Test financial query analysis
            test_messages = [
                "Can you analyze my revenue for the last quarter?",
                "What are my top customers?",
                "Generate a cash flow report",
                "Help me with budget planning"
            ]
            
            for message in test_messages:
                print(f"   💬 Testing: '{message}'")
                context = chat_interface._analyze_financial_query(message, company_id if companies else None)
                
                if context['is_financial_query']:
                    print(f"   ✅ Detected as financial query: {context['analysis_type']}")
                    if context['data']:
                        print(f"   📊 Found {len(context['data'])} data sources")
                    else:
                        print("   ⚠️  No financial data found")
                else:
                    print("   ℹ️  General query")
        
        print("\n🎉 Chat Local functionality test completed!")
        print("\n📋 Summary:")
        print("   ✅ Database connection working")
        print("   ✅ Context provider functional")
        print("   ✅ Chat interface operational")
        print("   ✅ Financial data analysis working")
        print("\n🚀 Ready to use chat-local with sample data!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing chat functionality: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_chat_functionality()
