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
    """

    def __init__(self):
        self.seen_titles = set()

    def process_item(self, item, spider):
        """Check for duplicate events."""
        title = item.get("title")

        if title in self.seen_titles:
            logger.info(f"Duplicate found: {title}")
            raise DropItem(f"Duplicate event: {title}")

        self.seen_titles.add(title)

        # Also check database for existing event
        existing = EventNode.find_by_title(title)
        if existing:
            logger.info(f"Event already in database: {title}")
            raise DropItem(f"Event exists in database: {title}")

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
