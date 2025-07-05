from abc import ABC, abstractmethod
from typing import Any, Dict, List

from src.models.schemas import Post, SentimentResult, SentimentType


class SentimentAnalyzer(ABC):
    """Abstract base class for sentiment analysis implementations"""

    @abstractmethod
    def analyze(self, text: str) -> Dict[str, Any]:
        """
        Analyze sentiment of given text

        Returns:
            Dict containing sentiment, confidence, polarity, and subjectivity
        """
        pass

    @abstractmethod
    def analyze_batch(self, texts: List[str]) -> List[Dict[str, Any]]:
        """
        Analyze sentiment for multiple texts

        Returns:
            List of sentiment analysis results
        """
        pass

    @abstractmethod
    def get_name(self) -> str:
        """Return the name of the analyzer"""
        pass

    def process_posts(self, posts: List[Post]) -> List[SentimentResult]:
        """
        Process a list of posts and return sentiment results
        """
        texts = [post.text for post in posts]
        results = self.analyze_batch(texts)

        sentiment_results = []
        for i, (post, result) in enumerate(zip(posts, results)):
            sentiment_result = SentimentResult(
                post_id=post.id,
                sentiment=result["sentiment"],
                confidence=result["confidence"],
                polarity=result["polarity"],
                subjectivity=result["subjectivity"],
                analyzer_used=self.get_name(),
                created_at=post.timestamp,
            )
            sentiment_results.append(sentiment_result)

        return sentiment_results

    def _classify_sentiment(self, polarity: float) -> SentimentType:
        """
        Classify sentiment based on polarity score
        """
        if polarity > 0.1:
            return SentimentType.POSITIVE
        elif polarity < -0.1:
            return SentimentType.NEGATIVE
        else:
            return SentimentType.NEUTRAL
