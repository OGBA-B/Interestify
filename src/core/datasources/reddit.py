import asyncio
import json
from datetime import datetime
from typing import Any, Dict, List, Optional

import aiohttp

from src.models.schemas import DataSourceConfig, EngagementStats, Post, SearchQuery

from .base import DataSource


class RedditDataSource(DataSource):
    """Reddit data source implementation"""

    def __init__(self, config: DataSourceConfig):
        super().__init__(config)
        self.base_url = "https://www.reddit.com"
        self.session = None

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session"""
        if self.session is None:
            headers = {
                "User-Agent": "Interestify/1.0",
                "Content-Type": "application/json",
            }
            timeout = aiohttp.ClientTimeout(total=self.config.timeout)
            self.session = aiohttp.ClientSession(headers=headers, timeout=timeout)
        return self.session

    async def search_posts(self, query: SearchQuery) -> List[Post]:
        """
        Search for Reddit posts using Reddit API
        """
        if not self.is_available():
            return []

        session = await self._get_session()

        # Use Reddit search API
        params = {
            "q": query.query,
            "limit": min(query.limit, 100),
            "sort": "relevance",
            "type": "link",
            "include_over_18": "false",
        }

        try:
            async with session.get(
                f"{self.base_url}/search.json", params=params
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._parse_reddit_response(data)
                else:
                    print(f"Reddit API error: {response.status}")
                    return []
        except Exception as e:
            print(f"Reddit search error: {e}")
            return []

    async def get_user_posts(self, user_id: str, limit: int = 50) -> List[Post]:
        """
        Get posts from a specific Reddit user
        """
        if not self.is_available():
            return []

        session = await self._get_session()

        params = {"limit": min(limit, 100), "sort": "new"}

        try:
            async with session.get(
                f"{self.base_url}/user/{user_id}/submitted.json", params=params
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._parse_reddit_response(data)
                else:
                    print(f"Reddit API error: {response.status}")
                    return []
        except Exception as e:
            print(f"Reddit user posts error: {e}")
            return []

    def is_available(self) -> bool:
        """Check if Reddit API is available"""
        return self.config.enabled

    def get_rate_limit_info(self) -> Dict[str, Any]:
        """Get Reddit API rate limit info"""
        return {
            "requests_per_hour": self.config.rate_limit,
            "remaining": self.config.rate_limit,
            "reset_time": None,
        }

    def _parse_reddit_response(self, data: Dict[str, Any]) -> List[Post]:
        """Parse Reddit API response into Post objects"""
        posts = []

        # Reddit API returns data in a nested structure
        items = data.get("data", {}).get("children", [])

        for item in items:
            try:
                post_data = item.get("data", {})

                # Skip removed or deleted posts
                if (
                    post_data.get("removed_by_category")
                    or post_data.get("author") == "[deleted]"
                ):
                    continue

                # Parse engagement metrics
                engagement_stats = EngagementStats(
                    likes=post_data.get("ups", 0),
                    shares=0,  # Reddit doesn't have shares
                    comments=post_data.get("num_comments", 0),
                    views=0,  # Not available in Reddit API
                )

                # Combine title and selftext for full content
                title = post_data.get("title", "")
                selftext = post_data.get("selftext", "")
                full_text = f"{title}\n{selftext}".strip()

                if not full_text:
                    continue

                # Create Post object
                post = Post(
                    id=post_data["id"],
                    text=self._normalize_text(full_text),
                    timestamp=datetime.fromtimestamp(post_data["created_utc"]),
                    author=post_data.get("author", "unknown"),
                    author_id=post_data.get("author", "unknown"),
                    location=None,  # Reddit doesn't provide location
                    engagement_stats=engagement_stats,
                    source="reddit",
                    confidence_score=1.0,  # Will be set by bot detection
                    language="en",  # Reddit is primarily English
                    hashtags=self._extract_hashtags(full_text),
                    mentions=self._extract_mentions(full_text),
                    urls=self._extract_urls(full_text),
                )

                posts.append(post)

            except Exception as e:
                print(
                    f"Error parsing Reddit post {item.get('data', {}).get('id', 'unknown')}: {e}"
                )
                continue

        return self.filter_posts(posts, self.config.bot_detection_threshold)

    async def close(self):
        """Close the HTTP session"""
        if self.session:
            await self.session.close()
            self.session = None
