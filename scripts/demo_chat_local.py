#!/usr/bin/env python3
"""
Chat Local Demo
Demonstrates the chat-local functionality with sample financial data
"""

import sys
sys.path.append('.')

def demo_chat_local():
    """Demonstrate chat-local functionality"""
    
    try:
        from src.ai_local_models import EnhancedChatInterface, FinancialContextProvider
        
        print("🎯 Chat Local Demo - Financial Analysis with AI")
        print("=" * 60)
        
        # Initialize components
        chat_interface = EnhancedChatInterface()
        context_provider = FinancialContextProvider()
        
        # Get sample company
        companies = context_provider.get_companies()
        if not companies:
            print("❌ No companies found in database")
            return
        
        company = companies[0]
        company_id = company['id']
        print(f"📊 Using company: {company['name']}")
        print()
        
        # Demo questions and responses
        demo_questions = [
            "Can you analyze my revenue for the last quarter?",
            "What are my top customers?",
            "Generate a cash flow report",
            "Help me with budget planning",
            "Show me my financial summary"
        ]
        
        for i, question in enumerate(demo_questions, 1):
            print(f"💬 Question {i}: {question}")
            print("-" * 40)
            
            # Analyze the question
            context = chat_interface._analyze_financial_query(question, company_id)
            
            if context['is_financial_query']:
                print(f"🔍 Detected: {context['analysis_type']} analysis")
                
                # Get relevant data
                if context['data']:
                    if 'summary' in context['data']:
                        summary = context['data']['summary']
                        if 'revenue' in summary:
                            revenue = summary['revenue']
                            print(f"💰 Revenue: €{revenue.get('total', 0):,.2f}")
                            print(f"📄 Invoices: {revenue.get('invoice_count', 0)}")
                    
                    if 'partners' in context['data']:
                        partners = context['data']['partners']
                        print(f"👥 Partners: {len(partners)} found")
                        if partners:
                            top_partner = partners[0]
                            print(f"   Top: {top_partner.get('name', 'N/A')} - €{top_partner.get('total_amount', 0):,.2f}")
                
                # Generate response
                response = chat_interface.generateEnhancedResponse(question)
                print(f"🤖 AI Response: {response[:200]}...")
            else:
                print("ℹ️  General query")
                response = "I can help you with financial analysis, reporting, and business insights. What specific aspect would you like to explore?"
                print(f"🤖 AI Response: {response}")
            
            print()
        
        print("🎉 Demo completed!")
        print("\n📋 Key Features Demonstrated:")
        print("   ✅ Financial data analysis")
        print("   ✅ Revenue and partner analysis")
        print("   ✅ Cash flow and budget planning")
        print("   ✅ Context-aware AI responses")
        print("   ✅ Sample data integration")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in demo: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    demo_chat_local()
