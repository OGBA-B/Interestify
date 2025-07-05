# Configuration settings for Interestify

import os
from typing import List, Optional

from pydantic import BaseSettings


class Settings(BaseSettings):
    """Application settings"""

    # Database
    database_url: str = "sqlite+aiosqlite:///./interestify.db"

    # API Keys
    twitter_api_key: Optional[str] = None
    twitter_api_secret: Optional[str] = None
    twitter_access_token: Optional[str] = None
    twitter_access_token_secret: Optional[str] = None

    reddit_client_id: Optional[str] = None
    reddit_client_secret: Optional[str] = None

    # Cache Settings
    cache_ttl: int = 3600
    cache_max_size: int = 1000

    # Rate Limiting
    default_rate_limit: int = 100
    twitter_rate_limit: int = 300
    reddit_rate_limit: int = 60

    # Bot Detection
    bot_detection_threshold: float = 0.8

    # API Settings
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_debug: bool = True

    # CORS Settings
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:8000"]

    # Logging
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Sentiment Analysis
    default_sentiment_analyzer: str = "textblob"

    # Pagination
    default_page_size: int = 50
    max_page_size: int = 500

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings"""
    return settings
