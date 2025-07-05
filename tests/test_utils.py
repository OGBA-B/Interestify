from datetime import datetime
from unittest.mock import AsyncMock, Mock, patch

import pytest

from src.utils.pagination import (
    PaginatedResponse,
    create_paginated_response,
    paginate_results,
)


class TestPagination:
    """Test pagination utilities"""

    def test_paginate_results_normal_case(self):
        """Test normal pagination"""
        items = list(range(100))

        # First page
        page1 = paginate_results(items, offset=0, limit=10)
        assert len(page1) == 10
        assert page1 == list(range(10))

        # Middle page
        page5 = paginate_results(items, offset=40, limit=10)
        assert len(page5) == 10
        assert page5 == list(range(40, 50))

        # Last page
        page10 = paginate_results(items, offset=90, limit=10)
        assert len(page10) == 10
        assert page10 == list(range(90, 100))

    def test_paginate_results_partial_page(self):
        """Test pagination with partial last page"""
        items = list(range(25))

        # Partial last page
        last_page = paginate_results(items, offset=20, limit=10)
        assert len(last_page) == 5
        assert last_page == list(range(20, 25))

    def test_paginate_results_empty(self):
        """Test pagination with empty list"""
        items = []

        result = paginate_results(items, offset=0, limit=10)
        assert len(result) == 0
        assert result == []

    def test_paginate_results_single_item(self):
        """Test pagination with single item"""
        items = [1]

        result = paginate_results(items, offset=0, limit=10)
        assert len(result) == 1
        assert result == [1]

    def test_paginate_results_beyond_range(self):
        """Test pagination beyond available items"""
        items = list(range(10))

        result = paginate_results(items, offset=20, limit=10)
        assert len(result) == 0
        assert result == []

    def test_paginate_results_negative_offset(self):
        """Test pagination with negative offset"""
        items = list(range(10))

        result = paginate_results(items, offset=-5, limit=3)
        assert len(result) == 3
        assert result == list(range(3))

    def test_paginate_results_zero_limit(self):
        """Test pagination with zero limit"""
        items = list(range(100))

        result = paginate_results(items, offset=0, limit=0)
        assert len(result) == 50  # Default limit
        assert result == list(range(50))

    def test_paginate_results_negative_limit(self):
        """Test pagination with negative limit"""
        items = list(range(100))

        result = paginate_results(items, offset=0, limit=-5)
        assert len(result) == 50  # Default limit
        assert result == list(range(50))

    def test_create_paginated_response_first_page(self):
        """Test creating paginated response for first page"""
        items = list(range(10))

        response = create_paginated_response(items, offset=0, limit=10, total_items=100)

        assert response.total == 100
        assert response.page == 1
        assert response.page_size == 10
        assert response.total_pages == 10
        assert response.has_next is True
        assert response.has_previous is False
        assert len(response.items) == 10

    def test_create_paginated_response_middle_page(self):
        """Test creating paginated response for middle page"""
        items = list(range(20, 30))

        response = create_paginated_response(
            items, offset=20, limit=10, total_items=100
        )

        assert response.total == 100
        assert response.page == 3
        assert response.page_size == 10
        assert response.total_pages == 10
        assert response.has_next is True
        assert response.has_previous is True
        assert len(response.items) == 10

    def test_create_paginated_response_last_page(self):
        """Test creating paginated response for last page"""
        items = list(range(90, 100))

        response = create_paginated_response(
            items, offset=90, limit=10, total_items=100
        )

        assert response.total == 100
        assert response.page == 10
        assert response.page_size == 10
        assert response.total_pages == 10
        assert response.has_next is False
        assert response.has_previous is True
        assert len(response.items) == 10

    def test_create_paginated_response_partial_last_page(self):
        """Test creating paginated response for partial last page"""
        items = list(range(95, 100))

        response = create_paginated_response(
            items, offset=95, limit=10, total_items=100
        )

        assert response.total == 100
        assert response.page == 10
        assert response.page_size == 10
        assert response.total_pages == 10
        assert response.has_next is False
        assert response.has_previous is True
        assert len(response.items) == 5

    def test_create_paginated_response_single_page(self):
        """Test creating paginated response for single page"""
        items = list(range(5))

        response = create_paginated_response(items, offset=0, limit=10, total_items=5)

        assert response.total == 5
        assert response.page == 1
        assert response.page_size == 10
        assert response.total_pages == 1
        assert response.has_next is False
        assert response.has_previous is False
        assert len(response.items) == 5

    def test_create_paginated_response_empty(self):
        """Test creating paginated response for empty results"""
        items = []

        response = create_paginated_response(items, offset=0, limit=10, total_items=0)

        assert response.total == 0
        assert response.page == 1
        assert response.page_size == 10
        assert response.total_pages == 0
        assert response.has_next is False
        assert response.has_previous is False
        assert len(response.items) == 0

    def test_create_paginated_response_zero_limit(self):
        """Test creating paginated response with zero limit"""
        items = []

        response = create_paginated_response(items, offset=0, limit=0, total_items=100)

        assert response.total == 100
        assert response.page == 1
        assert response.page_size == 0
        assert response.total_pages == 1
        assert response.has_next is False
        assert response.has_previous is False

    def test_paginated_response_model(self):
        """Test PaginatedResponse model"""
        items = [1, 2, 3, 4, 5]

        response = PaginatedResponse(
            items=items,
            total=50,
            page=2,
            page_size=5,
            total_pages=10,
            has_next=True,
            has_previous=True,
        )

        assert response.items == items
        assert response.total == 50
        assert response.page == 2
        assert response.page_size == 5
        assert response.total_pages == 10
        assert response.has_next is True
        assert response.has_previous is True


