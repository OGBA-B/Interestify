from typing import List, Dict, Any
from textblob import TextBlob
from .base import SentimentAnalyzer
from src.models.schemas import SentimentType


class TextBlobAnalyzer(SentimentAnalyzer):
    """TextBlob-based sentiment analyzer"""

    def get_name(self) -> str:
        return "TextBlob"

    def analyze(self, text: str) -> Dict[str, Any]:
        """
        Analyze sentiment using TextBlob
        """
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity
        subjectivity = blob.sentiment.subjectivity

        sentiment = self._classify_sentiment(polarity)

        # Convert polarity to confidence (0-1 scale)
        confidence = min(abs(polarity) + 0.5, 1.0)

        return {
            "sentiment": sentiment,
            "confidence": confidence,
            "polarity": polarity,
            "subjectivity": subjectivity,
        }

    def analyze_batch(self, texts: List[str]) -> List[Dict[str, Any]]:
        """
        Analyze sentiment for multiple texts
        """
        results = []
        for text in texts:
            try:
                result = self.analyze(text)
                results.append(result)
            except Exception as e:
                # Fallback result for failed analysis
                results.append(
                    {
                        "sentiment": SentimentType.NEUTRAL,
                        "confidence": 0.0,
                        "polarity": 0.0,
                        "subjectivity": 0.0,
                    }
                )

        return results
