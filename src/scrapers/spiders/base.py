"""
Base spider class with common functionality.
Implements Template Method pattern for scrapers.
"""

from abc import ABC, abstractmethod
import scrapy
from loguru import logger


class BaseEventSpider(scrapy.Spider, ABC):
    """
    Abstract base class for event spiders.
    Provides common functionality and defines interface for subclasses.
    """

    # Spider settings
    custom_settings = {
        "PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT": 30000,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.events_scraped = 0

    @abstractmethod
    def parse(self, response):
        """
        Main parsing method.
        Must be implemented by subclasses.
        """
        pass

    def log_event(self, event_data):
        """Log scraped event information."""
        self.events_scraped += 1
        logger.info(f"Scraped event #{self.events_scraped}: {event_data.get('title', 'Unknown')}")

    def clean_text(self, text):
        """Clean and normalize text."""
        if not text:
            return ""
        return " ".join(text.strip().split())

    def extract_price(self, price_text):
        """
        Extract numeric price from text.
        Examples: "150 TL" -> 150.0, "Free" -> 0.0
        """
        if not price_text:
            return None

        # Remove common currency symbols and text
        price_text = price_text.replace("TL", "").replace("₺", "").replace(",", ".")
        price_text = price_text.strip()

        # Handle "Free" or "Ücretsiz"
        if any(word in price_text.lower() for word in ["free", "ücretsiz", "bedava"]):
            return 0.0

        # Extract first number
        import re

        match = re.search(r"(\d+(?:\.\d+)?)", price_text)
        if match:
            return float(match.group(1))

        return None

    def closed(self, reason):
        """Called when spider is closed."""
        logger.info(f"Spider closed: {self.name}")
        logger.info(f"Total events scraped: {self.events_scraped}")
        logger.info(f"Reason: {reason}")
