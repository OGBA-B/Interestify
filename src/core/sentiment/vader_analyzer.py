from typing import List, Dict, Any
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from .base import SentimentAnalyzer
from src.models.schemas import SentimentType


class VaderAnalyzer(SentimentAnalyzer):
    """VADER sentiment analyzer"""

    def __init__(self):
        self.analyzer = SentimentIntensityAnalyzer()

    def get_name(self) -> str:
        return "VADER"

    def analyze(self, text: str) -> Dict[str, Any]:
        """
        Analyze sentiment using VADER
        """
        scores = self.analyzer.polarity_scores(text)

        # VADER returns compound score (-1 to 1)
        compound = scores["compound"]

        sentiment = self._classify_sentiment(compound)

        # Use compound score magnitude as confidence
        confidence = min(abs(compound) + 0.3, 1.0)

        return {
            "sentiment": sentiment,
            "confidence": confidence,
            "polarity": compound,
            "subjectivity": max(scores["pos"], scores["neg"]),  # Approximation
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
