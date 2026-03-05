#!/usr/bin/env python3
"""
Sentiment Analysis Demo
======================

Demonstrate the ValidoAI sentiment analysis capabilities.
This script shows how to analyze text sentiment using multiple methods.
"""

import os
import sys
import json
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def demo_sentiment_analysis():
    """Demonstrate sentiment analysis capabilities"""
    print("🧠 Sentiment Analysis Demo")
    print("=" * 50)

    try:
        from src.ai.sentiment import sentiment_analyzer

        print("✅ Sentiment analyzer loaded successfully")

        # Sample texts for analysis
        sample_texts = [
            "This product is absolutely amazing! I love it so much.",
            "The service was terrible and completely unsatisfactory.",
            "The quality is decent, nothing special but it works.",
            "I'm extremely disappointed with this purchase. Waste of money!",
            "Outstanding customer support and excellent product quality.",
            "This is just okay, could be better but I'm not complaining.",
            "Absolutely fantastic! Best purchase I've ever made.",
            "Poor quality and terrible customer service experience.",
            "The features are good but the price is too high.",
            "Neutral experience, neither good nor bad."
        ]

        print("\\n📝 Analyzing sample texts...")
        print("-" * 30)

        # Analyze each text
        for i, text in enumerate(sample_texts, 1):
            print(f"\\nText {i}: '{text}'")
            print("-" * 50)

            # Analyze with different methods
            methods = ['hybrid', 'afinn', 'vader', 'custom']

            for method in methods:
                result = sentiment_analyzer.analyze_text(text, method=method)
                print(f"{method.upper():8}: {result['sentiment']:8} "
                      f"(score: {result['compound']:.3f}, "
                      f"confidence: {result['confidence']:.1%})")

            print()

        print("\\n📊 Batch Analysis Demo")
        print("-" * 30)

        # Batch analysis
        batch_results = sentiment_analyzer.analyze_batch(sample_texts[:5])

        sentiment_counts = {'positive': 0, 'negative': 0, 'neutral': 0}
        for result in batch_results:
            sentiment_counts[result['sentiment']] += 1

        print("Batch analysis of 5 texts:")
        print(f"Positive: {sentiment_counts['positive']}")
        print(f"Negative: {sentiment_counts['negative']}")
        print(f"Neutral:  {sentiment_counts['neutral']}")

        print("\\n🔍 Detailed Analysis with Word Scores")
        print("-" * 40)

        # Detailed analysis with word scores
        detailed_result = sentiment_analyzer.analyze_text(
            "This amazing product exceeded my expectations completely!",
            method='hybrid',
            include_details=True
        )

        print("Text: 'This amazing product exceeded my expectations completely!'")
        print(f"Overall sentiment: {detailed_result['sentiment']} (confidence: {detailed_result['confidence']:.1%})")
        print(f"Compound score: {detailed_result['compound']:.3f}")
        print(f"Positive: {detailed_result['positive']:.1%}")
        print(f"Negative: {detailed_result['negative']:.1%}")
        print(f"Neutral:  {detailed_result['neutral']:.1%}")

        if 'word_scores' in detailed_result and detailed_result['word_scores']:
            print("\\nKey word scores:")
            for word, score in list(detailed_result['word_scores'].items())[:5]:
                print(f"  {word}: {score:.3f}")

        print("\\n📈 Business-Focused Analysis")
        print("-" * 30)

        # Business-focused texts
        business_texts = [
            "The ROI on this investment has been excellent.",
            "Customer satisfaction scores have improved significantly.",
            "Revenue growth is exceeding quarterly targets.",
            "Market share has increased by 15% this quarter.",
            "The new feature set is driving user engagement.",
            "Competitive pricing strategy is working well.",
            "Brand awareness has reached record levels.",
            "Customer retention rates are above industry average."
        ]

        print("Analyzing business-focused texts:")
        positive_business = 0

        for text in business_texts:
            result = sentiment_analyzer.analyze_text(text, method='custom')
            if result['sentiment'] == 'positive':
                positive_business += 1
            print(f"  {result['sentiment'].upper():8}: {text}")

        print(f"\\nBusiness sentiment: {positive_business}/{len(business_texts)} positive")

        print("\\n🔧 System Statistics")
        print("-" * 20)

        # Get system statistics
        stats = sentiment_analyzer.get_statistics()
        print(f"Lexicons loaded: {stats['lexicons_loaded']}")
        print(f"AFINN words: {stats['total_words_afinn']}")
        print(f"VADER words: {stats['total_words_vader']}")
        print(f"Business words: {stats['total_words_custom']}")
        print(f"ML models available: {stats['ml_models_available']}")

        print("\\n🧹 Cache Management")
        print("-" * 20)

        # Test cache operations
        initial_cache = len(sentiment_analyzer.cache)
        print(f"Initial cache size: {initial_cache} items")

        # Clear cache
        clear_result = sentiment_analyzer.clear_cache()
        print(f"Cache cleared: {clear_result['items_cleared']} items")

        print("\\n✅ Sentiment Analysis Demo Completed Successfully!")
        print("\\n🎯 Key Features Demonstrated:")
        print("   • Multiple analysis methods (AFINN, VADER, Custom, Hybrid)")
        print("   • Real-time text sentiment analysis")
        print("   • Batch processing capabilities")
        print("   • Business-focused sentiment lexicon")
        print("   • Confidence scoring and detailed results")
        print("   • Word-level sentiment analysis")
        print("   • Cache management and optimization")
        print("   • System statistics and monitoring")

        print("\\n💡 Business Applications:")
        print("   • Customer feedback analysis")
        print("   • Social media monitoring")
        print("   • Product review analysis")
        print("   • Brand sentiment tracking")
        print("   • Market research automation")
        print("   • Competitive analysis")
        print("   • Customer service optimization")

    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()

