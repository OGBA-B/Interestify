import pytest


# Import all test modules to make them discoverable
from . import (
    test_sentiment,
    test_datasources,
    test_cache,
    test_api,
    test_utils,
    test_database,
    test_integration,
)

# Configuration for pytest
pytest_plugins = []


# Test markers
def pytest_configure(config):
    """Configure pytest markers"""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line("markers", "integration: marks tests as integration tests")
    config.addinivalue_line("markers", "unit: marks tests as unit tests")
    config.addinivalue_line("markers", "api: marks tests as API tests")
    config.addinivalue_line("markers", "database: marks tests as database tests")


# Test collection
def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers"""
    for item in items:
        # Add markers based on test file or test name
        if "test_integration" in item.nodeid:
            item.add_marker(pytest.mark.integration)
        elif "test_api" in item.nodeid:
            item.add_marker(pytest.mark.api)
        elif "test_database" in item.nodeid:
            item.add_marker(pytest.mark.database)
        else:
            item.add_marker(pytest.mark.unit)

        # Mark slow tests
        if "performance" in item.name.lower() or "slow" in item.name.lower():
            item.add_marker(pytest.mark.slow)


# Fixtures for all tests
@pytest.fixture
def sample_post():
    """Sample post for testing"""
    from src.models.schemas import Post, EngagementStats
    from datetime import datetime

    return Post(
        id="test_post_1",
        text="This is a test post about machine learning and AI",
        timestamp=datetime.now(),
        author="testuser",
        author_id="testuser123",
        engagement_stats=EngagementStats(
            likes=10, shares=5, comments=3, views=100, replies=2
        ),
        source="test",
        confidence_score=0.9,
        language="en",
        hashtags=["#test", "#ai", "#ml"],
        mentions=["@user1", "@user2"],
        urls=["https://example.com"],
    )


@pytest.fixture
def sample_search_query():
    """Sample search query for testing"""
    from src.models.schemas import SearchQuery

    return SearchQuery(
        query="machine learning",
        limit=50,
        offset=0,
        include_sentiment=True,
        min_confidence=0.5,
        language="en",
    )


@pytest.fixture
def sample_analysis_result():
    """Sample analysis result for testing"""
    from src.models.schemas import AnalysisResult, SentimentType
    from datetime import datetime

    return AnalysisResult(
        query="test query",
        total_posts=10,
        sentiment_distribution={
            SentimentType.POSITIVE: 6,
            SentimentType.NEGATIVE: 2,
            SentimentType.NEUTRAL: 2,
        },
        average_confidence=0.75,
        sources_used=["twitter", "reddit"],
        posts=[],
        sentiment_results=[],
        created_at=datetime.now(),
        processing_time=2.5,
    )


@pytest.fixture
def sample_data_source_config():
    """Sample data source configuration for testing"""
    from src.models.schemas import DataSourceConfig

    return DataSourceConfig(
        name="test_source",
        enabled=True,
        api_key="test_api_key",
        api_secret="test_api_secret",
        rate_limit=100,
        timeout=30,
        cache_ttl=3600,
        bot_detection_threshold=0.8,
    )
