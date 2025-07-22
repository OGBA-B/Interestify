import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


def test_dashboard_heat_map_comprehensive():
    """Comprehensive test for heat map functionality"""
    # Test default parameters
    response = client.get("/api/v1/dashboard/heat-map")
    assert response.status_code == 200
    data = response.json()
    
    # Verify response structure
    assert "heat_map_data" in data
    assert "timeframe" in data
    assert "resolution" in data
    assert "start_date" in data
    assert "end_date" in data
    assert "total_topics" in data
    
    # Test with specific topic filter
    response = client.get("/api/v1/dashboard/heat-map?topic=machine_learning")
    assert response.status_code == 200
    data = response.json()
    assert data["topic_filter"] == "machine_learning"
    
    # Test with different timeframes
    for timeframe in ["1d", "7d", "30d"]:
        response = client.get(f"/api/v1/dashboard/heat-map?timeframe={timeframe}")
        assert response.status_code == 200
        data = response.json()
        assert data["timeframe"] == timeframe
    
    # Test with different resolutions
    for resolution in ["hourly", "daily", "weekly"]:
        response = client.get(f"/api/v1/dashboard/heat-map?resolution={resolution}")
        assert response.status_code == 200
        data = response.json()
        assert data["resolution"] == resolution


def test_dashboard_analytics_comprehensive():
    """Comprehensive test for analytics endpoint"""
    response = client.get("/api/v1/dashboard/analytics")
    assert response.status_code == 200
    data = response.json()
    
    # Test all required sections
    required_sections = [
        "engagement_metrics",
        "user_demographics", 
        "platform_performance",
        "sentiment_trends",
        "topic_sentiment_matrix",
        "generated_at"
    ]
    
    for section in required_sections:
        assert section in data
    
    # Test engagement metrics structure
    engagement = data["engagement_metrics"]
    required_engagement_fields = [
        "avg_likes_per_post",
        "avg_shares_per_post", 
        "avg_comments_per_post",
        "engagement_rate"
    ]
    for field in required_engagement_fields:
        assert field in engagement
        assert isinstance(engagement[field], (int, float))
    
    # Test user demographics structure
    if data["user_demographics"]:
        demo = data["user_demographics"][0]
        assert "age_group" in demo
        assert "percentage" in demo
        assert "sentiment_bias" in demo
        assert isinstance(demo["percentage"], (int, float))
        assert isinstance(demo["sentiment_bias"], (int, float))
    
    # Test platform performance structure
    if data["platform_performance"]:
        platform = data["platform_performance"][0]
        assert "platform" in platform
        assert "posts" in platform
        assert "avg_sentiment" in platform
        assert "response_time" in platform
        assert isinstance(platform["posts"], int)
        assert isinstance(platform["avg_sentiment"], (int, float))
        assert isinstance(platform["response_time"], (int, float))
    
    # Test sentiment trends structure
    if data["sentiment_trends"]:
        trend = data["sentiment_trends"][0]
        assert "date" in trend
        assert "positive" in trend
        assert "negative" in trend
        assert "neutral" in trend
        assert isinstance(trend["positive"], int)
        assert isinstance(trend["negative"], int)
        assert isinstance(trend["neutral"], int)
    
    # Test topic sentiment matrix structure  
    if data["topic_sentiment_matrix"]:
        topic = data["topic_sentiment_matrix"][0]
        assert "topic" in topic
        assert "positive" in topic
        assert "negative" in topic
        assert "neutral" in topic
        assert isinstance(topic["positive"], (int, float))
        assert isinstance(topic["negative"], (int, float))
        assert isinstance(topic["neutral"], (int, float))


