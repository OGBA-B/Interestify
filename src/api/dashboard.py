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
    # Return sample summary data for demo
    return {
        "total_posts_with_location": 165,
        "total_unique_locations": 5,
        "overall_sentiment_distribution": {
            SentimentType.POSITIVE: 94,
            SentimentType.NEGATIVE: 33,
            SentimentType.NEUTRAL: 38
        },
        "top_regions": [
            {"location": "New York, NY", "post_count": 45},
            {"location": "California, USA", "post_count": 38},
            {"location": "London, UK", "post_count": 32},
            {"location": "Toronto, Canada", "post_count": 28},
            {"location": "Sydney, Australia", "post_count": 22}
        ],
        "last_updated": datetime.utcnow(),
        "note": "Sample data for dashboard demonstration. Dashboard ready for real data when posts with location information are analyzed."
    }


def _normalize_location(location: str) -> Optional[str]:
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