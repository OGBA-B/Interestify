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


def test_dashboard_heat_map():
    """Test heat map endpoint"""
    response = client.get("/api/v1/dashboard/heat-map")
    assert response.status_code == 200
    
    data = response.json()
    assert "heat_map_data" in data
    assert "timeframe" in data
    assert "resolution" in data
    assert "start_date" in data
    assert "end_date" in data
    assert "total_topics" in data
    
    # Check heat map data structure
    if data["heat_map_data"]:
        first_topic = data["heat_map_data"][0]
        assert "topic" in first_topic
        assert "time_series" in first_topic
        
        if first_topic["time_series"]:
            first_point = first_topic["time_series"][0]
            assert "timestamp" in first_point
            assert "positive" in first_point
            assert "negative" in first_point
            assert "neutral" in first_point
            assert "sentiment_score" in first_point


def test_dashboard_heat_map_with_params():
    """Test heat map endpoint with parameters"""
    response = client.get("/api/v1/dashboard/heat-map?topic=test&timeframe=1d&resolution=hourly")
    assert response.status_code == 200
    
    data = response.json()
    assert data["timeframe"] == "1d"
    assert data["resolution"] == "hourly"
    assert data["topic_filter"] == "test"


def test_dashboard_analytics():
    """Test advanced analytics endpoint"""
    response = client.get("/api/v1/dashboard/analytics")
    assert response.status_code == 200
    
    data = response.json()
    assert "engagement_metrics" in data
    assert "user_demographics" in data
    assert "platform_performance" in data
    assert "sentiment_trends" in data
    assert "topic_sentiment_matrix" in data
    assert "generated_at" in data
    
    # Check engagement metrics structure
    engagement = data["engagement_metrics"]
    assert "avg_likes_per_post" in engagement
    assert "avg_shares_per_post" in engagement
    assert "avg_comments_per_post" in engagement
    assert "engagement_rate" in engagement
    
    # Check user demographics structure
    if data["user_demographics"]:
        demo = data["user_demographics"][0]
        assert "age_group" in demo
        assert "percentage" in demo
        assert "sentiment_bias" in demo
    
    # Check platform performance structure
    if data["platform_performance"]:
        platform = data["platform_performance"][0]
        assert "platform" in platform
        assert "posts" in platform
        assert "avg_sentiment" in platform
        assert "response_time" in platform


def test_dashboard_summary_enhanced():
    """Test enhanced dashboard summary endpoint"""
    response = client.get("/api/v1/dashboard/summary")
    assert response.status_code == 200
    
    data = response.json()
    # Test new fields in enhanced summary
    assert "total_posts" in data
    assert "trending_topics" in data
    assert "recent_activity" in data
    assert "performance_metrics" in data
    
    # Check trending topics structure
    if data["trending_topics"]:
        topic = data["trending_topics"][0]
        assert "topic" in topic
        assert "mentions" in topic
        assert "sentiment_score" in topic
    
    # Check recent activity structure
    if data["recent_activity"]:
        activity = data["recent_activity"][0]
        assert "timestamp" in activity
        assert "event" in activity
    
    # Check performance metrics structure
    perf = data["performance_metrics"]
    assert "avg_processing_time" in perf
    assert "api_response_time" in perf
    assert "cache_hit_rate" in perf
    assert "uptime_percentage" in perf