from datetime import datetime
from unittest.mock import AsyncMock, Mock, patch

import pytest

from src.core.datasources import (
    DataSource,
    DataSourceManager,
    RedditDataSource,
    TwitterDataSource,
)
from src.models.schemas import DataSourceConfig, EngagementStats, Post, SearchQuery


class MockDataSource(DataSource):
    """Mock data source for testing"""

    def __init__(self, config):
        super().__init__(config)
        self.posts = []

    async def search_posts(self, query: SearchQuery):
        return self.posts

    async def get_user_posts(self, user_id: str, limit: int = 50):
        return self.posts

    def is_available(self):
        return self.config.enabled

    def get_rate_limit_info(self):
        return {"requests_per_hour": 100, "remaining": 100}


class TestDataSource:
    """Test data source base class"""

    def setup_method(self):
        config = DataSourceConfig(
            name="test",
            enabled=True,
            rate_limit=100,
            timeout=30,
            cache_ttl=3600,
            bot_detection_threshold=0.8,
        )
        self.data_source = MockDataSource(config)

    def test_detect_bot_normal_post(self):
        """Test bot detection for normal post"""
        post = Post(
            id="1",
            text="Just had a great day at the beach!",
            timestamp=datetime.now(),
            author="user1",
            author_id="user1",
            engagement_stats=EngagementStats(likes=10, comments=5),
            source="test",
            confidence_score=1.0,
        )

        confidence = self.data_source.detect_bot(post)
        assert confidence > 0.5

    def test_detect_bot_suspicious_post(self):
        """Test bot detection for suspicious post"""
        post = Post(
            id="2",
            text="AMAZING DEAL! Click here for free money! #deal #money #free #click #now #limited",
            timestamp=datetime.now(),
            author="spammer",
            author_id="spammer",
            engagement_stats=EngagementStats(likes=50000, comments=2),
            source="test",
            confidence_score=1.0,
            mentions=["@user1", "@user2", "@user3", "@user4"],
        )

        confidence = self.data_source.detect_bot(post)
        assert confidence < 0.5

    def test_filter_posts(self):
        """Test filtering posts by confidence"""
        posts = [
            Post(
                id="1",
                text="Normal post",
                timestamp=datetime.now(),
                author="user1",
                author_id="user1",
                engagement_stats=EngagementStats(),
                source="test",
                confidence_score=1.0,
            ),
            Post(
                id="2",
                text="click here for free money amazing deal",
                timestamp=datetime.now(),
                author="spammer",
                author_id="spammer",
                engagement_stats=EngagementStats(likes=100000),
                source="test",
                confidence_score=1.0,
            ),
        ]

        filtered = self.data_source.filter_posts(posts, min_confidence=0.5)
        assert len(filtered) == 1
        assert filtered[0].id == "1"

    def test_extract_hashtags(self):
        """Test hashtag extraction"""
        text = "Love this #awesome #product #deal"
        hashtags = self.data_source._extract_hashtags(text)
        assert "#awesome" in hashtags
        assert "#product" in hashtags
        assert "#deal" in hashtags

    def test_extract_mentions(self):
        """Test mention extraction"""
        text = "Hey @user1 and @user2 check this out!"
        mentions = self.data_source._extract_mentions(text)
        assert "@user1" in mentions
        assert "@user2" in mentions

    def test_extract_urls(self):
        """Test URL extraction"""
        text = "Check out https://example.com and http://test.com"
        urls = self.data_source._extract_urls(text)
        assert "https://example.com" in urls
        assert "http://test.com" in urls


