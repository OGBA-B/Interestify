import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock, Mock
from src.main import app


class TestMainApplication:
    """Test main FastAPI application endpoints"""

    def setup_method(self):
        self.client = TestClient(app)

    def test_health_endpoint(self):
        """Test health check endpoint"""
        response = self.client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "version" in data

    def test_nonexistent_endpoint(self):
        """Test that nonexistent endpoints return 404"""
        response = self.client.get("/api/v1/nonexistent")
        assert response.status_code == 404

    def test_cors_preflight(self):
        """Test CORS preflight request"""
        response = self.client.options(
            "/health",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
            }
        )
        # Should not return 405 for OPTIONS
        assert response.status_code in [200, 204]

    @patch("src.main.data_source_service")
    def test_datasources_list_endpoint(self, mock_data_source_service):
        """Test listing data sources"""
        mock_data_source_service.get_all_sources.return_value = [
            {
                "name": "twitter",
                "enabled": True,
                "available": True,
                "rate_limit": 100,
                "rate_limit_info": {"remaining": 90, "reset_time": "2023-01-01T00:00:00Z"}
            }
        ]
        
        response = self.client.get("/api/v1/datasources")
        assert response.status_code == 200
        sources = response.json()
        assert len(sources) == 1
        assert sources[0]["name"] == "twitter"

    @patch("src.main.cache_service")
    def test_cache_stats_endpoint(self, mock_cache_service):
        """Test cache statistics endpoint"""
        mock_cache_service.get_stats.return_value = {
            "hits": 100,
            "misses": 20,
            "hit_rate": 0.83,
            "size": 50
        }
        
        response = self.client.get("/api/v1/cache/stats")
        assert response.status_code == 200
        stats = response.json()
        assert "hits" in stats
        assert "hit_rate" in stats

    @patch("src.main.cache_service")
    def test_cache_clear_endpoint(self, mock_cache_service):
        """Test cache clear endpoint"""
        mock_cache_service.clear_all.return_value = 10  # Number of cleared entries
        
        response = self.client.delete("/api/v1/cache/clear")
        assert response.status_code == 200
        result = response.json()
        assert "cache entries" in result["message"]
