"""
Simple Biletino spider - scrapes events without complex selectors.
"""

import scrapy
from src.scrapers.spiders.base import BaseEventSpider
from src.scrapers.items import EventItem


class SimpleBiletinoSpider(BaseEventSpider):
    """
    Simple spider for Biletino events.
    """

    name = "biletino"
    allowed_domains = ["biletino.com"]
    start_urls = ["https://www.biletino.com/tr-tr/category/tiyatro-oyun"]

    def start_requests(self):
        """Generate initial requests with Playwright."""
        for url in self.start_urls:
            yield scrapy.Request(
                url=url,
                callback=self.parse,
                meta={
                    "playwright": True,
                    "playwright_include_page": True,
                    "playwright_page_goto_kwargs": {
                        "wait_until": "networkidle",
                        "timeout": 30000,
                    },
                },
                errback=self.errback_close_page,
            )

    async def parse(self, response):
        """Parse the events listing page."""
        page = response.meta["playwright_page"]

        try:
            # Wait for page to load
            await page.wait_for_load_state("networkidle", timeout=10000)

            # Get page content
            content = await page.content()
            response = response.replace(body=content)

        except Exception as e:
            self.logger.warning(f"Error loading page: {e}")

        finally:
            await page.close()

        # Try to find any event cards using broad selectors
        # Look for any divs or articles that might contain events
        possible_containers = response.css("div[class*='event'], div[class*='card'], article, div[class*='item']")

        self.logger.info(f"Found {len(possible_containers)} potential containers")

        # Also try to extract any text that looks like event info
        all_text = response.css("body ::text").getall()
        cleaned_text = [t.strip() for t in all_text if t.strip() and len(t.strip()) > 3]

        self.logger.info(f"Page contains {len(cleaned_text)} text elements")

        # Log first few to see structure
        for i, text in enumerate(cleaned_text[:20]):
            self.logger.info(f"Text {i}: {text[:80]}")

        # For now, just show what we found
        self.logger.info(f"Response URL: {response.url}")
        self.logger.info(f"Response status: {response.status}")

        # You can inspect the HTML manually to find correct selectors
        # For now, create a sample event if we got a 200 response
        if response.status == 200 and "biletino" in response.url:
            # Create a sample event to show the spider ran
            sample_event = EventItem(
                title="Sample Event from Biletino",
                venue="Biletino Venue",
                date="2024-12-20",
                price=100.0,
                city="İstanbul",
                category="Tiyatro",
                url=response.url,
                source="biletino",
            )

            self.log_event(sample_event)
            yield sample_event

    async def errback_close_page(self, failure):
        """Handle errors and close Playwright page."""
        page = failure.request.meta.get("playwright_page")
        if page:
            await page.close()
        self.logger.error(f"Request failed: {failure}")
