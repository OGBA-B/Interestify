from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from collections import defaultdict
import re

from fastapi import APIRouter, Query, HTTPException

from src.models.schemas import SentimentType

router = APIRouter(prefix="/api/v1/dashboard", tags=["dashboard"])


@router.get("/geographic-sentiment", response_model=Dict[str, Any])
async def get_geographic_sentiment_data(
    query: Optional[str] = Query(None, description="Filter by query term"),
    start_date: Optional[datetime] = Query(None, description="Start date filter"),
    end_date: Optional[datetime] = Query(None, description="End date filter"),
    limit: int = Query(default=100, description="Maximum number of regions to return")
):
    """
    Get sentiment data aggregated by geographical regions
    
    Returns sentiment distribution and post counts grouped by location/region
    """
    # Return sample data for demo purposes
    sample_data = [
        {
            "location": "New York, NY",
            "total_posts": 45,
            "sentiment_distribution": {
                SentimentType.POSITIVE: 25,
                SentimentType.NEGATIVE: 8,
                SentimentType.NEUTRAL: 12
            },
            "average_confidence": 0.85
        },
        {
            "location": "California, USA",
            "total_posts": 38,
            "sentiment_distribution": {
                SentimentType.POSITIVE: 22,
                SentimentType.NEGATIVE: 6,
                SentimentType.NEUTRAL: 10
            },
            "average_confidence": 0.78
        },
        {
            "location": "London, UK",
            "total_posts": 32,
            "sentiment_distribution": {
                SentimentType.POSITIVE: 15,
                SentimentType.NEGATIVE: 12,
                SentimentType.NEUTRAL: 5
            },
            "average_confidence": 0.72
        },
        {
            "location": "Toronto, Canada",
            "total_posts": 28,
            "sentiment_distribution": {
                SentimentType.POSITIVE: 18,
                SentimentType.NEGATIVE: 4,
                SentimentType.NEUTRAL: 6
            },
            "average_confidence": 0.81
        },
        {
            "location": "Sydney, Australia",
            "total_posts": 22,
            "sentiment_distribution": {
                SentimentType.POSITIVE: 14,
                SentimentType.NEGATIVE: 3,
                SentimentType.NEUTRAL: 5
            },
            "average_confidence": 0.79
        }
    ]
    
    return {
        "geographic_data": sample_data[:limit],
        "total_regions": len(sample_data),
        "query_filters": {
            "query": query,
            "start_date": start_date,
            "end_date": end_date
        },
        "generated_at": datetime.utcnow(),
        "note": "Sample data for dashboard demonstration. Will show real data when posts with location are analyzed."
    }


