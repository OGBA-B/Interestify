from datetime import datetime

from sqlalchemy import JSON, Boolean, Column, DateTime, Float, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class PostTable(Base):
    __tablename__ = "posts"

    id = Column(String, primary_key=True)
    text = Column(Text, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    author = Column(String, nullable=False)
    author_id = Column(String, nullable=False)
    location = Column(String, nullable=True)
    engagement_stats = Column(JSON, nullable=False)
    source = Column(String, nullable=False)
    confidence_score = Column(Float, nullable=False)
    language = Column(String, default="en")
    hashtags = Column(JSON, default=list)
    mentions = Column(JSON, default=list)
    urls = Column(JSON, default=list)
    created_at = Column(DateTime, default=func.now())


class SentimentResultTable(Base):
    __tablename__ = "sentiment_results"

    id = Column(Integer, primary_key=True, autoincrement=True)
    post_id = Column(String, nullable=False)
    sentiment = Column(String, nullable=False)
    confidence = Column(Float, nullable=False)
    polarity = Column(Float, nullable=False)
    subjectivity = Column(Float, nullable=False)
    analyzer_used = Column(String, nullable=False)
    created_at = Column(DateTime, default=func.now())


class DataSourceConfigTable(Base):
    __tablename__ = "data_source_configs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True, nullable=False)
    enabled = Column(Boolean, default=True)
    api_key = Column(String, nullable=True)
    api_secret = Column(String, nullable=True)
    rate_limit = Column(Integer, default=100)
    timeout = Column(Integer, default=30)
    cache_ttl = Column(Integer, default=3600)
    bot_detection_threshold = Column(Float, default=0.8)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class CachedQueryTable(Base):
    __tablename__ = "cached_queries"

    id = Column(Integer, primary_key=True, autoincrement=True)
    query_hash = Column(String, unique=True, nullable=False)
    query_params = Column(JSON, nullable=False)
    result_data = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=func.now())
    expires_at = Column(DateTime, nullable=False)
    hit_count = Column(Integer, default=0)
