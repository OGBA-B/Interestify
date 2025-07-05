import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime
import time
from src.models.schemas import SearchQuery, AnalysisResult, SentimentType
from src.core.sentiment import SentimentAnalyzerFactory
from src.core.datasources import DataSourceManager
from src.core.cache import CacheManager


class TestIntegration:
    """Integration tests for the entire system"""

    @pytest.fixture
    def mock_data_source_manager(self):
        """Create mock data source manager"""
        manager = Mock(spec=DataSourceManager)
        manager.get_enabled_sources.return_value = []
        manager.get_configured_sources.return_value = []
        manager.get_data_source.return_value = None
        return manager

    @pytest.fixture
    def cache_manager(self):
        """Create cache manager for testing"""
        return CacheManager(default_ttl=3600)

    def test_sentiment_analyzer_factory_integration(self):
        """Test sentiment analyzer factory with different analyzers"""
        # Test TextBlob analyzer
        textblob_analyzer = SentimentAnalyzerFactory.create_analyzer("textblob")
        assert textblob_analyzer.get_name() == "TextBlob"

        # Test VADER analyzer
        vader_analyzer = SentimentAnalyzerFactory.create_analyzer("vader")
        assert vader_analyzer.get_name() == "VADER"

        # Test both analyzers on same text
        text = "I love this product! It's amazing!"

        textblob_result = textblob_analyzer.analyze(text)
        vader_result = vader_analyzer.analyze(text)

        # Both should detect positive sentiment
        assert textblob_result["sentiment"] == SentimentType.POSITIVE
        assert vader_result["sentiment"] == SentimentType.POSITIVE

        # Both should have reasonable confidence
        assert textblob_result["confidence"] > 0.5
        assert vader_result["confidence"] > 0.5

    def test_cache_and_sentiment_integration(self, cache_manager):
        """Test cache integration with sentiment analysis"""
        query = SearchQuery(query="test", limit=10)

        # Create mock analysis result
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
            processing_time=1.5,
        )

        # Cache the result
        cache_manager.set(query, result)

        # Retrieve from cache
        cached_result = cache_manager.get(query)

        assert cached_result is not None
        assert cached_result.query == "test"
        assert cached_result.total_posts == 5
        assert cached_result.sentiment_distribution[SentimentType.POSITIVE] == 3
        assert cached_result.average_confidence == 0.8

    def test_multiple_analyzers_same_text(self):
        """Test multiple analyzers on the same text"""
        texts = [
            "I love this product! It's absolutely amazing!",
            "This is terrible! I hate everything about it!",
            "The weather is okay today. Nothing special.",
            "This product is good but could be better.",
            "Absolutely fantastic! Best purchase ever!",
        ]

        textblob_analyzer = SentimentAnalyzerFactory.create_analyzer("textblob")
        vader_analyzer = SentimentAnalyzerFactory.create_analyzer("vader")

        for text in texts:
            textblob_result = textblob_analyzer.analyze(text)
            vader_result = vader_analyzer.analyze(text)

            # Results should be structured correctly
            assert "sentiment" in textblob_result
            assert "confidence" in textblob_result
            assert "polarity" in textblob_result
            assert "subjectivity" in textblob_result

            assert "sentiment" in vader_result
            assert "confidence" in vader_result
            assert "polarity" in vader_result
            assert "subjectivity" in vader_result

            # Confidence should be reasonable
            assert 0 <= textblob_result["confidence"] <= 1
            assert 0 <= vader_result["confidence"] <= 1

            # Polarity should be in range
            assert -1 <= textblob_result["polarity"] <= 1
            assert -1 <= vader_result["polarity"] <= 1

    def test_query_variation_cache_keys(self, cache_manager):
        """Test that different queries generate different cache keys"""
        queries = [
            SearchQuery(query="test", limit=10),
            SearchQuery(query="test", limit=20),
            SearchQuery(query="different", limit=10),
            SearchQuery(query="test", limit=10, data_sources=["twitter"]),
            SearchQuery(query="test", limit=10, include_sentiment=False),
        ]

        keys = []
        for query in queries:
            key = cache_manager._generate_key(query)
            keys.append(key)

        # All keys should be different
        assert len(set(keys)) == len(keys)

    def test_cache_expiry_simulation(self, cache_manager):
        """Test cache expiry behavior"""
        query = SearchQuery(query="test", limit=10)

        result = AnalysisResult(
            query="test",
            total_posts=1,
            sentiment_distribution={
                SentimentType.POSITIVE: 1,
                SentimentType.NEGATIVE: 0,
                SentimentType.NEUTRAL: 0,
            },
            average_confidence=0.8,
            sources_used=["test"],
            posts=[],
            sentiment_results=[],
            created_at=datetime.now(),
            processing_time=0.5,
        )

        # Set cache with short TTL
        cache_manager.set(query, result, ttl=1)

        # Should be available immediately
        cached_result = cache_manager.get(query)
        assert cached_result is not None

        # Wait for expiry
        time.sleep(1.1)

        # Should be expired
        cached_result = cache_manager.get(query)
        assert cached_result is None

    def test_batch_sentiment_analysis(self):
        """Test batch sentiment analysis"""
        texts = [
            "I love this!",
            "This is terrible!",
            "It's okay.",
            "Amazing product!",
            "Worst experience ever!",
            "Average quality.",
            "Excellent service!",
            "Poor quality control.",
            "Good value for money.",
            "Completely satisfied!",
        ]

        analyzer = SentimentAnalyzerFactory.create_analyzer("textblob")
        results = analyzer.analyze_batch(texts)

        assert len(results) == len(texts)

        # Check that all results have required fields
        for result in results:
            assert "sentiment" in result
            assert "confidence" in result
            assert "polarity" in result
            assert "subjectivity" in result

            # Validate ranges
            assert result["sentiment"] in [
                SentimentType.POSITIVE,
                SentimentType.NEGATIVE,
                SentimentType.NEUTRAL,
            ]
            assert 0 <= result["confidence"] <= 1
            assert -1 <= result["polarity"] <= 1
            assert 0 <= result["subjectivity"] <= 1

    def test_cache_statistics_tracking(self, cache_manager):
        """Test cache statistics tracking"""
        query = SearchQuery(query="test", limit=10)

        result = AnalysisResult(
            query="test",
            total_posts=1,
            sentiment_distribution={
                SentimentType.POSITIVE: 1,
                SentimentType.NEGATIVE: 0,
                SentimentType.NEUTRAL: 0,
            },
            average_confidence=0.8,
            sources_used=["test"],
            posts=[],
            sentiment_results=[],
            created_at=datetime.now(),
            processing_time=0.5,
        )

        # Initial stats
        stats = cache_manager.get_stats()
        initial_entries = stats["total_entries"]
        initial_hits = stats["total_hits"]

        # Add cache entry
        cache_manager.set(query, result)

        # Check stats after adding
        stats = cache_manager.get_stats()
        assert stats["total_entries"] == initial_entries + 1
        assert stats["total_hits"] == initial_hits

        # Access cache multiple times
        for _ in range(3):
            cache_manager.get(query)

        # Check stats after accessing
        stats = cache_manager.get_stats()
        assert stats["total_hits"] == initial_hits + 3

    def test_error_handling_in_sentiment_analysis(self):
        """Test error handling in sentiment analysis"""
        analyzer = SentimentAnalyzerFactory.create_analyzer("textblob")

        # Test with problematic texts
        problematic_texts = [
            "",  # Empty string
            "   ",  # Only whitespace
            "\x00\x01\x02",  # Control characters
            "A" * 10000,  # Very long text
            "🎉🎊🎈🎁🎀",  # Only emojis
        ]

        for text in problematic_texts:
            try:
                result = analyzer.analyze(text)
                # Should not raise exception
                assert "sentiment" in result
                assert "confidence" in result
                assert "polarity" in result
                assert "subjectivity" in result
            except Exception as e:
                # If exception occurs, it should be handled gracefully
                pytest.fail(
                    f"Sentiment analysis failed for text: {repr(text)}, error: {e}"
                )

    def test_cache_memory_efficiency(self, cache_manager):
        """Test cache memory efficiency"""
        # Create many cache entries
        for i in range(100):
            query = SearchQuery(query=f"test{i}", limit=10)
            result = AnalysisResult(
                query=f"test{i}",
                total_posts=1,
                sentiment_distribution={
                    SentimentType.POSITIVE: 1,
                    SentimentType.NEGATIVE: 0,
                    SentimentType.NEUTRAL: 0,
                },
                average_confidence=0.8,
                sources_used=["test"],
                posts=[],
                sentiment_results=[],
                created_at=datetime.now(),
                processing_time=0.5,
            )
            cache_manager.set(query, result)

        # Get stats
        stats = cache_manager.get_stats()

        assert stats["total_entries"] == 100
        assert stats["memory_usage_mb"] > 0

        # Clear cache
        cleared = cache_manager.clear_all()
        assert cleared == 100

        # Check stats after clearing
        stats = cache_manager.get_stats()
        assert stats["total_entries"] == 0