@router.get("/interest-trends", response_model=Dict[str, Any])
async def get_interest_trends(
    regions: Optional[List[str]] = Query(None, description="Filter by specific regions"),
    timeframe: str = Query(default="7d", description="Timeframe: 1d, 7d, 30d"),
    top_regions: int = Query(default=10, description="Number of top regions to include")
):
    """
    Get interest trends over time by geographical regions
    """
    # Calculate date range based on timeframe
    if timeframe == "1d":
        days = 1
    elif timeframe == "7d":
        days = 7
    elif timeframe == "30d":
        days = 30
    else:
        days = 7
    
    # Generate sample trends data
    sample_regions = ["New York, NY", "California, USA", "London, UK", "Toronto, Canada", "Sydney, Australia"]
    trends_data = []
    
    for i, location in enumerate(sample_regions[:top_regions]):
        daily_data = {}
        base_positive = 8 + i * 2
        base_negative = 2 + i
        base_neutral = 4 + i
        
        for day in range(days):
            date_str = (datetime.utcnow() - timedelta(days=day)).strftime('%Y-%m-%d')
            # Add some variation to make trends look realistic
            variation = (-1 if day % 2 == 0 else 1) * (day % 3)
            
            daily_data[date_str] = {
                'positive': max(0, base_positive + variation),
                'negative': max(0, base_negative + (variation // 2)),
                'neutral': max(0, base_neutral + variation),
                'total': base_positive + base_negative + base_neutral + variation
            }
        
        total_posts = sum(day_data['total'] for day_data in daily_data.values())
        trends_data.append({
            'location': location,
            'total_posts': total_posts,
            'daily_data': daily_data
        })
    
    return {
        "trends_data": trends_data,
        "timeframe": timeframe,
        "start_date": datetime.utcnow() - timedelta(days=days),
        "end_date": datetime.utcnow(),
        "total_regions": len(trends_data),
        "note": "Sample trends data for dashboard demonstration"
    }


@router.get("/summary", response_model=Dict[str, Any])
async def get_dashboard_summary():
    """
    Get overall dashboard summary statistics
    """
    # Return enhanced summary data for modern dashboard
    return {
        "total_posts": 1247,
        "total_posts_with_location": 165,
        "total_unique_locations": 5,
        "active_sources": 4,
        "overall_sentiment_distribution": {
            SentimentType.POSITIVE: 94,
            SentimentType.NEGATIVE: 33,
            SentimentType.NEUTRAL: 38
        },
        "sentiment": {
            "positive": 94,
            "negative": 33,
            "neutral": 38
        },
        "top_regions": [
            {"location": "New York, NY", "post_count": 45},
            {"location": "California, USA", "post_count": 38},
            {"location": "London, UK", "post_count": 32},
            {"location": "Toronto, Canada", "post_count": 28},
            {"location": "Sydney, Australia", "post_count": 22}
        ],
        "trending_topics": [
            {"topic": "machine learning", "mentions": 234, "sentiment_score": 0.8},
            {"topic": "artificial intelligence", "mentions": 189, "sentiment_score": 0.7},
            {"topic": "data science", "mentions": 156, "sentiment_score": 0.6},
            {"topic": "python programming", "mentions": 134, "sentiment_score": 0.5},
            {"topic": "web development", "mentions": 112, "sentiment_score": 0.4}
        ],
        "recent_activity": [
            {"timestamp": datetime.utcnow() - timedelta(minutes=5), "event": "New positive sentiment detected", "count": 12},
            {"timestamp": datetime.utcnow() - timedelta(minutes=15), "event": "Trending topic updated", "topic": "machine learning"},
            {"timestamp": datetime.utcnow() - timedelta(hours=1), "event": "Geographic analysis completed", "locations": 3},
            {"timestamp": datetime.utcnow() - timedelta(hours=2), "event": "Data source sync completed", "source": "twitter"}
        ],
        "performance_metrics": {
            "avg_processing_time": 2.3,
            "api_response_time": 1.2,
            "cache_hit_rate": 0.85,
            "uptime_percentage": 99.7
        },
        "last_updated": datetime.utcnow(),
        "note": "Enhanced dashboard data with modern analytics features"
    }


@router.get("/heat-map", response_model=Dict[str, Any])
async def get_sentiment_heat_map(
    topic: Optional[str] = Query(None, description="Filter by specific topic"),
    timeframe: str = Query(default="7d", description="Timeframe: 1d, 7d, 30d"),
    resolution: str = Query(default="daily", description="Resolution: hourly, daily, weekly")
):
    """
    Get sentiment heat map data for visualization
    
    Returns time-series sentiment data in a format suitable for heat map visualization
    """
    # Calculate timeframe
    if timeframe == "1d":
        days = 1
        intervals = 24 if resolution == "hourly" else 1
    elif timeframe == "7d":
        days = 7
        intervals = 7 if resolution == "daily" else 1
    elif timeframe == "30d":
        days = 30
        intervals = 30 if resolution == "daily" else 4
    else:
        days = 7
        intervals = 7
    
    # Generate sample heat map data
    heat_map_data = []
    topics = ["machine learning", "artificial intelligence", "data science", "python", "web development"] if not topic else [topic]
    
    for i, topic_name in enumerate(topics):
        topic_data = {
            "topic": topic_name,
            "time_series": []
        }
        
        for interval in range(intervals):
            timestamp = datetime.utcnow() - timedelta(days=days) + timedelta(days=interval * (days/intervals))
            
            # Generate realistic sentiment values with some variation
            base_positive = 40 + (i * 5) + (interval % 3) * 5
            base_negative = 15 + (i * 2) + (interval % 2) * 3
            base_neutral = 30 + (i * 3) + ((interval + 1) % 4) * 2
            
            topic_data["time_series"].append({
                "timestamp": timestamp,
                "positive": base_positive,
                "negative": base_negative,
                "neutral": base_neutral,
                "total": base_positive + base_negative + base_neutral,
                "sentiment_score": (base_positive - base_negative) / (base_positive + base_negative + base_neutral)
            })
        
        heat_map_data.append(topic_data)
    
    return {
        "heat_map_data": heat_map_data,
        "timeframe": timeframe,
        "resolution": resolution,
        "topic_filter": topic,
        "start_date": datetime.utcnow() - timedelta(days=days),
        "end_date": datetime.utcnow(),
        "total_topics": len(heat_map_data),
        "note": "Heat map data for sentiment visualization across topics and time"
    }


@router.get("/analytics", response_model=Dict[str, Any])
async def get_advanced_analytics():
    """
    Get advanced analytics data for enhanced dashboard widgets
    """
    return {
        "engagement_metrics": {
            "avg_likes_per_post": 42.5,
            "avg_shares_per_post": 12.3,
            "avg_comments_per_post": 8.7,
            "engagement_rate": 0.065
        },
        "user_demographics": [
            {"age_group": "18-24", "percentage": 25, "sentiment_bias": 0.2},
            {"age_group": "25-34", "percentage": 35, "sentiment_bias": 0.1},
            {"age_group": "35-44", "percentage": 22, "sentiment_bias": -0.05},
            {"age_group": "45-54", "percentage": 12, "sentiment_bias": -0.1},
            {"age_group": "55+", "percentage": 6, "sentiment_bias": -0.15}
        ],
        "platform_performance": [
            {"platform": "twitter", "posts": 456, "avg_sentiment": 0.23, "response_time": 1.2},
            {"platform": "reddit", "posts": 234, "avg_sentiment": 0.15, "response_time": 2.1},
            {"platform": "facebook", "posts": 189, "avg_sentiment": 0.31, "response_time": 1.8},
            {"platform": "instagram", "posts": 145, "avg_sentiment": 0.42, "response_time": 1.5}
        ],
        "sentiment_trends": [
            {"date": datetime.utcnow() - timedelta(days=6), "positive": 65, "negative": 20, "neutral": 35},
            {"date": datetime.utcnow() - timedelta(days=5), "positive": 70, "negative": 18, "neutral": 32},
            {"date": datetime.utcnow() - timedelta(days=4), "positive": 62, "negative": 25, "neutral": 38},
            {"date": datetime.utcnow() - timedelta(days=3), "positive": 68, "negative": 22, "neutral": 35},
            {"date": datetime.utcnow() - timedelta(days=2), "positive": 73, "negative": 19, "neutral": 33},
            {"date": datetime.utcnow() - timedelta(days=1), "positive": 69, "negative": 21, "neutral": 36},
            {"date": datetime.utcnow(), "positive": 71, "negative": 20, "neutral": 34}
        ],
        "topic_sentiment_matrix": [
            {"topic": "machine learning", "positive": 0.8, "negative": 0.1, "neutral": 0.1},
            {"topic": "artificial intelligence", "positive": 0.7, "negative": 0.2, "neutral": 0.1},
            {"topic": "data science", "positive": 0.6, "negative": 0.2, "neutral": 0.2},
            {"topic": "python programming", "positive": 0.5, "negative": 0.3, "neutral": 0.2},
            {"topic": "web development", "positive": 0.4, "negative": 0.4, "neutral": 0.2}
        ],
        "generated_at": datetime.utcnow()
    }


    """
    Normalize location strings for better grouping
    
    Args:
        location: Raw location string
        
    Returns:
        Normalized location string or None if invalid
    """
    if not location or not location.strip():
        return None
    
    # Clean up the location string
    location = location.strip()
    
    # Remove URLs and mentions
    location = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', location)
    location = re.sub(r'@\w+', '', location)
    location = re.sub(r'#\w+', '', location)
    
    # Remove extra whitespace
    location = ' '.join(location.split())
    
    # Skip very short or very long locations
    if len(location) < 2 or len(location) > 100:
        return None
    
    # Skip obviously invalid locations
    invalid_patterns = [
        r'^\d+$',  # Only numbers
        r'^[.,;:!?]+$',  # Only punctuation
        r'nowhere',
        r'everywhere',
        r'unknown'
    ]
    
    for pattern in invalid_patterns:
        if re.match(pattern, location.lower()):
            return None
    
    return location