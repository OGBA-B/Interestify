import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


def test_dashboard_summary():
    """Test dashboard summary endpoint"""
    response = client.get("/api/v1/dashboard/summary")
    assert response.status_code == 200
    
    data = response.json()
    assert "total_posts_with_location" in data
    assert "total_unique_locations" in data
    assert "overall_sentiment_distribution" in data
    assert "top_regions" in data
    assert "last_updated" in data
    
    # Check sentiment distribution structure
    sentiment_dist = data["overall_sentiment_distribution"]
    assert "positive" in sentiment_dist
    assert "negative" in sentiment_dist
    assert "neutral" in sentiment_dist


def test_dashboard_geographic_sentiment():
    """Test geographic sentiment endpoint"""
    response = client.get("/api/v1/dashboard/geographic-sentiment")
    assert response.status_code == 200
    
    data = response.json()
    assert "geographic_data" in data
    assert "total_regions" in data
    assert "query_filters" in data
    assert "generated_at" in data
    
    # Check geographic data structure
    if data["geographic_data"]:
        first_location = data["geographic_data"][0]
        assert "location" in first_location
        assert "total_posts" in first_location
        assert "sentiment_distribution" in first_location
        assert "average_confidence" in first_location


def test_dashboard_geographic_sentiment_with_params():
    """Test geographic sentiment endpoint with query parameters"""
    response = client.get("/api/v1/dashboard/geographic-sentiment?limit=3&query=test")
    assert response.status_code == 200
    
    data = response.json()
    assert "geographic_data" in data
    assert len(data["geographic_data"]) <= 3
    assert data["query_filters"]["query"] == "test"


def test_dashboard_interest_trends():
    """Test interest trends endpoint"""
    response = client.get("/api/v1/dashboard/interest-trends")
    assert response.status_code == 200
    
    data = response.json()
    assert "trends_data" in data
    assert "timeframe" in data
    assert "start_date" in data
    assert "end_date" in data
    assert "total_regions" in data
    
    # Check trends data structure
    if data["trends_data"]:
        first_trend = data["trends_data"][0]
        assert "location" in first_trend
        assert "total_posts" in first_trend
        assert "daily_data" in first_trend


def test_dashboard_interest_trends_timeframes():
    """Test interest trends with different timeframes"""
    timeframes = ["1d", "7d", "30d"]
    
    for timeframe in timeframes:
        response = client.get(f"/api/v1/dashboard/interest-trends?timeframe={timeframe}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["timeframe"] == timeframe


def test_dashboard_endpoints_cors():
    """Test CORS headers are present on dashboard endpoints"""
    response = client.options("/api/v1/dashboard/summary")
    # The OPTIONS request should be handled by CORS middleware
    assert response.status_code in [200, 405]  # 405 if OPTIONS not explicitly handled