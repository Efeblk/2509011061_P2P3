"""
Simple script to test the scraper and view results.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from loguru import logger
from config.settings import settings
from src.database.connection import db_connection
from src.models.event import EventNode


def main():
    """Test scraper and display results."""
    logger.info("=" * 60)
    logger.info("EventGraph - Scraper Test")
    logger.info("=" * 60)

    # Check database connection
    if not db_connection.health_check():
        logger.error("❌ Database connection failed!")
        logger.error("Please start FalkorDB: docker-compose up -d falkordb")
        return

    logger.info("✅ Database connected")

    # Get current stats
    stats = db_connection.get_stats()
    logger.info(f"\n📊 Current Database Stats:")
    logger.info(f"   Events: {stats.get('event_count', 0)}")
    logger.info(f"   Total nodes: {stats.get('event_count', 0)}")
    logger.info(f"   Memory: {stats.get('memory_used', 'N/A')}")

    # Get all events
    events = EventNode.find_all()

    if not events:
        logger.info("\n⚠️  No events found in database")
        logger.info("\n💡 To scrape events, run:")
        logger.info("   scrapy crawl biletix")
    else:
        logger.info(f"\n📋 Found {len(events)} events:")
        logger.info("-" * 60)

        for i, event in enumerate(events, 1):
            logger.info(f"\n{i}. {event.title}")
            logger.info(f"   Venue: {event.venue or 'N/A'}")
            logger.info(f"   Date: {event.date or 'N/A'}")
            logger.info(f"   Price: {event.price or 'N/A'} TL")
            logger.info(f"   Category: {event.category or 'N/A'}")
            logger.info(f"   Source: {event.source}")
            if event.url:
                logger.info(f"   URL: {event.url}")

    logger.info("\n" + "=" * 60)


if __name__ == "__main__":
    main()
