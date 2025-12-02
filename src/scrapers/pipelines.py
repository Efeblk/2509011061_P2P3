"""
Scrapy pipelines for processing scraped items.
"""

from loguru import logger
from src.models.event import EventNode


class ValidationPipeline:
    """
    Pipeline for validating scraped data.
    Ensures required fields are present and valid.
    """

    def process_item(self, item, spider):
        """Validate item data."""
        # Check required fields
        if not item.get("title"):
            logger.warning("Dropping item: missing title")
            raise DropItem("Missing title")

        # Clean and validate price
        if item.get("price"):
            try:
                price = float(item["price"])
                if price < 0:
                    logger.warning(f"Invalid negative price: {price}")
                    item["price"] = None
                elif price > 100000:
                    logger.warning(f"Suspiciously high price: {price}")
                    item["price"] = None
            except (ValueError, TypeError):
                logger.warning(f"Invalid price format: {item.get('price')}")
                item["price"] = None

        # Ensure source is set
        if not item.get("source"):
            item["source"] = spider.name

        logger.debug(f"Validated item: {item.get('title')}")
        return item


class DuplicatesPipeline:
    """
    Pipeline for detecting and handling duplicate events.
    Uses title + venue as unique key since same event can occur at different venues.
    """

    def __init__(self):
        self.seen_events = set()  # Store (title, venue) tuples

    def process_item(self, item, spider):
        """Check for duplicate events based on title + venue."""
        title = item.get("title")
        venue = item.get("venue", "")  # Empty string if no venue

        # Create unique key from title and venue
        event_key = (title, venue)

        # Check in-memory duplicates in current scraping session
        if event_key in self.seen_events:
            logger.info(f"Duplicate found: {title} @ {venue}")
            raise DropItem(f"Duplicate event: {title} @ {venue}")

        self.seen_events.add(event_key)

        # Also check database for existing event with same title AND venue
        existing = EventNode.find_by_title_and_venue(title, venue)
        if existing:
            logger.info(f"Event already in database: {title} @ {venue}")
            raise DropItem(f"Event exists in database: {title} @ {venue}")

        return item


class FalkorDBPipeline:
    """
    Pipeline for saving scraped events to FalkorDB.
    """

    def __init__(self):
        self.events_saved = 0
        self.events_failed = 0

    def open_spider(self, spider):
        """Called when spider opens."""
        logger.info(f"Opening FalkorDB pipeline for spider: {spider.name}")

    def close_spider(self, spider):
        """Called when spider closes."""
        logger.info(f"FalkorDB pipeline closed for spider: {spider.name}")
        logger.info(f"Events saved: {self.events_saved}")
        logger.info(f"Events failed: {self.events_failed}")

    def process_item(self, item, spider):
        """Save item to FalkorDB."""
        try:
            # Create EventNode from item
            event = EventNode(
                title=item.get("title", ""),
                description=item.get("description"),
                date=item.get("date"),
                venue=item.get("venue"),
                city=item.get("city"),
                price=item.get("price"),
                price_range=item.get("price_range"),
                url=item.get("url"),
                image_url=item.get("image_url"),
                category=item.get("category"),
                source=item.get("source"),
            )

            # Save to database
            if event.save():
                self.events_saved += 1
                logger.info(f"✓ Saved event to database: {event.title}")
            else:
                self.events_failed += 1
                logger.error(f"✗ Failed to save event: {event.title}")

            return item

        except Exception as e:
            self.events_failed += 1
            logger.error(f"Error saving event to database: {e}")
            logger.error(f"Item: {item}")
            raise DropItem(f"Database error: {e}")


class DropItem(Exception):
    """Exception to drop an item from the pipeline."""
    pass
