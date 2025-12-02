"""
Biletix spider for scraping events from biletix.com
"""

import asyncio
from src.scrapers.spiders.base import BaseEventSpider
from src.scrapers.items import EventItem


class BiletixSpider(BaseEventSpider):
    """
    Spider for scraping events from Biletix.
    """

    name = "biletix"
    allowed_domains = ["biletix.com"]

    # Updated URL that works - Istanbul events for next 14 days
    start_urls = ["https://www.biletix.com/search/TURKIYE/tr?category_sb=-1&date_sb=next14days&city_sb=İstanbul"]

    custom_settings = {
        **BaseEventSpider.custom_settings,
        "PLAYWRIGHT_PROCESS_REQUEST_HEADERS": None,
        "DOWNLOAD_DELAY": 3,
    }

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
                        "wait_until": "domcontentloaded",
                        "timeout": 60000,
                    },
                },
                errback=self.errback_close_page,
            )

    async def parse(self, response):
        """Parse the main events listing page."""
        page = response.meta["playwright_page"]

        try:
            # Wait for basic page load
            await asyncio.sleep(5)

            # Try to wait for events, but don't fail if not found
            try:
                await page.wait_for_selector('[class*="searchResultEvent"]', timeout=10000)
                self.logger.info("✓ Found searchResultEvent selector")
            except Exception as e:
                self.logger.warning(f"Selector not found, continuing anyway: {e}")

            # Extract page content and save for debugging
            content = await page.content()

            # Save to file for debugging
            with open("scrapy_page_content.html", "w", encoding="utf-8") as f:
                f.write(content)

            self.logger.info(f"Page content length: {len(content)} chars")
            self.logger.info(f"✓ Saved page content to scrapy_page_content.html")

            # Replace response body
            from scrapy.http import HtmlResponse
            response = HtmlResponse(url=response.url, body=content, encoding='utf-8')

        except Exception as e:
            self.logger.error(f"Critical error in parse: {e}")

        finally:
            await page.close()

        # Parse events from the page using correct selector
        # Filter to actual event containers (not mobile status elements)
        events = response.css('div.listevent.searchResultEvent')

        self.logger.info(f"Found {len(events)} actual event elements")

        for event in events[:20]:  # Limit to first 20 events
            try:
                # Extract data using multiple possible selectors
                title = self.extract_title(event)
                venue = self.extract_venue(event)
                date = self.extract_date(event)
                price = self.extract_price_from_element(event)
                url = self.extract_url(event, response)
                image_url = self.extract_image(event)

                if title:  # Only yield if we have at least a title
                    event_item = EventItem(
                        title=self.clean_text(title),
                        venue=self.clean_text(venue) if venue else None,
                        date=date,
                        price=price,
                        url=url,
                        image_url=image_url,
                        city="İstanbul",  # Default for Biletix
                        category="Tiyatro",  # We're scraping theater section
                        source="biletix",
                    )

                    self.log_event(event_item)
                    yield event_item

            except Exception as e:
                self.logger.error(f"Error parsing event: {e}")
                continue

    def extract_title(self, element):
        """Extract event title from element."""
        # Based on actual Biletix HTML structure
        # Try event name selectors
        selectors = [
            "a.searchResultEventNameMobile::text",  # Mobile view
            "a.ln1.searchResultPlace::attr(href)",  # Has event ID in href
        ]

        # Try to get from mobile name first
        title = element.css("a.searchResultEventNameMobile::text").get()
        if title and title.strip():
            return title.strip()

        # Try to extract from searchResultInfo3
        title_spans = element.css(".searchResultInfo3 span.ln1::text").getall()
        if title_spans:
            # Often event name is in the spans
            for span_text in title_spans:
                if span_text and len(span_text.strip()) > 5:
                    return span_text.strip()

        # Fallback: get all ln1 text
        all_ln1 = element.css(".ln1::text").getall()
        if all_ln1:
            for text in all_ln1:
                if text and len(text.strip()) > 5 and not text.strip().startswith("Sal"):
                    return text.strip()

        return None

    def extract_venue(self, element):
        """Extract venue name from element."""
        # Venue is in <a class="ln1 searchResultPlace">
        venue = element.css("a.searchResultPlace::text").get()
        if venue and venue.strip():
            return venue.strip()

        # Alternative: look in searchResultInfo3
        venue_spans = element.css(".searchResultInfo3 span.ln1::text").getall()
        if len(venue_spans) > 1:
            return venue_spans[1].strip() if venue_spans[1] else None

        return None

    def extract_date(self, element):
        """Extract event date from element."""
        # Date is in <span class="ln1"> like "Sal, 02/12/25"
        date_spans = element.css(".searchResultInfo3 span.ln1::text").getall()

        for date_text in date_spans:
            if date_text and "," in date_text and "/" in date_text:
                # Found date like "Sal, 02/12/25"
                return date_text.strip()

        # Alternative: just look for any span with date format
        all_text = element.css("span.ln1::text").getall()
        for text in all_text:
            if text and "/" in text:
                return text.strip()

        return None

    def extract_price_from_element(self, element):
        """Extract price from element."""
        selectors = [
            ".price::text",
            ".event-price::text",
            "[class*='price']::text",
        ]

        for selector in selectors:
            price_text = element.css(selector).get()
            if price_text:
                return self.extract_price(price_text)

        return None

    def extract_url(self, element, response):
        """Extract event URL from element."""
        selectors = [
            "a::attr(href)",
            "[href]::attr(href)",
        ]

        for selector in selectors:
            url = element.css(selector).get()
            if url:
                return response.urljoin(url)

        return None

    def extract_image(self, element):
        """Extract image URL from element."""
        selectors = [
            "img::attr(src)",
            "img::attr(data-src)",
            "[style*='background-image']::attr(style)",
        ]

        for selector in selectors:
            img = element.css(selector).get()
            if img:
                if "url(" in img:  # Handle background-image
                    import re
                    match = re.search(r'url\(["\']?([^"\']+)["\']?\)', img)
                    if match:
                        return match.group(1)
                return img

        return None

    async def errback_close_page(self, failure):
        """Handle errors and close Playwright page."""
        page = failure.request.meta.get("playwright_page")
        if page:
            await page.close()
        self.logger.error(f"Request failed: {failure}")


import scrapy  # Import at the end to avoid circular dependency
