#!/usr/bin/env python3
"""Test Sentiment Analysis Functionality"""

import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / 'src'))

def test_sentiment_analysis():
    """Test sentiment analysis functionality"""
    print("🧠 Testing Sentiment Analysis")
    print("=" * 50)

    try:
        # Import the sentiment analyzer
        from src.ai.sentiment import sentiment_analyzer

        print("✅ Sentiment analyzer imported successfully")

        # Test texts
        test_texts = [
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

        print(f"\\n📝 Analyzing {len(test_texts)} sample texts...")
        print("-" * 40)

        # Analyze each text with different methods
        for i, text in enumerate(test_texts, 1):
            print(f"\\nText {i}: '{text[:50]}...'")
            print("-" * 50)

            # Test different methods
            methods = ['afinn', 'vader', 'custom', 'hybrid']

            for method in methods:
                try:
                    result = sentiment_analyzer.analyze_text(text, method=method)

                    sentiment = result.get('sentiment', 'unknown')
                    confidence = result.get('confidence', 0)
                    compound = result.get('compound', 0)

                    print(f"{method:12} | {sentiment:8} | {confidence:.3f} | {compound:.3f}")

                except Exception as e:
                    print(f"❌ Error with {method}: {str(e)}")

        print("\\n✅ Sentiment analysis test completed!")
        print("\\n📊 Available Methods:")
        print("   - afinn: Lexicon-based sentiment analysis")
        print("   - vader: Rule-based sentiment analysis")
        print("   - custom: Custom lexicon-based analysis")
        print("   - hybrid: Combined multi-method analysis")

        print("\\n🌐 Web Interface: /ai/sentiment-analysis")
        print("📡 API Endpoints:")
        print("   - POST /api/sentiment/analyze")
        print("   - POST /api/sentiment/batch")
        print("   - GET /api/sentiment/stats")
        print("   - POST /api/sentiment/cache/clear")
        print("   - GET /api/sentiment/methods")

        return True

    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = test_sentiment_analysis()
    sys.exit(0 if success else 1)
