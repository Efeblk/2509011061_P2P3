"""
Unit tests for EventContent node model.
"""

import pytest
from datetime import datetime
from src.models.event_content import EventContentNode


class TestEventContentNode:
    """Test EventContentNode creation and basic functionality."""

    def test_create_event_content_node(self):
        """Test creating an EventContent node with required fields."""
        content = EventContentNode(
            event_uuid="test-event-123",
            content_type="user_review",
            text="Great concert! Really enjoyed it.",
            rating=4.5,
        )

        assert content.event_uuid == "test-event-123"
        assert content.content_type == "user_review"
        assert content.text == "Great concert! Really enjoyed it."
        assert content.rating == 4.5
        assert content.uuid is not None
        assert isinstance(content.created_at, datetime)

    def test_default_values(self):
        """Test default field values."""
        content = EventContentNode(event_uuid="test-123", content_type="description")

        assert content.language == "tr"
        assert content.likes_count == 0
        assert content.views_count == 0
        assert content.helpful_count == 0
        assert content.rating is None
        assert content.text is None

    def test_label_property(self):
        """Test that label property returns correct value."""
        content = EventContentNode(event_uuid="test-123", content_type="review")
        assert content.label == "EventContent"

    def test_get_properties(self):
        """Test _get_properties returns correct dictionary."""
        content = EventContentNode(
            event_uuid="event-123",
            content_type="user_review",
            text="Awesome show!",
            rating=5.0,
            author="user-456",
            language="en",
            sentiment_score=0.9,
            keywords="awesome,great,amazing",
            likes_count=10,
            views_count=100,
            helpful_count=8,
        )

        props = content._get_properties()

        assert props["uuid"] == content.uuid
        assert props["event_uuid"] == "event-123"
        assert props["content_type"] == "user_review"
        assert props["text"] == "Awesome show!"
        assert props["rating"] == 5.0
        assert props["author"] == "user-456"
        assert props["language"] == "en"
        assert props["sentiment_score"] == 0.9
        assert props["keywords"] == "awesome,great,amazing"
        assert props["likes_count"] == 10
        assert props["views_count"] == 100
        assert props["helpful_count"] == 8
        assert "created_at" in props
        assert isinstance(props["created_at"], str)

    def test_get_properties_with_none_values(self):
        """Test _get_properties handles None values correctly."""
        content = EventContentNode(event_uuid="event-123", content_type="description")

        props = content._get_properties()

        # None values should be converted to empty strings or 0
        assert props["text"] == ""
        assert props["summary"] == ""
        assert props["rating"] == 0.0
        assert props["author"] == ""
        assert props["keywords"] == ""

    def test_to_dict(self):
        """Test to_dict conversion."""
        content = EventContentNode(
            event_uuid="event-123",
            content_type="ai_summary",
            text="AI-generated summary",
            rating=4.2,
        )

        data = content.to_dict()

        assert data["event_uuid"] == "event-123"
        assert data["content_type"] == "ai_summary"
        assert data["text"] == "AI-generated summary"
        assert data["rating"] == 4.2
        assert isinstance(data["created_at"], str)

    def test_from_dict(self):
        """Test creating EventContent from dictionary."""
        data = {
            "uuid": "content-123",
            "event_uuid": "event-456",
            "content_type": "editorial",
            "text": "Editorial review",
            "summary": "Short summary",
            "rating": 4.0,
            "rating_count": 10,
            "author": "editor-1",
            "language": "tr",
            "sentiment_score": 0.7,
            "keywords": "good,nice",
            "embedding_vector": "[0.1, 0.2, 0.3]",
            "likes_count": 5,
            "views_count": 50,
            "helpful_count": 3,
            "created_at": "2024-01-01T10:00:00",
            "updated_at": "2024-01-01T12:00:00",
        }

        content = EventContentNode.from_dict(data)

        assert content.uuid == "content-123"
        assert content.event_uuid == "event-456"
        assert content.content_type == "editorial"
        assert content.text == "Editorial review"
        assert content.summary == "Short summary"
        assert content.rating == 4.0
        assert content.rating_count == 10
        assert content.author == "editor-1"
        assert content.language == "tr"
        assert content.sentiment_score == 0.7
        assert content.keywords == "good,nice"
        assert content.embedding_vector == "[0.1, 0.2, 0.3]"
        assert content.likes_count == 5
        assert content.views_count == 50
        assert content.helpful_count == 3
        assert isinstance(content.created_at, datetime)
        assert isinstance(content.updated_at, datetime)

    def test_repr(self):
        """Test string representation."""
        content = EventContentNode(event_uuid="event-123", content_type="user_review", rating=4.5)

        repr_str = repr(content)

        assert "EventContentNode" in repr_str
        assert "event-123" in repr_str
        assert "user_review" in repr_str
        assert "4.5" in repr_str


