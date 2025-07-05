import pytest
from unittest.mock import patch
from datetime import datetime
from src.models.schemas import Post, EngagementStats, SentimentType
from src.core.sentiment import TextBlobAnalyzer, VaderAnalyzer, SentimentAnalyzerFactory


class TestTextBlobAnalyzer:
    def test_analyze_with_followers_following(self):
        """Test sentiment analysis with follower/following data"""
        # Simulate a post with follower/following info
        post = Post(
            id="3",
            text="People love my new product!",
            timestamp=datetime.now(),
            author="celebrity1",
            author_id="celebrity1",
            source="test",
            engagement_stats=EngagementStats(likes=10000, shares=500, comments=200),
            confidence_score=0.95,
            followers=1000000,
            following=100,
        )
        result = self.analyzer.analyze(post.text)
        assert result["sentiment"] == SentimentType.POSITIVE
        # Optionally, you could add logic to boost confidence if followers >> following
        # For now, just check that the analysis works

    def test_product_sentiment(self):
        """Test sentiment analysis for product queries"""
        result = self.analyzer.analyze("The PlayStation is fantastic!")
        assert result["sentiment"] == SentimentType.POSITIVE
        result2 = self.analyzer.analyze("The Xbox is terrible.")
        assert result2["sentiment"] == SentimentType.NEGATIVE

    """Test TextBlob sentiment analyzer"""

    def setup_method(self):
        self.analyzer = TextBlobAnalyzer()

    def test_analyzer_name(self):
        assert self.analyzer.get_name() == "TextBlob"

    def test_analyze_positive_text(self):
        result = self.analyzer.analyze("I love this amazing product!")
        assert result["sentiment"] == SentimentType.POSITIVE
        assert 0 <= result["confidence"] <= 1
        assert result["polarity"] > 0
        assert 0 <= result["subjectivity"] <= 1

    def test_analyze_negative_text(self):
        result = self.analyzer.analyze("I hate this terrible product!")
        assert result["sentiment"] == SentimentType.NEGATIVE
        assert 0 <= result["confidence"] <= 1
        assert result["polarity"] < 0
        assert 0 <= result["subjectivity"] <= 1

    def test_analyze_neutral_text(self):
        result = self.analyzer.analyze("It is a table.")
        assert result["sentiment"] == SentimentType.NEUTRAL
        assert 0 <= result["confidence"] <= 1
        assert -0.1 <= result["polarity"] <= 0.1
        assert 0 <= result["subjectivity"] <= 1

    def test_analyze_batch(self):
        texts = ["I love this!", "I hate this!", "It is a table."]
        results = self.analyzer.analyze_batch(texts)
        assert len(results) == 3
        assert results[0]["sentiment"] == SentimentType.POSITIVE
        assert results[1]["sentiment"] == SentimentType.NEGATIVE
        assert results[2]["sentiment"] == SentimentType.NEUTRAL

    def test_analyze_batch_with_errors(self):
        texts = ["I love this!", "", "Normal text"]  # Empty string might cause issues
        results = self.analyzer.analyze_batch(texts)
        assert len(results) == 3
        for result in results:
            assert "sentiment" in result
            assert "confidence" in result
            assert "polarity" in result
            assert "subjectivity" in result

    def test_process_posts(self):
        posts = [
            Post(
                id="1",
                text="I love this product!",
                timestamp=datetime.now(),
                author="user1",
                author_id="user1",
                source="test",
                engagement_stats=EngagementStats(likes=10, shares=5, comments=3),
                confidence_score=0.9,
            ),
            Post(
                id="2",
                text="I hate this service!",
                timestamp=datetime.now(),
                author="user2",
                author_id="user2",
                source="test",
                engagement_stats=EngagementStats(likes=0, shares=0, comments=1),
                confidence_score=0.8,
            ),
        ]
        results = self.analyzer.process_posts(posts)
        assert len(results) == 2
        assert results[0].sentiment == SentimentType.POSITIVE
        assert results[1].sentiment == SentimentType.NEGATIVE
        assert results[0].analyzer_used == "TextBlob"
        assert results[1].analyzer_used == "TextBlob"


class TestVaderAnalyzer:
    """Test VADER sentiment analyzer"""

    def setup_method(self):
        self.analyzer = VaderAnalyzer()

    def test_analyzer_name(self):
        assert self.analyzer.get_name() == "VADER"

    def test_analyze_positive_text(self):
        result = self.analyzer.analyze("I love this amazing product!")
        assert result["sentiment"] == SentimentType.POSITIVE
        assert 0 <= result["confidence"] <= 1
        assert result["polarity"] > 0
        assert 0 <= result["subjectivity"] <= 1

    def test_analyze_negative_text(self):
        result = self.analyzer.analyze("I hate this terrible product!")
        assert result["sentiment"] == SentimentType.NEGATIVE
        assert 0 <= result["confidence"] <= 1
        assert result["polarity"] < 0
        assert 0 <= result["subjectivity"] <= 1

    def test_analyze_neutral_text(self):
        result = self.analyzer.analyze("It is a table.")
        assert result["sentiment"] == SentimentType.NEUTRAL
        assert 0 <= result["confidence"] <= 1
        assert -0.1 <= result["polarity"] <= 0.1
        assert 0 <= result["subjectivity"] <= 1

    def test_analyze_batch(self):
        texts = ["I love this!", "I hate this!", "It is a table."]
        results = self.analyzer.analyze_batch(texts)
        assert len(results) == 3
        assert results[0]["sentiment"] == SentimentType.POSITIVE
        assert results[1]["sentiment"] == SentimentType.NEGATIVE
        assert results[2]["sentiment"] == SentimentType.NEUTRAL


class TestSentimentAnalyzerFactory:
    """Test sentiment analyzer factory"""

    def test_create_textblob_analyzer(self):
        analyzer = SentimentAnalyzerFactory.create_analyzer("textblob")
        assert isinstance(analyzer, TextBlobAnalyzer)
        assert analyzer.get_name() == "TextBlob"

    def test_create_vader_analyzer(self):
        analyzer = SentimentAnalyzerFactory.create_analyzer("vader")
        assert isinstance(analyzer, VaderAnalyzer)
        assert analyzer.get_name() == "VADER"

    def test_create_invalid_analyzer(self):
        with pytest.raises(ValueError, match="Unknown analyzer"):
            SentimentAnalyzerFactory.create_analyzer("invalid")

    def test_get_available_analyzers(self):
        analyzers = SentimentAnalyzerFactory.get_available_analyzers()
        assert "textblob" in analyzers
        assert "vader" in analyzers
        assert len(analyzers) == 2
