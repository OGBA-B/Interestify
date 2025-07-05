import pytest
from datetime import datetime
from src.models.schemas import (
    SearchQuery,
    AnalysisResult,
    Post,
    EngagementStats,
    SentimentType,
)
from src.core.cache import CacheManager


class TestCacheManager:
    """Test cache manager"""

    def setup_method(self):
        self.cache_manager = CacheManager(default_ttl=3600)

    def test_cache_set_and_get(self):
        """Test setting and getting cache entries"""
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

        # Set cache
        self.cache_manager.set(query, result)

        # Get cache
        cached_result = self.cache_manager.get(query)
        assert cached_result is not None
        assert cached_result.query == "test"
        assert cached_result.total_posts == 1

    def test_cache_miss(self):
        """Test cache miss"""
        query = SearchQuery(query="nonexistent", limit=10)
        result = self.cache_manager.get(query)
        assert result is None

    def test_cache_key_generation(self):
        """Test cache key generation consistency"""
        query1 = SearchQuery(query="test", limit=10, data_sources=["twitter"])
        query2 = SearchQuery(query="test", limit=10, data_sources=["twitter"])

        key1 = self.cache_manager._generate_key(query1)
        key2 = self.cache_manager._generate_key(query2)

        assert key1 == key2

    def test_cache_key_different_queries(self):
        """Test different queries generate different keys"""
        query1 = SearchQuery(query="test1", limit=10)
        query2 = SearchQuery(query="test2", limit=10)

        key1 = self.cache_manager._generate_key(query1)
        key2 = self.cache_manager._generate_key(query2)

        assert key1 != key2

    def test_cache_invalidation(self):
        """Test cache invalidation"""
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

        # Set cache
        self.cache_manager.set(query, result)

        # Verify cached
        cached_result = self.cache_manager.get(query)
        assert cached_result is not None

        # Invalidate
        success = self.cache_manager.invalidate(query)
        assert success

        # Verify not cached
        cached_result = self.cache_manager.get(query)
        assert cached_result is None

    def test_cache_clear_all(self):
        """Test clearing all cache entries"""
        query1 = SearchQuery(query="test1", limit=10)
        query2 = SearchQuery(query="test2", limit=10)

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

        # Set multiple cache entries
        self.cache_manager.set(query1, result)
        self.cache_manager.set(query2, result)

        # Clear all
        cleared = self.cache_manager.clear_all()
        assert cleared == 2

        # Verify all cleared
        assert self.cache_manager.get(query1) is None
        assert self.cache_manager.get(query2) is None

    def test_cache_stats(self):
        """Test cache statistics"""
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

        # Set cache
        self.cache_manager.set(query, result)

        # Get stats
        stats = self.cache_manager.get_stats()
        assert stats["total_entries"] == 1
        assert stats["active_entries"] == 1
        assert stats["expired_entries"] == 0
        assert stats["total_hits"] == 0

        # Access cache to increment hit count
        self.cache_manager.get(query)

        stats = self.cache_manager.get_stats()
        assert stats["total_hits"] == 1

    def test_cache_hit_count(self):
        """Test cache hit count tracking"""
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

        # Set cache
        self.cache_manager.set(query, result)

        # Access multiple times
        for i in range(5):
            self.cache_manager.get(query)

        stats = self.cache_manager.get_stats()
        assert stats["total_hits"] == 5

    def test_cache_expiry(self):
        """Test cache expiry (simulated)"""
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

        # Set cache with very short TTL
        self.cache_manager.set(query, result, ttl=0.1)

        # Should be available immediately
        cached_result = self.cache_manager.get(query)
        assert cached_result is not None

        # Wait for expiry (simulate by directly manipulating expires_at)
        import time

        time.sleep(0.2)

        # Should be expired and removed
        cached_result = self.cache_manager.get(query)
        assert cached_result is None

    def test_clear_expired_entries(self):
        """Test clearing expired entries"""
        query1 = SearchQuery(query="test1", limit=10)
        query2 = SearchQuery(query="test2", limit=10)

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

        # Set one with short TTL, one with long TTL
        self.cache_manager.set(query1, result, ttl=0.1)
        self.cache_manager.set(query2, result, ttl=3600)

        # Wait for first to expire
        import time

        time.sleep(0.2)

        # Clear expired
        cleared = self.cache_manager.clear_expired()
        assert cleared == 1

        # Verify correct one was cleared
        assert self.cache_manager.get(query1) is None
        assert self.cache_manager.get(query2) is not None


if __name__ == "__main__":
    pytest.main([__file__])