class TestTextProcessing:
    """Test text processing utilities"""

    def test_normalize_text(self):
        """Test text normalization"""
        from src.core.datasources.base import DataSource
        from src.models.schemas import DataSourceConfig

        config = DataSourceConfig(name="test", enabled=True)

        # Create a concrete implementation for testing
        class TestDataSource(DataSource):
            async def search_posts(self, query):
                return []

            async def get_user_posts(self, user_id, limit=50):
                return []

            def is_available(self):
                return True

            def get_rate_limit_info(self):
                return {}

        data_source = TestDataSource(config)

        # Test excessive whitespace
        text = "This    has    too    much    whitespace"
        normalized = data_source._normalize_text(text)
        assert normalized == "This has too much whitespace"

        # Test null bytes and problematic characters
        text = "Text with\x00null\rbytes\nand\nlines"
        normalized = data_source._normalize_text(text)
        assert "\x00" not in normalized
        assert "\r" not in normalized
        assert "\n" not in normalized

        # Test stripping
        text = "   Text with spaces   "
        normalized = data_source._normalize_text(text)
        assert normalized == "Text with spaces"

    def test_extract_hashtags(self):
        """Test hashtag extraction"""
        from src.core.datasources.base import DataSource
        from src.models.schemas import DataSourceConfig

        config = DataSourceConfig(name="test", enabled=True)

        class TestDataSource(DataSource):
            async def search_posts(self, query):
                return []

            async def get_user_posts(self, user_id, limit=50):
                return []

            def is_available(self):
                return True

            def get_rate_limit_info(self):
                return {}

        data_source = TestDataSource(config)

        text = "Love this #awesome #product! #BestDeal ever #sale"
        hashtags = data_source._extract_hashtags(text)

        assert "#awesome" in hashtags
        assert "#product" in hashtags
        assert "#bestdeal" in hashtags  # Should be lowercase
        assert "#sale" in hashtags
        assert len(hashtags) == 4

    def test_extract_mentions(self):
        """Test mention extraction"""
        from src.core.datasources.base import DataSource
        from src.models.schemas import DataSourceConfig

        config = DataSourceConfig(name="test", enabled=True)

        class TestDataSource(DataSource):
            async def search_posts(self, query):
                return []

            async def get_user_posts(self, user_id, limit=50):
                return []

            def is_available(self):
                return True

            def get_rate_limit_info(self):
                return {}

        data_source = TestDataSource(config)

        text = "Hey @user1 and @User2, check out @AWESOME_USER's post!"
        mentions = data_source._extract_mentions(text)

        assert "@user1" in mentions
        assert "@user2" in mentions  # Should be lowercase
        assert "@awesome_user" in mentions  # Should be lowercase
        assert len(mentions) == 3

    def test_extract_urls(self):
        """Test URL extraction"""
        from src.core.datasources.base import DataSource
        from src.models.schemas import DataSourceConfig

        config = DataSourceConfig(name="test", enabled=True)

        class TestDataSource(DataSource):
            async def search_posts(self, query):
                return []

            async def get_user_posts(self, user_id, limit=50):
                return []

            def is_available(self):
                return True

            def get_rate_limit_info(self):
                return {}

        data_source = TestDataSource(config)

        text = "Check out https://example.com and http://test.com/path?param=value"
        urls = data_source._extract_urls(text)

        assert "https://example.com" in urls
        assert "http://test.com/path?param=value" in urls
        assert len(urls) == 2


if __name__ == "__main__":
    pytest.main([__file__])
