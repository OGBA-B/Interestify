"""
Tests for the repository layer components
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, AsyncMock

from src.models.schemas import AnalysisResult, DataSourceConfig, Post, SentimentResult, SentimentType, EngagementStats
from src.repositories.analysis_repository import DatabaseAnalysisRepository
from src.repositories.data_source_repository import DatabaseDataSourceRepository


class TestDatabaseAnalysisRepository:
    """Test the DatabaseAnalysisRepository"""
    
    def setup_method(self):
        self.mock_db_manager = Mock()
        self.repository = DatabaseAnalysisRepository(self.mock_db_manager)
    
    @pytest.mark.asyncio
    async def test_save_analysis_result_success(self):
        """Test saving analysis result successfully"""
        self.mock_db_manager.store_analysis_result = AsyncMock()
        
        result = AnalysisResult(
            query="test",
            total_posts=10,
            sentiment_distribution={SentimentType.POSITIVE: 5, SentimentType.NEGATIVE: 3, SentimentType.NEUTRAL: 2},
            average_confidence=0.8,
            sources_used=["twitter"],
            posts=[],
            sentiment_results=[],
            created_at=datetime.utcnow(),
            processing_time=1.0
        )
        
        success = await self.repository.save_analysis_result(result)
        
        assert success is True
        self.mock_db_manager.store_analysis_result.assert_called_once_with(result)
    
    @pytest.mark.asyncio
    async def test_save_analysis_result_failure(self):
        """Test saving analysis result with error"""
        self.mock_db_manager.store_analysis_result = AsyncMock(side_effect=Exception("DB Error"))
        
        result = Mock()
        success = await self.repository.save_analysis_result(result)
        
        assert success is False
    
    @pytest.mark.asyncio
    async def test_get_analysis_result(self):
        """Test getting analysis result"""
        # Currently returns None as method is not fully implemented
        result = await self.repository.get_analysis_result("test")
        assert result is None
    
    @pytest.mark.asyncio
    async def test_save_posts_success(self):
        """Test saving posts successfully"""
        self.mock_db_manager.store_post = AsyncMock()
        
        posts = [
            Post(
                id="1",
                text="Test post",
                timestamp=datetime.utcnow(),
                author="user1",
                author_id="123",
                engagement_stats=EngagementStats(),
                source="twitter",
                confidence_score=0.9
            )
        ]
        
        success = await self.repository.save_posts(posts)
        
        assert success is True
        self.mock_db_manager.store_post.assert_called_once_with(posts[0])
    
    @pytest.mark.asyncio
    async def test_save_posts_failure(self):
        """Test saving posts with error"""
        self.mock_db_manager.store_post = AsyncMock(side_effect=Exception("DB Error"))
        
        posts = [Mock()]
        success = await self.repository.save_posts(posts)
        
        assert success is False
    
    @pytest.mark.asyncio
    async def test_get_posts_by_source(self):
        """Test getting posts by source"""
        # Currently returns empty list as method is not fully implemented
        posts = await self.repository.get_posts_by_source("twitter", 10)
        assert posts == []
    
    @pytest.mark.asyncio
    async def test_save_sentiment_results_success(self):
        """Test saving sentiment results successfully"""
        self.mock_db_manager.store_sentiment_result = AsyncMock()
        
        results = [
            SentimentResult(
                post_id="1",
                sentiment=SentimentType.POSITIVE,
                confidence=0.8,
                polarity=0.5,
                subjectivity=0.6,
                analyzer_used="textblob",
                created_at=datetime.utcnow()
            )
        ]
        
        success = await self.repository.save_sentiment_results(results)
        
        assert success is True
        self.mock_db_manager.store_sentiment_result.assert_called_once_with(results[0])
    
    @pytest.mark.asyncio
    async def test_save_sentiment_results_failure(self):
        """Test saving sentiment results with error"""
        self.mock_db_manager.store_sentiment_result = AsyncMock(side_effect=Exception("DB Error"))
        
        results = [Mock()]
        success = await self.repository.save_sentiment_results(results)
        
        assert success is False
    
    @pytest.mark.asyncio
    async def test_get_sentiment_results_by_post_ids(self):
        """Test getting sentiment results by post IDs"""
        # Currently returns empty list as method is not fully implemented
        results = await self.repository.get_sentiment_results_by_post_ids(["1", "2"])
        assert results == []
    
    @pytest.mark.asyncio
    async def test_cleanup_old_data(self):
        """Test cleaning up old data"""
        # Currently returns 0 as method is not fully implemented
        count = await self.repository.cleanup_old_data(30)
        assert count == 0


class TestDatabaseDataSourceRepository:
    """Test the DatabaseDataSourceRepository"""
    
    def setup_method(self):
        self.mock_db_manager = Mock()
        self.repository = DatabaseDataSourceRepository(self.mock_db_manager)
    
    @pytest.mark.asyncio
    async def test_save_config_success(self):
        """Test saving data source config successfully"""
        self.mock_db_manager.save_data_source_config = AsyncMock()
        
        config = DataSourceConfig(name="twitter", enabled=True)
        success = await self.repository.save_config(config)
        
        assert success is True
        self.mock_db_manager.save_data_source_config.assert_called_once_with(config)
    
    @pytest.mark.asyncio
    async def test_save_config_failure(self):
        """Test saving data source config with error"""
        self.mock_db_manager.save_data_source_config = AsyncMock(side_effect=Exception("DB Error"))
        
        config = DataSourceConfig(name="twitter", enabled=True)
        success = await self.repository.save_config(config)
        
        assert success is False
    
    @pytest.mark.asyncio
    async def test_get_config_found(self):
        """Test getting data source config when found"""
        expected_config = DataSourceConfig(name="twitter", enabled=True)
        self.mock_db_manager.get_all_data_source_configs = AsyncMock(return_value=[expected_config])
        
        config = await self.repository.get_config("twitter")
        
        assert config == expected_config
    
    @pytest.mark.asyncio
    async def test_get_config_not_found(self):
        """Test getting data source config when not found"""
        self.mock_db_manager.get_all_data_source_configs = AsyncMock(return_value=[])
        
        config = await self.repository.get_config("nonexistent")
        
        assert config is None
    
    @pytest.mark.asyncio
    async def test_get_config_error(self):
        """Test getting data source config with error"""
        self.mock_db_manager.get_all_data_source_configs = AsyncMock(side_effect=Exception("DB Error"))
        
        config = await self.repository.get_config("twitter")
        
        assert config is None
    
    @pytest.mark.asyncio
    async def test_get_all_configs_success(self):
        """Test getting all configs successfully"""
        expected_configs = [
            DataSourceConfig(name="twitter", enabled=True),
            DataSourceConfig(name="reddit", enabled=False)
        ]
        self.mock_db_manager.get_all_data_source_configs = AsyncMock(return_value=expected_configs)
        
        configs = await self.repository.get_all_configs()
        
        assert configs == expected_configs
    
    @pytest.mark.asyncio
    async def test_get_all_configs_failure(self):
        """Test getting all configs with error"""
        self.mock_db_manager.get_all_data_source_configs = AsyncMock(side_effect=Exception("DB Error"))
        
        configs = await self.repository.get_all_configs()
        
        assert configs == []
    
    @pytest.mark.asyncio
    async def test_update_config_success(self):
        """Test updating config successfully"""
        self.mock_db_manager.update_data_source_config = AsyncMock()
        
        config = DataSourceConfig(name="twitter", enabled=False)
        success = await self.repository.update_config("twitter", config)
        
        assert success is True
        self.mock_db_manager.update_data_source_config.assert_called_once_with("twitter", config)
    
    @pytest.mark.asyncio
    async def test_update_config_failure(self):
        """Test updating config with error"""
        self.mock_db_manager.update_data_source_config = AsyncMock(side_effect=Exception("DB Error"))
        
        config = DataSourceConfig(name="twitter", enabled=False)
        success = await self.repository.update_config("twitter", config)
        
        assert success is False
    
    @pytest.mark.asyncio
    async def test_delete_config_success(self):
        """Test deleting config successfully"""
        self.mock_db_manager.delete_data_source_config = AsyncMock()
        
        success = await self.repository.delete_config("twitter")
        
        assert success is True
        self.mock_db_manager.delete_data_source_config.assert_called_once_with("twitter")
    
    @pytest.mark.asyncio
    async def test_delete_config_failure(self):
        """Test deleting config with error"""
        self.mock_db_manager.delete_data_source_config = AsyncMock(side_effect=Exception("DB Error"))
        
        success = await self.repository.delete_config("twitter")
        
        assert success is False
    
    @pytest.mark.asyncio
    async def test_get_enabled_configs(self):
        """Test getting enabled configs"""
        all_configs = [
            DataSourceConfig(name="twitter", enabled=True),
            DataSourceConfig(name="reddit", enabled=False),
            DataSourceConfig(name="facebook", enabled=True)
        ]
        self.mock_db_manager.get_all_data_source_configs = AsyncMock(return_value=all_configs)
        
        enabled_configs = await self.repository.get_enabled_configs()
        
        assert len(enabled_configs) == 2
        assert all(config.enabled for config in enabled_configs)
        assert enabled_configs[0].name == "twitter"
        assert enabled_configs[1].name == "facebook"