class TestContentTypes:
    """Test different content type scenarios."""

    def test_user_review_content(self):
        """Test user review content type."""
        review = EventContentNode(
            event_uuid="event-1",
            content_type="user_review",
            text="Amazing concert! Best night ever.",
            rating=5.0,
            author="user-123",
            sentiment_score=0.95,
        )

        assert review.content_type == "user_review"
        assert review.rating == 5.0
        assert review.sentiment_score == 0.95

    def test_ai_summary_content(self):
        """Test AI-generated summary content type."""
        ai_summary = EventContentNode(
            event_uuid="event-1",
            content_type="ai_summary",
            text="This concert features classical music performances.",
            summary="Classical concert",
            author="AI",
            keywords="classical,music,concert",
            embedding_vector="[0.1, 0.2, 0.3, 0.4, 0.5]",
        )

        assert ai_summary.content_type == "ai_summary"
        assert ai_summary.author == "AI"
        assert ai_summary.keywords == "classical,music,concert"
        assert ai_summary.embedding_vector is not None

    def test_description_content(self):
        """Test event description content type."""
        description = EventContentNode(
            event_uuid="event-1",
            content_type="description",
            text="A full orchestra performance featuring Beethoven's symphonies.",
            summary="Orchestra performance",
            language="tr",
        )

        assert description.content_type == "description"
        assert description.language == "tr"

    def test_editorial_content(self):
        """Test editorial content type."""
        editorial = EventContentNode(
            event_uuid="event-1",
            content_type="editorial",
            text="Expert analysis of the upcoming theater performance.",
            rating=4.0,
            author="editor-chief",
        )

        assert editorial.content_type == "editorial"
        assert editorial.author == "editor-chief"


class TestEngagementFields:
    """Test engagement-related fields."""

    def test_increment_likes(self):
        """Test incrementing likes count."""
        content = EventContentNode(event_uuid="event-1", content_type="user_review", likes_count=5)

        content.likes_count += 1
        assert content.likes_count == 6

    def test_increment_views(self):
        """Test incrementing views count."""
        content = EventContentNode(event_uuid="event-1", content_type="description", views_count=100)

        content.views_count += 1
        assert content.views_count == 101

    def test_increment_helpful(self):
        """Test incrementing helpful count."""
        content = EventContentNode(event_uuid="event-1", content_type="user_review", helpful_count=3)

        content.helpful_count += 1
        assert content.helpful_count == 4


class TestRatingValidation:
    """Test rating field scenarios."""

    def test_valid_ratings(self):
        """Test various valid rating values."""
        ratings = [0.0, 2.5, 4.0, 5.0]

        for rating in ratings:
            content = EventContentNode(event_uuid="event-1", content_type="user_review", rating=rating)
            assert content.rating == rating

    def test_none_rating(self):
        """Test None rating (no rating provided)."""
        content = EventContentNode(event_uuid="event-1", content_type="description", rating=None)

        assert content.rating is None


class TestMultilingualSupport:
    """Test language field functionality."""

    def test_turkish_language(self):
        """Test Turkish language content."""
        content = EventContentNode(
            event_uuid="event-1",
            content_type="user_review",
            text="Harika bir konserdi!",
            language="tr",
        )

        assert content.language == "tr"

    def test_english_language(self):
        """Test English language content."""
        content = EventContentNode(
            event_uuid="event-1",
            content_type="user_review",
            text="Amazing concert!",
            language="en",
        )

        assert content.language == "en"

    def test_default_language(self):
        """Test default language is Turkish."""
        content = EventContentNode(event_uuid="event-1", content_type="description")

        assert content.language == "tr"
