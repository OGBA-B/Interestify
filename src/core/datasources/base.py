from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime
from src.models.schemas import Post, SearchQuery, DataSourceConfig


class DataSource(ABC):
    """Abstract base class for data sources"""

    def __init__(self, config: DataSourceConfig):
        self.config = config
        self.name = config.name

    @abstractmethod
    async def search_posts(self, query: SearchQuery) -> List[Post]:
        """
        Search for posts based on query parameters

        Args:
            query: SearchQuery object with search parameters

        Returns:
            List of Post objects
        """
        pass

    @abstractmethod
    async def get_user_posts(self, user_id: str, limit: int = 50) -> List[Post]:
        """
        Get posts from a specific user

        Args:
            user_id: User identifier
            limit: Maximum number of posts to return

        Returns:
            List of Post objects
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if the data source is available and properly configured

        Returns:
            True if available, False otherwise
        """
        pass

    @abstractmethod
    def get_rate_limit_info(self) -> Dict[str, Any]:
        """
        Get current rate limit information

        Returns:
            Dict with rate limit details
        """
        pass

    def detect_bot(self, post: Post) -> float:
        """
        Detect if a post is likely from a bot

        Args:
            post: Post object to analyze

        Returns:
            Confidence score (0-1) where 1 is definitely human
        """
        # Basic bot detection heuristics
        confidence = 1.0

        # Check for very high engagement ratios (suspicious)
        if post.engagement_stats.likes > 10000 and len(post.text) < 50:
            confidence -= 0.3

        # Check for repetitive patterns
        if post.text.count("#") > 5:
            confidence -= 0.2

        # Check for excessive mentions
        if len(post.mentions) > 3:
            confidence -= 0.2

        # Check for generic/template-like text
        generic_phrases = [
            "click here",
            "follow me",
            "check out",
            "amazing deal",
            "limited time",
            "act now",
            "free money",
            "get rich",
        ]

        text_lower = post.text.lower()
        for phrase in generic_phrases:
            if phrase in text_lower:
                confidence -= 0.1

        return max(0.0, min(1.0, confidence))

    def filter_posts(
        self, posts: List[Post], min_confidence: float = 0.5
    ) -> List[Post]:
        """
        Filter posts based on bot detection confidence

        Args:
            posts: List of posts to filter
            min_confidence: Minimum confidence threshold

        Returns:
            Filtered list of posts
        """
        filtered_posts = []

        for post in posts:
            confidence = self.detect_bot(post)
            post.confidence_score = confidence

            if confidence >= min_confidence:
                filtered_posts.append(post)

        return filtered_posts

    def _normalize_text(self, text: str) -> str:
        """
        Normalize text for consistent processing
        """
        # Remove excessive whitespace
        text = " ".join(text.split())

        # Remove null bytes and other problematic characters
        text = text.replace("\x00", "").replace("\r", " ").replace("\n", " ")

        return text.strip()

    def _extract_hashtags(self, text: str) -> List[str]:
        """Extract hashtags from text"""
        import re

        hashtags = re.findall(r"#\w+", text)
        return [tag.lower() for tag in hashtags]

    def _extract_mentions(self, text: str) -> List[str]:
        """Extract mentions from text"""
        import re

        mentions = re.findall(r"@\w+", text)
        return [mention.lower() for mention in mentions]

    def _extract_urls(self, text: str) -> List[str]:
        """Extract URLs from text"""
        import re

        urls = re.findall(
            r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+",
            text,
        )
        return urls
