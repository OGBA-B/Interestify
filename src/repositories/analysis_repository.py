"""
Analysis Repository Interface and Implementation

Handles persistence operations for analysis results, posts, and sentiment data.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional

from src.models.schemas import AnalysisResult, Post, SentimentResult
from src.utils.database import DatabaseManager


class AnalysisRepository(ABC):
    """Abstract repository for analysis data operations"""
    
    @abstractmethod
    async def save_analysis_result(self, result: AnalysisResult) -> bool:
        """Save an analysis result"""
        pass
    
    @abstractmethod
    async def get_analysis_result(self, query: str, created_after: Optional[datetime] = None) -> Optional[AnalysisResult]:
        """Get analysis result by query"""
        pass
    
    @abstractmethod
    async def save_posts(self, posts: List[Post]) -> bool:
        """Save a list of posts"""
        pass
    
    @abstractmethod
    async def get_posts_by_source(self, source: str, limit: int = 50) -> List[Post]:
        """Get posts by data source"""
        pass
    
    @abstractmethod
    async def save_sentiment_results(self, results: List[SentimentResult]) -> bool:
        """Save sentiment analysis results"""
        pass
    
    @abstractmethod
    async def get_sentiment_results_by_post_ids(self, post_ids: List[str]) -> List[SentimentResult]:
        """Get sentiment results for specific posts"""
        pass
    
    @abstractmethod
    async def cleanup_old_data(self, older_than_days: int = 30) -> int:
        """Clean up old data and return number of records removed"""
        pass


class DatabaseAnalysisRepository(AnalysisRepository):
    """Database implementation of analysis repository"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
    
    async def save_analysis_result(self, result: AnalysisResult) -> bool:
        """Save an analysis result to database"""
        try:
            # Delegate to existing database manager method
            await self.db_manager.store_analysis_result(result)
            return True
        except Exception as e:
            print(f"Error saving analysis result: {e}")
            return False
    
    async def get_analysis_result(self, query: str, created_after: Optional[datetime] = None) -> Optional[AnalysisResult]:
        """Get analysis result by query from database"""
        try:
            # This would need to be implemented in DatabaseManager
            # For now, return None to maintain existing behavior
            return None
        except Exception as e:
            print(f"Error retrieving analysis result: {e}")
            return None
    
    async def save_posts(self, posts: List[Post]) -> bool:
        """Save posts to database"""
        try:
            # Batch save posts - would need to be implemented in DatabaseManager
            # For now, save individually
            for post in posts:
                await self.db_manager.store_post(post)
            return True
        except Exception as e:
            print(f"Error saving posts: {e}")
            return False
    
    async def get_posts_by_source(self, source: str, limit: int = 50) -> List[Post]:
        """Get posts by data source from database"""
        try:
            # This would need to be implemented in DatabaseManager
            return []
        except Exception as e:
            print(f"Error retrieving posts: {e}")
            return []
    
    async def save_sentiment_results(self, results: List[SentimentResult]) -> bool:
        """Save sentiment analysis results to database"""
        try:
            # Batch save sentiment results
            for result in results:
                await self.db_manager.store_sentiment_result(result)
            return True
        except Exception as e:
            print(f"Error saving sentiment results: {e}")
            return False
    
    async def get_sentiment_results_by_post_ids(self, post_ids: List[str]) -> List[SentimentResult]:
        """Get sentiment results for specific posts from database"""
        try:
            # This would need to be implemented in DatabaseManager
            return []
        except Exception as e:
            print(f"Error retrieving sentiment results: {e}")
            return []
    
    async def cleanup_old_data(self, older_than_days: int = 30) -> int:
        """Clean up old data from database"""
        try:
            # This would need to be implemented in DatabaseManager
            return 0
        except Exception as e:
            print(f"Error cleaning up old data: {e}")
            return 0