class TestDataSourceManager:
    def test_dynamic_plugin_loading(self):
        """Test dynamic loading of plugin data sources"""
        # Should auto-load DummyInfluencerSource from plugins
        manager = DataSourceManager()
        available = manager.get_available_source_types()
        assert "dummy_influencer" in available or "dummyinfluencer" in available

        # Try to add the dummy influencer source
        config = DataSourceConfig(name="dummy_influencer", enabled=True, rate_limit=100)
        added = manager.add_data_source(config)
        assert added
        source = manager.get_data_source("dummy_influencer")
        assert source is not None
        import asyncio

        posts = asyncio.get_event_loop().run_until_complete(
            source.search_posts(SearchQuery(query="irrelevant"))
        )
        assert isinstance(posts, list)
        assert any(hasattr(p, "followers") for p in posts)

    """Test data source manager"""

    def setup_method(self):
        self.manager = DataSourceManager()

    def test_register_data_source(self):
        """Test registering new data source type"""
        self.manager.register_data_source("mock", MockDataSource)
        assert "mock" in self.manager.get_available_source_types()

    def test_add_data_source(self):
        """Test adding data source"""
        self.manager.register_data_source("mock", MockDataSource)

        config = DataSourceConfig(name="mock", enabled=True, rate_limit=100)

        success = self.manager.add_data_source(config)
        assert success
        assert "mock" in self.manager.get_configured_sources()

    def test_add_unavailable_data_source(self):
        """Test adding unavailable data source"""
        self.manager.register_data_source("mock", MockDataSource)

        config = DataSourceConfig(
            name="mock", enabled=False, rate_limit=100  # Disabled
        )

        success = self.manager.add_data_source(config)
        assert not success

    def test_remove_data_source(self):
        """Test removing data source"""
        self.manager.register_data_source("mock", MockDataSource)

        config = DataSourceConfig(name="mock", enabled=True, rate_limit=100)

        self.manager.add_data_source(config)
        assert "mock" in self.manager.get_configured_sources()

        success = self.manager.remove_data_source("mock")
        assert success
        assert "mock" not in self.manager.get_configured_sources()

    def test_get_enabled_sources(self):
        """Test getting enabled sources"""
        self.manager.register_data_source("mock", MockDataSource)

        config = DataSourceConfig(name="mock", enabled=True, rate_limit=100)

        self.manager.add_data_source(config)
        enabled_sources = self.manager.get_enabled_sources()

        assert len(enabled_sources) == 1
        assert enabled_sources[0].name == "mock"

    def test_update_source_config(self):
        """Test updating source configuration"""
        self.manager.register_data_source("mock", MockDataSource)

        config = DataSourceConfig(name="mock", enabled=True, rate_limit=100)

        self.manager.add_data_source(config)

        # Update config
        new_config = DataSourceConfig(
            name="mock", enabled=True, rate_limit=200  # Changed
        )

        success = self.manager.update_source_config("mock", new_config)
        assert success

        source = self.manager.get_data_source("mock")
        assert source.config.rate_limit == 200

    def test_get_rate_limit_status(self):
        """Test getting rate limit status"""
        self.manager.register_data_source("mock", MockDataSource)

        config = DataSourceConfig(name="mock", enabled=True, rate_limit=100)

        self.manager.add_data_source(config)
        status = self.manager.get_rate_limit_status()

        assert "mock" in status
        assert status["mock"]["requests_per_hour"] == 100