def demo_api_simulation():
    """Simulate API calls for sentiment analysis"""
    print("\\n🔌 API Simulation Demo")
    print("=" * 30)

    try:
        from src.ai.sentiment import sentiment_analyzer

        print("📡 Simulating API calls...")

        # Simulate single text analysis
        print("\\n1. Single Text Analysis API")
        test_text = "This is an amazing product with excellent quality!"
        result = sentiment_analyzer.analyze_text(test_text, method='hybrid')

        print(f"   Text: '{test_text}'")
        print(f"   Sentiment: {result['sentiment']}")
        print(f"   Confidence: {result['confidence']:.1%}")
        print(f"   Score: {result['compound']:.3f}")

        # Simulate batch analysis
        print("\\n2. Batch Analysis API")
        batch_texts = [
            "Great product!",
            "Poor service",
            "Average experience"
        ]

        batch_results = sentiment_analyzer.analyze_batch(batch_texts)
        print(f"   Processed {len(batch_results)} texts")

        for i, result in enumerate(batch_results):
            print(f"   Text {i+1}: {result['sentiment']} ({result['compound']:.3f})")

        # Simulate methods info
        print("\\n3. Available Methods API")
        methods = {
            'afinn': {'name': 'AFINN', 'description': 'Lexicon-based analysis'},
            'vader': {'name': 'VADER', 'description': 'Social media focused'},
            'custom': {'name': 'Custom', 'description': 'Business domain'},
            'hybrid': {'name': 'Hybrid', 'description': 'Combined analysis'}
        }

        print("   Available methods:")
        for key, info in methods.items():
            print(f"   • {key}: {info['name']} - {info['description']}")

        # Simulate statistics
        print("\\n4. System Statistics API")
        stats = sentiment_analyzer.get_statistics()
        print(f"   Lexicons: {stats['lexicons_loaded']}")
        print(f"   Total words: {stats['total_words_afinn'] + stats['total_words_vader'] + stats['total_words_custom']}")
        print(f"   Cache size: {stats['cache_size']}")

        print("\\n✅ API Simulation Completed!")

    except Exception as e:
        print(f"❌ API simulation failed: {e}")

def create_sample_data():
    """Create sample sentiment analysis data"""
    print("\\n📊 Creating Sample Data")
    print("=" * 25)

    try:
        from src.ai.sentiment import sentiment_analyzer

        # Sample customer feedback
        customer_feedback = [
            "The customer support was incredibly helpful and resolved my issue quickly.",
            "Delivery was delayed and the packaging was damaged upon arrival.",
            "Excellent product quality and fast shipping. Highly recommend!",
            "The user interface is confusing and not intuitive at all.",
            "Great value for money. The features work exactly as advertised.",
            "Customer service was rude and unprofessional. Very disappointed.",
            "The product exceeded my expectations. Fantastic quality!",
            "Shipping took forever and there was no tracking information.",
            "Easy to use and great customer support. 5 stars!",
            "The item arrived broken. Poor quality control."
        ]

        print("Analyzing customer feedback:")

        analysis_results = []
        for i, feedback in enumerate(customer_feedback, 1):
            result = sentiment_analyzer.analyze_text(feedback, method='hybrid')
            analysis_results.append({
                'text': feedback,
                'sentiment': result['sentiment'],
                'confidence': result['confidence'],
                'score': result['compound']
            })

            print(f"\\n{i}. {result['sentiment'].upper()}: {feedback[:50]}...")
            print(f"   Confidence: {result['confidence']:.1%}, Score: {result['compound']:.3f}")

        # Summary statistics
        sentiment_counts = {'positive': 0, 'negative': 0, 'neutral': 0}
        avg_confidence = 0

        for result in analysis_results:
            sentiment_counts[result['sentiment']] += 1
            avg_confidence += result['confidence']

        avg_confidence /= len(analysis_results)

        print(f"\\n📈 Summary:")
        print(f"   Total reviews: {len(customer_feedback)}")
        print(f"   Positive: {sentiment_counts['positive']}")
        print(f"   Negative: {sentiment_counts['negative']}")
        print(f"   Neutral:  {sentiment_counts['neutral']}")
        print(f"   Average confidence: {avg_confidence:.1%}")

        # Business insights
        positive_ratio = sentiment_counts['positive'] / len(customer_feedback)
        if positive_ratio > 0.6:
            print("   🎉 Strong positive sentiment - good customer satisfaction!")
        elif positive_ratio > 0.4:
            print("   ⚖️  Mixed sentiment - room for improvement")
        else:
            print("   ⚠️  Predominantly negative - action required!")

        return analysis_results

    except Exception as e:
        print(f"❌ Sample data creation failed: {e}")
        return []

if __name__ == "__main__":
    print("🎯 ValidoAI Sentiment Analysis Demo")
    print("===================================")

    # Run demos
    demo_sentiment_analysis()
    demo_api_simulation()
    sample_data = create_sample_data()

    print("\\n🎉 Demo completed! Check the output above for details.")
    print("\\n🌐 To use the Sentiment Analysis System:")
    print("   1. Visit /ai/sentiment-analysis in your browser")
    print("   2. Use the API endpoints for programmatic access")
    print("   3. Integrate with content management for automatic analysis")
    print("   4. Check the analytics dashboard for sentiment insights")

    if sample_data:
        print(f"\\n📊 Processed {len(sample_data)} sample reviews")
        print("   • Use this data for customer feedback analysis")
        print("   • Monitor sentiment trends over time")
        print("   • Identify areas for improvement")
        print("   • Track customer satisfaction metrics")
