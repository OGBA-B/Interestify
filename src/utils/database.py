import asyncio
from datetime import datetime
from typing import List, Optional

from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from src.models.database import (
    Base,
    DataSourceConfigTable,
    PostTable,
    SentimentResultTable,
)
from src.models.schemas import AnalysisResult, DataSourceConfig, Post, SentimentResult


class DatabaseManager:
    """Database manager for storing and retrieving data"""

    def __init__(self, database_url: str = "sqlite+aiosqlite:///./interestify.db"):
        self.database_url = database_url
        self.engine = create_async_engine(database_url)
        self.SessionLocal = sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )

    async def init_db(self):
        """Initialize database tables"""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    def get_session(self) -> AsyncSession:
        """Get database session"""
        return self.SessionLocal()

    async def close(self):
        """Close database connection"""
        await self.engine.dispose()

    # Data source configuration methods
    async def save_data_source_config(self, config: DataSourceConfig) -> bool:
        """Save or update data source configuration (upsert)"""
        try:
            async with self.get_session() as session:
                # Check if config exists
                result = await session.execute(
                    text("SELECT * FROM data_source_configs WHERE name = :name"),
                    {"name": config.name},
                )
                row = result.fetchone()
                if row:
                    # Update existing config
                    await session.execute(
                        text(
                            """
                            UPDATE data_source_configs SET enabled=:enabled, api_key=:api_key, api_secret=:api_secret, rate_limit=:rate_limit, timeout=:timeout, cache_ttl=:cache_ttl, bot_detection_threshold=:bot_detection_threshold, updated_at=CURRENT_TIMESTAMP WHERE name=:name
                            """
                        ),
                        {
                            "enabled": config.enabled,
                            "api_key": config.api_key,
                            "api_secret": config.api_secret,
                            "rate_limit": config.rate_limit,
                            "timeout": config.timeout,
                            "cache_ttl": config.cache_ttl,
                            "bot_detection_threshold": config.bot_detection_threshold,
                            "name": config.name,
                        },
                    )
                else:
                    db_config = DataSourceConfigTable(
                        name=config.name,
                        enabled=config.enabled,
                        api_key=config.api_key,
                        api_secret=config.api_secret,
                        rate_limit=config.rate_limit,
                        timeout=config.timeout,
                        cache_ttl=config.cache_ttl,
                        bot_detection_threshold=config.bot_detection_threshold,
                    )
                    session.add(db_config)
                await session.commit()
                return True
        except Exception as e:
            print(f"Error saving data source config: {e}")
            return False

    async def get_data_source_config(self, name: str) -> Optional[DataSourceConfig]:
        """Get data source configuration by name"""
        try:
            async with self.get_session() as session:
                result = await session.execute(
                    text("SELECT * FROM data_source_configs WHERE name = :name"),
                    {"name": name},
                )
                row = result.fetchone()

                if row:
                    return DataSourceConfig(
                        name=row.name,
                        enabled=row.enabled,
                        api_key=row.api_key,
                        api_secret=row.api_secret,
                        rate_limit=row.rate_limit,
                        timeout=row.timeout,
                        cache_ttl=row.cache_ttl,
                        bot_detection_threshold=row.bot_detection_threshold,
                    )
                return None
        except Exception as e:
            print(f"Error getting data source config: {e}")
            return None

    async def get_all_data_source_configs(self) -> List[DataSourceConfig]:
        """Get all data source configurations"""
        try:
            async with self.get_session() as session:
                result = await session.execute(
                    text("SELECT * FROM data_source_configs")
                )
                rows = result.fetchall()

                configs = []
                for row in rows:
                    config = DataSourceConfig(
                        name=row.name,
                        enabled=row.enabled,
                        api_key=row.api_key,
                        api_secret=row.api_secret,
                        rate_limit=row.rate_limit,
                        timeout=row.timeout,
                        cache_ttl=row.cache_ttl,
                        bot_detection_threshold=row.bot_detection_threshold,
                    )
                    configs.append(config)

                return configs
        except Exception as e:
            print(f"Error getting all data source configs: {e}")
            return []

    async def update_data_source_config(
        self, name: str, config: DataSourceConfig
    ) -> bool:
        """Update data source configuration"""
        try:
            async with self.get_session() as session:
                await session.execute(
                    text(
                        """
                        UPDATE data_source_configs 
                        SET enabled = :enabled, api_key = :api_key, api_secret = :api_secret,
                            rate_limit = :rate_limit, timeout = :timeout, cache_ttl = :cache_ttl,
                            bot_detection_threshold = :bot_detection_threshold, updated_at = :updated_at
                        WHERE name = :name
                    """
                    ),
                    {
                        "name": name,
                        "enabled": config.enabled,
                        "api_key": config.api_key,
                        "api_secret": config.api_secret,
                        "rate_limit": config.rate_limit,
                        "timeout": config.timeout,
                        "cache_ttl": config.cache_ttl,
                        "bot_detection_threshold": config.bot_detection_threshold,
                        "updated_at": datetime.utcnow(),
                    },
                )
                await session.commit()
                return True
        except Exception as e:
            print(f"Error updating data source config: {e}")
            return False

    async def delete_data_source_config(self, name: str) -> bool:
        """Delete data source configuration"""
        try:
            async with self.get_session() as session:
                await session.execute(
                    text("DELETE FROM data_source_configs WHERE name = :name"),
                    {"name": name},
                )
                await session.commit()
                return True
        except Exception as e:
            print(f"Error deleting data source config: {e}")
            return False

    # Posts and sentiment results storage
    async def store_analysis_result(self, result: AnalysisResult) -> bool:
        """Store analysis result in database"""
        try:
            async with self.get_session() as session:
                # Store posts
                for post in result.posts:
                    db_post = PostTable(
                        id=post.id,
                        text=post.text,
                        timestamp=post.timestamp,
                        author=post.author,
                        author_id=post.author_id,
                        location=post.location,
                        engagement_stats=post.engagement_stats.dict(),
                        source=post.source,
                        confidence_score=post.confidence_score,
                        language=post.language,
                        hashtags=post.hashtags,
                        mentions=post.mentions,
                        urls=post.urls,
                    )
                    await session.merge(db_post)  # Use merge to handle duplicates

                # Store sentiment results
                for sentiment_result in result.sentiment_results:
                    db_sentiment = SentimentResultTable(
                        post_id=sentiment_result.post_id,
                        sentiment=sentiment_result.sentiment.value,
                        confidence=sentiment_result.confidence,
                        polarity=sentiment_result.polarity,
                        subjectivity=sentiment_result.subjectivity,
                        analyzer_used=sentiment_result.analyzer_used,
                    )
                    session.add(db_sentiment)

                await session.commit()
                return True
        except Exception as e:
            print(f"Error storing analysis result: {e}")
            return False

    async def get_posts_by_query(self, query: str, limit: int = 100) -> List[Post]:
        """Get posts by search query"""
        try:
            async with self.get_session() as session:
                result = await session.execute(
                    text(
                        """
                        SELECT * FROM posts 
                        WHERE text LIKE :query 
                        ORDER BY timestamp DESC 
                        LIMIT :limit
                    """
                    ),
                    {"query": f"%{query}%", "limit": limit},
                )
                rows = result.fetchall()

                posts = []
                import json

                for row in rows:
                    post = Post(
                        id=row.id,
                        text=row.text,
                        timestamp=row.timestamp,
                        author=row.author,
                        author_id=row.author_id,
                        location=row.location,
                        engagement_stats=(
                            json.loads(row.engagement_stats)
                            if isinstance(row.engagement_stats, str)
                            else row.engagement_stats
                        ),
                        source=row.source,
                        confidence_score=row.confidence_score,
                        language=row.language,
                        hashtags=(
                            json.loads(row.hashtags)
                            if isinstance(row.hashtags, str)
                            else row.hashtags
                        ),
                        mentions=(
                            json.loads(row.mentions)
                            if isinstance(row.mentions, str)
                            else row.mentions
                        ),
                        urls=(
                            json.loads(row.urls)
                            if isinstance(row.urls, str)
                            else row.urls
                        ),
                    )
                    posts.append(post)

                return posts
        except Exception as e:
            print(f"Error getting posts by query: {e}")
            return []