@pytest.mark.asyncio
class TestTwitterDataSource:
    """Test Twitter data source"""

    def setup_method(self):
        config = DataSourceConfig(
            name="twitter", enabled=True, api_key="test_key", rate_limit=100
        )
        self.twitter_source = TwitterDataSource(config)

    def test_is_available_with_key(self):
        """Test availability with API key"""
        assert self.twitter_source.is_available()

    def test_is_available_without_key(self):
        """Test availability without API key"""
        config = DataSourceConfig(
            name="twitter", enabled=True, api_key=None, rate_limit=100
        )
        twitter_source = TwitterDataSource(config)
        assert not twitter_source.is_available()

    @patch("aiohttp.ClientSession.get")
    async def test_search_posts_success(self, mock_get):
        """Test successful post search"""
        mock_response = Mock()
        mock_response.status = 200
        mock_response.json = AsyncMock(
            return_value={
                "data": [
                    {
                        "id": "1",
                        "text": "Test tweet",
                        "created_at": "2023-01-01T00:00:00.000Z",
                        "author_id": "user1",
                        "public_metrics": {
                            "like_count": 10,
                            "retweet_count": 5,
                            "reply_count": 2,
                        },
                        "lang": "en",
                        "entities": {
                            "hashtags": [{"tag": "test"}],
                            "mentions": [{"username": "user2"}],
                            "urls": [{"expanded_url": "https://example.com"}],
                        },
                    }
                ],
                "includes": {
                    "users": [
                        {
                            "id": "user1",
                            "username": "testuser",
                            "name": "Test User",
                            "location": "Test City",
                        }
                    ]
                },
            }
        )
        mock_get.return_value.__aenter__.return_value = mock_response

        query = SearchQuery(query="test", limit=10)
        posts = await self.twitter_source.search_posts(query)

        assert len(posts) == 1
        assert posts[0].id == "1"
        assert posts[0].text == "Test tweet"
        assert posts[0].author == "testuser"
        assert posts[0].source == "twitter"

    @patch("aiohttp.ClientSession.get")
    async def test_search_posts_disabled_source(self, mock_get):
        """Test search when source is disabled"""
        config = DataSourceConfig(
            name="twitter", enabled=False, api_key="test_key", rate_limit=100
        )
        twitter_source = TwitterDataSource(config)
        
        query = SearchQuery(query="test", limit=10)
        posts = await twitter_source.search_posts(query)
        
        assert posts == []
        mock_get.assert_not_called()

    @patch("aiohttp.ClientSession.get")
    async def test_search_posts_api_error(self, mock_get):
        """Test search with API error"""
        mock_response = Mock()
        mock_response.status = 429  # Rate limit error
        mock_get.return_value.__aenter__.return_value = mock_response

        query = SearchQuery(query="test", limit=10)
        posts = await self.twitter_source.search_posts(query)

        assert posts == []

    @patch("aiohttp.ClientSession.get")
    async def test_search_posts_exception(self, mock_get):
        """Test search with exception"""
        mock_get.side_effect = Exception("Network error")

        query = SearchQuery(query="test", limit=10)
        posts = await self.twitter_source.search_posts(query)

        assert posts == []

    @patch("aiohttp.ClientSession.get")
    async def test_get_user_posts_success(self, mock_get):
        """Test successful user posts retrieval"""
        mock_response = Mock()
        mock_response.status = 200
        mock_response.json = AsyncMock(
            return_value={
                "data": [
                    {
                        "id": "1",
                        "text": "User tweet",
                        "created_at": "2023-01-01T00:00:00.000Z",
                        "author_id": "user1",
                        "public_metrics": {
                            "like_count": 5,
                            "retweet_count": 1,
                            "reply_count": 0,
                        },
                        "lang": "en",
                        "entities": {},
                    }
                ],
                "includes": {
                    "users": [
                        {
                            "id": "user1",
                            "username": "testuser",
                            "name": "Test User",
                        }
                    ]
                },
            }
        )
        mock_get.return_value.__aenter__.return_value = mock_response

        posts = await self.twitter_source.get_user_posts("user1", limit=10)

        assert len(posts) == 1
        assert posts[0].id == "1"
        assert posts[0].text == "User tweet"
        assert posts[0].author == "testuser"

    @patch("aiohttp.ClientSession.get")
    async def test_get_user_posts_disabled_source(self, mock_get):
        """Test user posts when source is disabled"""
        config = DataSourceConfig(
            name="twitter", enabled=False, api_key="test_key", rate_limit=100
        )
        twitter_source = TwitterDataSource(config)
        
        posts = await twitter_source.get_user_posts("user1", limit=10)
        
        assert posts == []
        mock_get.assert_not_called()

    @patch("aiohttp.ClientSession.get")
    async def test_get_user_posts_api_error(self, mock_get):
        """Test user posts with API error"""
        mock_response = Mock()
        mock_response.status = 404
        mock_get.return_value.__aenter__.return_value = mock_response

        posts = await self.twitter_source.get_user_posts("user1", limit=10)

        assert posts == []

    @patch("aiohttp.ClientSession.get")
    async def test_get_user_posts_exception(self, mock_get):
        """Test user posts with exception"""
        mock_get.side_effect = Exception("Network error")

        posts = await self.twitter_source.get_user_posts("user1", limit=10)

        assert posts == []

    def test_get_rate_limit_info(self):
        """Test rate limit info"""
        info = self.twitter_source.get_rate_limit_info()
        assert info["requests_per_hour"] == 100
        assert "remaining" in info
        assert "reset_time" in info

    async def test_close_session(self):
        """Test closing session"""
        # Create a session first
        await self.twitter_source._get_session()
        assert self.twitter_source.session is not None
        
        # Close it
        await self.twitter_source.close()
        assert self.twitter_source.session is None

    async def test_close_no_session(self):
        """Test closing when no session exists"""
        assert self.twitter_source.session is None
        await self.twitter_source.close()  # Should not raise error
        assert self.twitter_source.session is None

    @patch("aiohttp.ClientSession.get")
    async def test_parse_twitter_response_with_date_params(self, mock_get):
        """Test search with date parameters"""
        from datetime import datetime
        
        mock_response = Mock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={"data": []})
        mock_get.return_value.__aenter__.return_value = mock_response

        query = SearchQuery(
            query="test", 
            limit=10,
            start_date=datetime(2023, 1, 1),
            end_date=datetime(2023, 1, 2)
        )
        await self.twitter_source.search_posts(query)

        # Verify the call was made with date parameters
        call_args = mock_get.call_args
        params = call_args[1]['params']
        assert 'start_time' in params
        assert 'end_time' in params

    @patch("aiohttp.ClientSession.get")
    async def test_parse_twitter_malformed_tweet(self, mock_get):
        """Test parsing malformed tweet data"""
        mock_response = Mock()
        mock_response.status = 200
        mock_response.json = AsyncMock(
            return_value={
                "data": [
                    {
                        "id": "1",
                        "text": "Valid tweet",
                        "created_at": "2023-01-01T00:00:00.000Z",
                        "author_id": "user1",
                    },
                    {
                        # Missing required fields - should be skipped
                        "id": "2",
                        "text": "Invalid tweet",
                    }
                ],
                "includes": {
                    "users": [
                        {
                            "id": "user1",
                            "username": "testuser",
                        }
                    ]
                },
            }
        )
        mock_get.return_value.__aenter__.return_value = mock_response

        query = SearchQuery(query="test", limit=10)
        posts = await self.twitter_source.search_posts(query)

        # Should only get the valid tweet
        assert len(posts) == 1
        assert posts[0].id == "1"


