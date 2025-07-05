from datetime import datetime
from typing import Dict, Optional, List
from pydantic import BaseModel, Field
from enum import Enum


class SentimentType(str, Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"


class EngagementStats(BaseModel):
    likes: int = 0
    shares: int = 0
    comments: int = 0
    views: int = 0
    replies: int = 0


class Post(BaseModel):
    id: str
    text: str
    timestamp: datetime
    author: str
    author_id: str
    location: Optional[str] = None
    engagement_stats: EngagementStats
    source: str  # twitter, reddit, facebook, etc.
    confidence_score: float = Field(..., ge=0.0, le=1.0)  # bot detection confidence
    language: Optional[str] = "en"
    hashtags: List[str] = []
    mentions: List[str] = []
    urls: List[str] = []


class SentimentResult(BaseModel):
    post_id: str
    sentiment: SentimentType
    confidence: float = Field(..., ge=0.0, le=1.0)
    polarity: float = Field(..., ge=-1.0, le=1.0)  # -1 (negative) to 1 (positive)
    subjectivity: float = Field(..., ge=0.0, le=1.0)  # 0 (objective) to 1 (subjective)
    analyzer_used: str
    created_at: datetime


class SearchQuery(BaseModel):
    query: str
    data_sources: List[str] = []  # empty means all available sources
    limit: int = Field(default=50, ge=1, le=500)
    offset: int = Field(default=0, ge=0)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    include_sentiment: bool = True
    min_confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    language: Optional[str] = "en"


class DataSourceConfig(BaseModel):
    name: str
    enabled: bool = True
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    rate_limit: int = 100  # requests per hour
    timeout: int = 30  # seconds
    cache_ttl: int = 3600  # seconds
    bot_detection_threshold: float = 0.8


class AnalysisResult(BaseModel):
    query: str
    total_posts: int
    sentiment_distribution: Dict[SentimentType, int]
    average_confidence: float
    sources_used: List[str]
    posts: List[Post]
    sentiment_results: List[SentimentResult]
    created_at: datetime
    processing_time: float
