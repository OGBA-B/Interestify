import asyncio
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles

from src.api.dashboard import router as dashboard_router
from src.config import get_app_config, get_security_config
from src.core.sentiment import SentimentAnalyzerFactory
from src.models.schemas import (
    AnalysisResult,
    DataSourceConfig,
    Post,
    SearchQuery,
    SentimentResult,
    SentimentType,
)
from src.services.analysis_service import AnalysisService
from src.services.cache_service import CacheService
from src.services.config import get_service
from src.services.data_source_service import DataSourceService
from src.utils.database import DatabaseManager
from src.utils.pagination import PaginatedResponse, paginate_results

# Get configuration
config = get_app_config()
security_config = get_security_config()

app = FastAPI(
    title="Interestify API",
    description="Social media sentiment analysis API",
    version=config.version,
)

# Add CORS middleware with configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.cors_origins,
    allow_credentials=True,
    allow_methods=config.cors_methods,
    allow_headers=config.cors_headers,
)

# Add security headers middleware
@app.middleware("http")
async def add_security_headers(request, call_next):
    """Add security headers to all responses"""
    response = await call_next(request)
    
    # Add Content Security Policy if enabled
    if security_config.enable_csp:
        response.headers["Content-Security-Policy"] = security_config.get_csp_header()
    
    # Add other security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    
    # Add HTTPS enforcement if enabled
    if security_config.force_https:
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    
    return response

# Include dashboard router
app.include_router(dashboard_router)

# Initialize database
db_manager = DatabaseManager()

# Get services from DI container
analysis_service = get_service(AnalysisService)
data_source_service = get_service(DataSourceService)
cache_service = get_service(CacheService)


@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    await db_manager.init_db()

    # Load configured data sources from repository via service
    await data_source_service.load_configurations_from_repository()


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    await data_source_service.close_all_sources()
    await db_manager.close()


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy", 
        "timestamp": datetime.utcnow(), 
        "version": config.version,
        "app_name": config.app_name
    }


# Dashboard demo page
@app.get("/dashboard")
async def dashboard_demo():
    """Serve dashboard demo page"""
    return FileResponse("dashboard_demo.html")


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
    # Check cache first
    if use_cache:
        cached_result = cache_service.get_cached_result(query)
        if cached_result:
            return cached_result

    # Perform analysis using service
    try:
        analysis_result = await analysis_service.analyze_posts(
            query, analyzer_name, use_cache
        )
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))

    # Cache the result
    if use_cache:
        cache_service.cache_result(query, analysis_result)

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
    try:
        posts = await analysis_service.get_user_posts(
            user_id, source, limit, include_sentiment
        )
        return posts
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))


# Data source management endpoints
@app.get("/api/v1/datasources", response_model=List[Dict[str, Any]])
async def get_data_sources():
    """Get all configured data sources"""
    return data_source_service.get_all_sources()


@app.post("/api/v1/datasources", response_model=Dict[str, str])
async def add_data_source(config: DataSourceConfig):
    """Add a new data source"""
    if await data_source_service.add_source(config):
        return {"message": f"Data source '{config.name}' added successfully"}
    else:
        raise HTTPException(status_code=400, detail="Failed to add data source")


@app.put("/api/v1/datasources/{name}", response_model=Dict[str, str])
async def update_data_source(name: str, config: DataSourceConfig):
    """Update data source configuration"""
    if await data_source_service.update_source(name, config):
        return {"message": f"Data source '{name}' updated successfully"}
    else:
        raise HTTPException(status_code=404, detail="Data source not found")


@app.delete("/api/v1/datasources/{name}", response_model=Dict[str, str])
async def remove_data_source(name: str):
    """Remove a data source"""
    if await data_source_service.remove_source(name):
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
        result = analysis_service.analyze_single_text(text, analyzer_name)
        return result
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))


# Cache management endpoints
@app.get("/api/v1/cache/stats", response_model=Dict[str, Any])
async def get_cache_stats():
    """Get cache statistics"""
    return cache_service.get_stats()


@app.delete("/api/v1/cache/clear", response_model=Dict[str, Any])
async def clear_cache():
    """Clear all cache entries"""
    cleared = cache_service.clear_all()
    return {"message": f"Cleared {cleared} cache entries"}


@app.delete("/api/v1/cache/expired", response_model=Dict[str, Any])
async def clear_expired_cache():
    """Clear expired cache entries"""
    cleared = cache_service.clear_expired()
    return {"message": f"Cleared {cleared} expired cache entries"}





if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, debug=True)
