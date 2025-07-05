from datetime import datetime
from unittest.mock import Mock, patch

import pytest
from fastapi.testclient import TestClient

from src.main import app
from src.models.schemas import (
    AnalysisResult,
    EngagementStats,
    Post,
    SearchQuery,
    SentimentType,
)


class TestAPI:
    """Test FastAPI endpoints"""

    def setup_method(self):
        self.client = TestClient(app)

    def test_health_check(self):
        """Test health check endpoint"""
        response = self.client.get("/health")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert data["version"] == "2.0.0"

    def test_get_analyzers(self):
        """Test getting available analyzers"""
        response = self.client.get("/api/v1/analyzers")
        assert response.status_code == 200

        data = response.json()
        assert "textblob" in data
        assert "vader" in data

    def test_analyze_text(self):
        """Test text analysis endpoint"""
        response = self.client.post(
            "/api/v1/analyze-text",
            params={"text": "I love this product!", "analyzer_name": "textblob"},
        )
        assert response.status_code == 200

        data = response.json()
        assert "sentiment" in data
        assert "confidence" in data
        assert "polarity" in data
        assert "subjectivity" in data

    def test_analyze_text_invalid_analyzer(self):
        """Test text analysis with invalid analyzer"""
        response = self.client.post(
            "/api/v1/analyze-text",
            params={"text": "I love this product!", "analyzer_name": "invalid"},
        )
        assert response.status_code == 500

    def test_get_cache_stats(self):
        """Test cache statistics endpoint"""
        response = self.client.get("/api/v1/cache/stats")
        assert response.status_code == 200

        data = response.json()
        assert "total_entries" in data
        assert "active_entries" in data
        assert "expired_entries" in data
        assert "total_hits" in data
        assert "memory_usage_mb" in data

    def test_clear_cache(self):
        """Test cache clearing endpoint"""
        response = self.client.delete("/api/v1/cache/clear")
        assert response.status_code == 200

        data = response.json()
        assert "message" in data
        assert "cleared" in data["message"].lower()

    def test_clear_expired_cache(self):
        """Test clearing expired cache entries"""
        response = self.client.delete("/api/v1/cache/expired")
        assert response.status_code == 200

        data = response.json()
        assert "message" in data
        assert "cleared" in data["message"].lower()

    @patch("src.core.datasources.data_source_manager.get_enabled_sources")
    def test_analyze_posts_no_sources(self, mock_get_sources):
        """Test analysis with no available sources"""
        mock_get_sources.return_value = []

        query_data = {
            "query": "test",
            "limit": 10,
            "offset": 0,
            "include_sentiment": True,
            "min_confidence": 0.5,
        }

        response = self.client.post("/api/v1/analyze", json=query_data)
        assert response.status_code == 503
        assert "No data sources available" in response.json()["detail"]

    def test_legacy_search_endpoint(self):
        """Test legacy search endpoint"""
        with patch(
            "src.core.datasources.data_source_manager.get_enabled_sources"
        ) as mock_sources:
            mock_sources.return_value = []

            response = self.client.get("/search/test")
            assert response.status_code == 503  # No sources available

    def test_legacy_followers_endpoint(self):
        """Test legacy followers endpoint (deprecated)"""
        response = self.client.get("/followers/testuser")
        assert response.status_code == 410  # Gone
        assert "deprecated" in response.json()["detail"].lower()

    def test_get_user_posts_invalid_source(self):
        """Test getting user posts with invalid source"""
        response = self.client.get(
            "/api/v1/users/testuser/posts", params={"source": "invalid"}
        )
        assert response.status_code == 404
        assert "Data source 'invalid' not found" in response.json()["detail"]

    def test_get_data_sources_empty(self):
        """Test getting data sources when none configured"""
        response = self.client.get("/api/v1/datasources")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)

    def test_add_data_source_invalid(self):
        """Test adding invalid data source"""
        config_data = {"name": "invalid_source", "enabled": True, "rate_limit": 100}

        response = self.client.post("/api/v1/datasources", json=config_data)
        assert response.status_code == 400
        assert "Failed to add data source" in response.json()["detail"]

    def test_update_nonexistent_data_source(self):
        """Test updating non-existent data source"""
        config_data = {"name": "nonexistent", "enabled": True, "rate_limit": 100}

        response = self.client.put("/api/v1/datasources/nonexistent", json=config_data)
        assert response.status_code == 404
        assert "Data source not found" in response.json()["detail"]

    def test_remove_nonexistent_data_source(self):
        """Test removing non-existent data source"""
        response = self.client.delete("/api/v1/datasources/nonexistent")
        assert response.status_code == 404
        assert "Data source not found" in response.json()["detail"]


