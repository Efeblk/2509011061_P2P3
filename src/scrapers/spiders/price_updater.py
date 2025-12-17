"""
Spider to re-scrape only prices for existing events without restarting the whole process.
Reads URLs from FalkorDB and visits them to update prices.
"""

import scrapy
from loguru import logger
from .biletinial_spider import BiletinialSpider
from src.database.connection import db_connection


class BiletinialPriceUpdaterSpider(BiletinialSpider):
    name = "biletinial_price_updater"

    custom_settings = {
        **BiletinialSpider.custom_settings,
        "ROBOTSTXT_OBEY": False,
        "CONCURRENT_REQUESTS": 128,  # Extreme performance
        "DOWNLOAD_TIMEOUT": 30,
        "LOG_LEVEL": "INFO",
        "PLAYWRIGHT_ABORT_REQUEST": lambda req: req.resource_type
        in ["image", "media", "font", "stylesheet"],  # Speed up
        "RETRY_ENABLED": False,  # Do not retry timeouts, just skip to avoid loops
    }

    def start_requests(self):
        """Fetch missing-price events from DB and crawl them directly."""
        logger.info("🔌 Connecting to DB to find events with missing prices...")

        # Query for Biletinial events with no price
        query = """
        MATCH (e:Event)
        WHERE e.source = 'biletinial' AND (e.price IS NULL)
        RETURN e.url, e.title, e.uuid
        """

        try:
            result = db_connection.graph.query(query).result_set
            # ...

        except Exception as e:
            logger.error(f"Failed to fetch events from DB: {e}")

    async def errback_close_page(self, failure):
        """Clean up Playwright page on error."""
        page = failure.request.meta.get("playwright_page")
        if page:
            await page.close()
            logger.warning(f"⚠️ Page closed due to error: {failure.reprFailure()}")
