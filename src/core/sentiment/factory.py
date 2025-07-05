from .base import SentimentAnalyzer
from .textblob_analyzer import TextBlobAnalyzer
from .vader_analyzer import VaderAnalyzer
from typing import Dict, Type


class SentimentAnalyzerFactory:
    """Factory class for creating sentiment analyzers"""

    _analyzers: Dict[str, Type[SentimentAnalyzer]] = {
        "textblob": TextBlobAnalyzer,
        "vader": VaderAnalyzer,
    }

    @classmethod
    def create_analyzer(cls, name: str = "textblob") -> SentimentAnalyzer:
        """
        Create a sentiment analyzer by name

        Args:
            name: Name of the analyzer ('textblob' or 'vader')

        Returns:
            SentimentAnalyzer instance
        """
        if name not in cls._analyzers:
            raise ValueError(
                f"Unknown analyzer: {name}. Available: {list(cls._analyzers.keys())}"
            )

        analyzer_class = cls._analyzers[name]
        return analyzer_class()

    @classmethod
    def get_available_analyzers(cls) -> list:
        """Get list of available analyzer names"""
        return list(cls._analyzers.keys())

    @classmethod
    def register_analyzer(cls, name: str, analyzer_class: Type[SentimentAnalyzer]):
        """Register a new analyzer"""
        cls._analyzers[name] = analyzer_class


# Default analyzer instance
default_analyzer = SentimentAnalyzerFactory.create_analyzer("textblob")
