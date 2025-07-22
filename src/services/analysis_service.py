"""
Analysis Service

Handles the core business logic for post analysis, sentiment analysis,
and result aggregation. Now uses repository pattern for data access.
"""

import time
from datetime import datetime
from typing import List, Optional

from src.core.datasources.manager import DataSourceManager
from src.core.sentiment.factory import SentimentAnalyzerFactory
from src.models.schemas import AnalysisResult, SearchQuery, SentimentType
from src.repositories.analysis_repository import AnalysisRepository
from src.utils.pagination import paginate_results


class AnalysisService:
    """Service for handling post analysis operations"""
    
    def __init__(self, data_source_manager: DataSourceManager, analysis_repository: AnalysisRepository):
        self.data_source_manager = data_source_manager
        self.analysis_repository = analysis_repository
    
    async def analyze_posts(
        self,
        query: SearchQuery,
        analyzer_name: str = "textblob",
        use_cache: bool = True
    ) -> AnalysisResult:
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
        
        # Get enabled data sources
        enabled_sources = self.data_source_manager.get_enabled_sources()
        
        if not enabled_sources:
            raise RuntimeError("No data sources available")
        
        # Filter sources based on query
        sources_to_use = enabled_sources
        if query.data_sources:
            sources_to_use = [
                source for source in enabled_sources 
                if source.name in query.data_sources
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
                
                # Save sentiment results to repository
                if sentiment_results:
                    await self.analysis_repository.save_sentiment_results(sentiment_results)
                
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
        
        # Save analysis result to repository
        await self.analysis_repository.save_analysis_result(analysis_result)
        
        # Save posts to repository
        if all_posts:
            await self.analysis_repository.save_posts(all_posts)
        
        return analysis_result
    
    async def get_user_posts(
        self,
        user_id: str,
        source: str,
        limit: int = 50,
        include_sentiment: bool = True
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
        data_source = self.data_source_manager.get_data_source(source)
        
        if not data_source:
            raise ValueError(f"Data source '{source}' not found")
        
        try:
            posts = await data_source.get_user_posts(user_id, limit)
            
            # Save posts to repository for future reference
            if posts:
                await self.analysis_repository.save_posts(posts)
            
            return posts
        except Exception as e:
            raise RuntimeError(f"Error fetching user posts: {str(e)}")
    
    def analyze_single_text(self, text: str, analyzer_name: str = "textblob"):
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
            raise RuntimeError(f"Analysis error: {str(e)}")
    
    async def get_posts_by_source(self, source: str, limit: int = 50):
        """
        Get posts from repository by data source
        
        Args:
            source: Data source name
            limit: Maximum number of posts to return
            
        Returns:
            List of posts from the source
        """
        return await self.analysis_repository.get_posts_by_source(source, limit)
    
    async def cleanup_old_analysis_data(self, older_than_days: int = 30) -> int:
        """
        Clean up old analysis data
        
        Args:
            older_than_days: Remove data older than this many days
            
        Returns:
            Number of records removed
        """
        return await self.analysis_repository.cleanup_old_data(older_than_days)