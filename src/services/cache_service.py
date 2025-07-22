"""
Cache Service

Handles caching operations for analysis results and API responses.
"""

from typing import Any, Dict

from src.core.cache.manager import CacheManager
from src.models.schemas import AnalysisResult, SearchQuery


class CacheService:
    """Service for handling cache operations"""
    
    def __init__(self, cache_manager: CacheManager):
        self.cache_manager = cache_manager
    
    def get_cached_result(self, query: SearchQuery) -> AnalysisResult:
        """
        Get cached analysis result for a query
        
        Args:
            query: Search query
            
        Returns:
            Cached analysis result or None if not found
        """
        return self.cache_manager.get(query)
    
    def cache_result(self, query: SearchQuery, result: AnalysisResult):
        """
        Cache an analysis result
        
        Args:
            query: Search query
            result: Analysis result to cache
        """
        self.cache_manager.set(query, result)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return self.cache_manager.get_stats()
    
    def clear_all(self) -> int:
        """
        Clear all cache entries
        
        Returns:
            Number of entries cleared
        """
        return self.cache_manager.clear_all()
    
    def clear_expired(self) -> int:
        """
        Clear expired cache entries
        
        Returns:
            Number of expired entries cleared
        """
        return self.cache_manager.clear_expired()