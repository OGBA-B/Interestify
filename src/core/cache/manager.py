import hashlib
import json
import time
from typing import Any, Dict, Optional, List
from datetime import datetime, timedelta
from src.models.schemas import SearchQuery, AnalysisResult


class CacheManager:
    """In-memory cache manager for API responses"""

    def __init__(self, default_ttl: int = 3600):
        self._cache: Dict[str, Dict] = {}
        self.default_ttl = default_ttl

    def _generate_key(self, query: SearchQuery) -> str:
        """Generate cache key from search query"""
        # Create a consistent hash of the query parameters
        query_dict = {
            "query": query.query,
            "data_sources": sorted(query.data_sources),
            "limit": query.limit,
            "start_date": query.start_date.isoformat() if query.start_date else None,
            "end_date": query.end_date.isoformat() if query.end_date else None,
            "include_sentiment": query.include_sentiment,
            "min_confidence": query.min_confidence,
            "language": query.language,
        }

        query_str = json.dumps(query_dict, sort_keys=True)
        return hashlib.md5(query_str.encode()).hexdigest()

    def get(self, query: SearchQuery) -> Optional[AnalysisResult]:
        """
        Get cached result for a query

        Args:
            query: Search query

        Returns:
            Cached AnalysisResult or None if not found/expired
        """
        cache_key = self._generate_key(query)

        if cache_key in self._cache:
            cache_entry = self._cache[cache_key]

            # Check if expired
            if time.time() < cache_entry["expires_at"]:
                cache_entry["hit_count"] += 1
                cache_entry["last_accessed"] = time.time()
                return cache_entry["data"]
            else:
                # Remove expired entry
                del self._cache[cache_key]

        return None

    def set(
        self, query: SearchQuery, result: AnalysisResult, ttl: Optional[int] = None
    ) -> None:
        """
        Cache a result

        Args:
            query: Search query
            result: Analysis result to cache
            ttl: Time to live in seconds (uses default if None)
        """
        cache_key = self._generate_key(query)
        ttl = ttl or self.default_ttl

        self._cache[cache_key] = {
            "data": result,
            "created_at": time.time(),
            "expires_at": time.time() + ttl,
            "hit_count": 0,
            "last_accessed": time.time(),
        }

    def invalidate(self, query: SearchQuery) -> bool:
        """
        Invalidate cache entry for a query

        Args:
            query: Search query

        Returns:
            True if entry was found and removed, False otherwise
        """
        cache_key = self._generate_key(query)

        if cache_key in self._cache:
            del self._cache[cache_key]
            return True

        return False

    def clear_expired(self) -> int:
        """
        Clear all expired cache entries

        Returns:
            Number of entries removed
        """
        current_time = time.time()
        expired_keys = []

        for key, entry in self._cache.items():
            if current_time >= entry["expires_at"]:
                expired_keys.append(key)

        for key in expired_keys:
            del self._cache[key]

        return len(expired_keys)

    def clear_all(self) -> int:
        """
        Clear all cache entries

        Returns:
            Number of entries removed
        """
        count = len(self._cache)
        self._cache.clear()
        return count

    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics

        Returns:
            Dictionary with cache statistics
        """
        current_time = time.time()
        total_entries = len(self._cache)
        expired_entries = 0
        total_hits = 0

        for entry in self._cache.values():
            if current_time >= entry["expires_at"]:
                expired_entries += 1
            total_hits += entry["hit_count"]

        return {
            "total_entries": total_entries,
            "expired_entries": expired_entries,
            "active_entries": total_entries - expired_entries,
            "total_hits": total_hits,
            "memory_usage_mb": self._estimate_memory_usage(),
        }

    def _estimate_memory_usage(self) -> float:
        """Estimate memory usage in MB (rough approximation)"""
        import sys

        total_size = 0

        for entry in self._cache.values():
            total_size += sys.getsizeof(entry)

        return total_size / (1024 * 1024)  # Convert to MB

    def get_cached_queries(self) -> List[Dict[str, Any]]:
        """Get list of cached queries with metadata"""
        queries = []
        current_time = time.time()

        for key, entry in self._cache.items():
            queries.append(
                {
                    "cache_key": key,
                    "created_at": datetime.fromtimestamp(entry["created_at"]),
                    "expires_at": datetime.fromtimestamp(entry["expires_at"]),
                    "hit_count": entry["hit_count"],
                    "last_accessed": datetime.fromtimestamp(entry["last_accessed"]),
                    "is_expired": current_time >= entry["expires_at"],
                    "time_to_expire": max(0, entry["expires_at"] - current_time),
                }
            )

        return queries


# Global cache instance
cache_manager = CacheManager()