class TestPerformance:
    """Performance tests"""

    @pytest.fixture
    def cache_manager(self):
        """Create cache manager for testing"""
        return CacheManager(default_ttl=3600)

    def test_sentiment_analysis_performance(self):
        """Test sentiment analysis performance"""
        analyzer = SentimentAnalyzerFactory.create_analyzer("textblob")

        # Test with 100 texts
        texts = [f"This is test text number {i}" for i in range(100)]

        start_time = time.time()
        results = analyzer.analyze_batch(texts)
        end_time = time.time()

        processing_time = end_time - start_time

        # Should complete within reasonable time (less than 10 seconds)
        assert processing_time < 10.0
        assert len(results) == 100

        # Calculate average time per text
        avg_time = processing_time / len(texts)
        assert avg_time < 0.1  # Less than 100ms per text

    def test_cache_performance(self, cache_manager):
        """Test cache performance"""
        # Create test data
        queries = []
        results = []

        for i in range(1000):
            query = SearchQuery(query=f"test{i}", limit=10)
            result = AnalysisResult(
                query=f"test{i}",
                total_posts=1,
                sentiment_distribution={
                    SentimentType.POSITIVE: 1,
                    SentimentType.NEGATIVE: 0,
                    SentimentType.NEUTRAL: 0,
                },
                average_confidence=0.8,
                sources_used=["test"],
                posts=[],
                sentiment_results=[],
                created_at=datetime.now(),
                processing_time=0.5,
            )
            queries.append(query)
            results.append(result)

        # Test cache setting performance
        start_time = time.time()
        for query, result in zip(queries, results):
            cache_manager.set(query, result)
        set_time = time.time() - start_time

        # Test cache getting performance
        start_time = time.time()
        for query in queries:
            cache_manager.get(query)
        get_time = time.time() - start_time

        # Should be reasonably fast
        assert set_time < 5.0  # Less than 5 seconds to set 1000 entries
        assert get_time < 1.0  # Less than 1 second to get 1000 entries

        # Calculate per-operation time
        avg_set_time = set_time / len(queries)
        avg_get_time = get_time / len(queries)

        assert avg_set_time < 0.01  # Less than 10ms per set operation
        assert avg_get_time < 0.001  # Less than 1ms per get operation


if __name__ == "__main__":
    pytest.main([__file__])
