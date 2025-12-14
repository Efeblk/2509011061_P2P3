"""
Unit tests for Scrapy pipelines.
"""

import pytest
from unittest.mock import Mock, patch
from src.scrapers.pipelines import (
    ValidationPipeline,
    DuplicatesPipeline,
    FalkorDBPipeline,
    DropItem,
)


class TestValidationPipeline:
    """Test ValidationPipeline functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.pipeline = ValidationPipeline()
        self.spider = Mock()
        self.spider.name = "test_spider"

    def test_valid_item_passes(self):
        """Test that valid items pass through the pipeline."""
        item = {
            "title": "Test Event",
            "date": "2025-12-15",
            "url": "https://example.com",
            "source": "biletix",
        }

        result = self.pipeline.process_item(item, self.spider)
        assert result == item

    def test_missing_title_raises_drop_item(self):
        """Test that items without title are dropped."""
        item = {
            "date": "2025-12-15",
            "url": "https://example.com",
        }

        with pytest.raises(DropItem, match="Missing title"):
            self.pipeline.process_item(item, self.spider)

    def test_empty_title_raises_drop_item(self):
        """Test that items with empty title are dropped."""
        item = {
            "title": "",
            "date": "2025-12-15",
        }

        with pytest.raises(DropItem, match="Missing title"):
            self.pipeline.process_item(item, self.spider)

    def test_valid_price_is_preserved(self):
        """Test that valid prices are kept."""
        item = {
            "title": "Test Event",
            "price": 100.0,
        }

        result = self.pipeline.process_item(item, self.spider)
        assert result["price"] == 100.0

    def test_negative_price_is_nullified(self):
        """Test that negative prices are set to None."""
        item = {
            "title": "Test Event",
            "price": -50.0,
        }

        result = self.pipeline.process_item(item, self.spider)
        assert result["price"] is None

    def test_suspiciously_high_price_is_nullified(self):
        """Test that unrealistically high prices are set to None."""
        item = {
            "title": "Test Event",
            "price": 150000.0,
        }

        result = self.pipeline.process_item(item, self.spider)
        assert result["price"] is None

    def test_invalid_price_format_is_nullified(self):
        """Test that invalid price formats are set to None."""
        item = {
            "title": "Test Event",
            "price": "invalid",
        }

        result = self.pipeline.process_item(item, self.spider)
        assert result["price"] is None

    def test_source_is_set_from_spider_if_missing(self):
        """Test that source is set to spider name if not provided."""
        item = {
            "title": "Test Event",
        }

        result = self.pipeline.process_item(item, self.spider)
        assert result["source"] == "test_spider"

    def test_existing_source_is_preserved(self):
        """Test that existing source is not overwritten."""
        item = {
            "title": "Test Event",
            "source": "biletix",
        }

        result = self.pipeline.process_item(item, self.spider)
        assert result["source"] == "biletix"


class TestDuplicatesPipeline:
    """Test DuplicatesPipeline functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.pipeline = DuplicatesPipeline()
        self.spider = Mock()

    @patch("src.scrapers.pipelines.EventNode.find_by_title_venue_and_date")
    def test_unique_item_passes(self, mock_find):
        """Test that unique items pass through."""
        mock_find.return_value = None  # Not found in database

        item = {
            "title": "Test Event",
            "venue": "Test Venue",
            "date": "2025-12-15",
        }

        result = self.pipeline.process_item(item, self.spider)
        assert result == item
        assert ("Test Event", "Test Venue", "2025-12-15") in self.pipeline.seen_events

    @patch("src.scrapers.pipelines.EventNode.find_by_title_venue_and_date")
    def test_duplicate_in_session_is_dropped(self, mock_find):
        """Test that duplicates within the same session are dropped."""
        mock_find.return_value = None

        item = {
            "title": "Test Event",
            "venue": "Test Venue",
            "date": "2025-12-15",
        }

        # First item passes
        self.pipeline.process_item(item, self.spider)

        # Second identical item is dropped
        with pytest.raises(DropItem, match="Duplicate event"):
            self.pipeline.process_item(item, self.spider)

    @patch("src.scrapers.pipelines.EventNode.find_by_title_venue_and_date")
    def test_duplicate_in_database_is_dropped(self, mock_find):
        """Test that items already in database are dropped."""
        mock_event = Mock()
        mock_find.return_value = mock_event  # Found in database

        item = {
            "title": "Test Event",
            "venue": "Test Venue",
            "date": "2025-12-15",
        }

        with pytest.raises(DropItem, match="Event exists in database"):
            self.pipeline.process_item(item, self.spider)

    @patch("src.scrapers.pipelines.EventNode.find_by_title_venue_and_date")
    def test_none_venue_normalized_to_empty_string(self, mock_find):
        """Test that None venue is normalized to empty string."""
        mock_find.return_value = None

        item = {
            "title": "Test Event",
            "venue": None,
            "date": "2025-12-15",
        }

        self.pipeline.process_item(item, self.spider)
        assert ("Test Event", "", "2025-12-15") in self.pipeline.seen_events

    @patch("src.scrapers.pipelines.EventNode.find_by_title_venue_and_date")
    def test_same_event_different_dates_allowed(self, mock_find):
        """Test that same event with different dates are not duplicates."""
        mock_find.return_value = None

        item1 = {
            "title": "Test Event",
            "venue": "Test Venue",
            "date": "2025-12-15",
        }

        item2 = {
            "title": "Test Event",
            "venue": "Test Venue",
            "date": "2025-12-16",
        }

        # Both items should pass
        self.pipeline.process_item(item1, self.spider)
        result = self.pipeline.process_item(item2, self.spider)
        assert result == item2