class TestModels:
    """Test data models"""

    def test_post_model(self):
        """Test Post model validation"""
        post_data = {
            "id": "1",
            "text": "Test post",
            "timestamp": datetime.now(),
            "author": "testuser",
            "author_id": "testuser",
            "engagement_stats": {
                "likes": 10,
                "shares": 5,
                "comments": 2,
                "views": 100,
                "replies": 1,
            },
            "source": "test",
            "confidence_score": 0.8,
            "language": "en",
            "hashtags": ["#test"],
            "mentions": ["@user"],
            "urls": ["https://example.com"],
        }

        post = Post(**post_data)
        assert post.id == "1"
        assert post.text == "Test post"
        assert post.author == "testuser"
        assert post.engagement_stats.likes == 10
        assert post.confidence_score == 0.8

    def test_post_model_invalid_confidence(self):
        """Test Post model with invalid confidence score"""
        post_data = {
            "id": "1",
            "text": "Test post",
            "timestamp": datetime.now(),
            "author": "testuser",
            "author_id": "testuser",
            "engagement_stats": {
                "likes": 10,
                "shares": 5,
                "comments": 2,
                "views": 100,
                "replies": 1,
            },
            "source": "test",
            "confidence_score": 1.5,  # Invalid - should be 0-1
        }

        with pytest.raises(ValueError):
            Post(**post_data)

    def test_search_query_model(self):
        """Test SearchQuery model validation"""
        query_data = {
            "query": "test",
            "limit": 50,
            "offset": 0,
            "include_sentiment": True,
            "min_confidence": 0.5,
        }

        query = SearchQuery(**query_data)
        assert query.query == "test"
        assert query.limit == 50
        assert query.include_sentiment is True
        assert query.min_confidence == 0.5

    def test_search_query_model_invalid_limit(self):
        """Test SearchQuery model with invalid limit"""
        query_data = {
            "query": "test",
            "limit": 0,  # Invalid - should be >= 1
            "offset": 0,
            "include_sentiment": True,
            "min_confidence": 0.5,
        }

        with pytest.raises(ValueError):
            SearchQuery(**query_data)

    def test_analysis_result_model(self):
        """Test AnalysisResult model"""
        result_data = {
            "query": "test",
            "total_posts": 10,
            "sentiment_distribution": {
                SentimentType.POSITIVE: 5,
                SentimentType.NEGATIVE: 2,
                SentimentType.NEUTRAL: 3,
            },
            "average_confidence": 0.7,
            "sources_used": ["twitter", "reddit"],
            "posts": [],
            "sentiment_results": [],
            "created_at": datetime.now(),
            "processing_time": 1.5,
        }

        result = AnalysisResult(**result_data)
        assert result.query == "test"
        assert result.total_posts == 10
        assert result.sentiment_distribution[SentimentType.POSITIVE] == 5
        assert result.average_confidence == 0.7
        assert result.processing_time == 1.5


class TestUtilityFunctions:
    """Test utility functions"""

    def test_paginate_results(self):
        """Test pagination utility"""
        from src.utils.pagination import paginate_results

        items = list(range(100))

        # First page
        page1 = paginate_results(items, offset=0, limit=10)
        assert len(page1) == 10
        assert page1 == list(range(10))

        # Second page
        page2 = paginate_results(items, offset=10, limit=10)
        assert len(page2) == 10
        assert page2 == list(range(10, 20))

        # Last page (partial)
        last_page = paginate_results(items, offset=90, limit=20)
        assert len(last_page) == 10
        assert last_page == list(range(90, 100))

    def test_paginate_results_invalid_params(self):
        """Test pagination with invalid parameters"""
        from src.utils.pagination import paginate_results

        items = list(range(100))

        # Negative offset
        result = paginate_results(items, offset=-10, limit=10)
        assert len(result) == 10
        assert result == list(range(10))

        # Zero limit
        result = paginate_results(items, offset=0, limit=0)
        assert len(result) == 50  # Default limit
        assert result == list(range(50))

        # Offset beyond items
        result = paginate_results(items, offset=200, limit=10)
        assert len(result) == 0

    def test_create_paginated_response(self):
        """Test creating paginated response"""
        from src.utils.pagination import create_paginated_response

        items = list(range(10))
        total_items = 100

        response = create_paginated_response(
            items, offset=20, limit=10, total_items=total_items
        )

        assert response.total == 100
        assert response.page == 3  # (20 // 10) + 1
        assert response.page_size == 10
        assert response.total_pages == 10  # (100 + 10 - 1) // 10
        assert response.has_next is True
        assert response.has_previous is True
        assert len(response.items) == 10


if __name__ == "__main__":
    pytest.main([__file__])