def test_dashboard_summary_enhanced_comprehensive():
    """Comprehensive test for enhanced summary endpoint"""
    response = client.get("/api/v1/dashboard/summary")
    assert response.status_code == 200
    data = response.json()
    
    # Test enhanced fields
    enhanced_fields = [
        "total_posts",
        "total_posts_with_location",
        "total_unique_locations", 
        "active_sources",
        "overall_sentiment_distribution",
        "sentiment",
        "top_regions",
        "trending_topics",
        "recent_activity",
        "performance_metrics",
        "last_updated"
    ]
    
    for field in enhanced_fields:
        assert field in data
    
    # Test trending topics structure
    if data["trending_topics"]:
        topic = data["trending_topics"][0]
        assert "topic" in topic
        assert "mentions" in topic
        assert "sentiment_score" in topic
        assert isinstance(topic["mentions"], int)
        assert isinstance(topic["sentiment_score"], (int, float))
        assert 0 <= topic["sentiment_score"] <= 1
    
    # Test recent activity structure
    if data["recent_activity"]:
        activity = data["recent_activity"][0]
        assert "timestamp" in activity
        assert "event" in activity
        assert isinstance(activity["event"], str)
    
    # Test performance metrics structure
    perf = data["performance_metrics"]
    perf_fields = [
        "avg_processing_time",
        "api_response_time",
        "cache_hit_rate", 
        "uptime_percentage"
    ]
    for field in perf_fields:
        assert field in perf
        assert isinstance(perf[field], (int, float))
        if field in ["cache_hit_rate", "uptime_percentage"]:
            assert 0 <= perf[field] <= 1 or 0 <= perf[field] <= 100


def test_dashboard_error_handling():
    """Test dashboard endpoints handle edge cases gracefully"""
    # Test invalid timeframe
    response = client.get("/api/v1/dashboard/heat-map?timeframe=invalid")
    assert response.status_code == 200  # Should default to 7d
    data = response.json()
    assert data["timeframe"] == "invalid"  # Backend accepts any value but processes it
    
    # Test invalid resolution
    response = client.get("/api/v1/dashboard/heat-map?resolution=invalid")
    assert response.status_code == 200
    data = response.json()
    assert data["resolution"] == "invalid"
    
    # Test extremely long topic name
    long_topic = "a" * 1000
    response = client.get(f"/api/v1/dashboard/heat-map?topic={long_topic}")
    assert response.status_code == 200
    data = response.json()
    assert data["topic_filter"] == long_topic


def test_dashboard_data_consistency():
    """Test data consistency across dashboard endpoints"""
    # Get summary data
    summary_response = client.get("/api/v1/dashboard/summary")
    summary_data = summary_response.json()
    
    # Get analytics data  
    analytics_response = client.get("/api/v1/dashboard/analytics")
    analytics_data = analytics_response.json()
    
    # Get heat map data
    heatmap_response = client.get("/api/v1/dashboard/heat-map")
    heatmap_data = heatmap_response.json()
    
    # All should succeed
    assert summary_response.status_code == 200
    assert analytics_response.status_code == 200
    assert heatmap_response.status_code == 200
    
    # Check that total_posts is consistent type across endpoints
    assert isinstance(summary_data["total_posts"], int)
    
    # Check that sentiment data is properly structured
    sentiment = summary_data["sentiment"]
    assert "positive" in sentiment
    assert "negative" in sentiment
    assert "neutral" in sentiment
    
    # Verify heat map has topics
    assert len(heatmap_data["heat_map_data"]) > 0
    
    # Verify analytics has platform data
    assert len(analytics_data["platform_performance"]) > 0


def test_dashboard_performance():
    """Test dashboard endpoint performance and response times"""
    import time
    
    endpoints = [
        "/api/v1/dashboard/summary",
        "/api/v1/dashboard/analytics", 
        "/api/v1/dashboard/heat-map",
        "/api/v1/dashboard/geographic-sentiment",
        "/api/v1/dashboard/interest-trends"
    ]
    
    for endpoint in endpoints:
        start_time = time.time()
        response = client.get(endpoint)
        end_time = time.time()
        
        assert response.status_code == 200
        # Ensure response time is reasonable (less than 2 seconds)
        assert (end_time - start_time) < 2.0
        
        # Ensure response has content
        data = response.json()
        assert len(data) > 0