@pytest.mark.asyncio
class TestRedditDataSource:
    """Test Reddit data source"""

    def setup_method(self):
        config = DataSourceConfig(name="reddit", enabled=True, rate_limit=100)
        self.reddit_source = RedditDataSource(config)

    def test_is_available(self):
        """Test availability"""
        assert self.reddit_source.is_available()

    @patch("aiohttp.ClientSession.get")
    async def test_search_posts_success(self, mock_get):
        """Test successful post search"""
        mock_response = Mock()
        mock_response.status = 200
        mock_response.json = AsyncMock(
            return_value={
                "data": {
                    "children": [
                        {
                            "data": {
                                "id": "1",
                                "title": "Test Post",
                                "selftext": "This is a test post",
                                "created_utc": 1672531200,  # 2023-01-01
                                "author": "testuser",
                                "ups": 100,
                                "num_comments": 10,
                            }
                        }
                    ]
                }
            }
        )
        mock_get.return_value.__aenter__.return_value = mock_response

        query = SearchQuery(query="test", limit=10)
        posts = await self.reddit_source.search_posts(query)

        assert len(posts) == 1
        assert posts[0].id == "1"
        assert "Test Post" in posts[0].text
        assert posts[0].author == "testuser"
        assert posts[0].source == "reddit"

    @patch("aiohttp.ClientSession.get")
    async def test_search_posts_disabled_source(self, mock_get):
        """Test search when source is disabled"""
        config = DataSourceConfig(name="reddit", enabled=False, rate_limit=100)
        reddit_source = RedditDataSource(config)
        
        query = SearchQuery(query="test", limit=10)
        posts = await reddit_source.search_posts(query)
        
        assert posts == []
        mock_get.assert_not_called()

    @patch("aiohttp.ClientSession.get")
    async def test_search_posts_api_error(self, mock_get):
        """Test search with API error"""
        mock_response = Mock()
        mock_response.status = 429  # Rate limit error
        mock_get.return_value.__aenter__.return_value = mock_response

        query = SearchQuery(query="test", limit=10)
        posts = await self.reddit_source.search_posts(query)

        assert posts == []

    @patch("aiohttp.ClientSession.get")
    async def test_search_posts_exception(self, mock_get):
        """Test search with exception"""
        mock_get.side_effect = Exception("Network error")

        query = SearchQuery(query="test", limit=10)
        posts = await self.reddit_source.search_posts(query)

        assert posts == []

    @patch("aiohttp.ClientSession.get")
    async def test_get_user_posts_success(self, mock_get):
        """Test successful user posts retrieval"""
        mock_response = Mock()
        mock_response.status = 200
        mock_response.json = AsyncMock(
            return_value={
                "data": {
                    "children": [
                        {
                            "data": {
                                "id": "2",
                                "title": "User Post",
                                "selftext": "",
                                "created_utc": 1672531200,
                                "author": "testuser",
                                "ups": 50,
                                "num_comments": 5,
                            }
                        }
                    ]
                }
            }
        )
        mock_get.return_value.__aenter__.return_value = mock_response

        posts = await self.reddit_source.get_user_posts("testuser", limit=10)

        assert len(posts) == 1
        assert posts[0].id == "2"
        assert posts[0].text == "User Post"
        assert posts[0].author == "testuser"

    @patch("aiohttp.ClientSession.get")
    async def test_get_user_posts_disabled_source(self, mock_get):
        """Test user posts when source is disabled"""
        config = DataSourceConfig(name="reddit", enabled=False, rate_limit=100)
        reddit_source = RedditDataSource(config)
        
        posts = await reddit_source.get_user_posts("testuser", limit=10)
        
        assert posts == []
        mock_get.assert_not_called()

    @patch("aiohttp.ClientSession.get")
    async def test_get_user_posts_api_error(self, mock_get):
        """Test user posts with API error"""
        mock_response = Mock()
        mock_response.status = 404
        mock_get.return_value.__aenter__.return_value = mock_response

        posts = await self.reddit_source.get_user_posts("testuser", limit=10)

        assert posts == []

    @patch("aiohttp.ClientSession.get")
    async def test_get_user_posts_exception(self, mock_get):
        """Test user posts with exception"""
        mock_get.side_effect = Exception("Network error")

        posts = await self.reddit_source.get_user_posts("testuser", limit=10)

        assert posts == []

    def test_get_rate_limit_info(self):
        """Test rate limit info"""
        info = self.reddit_source.get_rate_limit_info()
        assert info["requests_per_hour"] == 100
        assert "remaining" in info
        assert "reset_time" in info

    async def test_close_session(self):
        """Test closing session"""
        # Create a session first
        await self.reddit_source._get_session()
        assert self.reddit_source.session is not None
        
        # Close it
        await self.reddit_source.close()
        assert self.reddit_source.session is None

    async def test_close_no_session(self):
        """Test closing when no session exists"""
        assert self.reddit_source.session is None
        await self.reddit_source.close()  # Should not raise error
        assert self.reddit_source.session is None

    @patch("aiohttp.ClientSession.get")
    async def test_parse_reddit_response_deleted_post(self, mock_get):
        """Test parsing with deleted/removed posts"""
        mock_response = Mock()
        mock_response.status = 200
        mock_response.json = AsyncMock(
            return_value={
                "data": {
                    "children": [
                        {
                            "data": {
                                "id": "1",
                                "title": "Valid Post",
                                "selftext": "Content",
                                "created_utc": 1672531200,
                                "author": "testuser",
                                "ups": 100,
                                "num_comments": 10,
                            }
                        },
                        {
                            "data": {
                                "id": "2",
                                "title": "Deleted Post",
                                "author": "[deleted]",  # Should be skipped
                                "created_utc": 1672531200,
                            }
                        },
                        {
                            "data": {
                                "id": "3",
                                "title": "Removed Post",
                                "removed_by_category": "moderator",  # Should be skipped
                                "created_utc": 1672531200,
                                "author": "user",
                            }
                        },
                        {
                            "data": {
                                "id": "4",
                                "title": "",  # Empty title should be skipped
                                "selftext": "",
                                "created_utc": 1672531200,
                                "author": "user",
                            }
                        },
                    ]
                }
            }
        )
        mock_get.return_value.__aenter__.return_value = mock_response

        query = SearchQuery(query="test", limit=10)
        posts = await self.reddit_source.search_posts(query)

        # Should only get the valid post
        assert len(posts) == 1
        assert posts[0].id == "1"

    @patch("aiohttp.ClientSession.get")
    async def test_parse_reddit_malformed_post(self, mock_get):
        """Test parsing malformed post data"""
        mock_response = Mock()
        mock_response.status = 200
        mock_response.json = AsyncMock(
            return_value={
                "data": {
                    "children": [
                        {
                            "data": {
                                "id": "1",
                                "title": "Valid Post",
                                "selftext": "Content",
                                "created_utc": 1672531200,
                                "author": "testuser",
                                "ups": 100,
                                "num_comments": 10,
                            }
                        },
                        {
                            "data": {
                                # Missing required 'id' field - should be skipped
                                "title": "Malformed Post",
                                "created_utc": 1672531200,
                                "author": "user",
                            }
                        },
                    ]
                }
            }
        )
        mock_get.return_value.__aenter__.return_value = mock_response

        query = SearchQuery(query="test", limit=10)
        posts = await self.reddit_source.search_posts(query)

        # Should only get the valid post
        assert len(posts) == 1
        assert posts[0].id == "1"


if __name__ == "__main__":
    pytest.main([__file__])
