from fastapi import FastAPI, HTTPException, Depends, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List, Optional, Dict, Any
from datetime import datetime
import time
import asyncio

from src.models.schemas import (
    SearchQuery,
    AnalysisResult,
    Post,
    SentimentResult,
    DataSourceConfig,
    SentimentType,
)
from src.core.sentiment import SentimentAnalyzerFactory, default_analyzer
from src.core.datasources import data_source_manager
from src.core.cache import cache_manager
from src.utils.database import DatabaseManager
from src.utils.pagination import PaginatedResponse, paginate_results

app = FastAPI(
    title="Interestify API",
    description="Social media sentiment analysis API",
    version="2.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database
db_manager = DatabaseManager()


@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    await db_manager.init_db()

    # Load configured data sources from database
    configs = await db_manager.get_all_data_source_configs()
    for config in configs:
        data_source_manager.add_data_source(config)


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    await data_source_manager.close_all()
    await db_manager.close()


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow(), "version": "2.0.0"}


# Search and analyze posts
@app.post("/api/v1/analyze", response_model=AnalysisResult)
async def analyze_posts(
    query: SearchQuery,
    analyzer_name: str = Query(
        default="textblob", description="Sentiment analyzer to use"
    ),
    use_cache: bool = Query(
        default=True, description="Use cached results if available"
    ),
):
    """
    Analyze posts from various data sources

    Args:
        query: Search query parameters
        analyzer_name: Name of sentiment analyzer to use
        use_cache: Whether to use cached results

    Returns:
        Analysis results with posts and sentiment analysis
    """
    start_time = time.time()

    # Check cache first
    if use_cache:
        cached_result = cache_manager.get(query)
        if cached_result:
            return cached_result

    # Get enabled data sources
    enabled_sources = data_source_manager.get_enabled_sources()

    if not enabled_sources:
        raise HTTPException(status_code=503, detail="No data sources available")

    # Filter sources based on query
    sources_to_use = enabled_sources
    if query.data_sources:
        sources_to_use = [
            source for source in enabled_sources if source.name in query.data_sources
        ]

    # Collect posts from all sources
    all_posts = []
    sources_used = []

    for source in sources_to_use:
        try:
            posts = await source.search_posts(query)
            all_posts.extend(posts)
            sources_used.append(source.name)
        except Exception as e:
            print(f"Error fetching from {source.name}: {e}")
            continue

    # Apply pagination
    paginated_posts = paginate_results(all_posts, query.offset, query.limit)

    # Perform sentiment analysis if requested
    sentiment_results = []
    if query.include_sentiment:
        try:
            analyzer = SentimentAnalyzerFactory.create_analyzer(analyzer_name)
            sentiment_results = analyzer.process_posts(paginated_posts)
        except Exception as e:
            print(f"Sentiment analysis error: {e}")
            # Continue without sentiment analysis
            pass

    # Calculate sentiment distribution
    sentiment_distribution = {
        SentimentType.POSITIVE: 0,
        SentimentType.NEGATIVE: 0,
        SentimentType.NEUTRAL: 0,
    }

    for result in sentiment_results:
        sentiment_distribution[result.sentiment] += 1

    # Calculate average confidence
    avg_confidence = 0.0
    if sentiment_results:
        avg_confidence = sum(r.confidence for r in sentiment_results) / len(
            sentiment_results
        )

    # Create analysis result
    analysis_result = AnalysisResult(
        query=query.query,
        total_posts=len(all_posts),
        sentiment_distribution=sentiment_distribution,
        average_confidence=avg_confidence,
        sources_used=sources_used,
        posts=paginated_posts,
        sentiment_results=sentiment_results,
        created_at=datetime.utcnow(),
        processing_time=time.time() - start_time,
    )

    # Cache the result
    if use_cache:
        cache_manager.set(query, analysis_result)

    # Store in database (background task)
    background_tasks = BackgroundTasks()
    background_tasks.add_task(store_analysis_result, analysis_result)

    return analysis_result


# Get posts from specific user
@app.get("/api/v1/users/{user_id}/posts", response_model=List[Post])
async def get_user_posts(
    user_id: str,
    source: str = Query(..., description="Data source name"),
    limit: int = Query(default=50, ge=1, le=500),
    include_sentiment: bool = Query(default=True),
):
    """
    Get posts from a specific user

    Args:
        user_id: User identifier
        source: Data source name
        limit: Maximum number of posts to return
        include_sentiment: Whether to include sentiment analysis

    Returns:
        List of posts from the user
    """
    data_source = data_source_manager.get_data_source(source)

    if not data_source:
        raise HTTPException(status_code=404, detail=f"Data source '{source}' not found")

    try:
        posts = await data_source.get_user_posts(user_id, limit)
        return posts
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error fetching user posts: {str(e)}"
        )


