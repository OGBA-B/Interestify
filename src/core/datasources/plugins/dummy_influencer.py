from datetime import datetime

from src.core.datasources.base import DataSource
from src.models.schemas import EngagementStats, Post, SearchQuery


class DummyInfluencerSource(DataSource):
    """A dummy data source for influencer/celebrity testing"""

    async def search_posts(self, query: SearchQuery):
        # Simulate posts with follower/following info
        return [
            Post(
                id="1",
                text="I love my fans!",
                timestamp=datetime.now(),
                author="celebrity1",
                author_id="celebrity1",
                engagement_stats=EngagementStats(likes=10000, comments=500),
                source="dummy_influencer",
                confidence_score=0.99,
                followers=1000000,
                following=100,
            ),
            Post(
                id="2",
                text="Feeling grateful.",
                timestamp=datetime.now(),
                author="influencer2",
                author_id="influencer2",
                engagement_stats=EngagementStats(likes=5000, comments=200),
                source="dummy_influencer",
                confidence_score=0.98,
                followers=500000,
                following=50,
            ),
        ]

    async def get_user_posts(self, user_id: str, limit: int = 50):
        # Simulate user posts
        return [
            Post(
                id="3",
                text="Another day, another post!",
                timestamp=datetime.now(),
                author=user_id,
                author_id=user_id,
                engagement_stats=EngagementStats(likes=100, comments=10),
                source="dummy_influencer",
                confidence_score=0.95,
                followers=10000,
                following=100,
            )
        ]

    def is_available(self):
        return True

    def get_rate_limit_info(self):
        return {"limit": 1000, "remaining": 999}
