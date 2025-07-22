"""
Tests for the service layer components
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime
from src.services.analysis_service import AnalysisService
from src.services.cache_service import CacheService
from src.services.data_source_service import DataSourceService
from src.models.schemas import SearchQuery, AnalysisResult, DataSourceConfig, SentimentType


class TestAnalysisService:
    """Test the AnalysisService"""
    
    def setup_method(self):
        self.mock_data_source_manager = Mock()
        self.service = AnalysisService(self.mock_data_source_manager)
    
    @pytest.mark.asyncio
    async def test_analyze_posts_no_sources(self):
        """Test analyze_posts when no data sources are available"""
        self.mock_data_source_manager.get_enabled_sources.return_value = []
        
        query = SearchQuery(query="test", limit=10)
        
        with pytest.raises(RuntimeError, match="No data sources available"):
            await self.service.analyze_posts(query)
    
    @pytest.mark.asyncio
    async def test_analyze_posts_success(self):
        """Test successful post analysis"""
        # Mock data source
        mock_source = Mock()
        mock_source.name = "twitter"
        mock_source.search_posts = AsyncMock(return_value=[
            Mock(id="1", text="Test post", sentiment=SentimentType.POSITIVE)
        ])
        
        self.mock_data_source_manager.get_enabled_sources.return_value = [mock_source]
        
        query = SearchQuery(query="test", limit=10, include_sentiment=False)
        
        with patch('src.services.analysis_service.paginate_results') as mock_paginate:
            mock_paginate.return_value = []
            
            result = await self.service.analyze_posts(query)
            
            assert isinstance(result, AnalysisResult)
            assert result.query == "test"
            assert "twitter" in result.sources_used
    
    @pytest.mark.asyncio
    async def test_get_user_posts_success(self):
        """Test getting user posts successfully"""
        mock_source = Mock()
        mock_source.get_user_posts = AsyncMock(return_value=[Mock(id="1")])
        
        self.mock_data_source_manager.get_data_source.return_value = mock_source
        
        result = await self.service.get_user_posts("user1", "twitter", 10)
        
        assert len(result) == 1
        assert result[0].id == "1"
    
    @pytest.mark.asyncio
    async def test_get_user_posts_source_not_found(self):
        """Test getting user posts when source not found"""
        self.mock_data_source_manager.get_data_source.return_value = None
        
        with pytest.raises(ValueError, match="Data source 'invalid' not found"):
            await self.service.get_user_posts("user1", "invalid", 10)
    
    def test_analyze_single_text_success(self):
        """Test analyzing single text successfully"""
        with patch('src.services.analysis_service.SentimentAnalyzerFactory') as mock_factory:
            mock_analyzer = Mock()
            mock_analyzer.analyze.return_value = {"sentiment": "positive", "confidence": 0.8}
            mock_factory.create_analyzer.return_value = mock_analyzer
            
            result = self.service.analyze_single_text("Test text", "textblob")
            
            assert result["sentiment"] == "positive"
            assert result["confidence"] == 0.8


class TestCacheService:
    """Test the CacheService"""
    
    def setup_method(self):
        self.mock_cache_manager = Mock()
        self.service = CacheService(self.mock_cache_manager)
    
    def test_get_cached_result(self):
        """Test getting cached result"""
        query = SearchQuery(query="test", limit=10)
        expected_result = Mock()
        
        self.mock_cache_manager.get.return_value = expected_result
        
        result = self.service.get_cached_result(query)
        
        assert result == expected_result
        self.mock_cache_manager.get.assert_called_once_with(query)
    
    def test_cache_result(self):
        """Test caching a result"""
        query = SearchQuery(query="test", limit=10)
        result = Mock()
        
        self.service.cache_result(query, result)
        
        self.mock_cache_manager.set.assert_called_once_with(query, result)
    
    def test_get_stats(self):
        """Test getting cache statistics"""
        expected_stats = {"hits": 100, "misses": 20}
        self.mock_cache_manager.get_stats.return_value = expected_stats
        
        stats = self.service.get_stats()
        
        assert stats == expected_stats
    
    def test_clear_all(self):
        """Test clearing all cache entries"""
        self.mock_cache_manager.clear_all.return_value = 10
        
        cleared = self.service.clear_all()
        
        assert cleared == 10
    
    def test_clear_expired(self):
        """Test clearing expired cache entries"""
        self.mock_cache_manager.clear_expired.return_value = 5
        
        cleared = self.service.clear_expired()
        
        assert cleared == 5


class TestDataSourceService:
    """Test the DataSourceService"""
    
    def setup_method(self):
        self.mock_data_source_manager = Mock()
        self.service = DataSourceService(self.mock_data_source_manager)
    
    def test_get_all_sources(self):
        """Test getting all data sources"""
        mock_source = Mock()
        mock_source.config.enabled = True
        mock_source.is_available.return_value = True
        mock_source.config.rate_limit = 100
        mock_source.get_rate_limit_info.return_value = {"remaining": 90}
        
        self.mock_data_source_manager.get_configured_sources.return_value = ["twitter"]
        self.mock_data_source_manager.get_data_source.return_value = mock_source
        
        sources = self.service.get_all_sources()
        
        assert len(sources) == 1
        assert sources[0]["name"] == "twitter"
        assert sources[0]["enabled"] is True
    
    def test_add_source(self):
        """Test adding a data source"""
        config = DataSourceConfig(name="reddit", enabled=True)
        self.mock_data_source_manager.add_data_source.return_value = True
        
        result = self.service.add_source(config)
        
        assert result is True
        self.mock_data_source_manager.add_data_source.assert_called_once_with(config)
    
    def test_update_source(self):
        """Test updating a data source"""
        config = DataSourceConfig(name="twitter", enabled=False)
        self.mock_data_source_manager.update_source_config.return_value = True
        
        result = self.service.update_source("twitter", config)
        
        assert result is True
        self.mock_data_source_manager.update_source_config.assert_called_once_with("twitter", config)
    
    def test_remove_source(self):
        """Test removing a data source"""
        self.mock_data_source_manager.remove_data_source.return_value = True
        
        result = self.service.remove_source("twitter")
        
        assert result is True
        self.mock_data_source_manager.remove_data_source.assert_called_once_with("twitter")
    
    def test_get_available_types(self):
        """Test getting available data source types"""
        self.mock_data_source_manager.get_available_source_types.return_value = ["twitter", "reddit"]
        
        types = self.service.get_available_types()
        
        assert types == ["twitter", "reddit"]
    
    def test_get_rate_limit_status(self):
        """Test getting rate limit status"""
        expected_status = {"twitter": {"remaining": 90}}
        self.mock_data_source_manager.get_rate_limit_status.return_value = expected_status
        
        status = self.service.get_rate_limit_status()
        
        assert status == expected_status
    
    @pytest.mark.asyncio
    async def test_close_all_sources(self):
        """Test closing all data sources"""
        self.mock_data_source_manager.close_all = AsyncMock()
        
        await self.service.close_all_sources()
        
        self.mock_data_source_manager.close_all.assert_called_once()