# Data source management endpoints
@app.get("/api/v1/datasources", response_model=List[Dict[str, Any]])
async def get_data_sources():
    """Get all configured data sources"""
    sources = []
    for name in data_source_manager.get_configured_sources():
        source = data_source_manager.get_data_source(name)
        sources.append(
            {
                "name": name,
                "enabled": source.config.enabled,
                "available": source.is_available(),
                "rate_limit": source.config.rate_limit,
                "rate_limit_info": source.get_rate_limit_info(),
            }
        )
    return sources


@app.post("/api/v1/datasources", response_model=Dict[str, str])
async def add_data_source(config: DataSourceConfig):
    """Add a new data source"""
    if data_source_manager.add_data_source(config):
        # Store in database
        await db_manager.save_data_source_config(config)
        return {"message": f"Data source '{config.name}' added successfully"}
    else:
        raise HTTPException(status_code=400, detail="Failed to add data source")


@app.put("/api/v1/datasources/{name}", response_model=Dict[str, str])
async def update_data_source(name: str, config: DataSourceConfig):
    """Update data source configuration"""
    if data_source_manager.update_source_config(name, config):
        # Update in database
        await db_manager.update_data_source_config(name, config)
        return {"message": f"Data source '{name}' updated successfully"}
    else:
        raise HTTPException(status_code=404, detail="Data source not found")


@app.delete("/api/v1/datasources/{name}", response_model=Dict[str, str])
async def remove_data_source(name: str):
    """Remove a data source"""
    if data_source_manager.remove_data_source(name):
        # Remove from database
        await db_manager.delete_data_source_config(name)
        return {"message": f"Data source '{name}' removed successfully"}
    else:
        raise HTTPException(status_code=404, detail="Data source not found")


# Sentiment analyzer endpoints
@app.get("/api/v1/analyzers", response_model=List[str])
async def get_analyzers():
    """Get available sentiment analyzers"""
    return SentimentAnalyzerFactory.get_available_analyzers()


@app.post("/api/v1/analyze-text", response_model=Dict[str, Any])
async def analyze_text(
    text: str,
    analyzer_name: str = Query(
        default="textblob", description="Sentiment analyzer to use"
    ),
):
    """
    Analyze sentiment of a single text

    Args:
        text: Text to analyze
        analyzer_name: Name of sentiment analyzer to use

    Returns:
        Sentiment analysis result
    """
    try:
        analyzer = SentimentAnalyzerFactory.create_analyzer(analyzer_name)
        result = analyzer.analyze(text)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis error: {str(e)}")


# Cache management endpoints
@app.get("/api/v1/cache/stats", response_model=Dict[str, Any])
async def get_cache_stats():
    """Get cache statistics"""
    return cache_manager.get_stats()


@app.delete("/api/v1/cache/clear", response_model=Dict[str, Any])
async def clear_cache():
    """Clear all cache entries"""
    cleared = cache_manager.clear_all()
    return {"message": f"Cleared {cleared} cache entries"}


@app.delete("/api/v1/cache/expired", response_model=Dict[str, Any])
async def clear_expired_cache():
    """Clear expired cache entries"""
    cleared = cache_manager.clear_expired()
    return {"message": f"Cleared {cleared} expired cache entries"}


# Background tasks
async def store_analysis_result(result: AnalysisResult):
    """Store analysis result in database (background task)"""
    try:
        await db_manager.store_analysis_result(result)
    except Exception as e:
        print(f"Error storing analysis result: {e}")


# Legacy endpoints for backward compatibility
@app.get("/search/{search_term}")
async def legacy_search(search_term: str, limit: int = 50):
    """Legacy search endpoint for backward compatibility"""
    query = SearchQuery(query=search_term, limit=limit, include_sentiment=False)

    result = await analyze_posts(query, analyzer_name="textblob", use_cache=True)

    # Return in legacy format
    return {
        "posts": [post.dict() for post in result.posts],
        "total": result.total_posts,
        "sources": result.sources_used,
    }


@app.get("/followers/{screen_name}")
async def legacy_get_followers(screen_name: str):
    """Legacy followers endpoint (deprecated)"""
    raise HTTPException(
        status_code=410,
        detail="This endpoint is deprecated. Use /api/v1/users/{user_id}/posts instead",
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, debug=True)
