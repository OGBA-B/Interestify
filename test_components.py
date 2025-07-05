#!/usr/bin/env python3
"""
Simple test script to verify the Interestify v2 implementation
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, "/workspaces/Interestify")


def test_sentiment_analysis():
    """Test sentiment analysis functionality"""
    print("🧪 Testing Sentiment Analysis...")

    try:
        # Test VADER analyzer
        from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

        vader = SentimentIntensityAnalyzer()
        result = vader.polarity_scores("I love this product!")
        print(f"✅ VADER Direct Test: {result}")

        # Test our VADER wrapper
        from src.core.sentiment import SentimentAnalyzerFactory

        analyzer = SentimentAnalyzerFactory.create_analyzer("vader")
        result = analyzer.analyze("I love this product!")
        print(f"✅ VADER Wrapper Test: {result}")

        # Test TextBlob (might fail without NLTK data)
        try:
            analyzer = SentimentAnalyzerFactory.create_analyzer("textblob")
            result = analyzer.analyze("I love this product!")
            print(f"✅ TextBlob Test: {result}")
        except Exception as e:
            print(f"⚠️  TextBlob Test Failed (expected, needs NLTK data): {e}")

        print("✅ Sentiment Analysis Tests Passed!")
        return True

    except Exception as e:
        print(f"❌ Sentiment Analysis Test Failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_cache_system():
    """Test cache system"""
    print("\n🧪 Testing Cache System...")

    try:
        from src.core.cache import cache_manager
        from src.models.schemas import SearchQuery, AnalysisResult, SentimentType
        from datetime import datetime

        # Create test query
        query = SearchQuery(query="test", limit=10)

        # Create test result
        result = AnalysisResult(
            query="test",
            total_posts=5,
            sentiment_distribution={
                SentimentType.POSITIVE: 3,
                SentimentType.NEGATIVE: 1,
                SentimentType.NEUTRAL: 1,
            },
            average_confidence=0.8,
            sources_used=["test"],
            posts=[],
            sentiment_results=[],
            created_at=datetime.now(),
            processing_time=1.0,
        )

        # Test cache set/get
        cache_manager.set(query, result)
        cached_result = cache_manager.get(query)

        if cached_result and cached_result.query == "test":
            print("✅ Cache System Test Passed!")
            return True
        else:
            print("❌ Cache System Test Failed: Retrieved result doesn't match")
            return False

    except Exception as e:
        print(f"❌ Cache System Test Failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_data_source_manager():
    """Test data source manager"""
    print("\n🧪 Testing Data Source Manager...")

    try:
        from src.core.datasources import data_source_manager
        from src.models.schemas import DataSourceConfig

        # Test getting available source types
        available_types = data_source_manager.get_available_source_types()
        print(f"Available source types: {available_types}")

        if "twitter" in available_types and "reddit" in available_types:
            print("✅ Data Source Manager Test Passed!")
            return True
        else:
            print("❌ Data Source Manager Test Failed: Missing expected source types")
            return False

    except Exception as e:
        print(f"❌ Data Source Manager Test Failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_models():
    """Test data models"""
    print("\n🧪 Testing Data Models...")

    try:
        from src.models.schemas import Post, EngagementStats, SearchQuery
        from datetime import datetime

        # Test creating a post
        post = Post(
            id="test123",
            text="This is a test post",
            timestamp=datetime.now(),
            author="testuser",
            author_id="testuser123",
            engagement_stats=EngagementStats(likes=10, shares=5, comments=2),
            source="test",
            confidence_score=0.9,
        )

        # Test creating a search query
        query = SearchQuery(query="machine learning", limit=50, include_sentiment=True)

        print(f"✅ Created Post: {post.id} by {post.author}")
        print(f"✅ Created Query: '{query.query}' (limit: {query.limit})")
        print("✅ Data Models Test Passed!")
        return True

    except Exception as e:
        print(f"❌ Data Models Test Failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("🚀 Starting Interestify v2 Component Tests\n")

    tests = [
        test_models,
        test_sentiment_analysis,
        test_cache_system,
        test_data_source_manager,
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        if test():
            passed += 1
        print("-" * 50)

    print(f"\n📊 Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! Interestify v2 core components are working!")
        return True
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
