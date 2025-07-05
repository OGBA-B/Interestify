import asyncio
import json
from datetime import datetime
from typing import Any, Dict, List, Optional

import aiohttp

from src.models.schemas import DataSourceConfig, EngagementStats, Post, SearchQuery

from .base import DataSource


class TwitterDataSource(DataSource):
    """Twitter/X data source implementation"""

    def __init__(self, config: DataSourceConfig):
        super().__init__(config)
        self.base_url = "https://api.twitter.com/2"
        self.session = None

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session"""
        if self.session is None:
            headers = {
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json",
            }
            timeout = aiohttp.ClientTimeout(total=self.config.timeout)
            self.session = aiohttp.ClientSession(headers=headers, timeout=timeout)
        return self.session

    async def search_posts(self, query: SearchQuery) -> List[Post]:
        """
        Search for tweets using Twitter API v2
        """
        if not self.is_available():
            return []

        session = await self._get_session()

        # Build search parameters
        params = {
            "query": query.query,
            "max_results": min(query.limit, 100),  # Twitter API limit
            "tweet.fields": "created_at,author_id,context_annotations,entities,public_metrics,lang,geo",
            "user.fields": "username,name,location,verified",
            "expansions": "author_id",
        }

        if query.start_date:
            params["start_time"] = query.start_date.isoformat()

        if query.end_date:
            params["end_time"] = query.end_date.isoformat()

        try:
            async with session.get(
                f"{self.base_url}/tweets/search/recent", params=params
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._parse_twitter_response(data)
                else:
                    print(f"Twitter API error: {response.status}")
                    return []
        except Exception as e:
            print(f"Twitter search error: {e}")
            return []

    async def get_user_posts(self, user_id: str, limit: int = 50) -> List[Post]:
        """
        Get posts from a specific Twitter user
        """
        if not self.is_available():
            return []

        session = await self._get_session()

        params = {
            "max_results": min(limit, 100),
            "tweet.fields": "created_at,author_id,context_annotations,entities,public_metrics,lang,geo",
            "user.fields": "username,name,location,verified",
        }

        try:
            async with session.get(
                f"{self.base_url}/users/{user_id}/tweets", params=params
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._parse_twitter_response(data)
                else:
                    print(f"Twitter API error: {response.status}")
                    return []
        except Exception as e:
            print(f"Twitter user posts error: {e}")
            return []

    def is_available(self) -> bool:
        """Check if Twitter API is properly configured"""
        return bool(self.config.api_key and self.config.enabled)

    def get_rate_limit_info(self) -> Dict[str, Any]:
        """Get Twitter API rate limit info"""
        return {
            "requests_per_hour": self.config.rate_limit,
            "remaining": self.config.rate_limit,  # Would need to track this
            "reset_time": None,
        }

    def _parse_twitter_response(self, data: Dict[str, Any]) -> List[Post]:
        """Parse Twitter API response into Post objects"""
        posts = []

        tweets = data.get("data", [])
        users = {user["id"]: user for user in data.get("includes", {}).get("users", [])}

        for tweet in tweets:
            try:
                author_id = tweet.get("author_id")
                author_info = users.get(author_id, {})

                # Parse engagement metrics
                metrics = tweet.get("public_metrics", {})
                engagement_stats = EngagementStats(
                    likes=metrics.get("like_count", 0),
                    shares=metrics.get("retweet_count", 0),
                    comments=metrics.get("reply_count", 0),
                    views=metrics.get("impression_count", 0),
                )

                # Parse entities
                entities = tweet.get("entities", {})
                hashtags = [tag["tag"] for tag in entities.get("hashtags", [])]
                mentions = [
                    mention["username"] for mention in entities.get("mentions", [])
                ]
                urls = [url["expanded_url"] for url in entities.get("urls", [])]

                # Create Post object
                post = Post(
                    id=tweet["id"],
                    text=self._normalize_text(tweet["text"]),
                    timestamp=datetime.fromisoformat(
                        tweet["created_at"].replace("Z", "+00:00")
                    ),
                    author=author_info.get("username", "unknown"),
                    author_id=author_id,
                    location=author_info.get("location"),
                    engagement_stats=engagement_stats,
                    source="twitter",
                    confidence_score=1.0,  # Will be set by bot detection
                    language=tweet.get("lang", "en"),
                    hashtags=hashtags,
                    mentions=mentions,
                    urls=urls,
                )

                posts.append(post)

            except Exception as e:
                print(f"Error parsing tweet {tweet.get('id', 'unknown')}: {e}")
                continue

        return self.filter_posts(posts, self.config.bot_detection_threshold)

    async def close(self):
        """Close the HTTP session"""
        if self.session:
            await self.session.close()
            self.session = None
