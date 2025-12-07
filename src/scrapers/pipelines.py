"""
Scrapy pipelines for processing scraped items.
"""

from loguru import logger
from src.models.event import EventNode
from src.models.event_content import EventContentNode


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
    Uses title + venue + date as unique key to handle events with multiple dates.
    """

    def __init__(self):
        self.seen_events = set()  # Store (title, venue, date) tuples

    def process_item(self, item, spider):
        """Check for duplicate events based on title + venue + date."""
        title = item.get("title")
        # Normalize venue and date to empty string if None (match database storage)
        venue = item.get("venue") or ""
        date = item.get("date") or ""

        # Create unique key from title, venue, and date
        event_key = (title, venue, date)

        # Check in-memory duplicates in current scraping session
        if event_key in self.seen_events:
            logger.info(f"Duplicate found in session: {title} @ {venue} on {date}")
            raise DropItem(f"Duplicate event: {title} @ {venue} on {date}")

        self.seen_events.add(event_key)

        # Also check database for existing event with same title, venue, AND date
        existing = EventNode.find_by_title_venue_and_date(title, venue, date)
        if existing:
            logger.info(f"Duplicate found in database: {title} @ {venue} on {date}")
            raise DropItem(f"Event exists in database: {title} @ {venue} on {date}")

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

    async def process_item(self, item, spider):
        """Save item to FalkorDB asynchronously."""
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

            # Save to database in a separate thread to avoid blocking the reactor
            import asyncio

            save_success = await asyncio.to_thread(event.save)

            if save_success:
                self.events_saved += 1
                logger.info(f"✓ Saved event to database: {event.title}")

                # If rating data exists, create EventContent node
                if item.get("rating") is not None and item.get("rating_count") is not None:
                    event_content = EventContentNode(
                        event_uuid=event.uuid,
                        content_type="platform_rating",  # Rating from the ticketing platform
                        rating=item.get("rating"),
                        rating_count=item.get("rating_count"),
                        author=item.get("source", "platform"),  # e.g., "biletinial"
                    )

                    # Offload to thread
                    content_save_success = await asyncio.to_thread(event_content.save_with_relationship)

                    if content_save_success:
                        logger.info(
                            f"✓ Saved rating for event: {event.title} "
                            f"({item.get('rating')}/5, {item.get('rating_count')} reviews)"
                        )
                    else:
                        logger.warning(f"⚠️  Failed to save rating for event: {event.title}")

                # If reviews exist, create EventContent nodes for each review
                if item.get("reviews"):
                    reviews = item.get("reviews")
                    saved_reviews = 0
                    saved_ai_summaries = 0

                    for review in reviews:
                        content_type = review.get("content_type", "user_review")

                        review_content = EventContentNode(
                            event_uuid=event.uuid,
                            content_type=content_type,  # "user_review" or "ai_summary"
                            text=review.get("text"),
                            author=review.get("author", "Anonymous"),
                            rating=review.get("rating"),
                        )

                        # Offload to thread
                        review_save_success = await asyncio.to_thread(review_content.save_with_relationship)

                        if review_save_success:
                            if content_type == "ai_summary":
                                saved_ai_summaries += 1
                            else:
                                saved_reviews += 1
                        else:
                            logger.warning(f"⚠️  Failed to save {content_type} for event: {event.title}")

                    if saved_reviews > 0 or saved_ai_summaries > 0:
                        msg = f"✓ Saved "
                        parts = []
                        if saved_ai_summaries > 0:
                            parts.append(f"{saved_ai_summaries} AI summary")
                        if saved_reviews > 0:
                            parts.append(f"{saved_reviews} user reviews")
                        msg += " + ".join(parts) + f" for event: {event.title}"
                        logger.info(msg)

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
