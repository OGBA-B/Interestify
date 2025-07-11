import asyncio
from datetime import datetime
from unittest.mock import AsyncMock, Mock, patch

import pytest

from src.models.schemas import (
    AnalysisResult,
    DataSourceConfig,
    EngagementStats,
    Post,
    SentimentResult,
    SentimentType,
)
from src.utils.database import DatabaseManager


class TestDatabaseManager:
    """Test database manager"""

    @pytest.fixture
    def db_manager(self):
        """Create database manager for testing"""
        return DatabaseManager(database_url="sqlite+aiosqlite:///:memory:")

    @pytest.fixture
    async def setup_db(self, db_manager):
        """Setup database for testing"""
        await db_manager.init_db()
        yield db_manager
        await db_manager.close()

    @pytest.mark.asyncio
    async def test_init_db(self, setup_db):
        """Test database initialization"""
        # Database should be initialized without errors
        db_manager = await anext(setup_db)
        assert db_manager is not None
        assert db_manager.engine is not None

    @pytest.mark.asyncio
    async def test_save_data_source_config(self, setup_db):
        """Test saving data source configuration"""
        db_manager = await anext(setup_db)
        config = DataSourceConfig(
            name="test_source",
            enabled=True,
            api_key="test_key",
            api_secret="test_secret",
            rate_limit=100,
            timeout=30,
            cache_ttl=3600,
            bot_detection_threshold=0.8,
        )

        success = await db_manager.save_data_source_config(config)
        assert success is True

    @pytest.mark.asyncio
    async def test_get_data_source_config(self, setup_db):
        """Test getting data source configuration"""
        db_manager = await anext(setup_db)
        # First save a config
        config = DataSourceConfig(
            name="test_source",
            enabled=True,
            api_key="test_key",
            api_secret="test_secret",
            rate_limit=100,
            timeout=30,
            cache_ttl=3600,
            bot_detection_threshold=0.8,
        )

        await db_manager.save_data_source_config(config)

        # Then retrieve it
        retrieved_config = await db_manager.get_data_source_config("test_source")

        assert retrieved_config is not None
        assert retrieved_config.name == "test_source"
        assert retrieved_config.enabled is True
        assert retrieved_config.api_key == "test_key"
        assert retrieved_config.rate_limit == 100

    @pytest.mark.asyncio
    async def test_get_nonexistent_data_source_config(self, setup_db):
        """Test getting non-existent data source configuration"""
        db_manager = await anext(setup_db)
        config = await db_manager.get_data_source_config("nonexistent")
        assert config is None

    @pytest.mark.asyncio
    async def test_get_all_data_source_configs(self, setup_db):
        """Test getting all data source configurations"""
        db_manager = await anext(setup_db)
        # Save multiple configs
        configs = [
            DataSourceConfig(
                name="twitter", enabled=True, api_key="twitter_key", rate_limit=100
            ),
            DataSourceConfig(
                name="reddit", enabled=False, api_key="reddit_key", rate_limit=200
            ),
        ]

        for config in configs:
            await db_manager.save_data_source_config(config)

        # Get all configs
        all_configs = await db_manager.get_all_data_source_configs()

        assert len(all_configs) == 2
        config_names = [config.name for config in all_configs]
        assert "twitter" in config_names
        assert "reddit" in config_names

    @pytest.mark.asyncio
    async def test_update_data_source_config(self, setup_db):
        """Test updating data source configuration"""
        db_manager = await anext(setup_db)
        # Save initial config
        config = DataSourceConfig(
            name="test_source", enabled=True, api_key="old_key", rate_limit=100
        )

        await db_manager.save_data_source_config(config)

        # Update config
        updated_config = DataSourceConfig(
            name="test_source", enabled=False, api_key="new_key", rate_limit=200
        )

        success = await db_manager.save_data_source_config(updated_config)
        assert success is True

        # Verify update
        retrieved_config = await db_manager.get_data_source_config("test_source")
        assert retrieved_config.enabled is False
        assert retrieved_config.api_key == "new_key"
        assert retrieved_config.rate_limit == 200

    @pytest.mark.asyncio
    async def test_delete_data_source_config(self, setup_db):
        """Test deleting data source configuration"""
        db_manager = await anext(setup_db)
        # Save config
        config = DataSourceConfig(
            name="test_source", enabled=True, api_key="test_key", rate_limit=100
        )

        await db_manager.save_data_source_config(config)

        # Verify it exists
        retrieved_config = await db_manager.get_data_source_config("test_source")
        assert retrieved_config is not None

        # Delete it
        success = await db_manager.delete_data_source_config("test_source")
        assert success is True

        # Verify it's deleted
        retrieved_config = await db_manager.get_data_source_config("test_source")
        assert retrieved_config is None

    @pytest.mark.asyncio
    async def test_store_analysis_result(self, setup_db):
        """Test storing analysis result"""
        db_manager = await anext(setup_db)
        # Create test data
        posts = [
            Post(
                id="1",
                text="Test post 1",
                timestamp=datetime.now(),
                author="user1",
                author_id="user1",
                engagement_stats=EngagementStats(likes=10, comments=5),
                source="test",
                confidence_score=0.9,
            ),
            Post(
                id="2",
                text="Test post 2",
                timestamp=datetime.now(),
                author="user2",
                author_id="user2",
                engagement_stats=EngagementStats(likes=20, comments=3),
                source="test",
                confidence_score=0.8,
            ),
        ]

        sentiment_results = [
            SentimentResult(
                post_id="1",
                sentiment=SentimentType.POSITIVE,
                confidence=0.8,
                polarity=0.5,
                subjectivity=0.6,
                analyzer_used="textblob",
                created_at=datetime.now(),
            ),
            SentimentResult(
                post_id="2",
                sentiment=SentimentType.NEGATIVE,
                confidence=0.7,
                polarity=-0.3,
                subjectivity=0.4,
                analyzer_used="textblob",
                created_at=datetime.now(),
            ),
        ]

        analysis_result = AnalysisResult(
            query="test query",
            total_posts=2,
            sentiment_distribution={
                SentimentType.POSITIVE: 1,
                SentimentType.NEGATIVE: 1,
                SentimentType.NEUTRAL: 0,
            },
            average_confidence=0.75,
            sources_used=["test"],
            posts=posts,
            sentiment_results=sentiment_results,
            created_at=datetime.now(),
            processing_time=1.5,
        )

        # Store the result
        success = await db_manager.store_analysis_result(analysis_result)
        assert success is True

    @pytest.mark.asyncio
    async def test_get_posts_by_query(self, setup_db):
        """Test getting posts by query"""
        db_manager = await anext(setup_db)
        # First store some posts
        posts = [
            Post(
                id="1",
                text="This is about machine learning",
                timestamp=datetime.now(),
                author="user1",
                author_id="user1",
                engagement_stats=EngagementStats(likes=10),
                source="test",
                confidence_score=0.9,
            ),
            Post(
                id="2",
                text="This is about artificial intelligence",
                timestamp=datetime.now(),
                author="user2",
                author_id="user2",
                engagement_stats=EngagementStats(likes=15),
                source="test",
                confidence_score=0.8,
            ),
            Post(
                id="3",
                text="This is about cooking",
                timestamp=datetime.now(),
                author="user3",
                author_id="user3",
                engagement_stats=EngagementStats(likes=5),
                source="test",
                confidence_score=0.7,
            ),
        ]

        sentiment_results = []
        for post in posts:
            sentiment_results.append(
                SentimentResult(
                    post_id=post.id,
                    sentiment=SentimentType.NEUTRAL,
                    confidence=0.5,
                    polarity=0.0,
                    subjectivity=0.5,
                    analyzer_used="textblob",
                    created_at=datetime.now(),
                )
            )

        analysis_result = AnalysisResult(
            query="machine learning",  # Use a query that matches the posts
            total_posts=3,
            sentiment_distribution={
                SentimentType.POSITIVE: 0,
                SentimentType.NEGATIVE: 0,
                SentimentType.NEUTRAL: 3,
            },
            average_confidence=0.8,
            sources_used=["test"],
            posts=posts,
            sentiment_results=sentiment_results,
            created_at=datetime.now(),
            processing_time=1.0,
        )

        await db_manager.store_analysis_result(analysis_result)

        # Try to get posts by query - search for "machine" which appears in first post
        retrieved_posts = await db_manager.get_posts_by_query("machine", limit=10)

        assert (
            len(retrieved_posts) >= 1
        )  # Should find at least the machine learning post

    @pytest.mark.asyncio
    async def test_database_error_handling(self, setup_db):
        """Test database error handling"""
        db_manager = await anext(setup_db)
        # Test with invalid data that should cause an error
        with patch.object(db_manager, "get_session") as mock_session:
            mock_session.side_effect = Exception("Database error")

            # Should handle error gracefully
            config = await db_manager.get_data_source_config("test")
            assert config is None

    @pytest.mark.asyncio
    async def test_close_database(self, setup_db):
        """Test closing database connection"""
        db_manager = await anext(setup_db)
        # Database should close without errors
        await db_manager.close()
        # Note: setup_db fixture will also close, but multiple closes should be safe