@pytest.mark.asyncio
class TestFalkorDBPipeline:
    """Test FalkorDBPipeline functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.pipeline = FalkorDBPipeline()
        self.spider = Mock()
        self.spider.name = "test_spider"

    async def test_pipeline_initialization(self):
        """Test pipeline initializes counters."""
        assert self.pipeline.events_saved == 0
        assert self.pipeline.events_failed == 0

    @patch("src.scrapers.pipelines.db_connection")
    async def test_successful_save_increments_counter(self, mock_db):
        """Test that successful saves increment the counter."""
        # Mock execute_query to return True (simulating success)
        mock_db.execute_query.return_value = True

        item = {
            "title": "Test Event",
            "date": "2025-12-15",
            "venue": "Test Venue",
            "city": "Istanbul",
            "uuid": "test-uuid-1",
            "url": "http://example.com",
            "price": 100.0,
            "category": "Music",
            "image_url": "http://example.com/img.jpg",
            "description": "Test Description",
            "source": "test_spider",
        }

        await self.pipeline.process_item(item, self.spider)
        assert self.pipeline.events_saved == 1
        assert self.pipeline.events_failed == 0

    @patch("src.scrapers.pipelines.db_connection")
    async def test_failed_save_increments_failure_counter(self, mock_db):
        """Test that failed saves increment failure counter."""
        # Mock execute_query to return False/None (simulating failure)
        mock_db.execute_query.return_value = None

        item = {
            "title": "Test Event",
            "uuid": "test-uuid-2",
            "date": "2025-12-15",
            "city": "Istanbul",
            "venue": "Test Venue",
            "url": "http://example.com",
            "price": 100.0,
            "category": "Music",
            "image_url": "http://example.com/img.jpg",
            "description": "Test Description",
            "source": "test_spider",
        }

        await self.pipeline.process_item(item, self.spider)
        assert self.pipeline.events_saved == 0
        assert self.pipeline.events_failed == 1

    @patch("src.scrapers.pipelines.db_connection")
    async def test_exception_during_save_raises_drop_item(self, mock_db):
        """Test that exceptions during save raise DropItem."""
        mock_db.execute_query.side_effect = Exception("Database error")

        item = {
            "title": "Test Event",
            "uuid": "test-uuid-3",
            "date": "2025-12-15",
            "city": "Istanbul",
            "venue": "Test Venue",
            "url": "http://example.com",
            "price": 100.0,
            "category": "Music",
            "image_url": "http://example.com/img.jpg",
            "description": "Test Description",
            "source": "test_spider",
        }

        with pytest.raises(DropItem, match="Database error"):
            await self.pipeline.process_item(item, self.spider)

        assert self.pipeline.events_failed == 1
