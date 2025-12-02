"""
Simple test spider that creates dummy events to verify the pipeline works.
"""

from src.scrapers.spiders.base import BaseEventSpider
from src.scrapers.items import EventItem


class TestSpider(BaseEventSpider):
    """
    Test spider that creates dummy events without scraping any website.
    Use this to verify your database pipeline works.
    """

    name = "test"

    def start_requests(self):
        """Generate dummy request to trigger parse."""
        # We need to yield at least one request for parse to be called
        # Use a fake URL since we won't actually fetch it
        from scrapy import Request
        yield Request(
            url="http://example.com",
            callback=self.parse,
            dont_filter=True,
            errback=lambda x: None,  # Ignore errors
        )

    def parse(self, response):
        """Generate test events."""

        # Create 5 dummy events
        test_events = [
            {
                "title": "Kel Diva - Haluk Bilginer",
                "venue": "Zorlu PSM",
                "date": "2024-12-15",
                "price": 850.0,
                "city": "İstanbul",
                "category": "Tiyatro",
                "url": "https://example.com/kel-diva",
            },
            {
                "title": "Kral Lear - Haluk Bilginer",
                "venue": "Zorlu PSM",
                "date": "2024-12-20",
                "price": 950.0,
                "city": "İstanbul",
                "category": "Tiyatro",
                "url": "https://example.com/kral-lear",
            },
            {
                "title": "Amadeus",
                "venue": "Kadıköy Halk Eğitim Merkezi",
                "date": "2024-12-18",
                "price": 350.0,
                "city": "İstanbul",
                "category": "Tiyatro",
                "url": "https://example.com/amadeus",
            },
            {
                "title": "Çok Uzak Fazla Yakın",
                "venue": "İş Sanat",
                "date": "2024-12-22",
                "price": 450.0,
                "city": "İstanbul",
                "category": "Tiyatro",
                "url": "https://example.com/cok-uzak",
            },
            {
                "title": "Cehennem Eğlenceleri",
                "venue": "Bakırköy Belediye Tiyatrosu",
                "date": "2024-12-25",
                "price": 275.0,
                "city": "İstanbul",
                "category": "Tiyatro",
                "url": "https://example.com/cehennem",
            },
        ]

        # Yield each event
        for event_data in test_events:
            event_item = EventItem(
                title=event_data["title"],
                venue=event_data["venue"],
                date=event_data["date"],
                price=event_data["price"],
                city=event_data["city"],
                category=event_data["category"],
                url=event_data["url"],
                source="test",
            )

            self.log_event(event_item)
            yield event_item
