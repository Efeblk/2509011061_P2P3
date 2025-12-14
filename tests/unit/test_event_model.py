"""
Unit tests for EventNode model.
"""

import pytest
from datetime import datetime
from src.models.event import EventNode


class TestEventNode:
    """Test EventNode model functionality."""

    def test_event_creation(self):
        """Test creating an event with all fields."""
        event = EventNode(
            title="Test Concert",
            description="A great concert",
            date="2025-12-15",
            venue="Test Arena",
            city="Istanbul",
            price=150.0,
            price_range="100-200 TL",
            url="https://example.com/event",
            image_url="https://example.com/image.jpg",
            category="Concert",
            source="biletix",
        )

        assert event.title == "Test Concert"
        assert event.venue == "Test Arena"
        assert event.city == "Istanbul"
        assert event.price == 150.0
        assert event.category == "Concert"
        assert event.source == "biletix"

    def test_event_with_minimal_fields(self):
        """Test creating an event with only required fields."""
        event = EventNode(title="Minimal Event")

        assert event.title == "Minimal Event"
        assert event.description is None
        assert event.venue is None
        assert event.city is None
        assert event.price is None

    def test_event_label(self):
        """Test that event label is correct."""
        event = EventNode(title="Test Event")
        assert event.label == "Event"

    def test_event_properties_with_none_values(self):
        """Test that None values are converted to empty strings/zeros."""
        event = EventNode(
            title="Test Event",
            venue=None,
            city=None,
            description=None,
        )

        props = event._get_properties()

        assert props["venue"] == ""
        assert props["city"] == ""
        assert props["description"] == ""
        assert props["price"] is None

    def test_event_properties_with_values(self):
        """Test that actual values are preserved in properties."""
        event = EventNode(
            title="Test Event",
            venue="Test Venue",
            city="Istanbul",
            price=100.0,
            url="https://example.com",
        )

        props = event._get_properties()

        assert props["title"] == "Test Event"
        assert props["venue"] == "Test Venue"
        assert props["city"] == "Istanbul"
        assert props["price"] == 100.0
        assert props["url"] == "https://example.com"

    def test_event_created_at_timestamp(self):
        """Test that created_at timestamp is set."""
        event = EventNode(title="Test Event")

        assert event.created_at is not None
        assert isinstance(event.created_at, datetime)

    def test_event_uuid_is_unique(self):
        """Test that each event gets a unique UUID."""
        event1 = EventNode(title="Event 1")
        event2 = EventNode(title="Event 2")

        assert event1.uuid != event2.uuid

    def test_event_repr(self):
        """Test string representation of event."""
        event = EventNode(
            title="Test Concert",
            date="2025-12-15",
            venue="Test Arena",
        )

        repr_str = repr(event)
        assert "Test Concert" in repr_str
        assert "2025-12-15" in repr_str
        assert "Test Arena" in repr_str

    def test_event_ai_fields_default_to_none(self):
        """Test that AI analysis fields default to None."""
        event = EventNode(title="Test Event")

        assert event.ai_score is None
        assert event.ai_verdict is None
        assert event.ai_reasoning is None

    def test_event_ai_fields_in_properties(self):
        """Test that AI fields are included in properties."""
        event = EventNode(
            title="Test Event",
            ai_score=0.85,
            ai_verdict="recommended",
            ai_reasoning="Great event for music lovers",
        )

        props = event._get_properties()

        assert props["ai_score"] == 0.85
        assert props["ai_verdict"] == "recommended"
        assert props["ai_reasoning"] == "Great event for music lovers"

    def test_venue_handling(self):
        """Test specific venue handling logic."""
        # Case 1: Venue is None -> Empty string in props
        event_none = EventNode(title="No Venue", venue=None)
        assert event_none.venue is None
        assert event_none._get_properties()["venue"] == ""

        # Case 2: Venue is provided
        event_venue = EventNode(title="Venue", venue="AKM")
        assert event_venue.venue == "AKM"
        assert event_venue._get_properties()["venue"] == "AKM"
