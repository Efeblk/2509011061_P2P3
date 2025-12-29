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

    # Updated URL that works - All Turkey events for next 14 days
    start_urls = ["https://www.biletix.com/search/TURKIYE/tr?category_sb=-1&date_sb=next14days"]

    custom_settings = {
        **BaseEventSpider.custom_settings,
        "PLAYWRIGHT_PROCESS_REQUEST_HEADERS": None,
        "DOWNLOAD_DELAY": 0,
        "CONCURRENT_REQUESTS": 64,
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

            # Click "Daha Fazla Göster" (Show More) button until all events loaded
            max_clicks = 20  # Safety limit to prevent infinite loop
            clicks_performed = 0

            for click_num in range(1, max_clicks + 1):
                try:
                    # Look for "Show More" button
                    show_more_btn = await page.query_selector("a.search_load_more")

                    if not show_more_btn:
                        self.logger.info(
                            f"✓ No more 'Show More' button - all events loaded ({clicks_performed} clicks)"
                        )
                        break

                    # Check if visible
                    is_visible = await show_more_btn.is_visible()
                    if not is_visible:
                        self.logger.info(f"✓ 'Show More' button hidden - all events loaded ({clicks_performed} clicks)")
                        break

                    # Click and wait for new events to load
                    events_before = len(await page.query_selector_all("div.listevent.searchResultEvent"))
                    await show_more_btn.click()
                    await asyncio.sleep(2)  # Wait for events to load

                    events_after = len(await page.query_selector_all("div.listevent.searchResultEvent"))
                    new_events = events_after - events_before
                    clicks_performed += 1

                    self.logger.info(
                        f"📄 Click {click_num}: +{new_events} events ({events_before} → {events_after} total)"
                    )

                    if new_events == 0:
                        self.logger.info("✓ No new events loaded - stopping")
                        break

                except Exception as e:
                    self.logger.warning(f"Error clicking 'Show More': {e}")
                    break

            if clicks_performed > 0:
                self.logger.info(f"✅ Loaded all events with {clicks_performed} clicks")

            # Extract page content after loading all events
            content = await page.content()

            # Save to file for debugging
            with open("scrapy_page_content.html", "w", encoding="utf-8") as f:
                f.write(content)

            self.logger.info(f"Page content: {len(content)} chars")

            # Replace response body
            from scrapy.http import HtmlResponse

            response = HtmlResponse(url=response.url, body=content, encoding="utf-8")

        except Exception as e:
            self.logger.error(f"Critical error in parse: {e}")

        finally:
            await page.close()

        # Parse events from the page using correct selector
        # Filter to actual event containers (not mobile status elements)
        events = response.css("div.listevent.searchResultEvent")

        total_on_page = len(events)
        self.logger.info(f"📊 Found {total_on_page} event elements on page")

        events_yielded = 0
        events_skipped = 0

        for idx, event in enumerate(events, 1):
            try:
                # Extract data using multiple possible selectors
                title = self.extract_title(event)
                venue = self.extract_venue(event)
                city = self.extract_city(event)
                date = self.extract_date(event)
                price = self.extract_price_from_element(event)
                url = self.extract_url(event, response)
                image_url = self.extract_image(event)

                if title and url:  # Only yield if we have at least a title and URL
                    # Visit detail page to get price
                    yield scrapy.Request(
                        url=url,
                        callback=self.parse_event_detail,
                        meta={
                            "playwright": True,
                            "playwright_include_page": True,
                            "playwright_page_goto_kwargs": {
                                "wait_until": "domcontentloaded",
                                "timeout": 60000,
                            },
                            "title": title,
                            "venue": venue,
                            "city": city,
                            "date": date,
                            "image_url": image_url,
                            "source": "biletix",
                        },
                        errback=self.errback_close_page,
                    )
                    events_yielded += 1
                else:
                    events_skipped += 1
                    self.logger.debug(f"Event #{idx} skipped: no title or URL found")

            except Exception as e:
                events_skipped += 1
                self.logger.error(f"Error parsing event #{idx}: {e}")
                continue

        # Verification: Check if we processed all events
        processed_total = events_yielded + events_skipped

        self.logger.info(
            f"✓ Processed {processed_total}/{total_on_page} events: {events_yielded} yielded, {events_skipped} skipped"
        )

        # Alert if there's a mismatch
        if processed_total != total_on_page:
            self.logger.warning(f"⚠️  MISMATCH: Processed {processed_total} but found {total_on_page} on page!")
        elif events_skipped > 0:
            self.logger.info(f"✅ All {total_on_page} events processed ({events_skipped} skipped due to missing data)")
        else:
            self.logger.info(f"✅ All {total_on_page} events successfully processed!")

    async def parse_event_detail(self, response):
        """Parse event detail page to extract price."""
        page = response.meta["playwright_page"]

        try:
            # Wait for page to load
            await page.wait_for_load_state("domcontentloaded")
            await asyncio.sleep(2)

            # Extract price
            price = None

            # Try 1: Standard price block
            try:
                # Look for price elements
                # Common selectors: .price, .event-price, .ticket-price
                price_el = await page.query_selector(".price, .event-price, .ticket-price, [class*='price']")
                if price_el:
                    price_text = await price_el.inner_text()
                    if price_text:
                        price = self.extract_price(price_text)
            except Exception:
                pass

            # Try 2: Look for "Satın Al" button context or specific price containers
            if not price:
                try:
                    # Sometimes price is near the buy button
                    buy_section = await page.query_selector("#buy-tickets, .buy-tickets")
                    if buy_section:
                        text = await buy_section.inner_text()
                        # regex for price
                        import re

                        match = re.search(r"(\d+[,.]\d{2})\s*TL", text)
                        if match:
                            price = self.extract_price(match.group(1))
                except Exception:
                    pass

            # DEBUG: Dump HTML if price is missing
            if not price:
                try:
                    content = await page.content()
                    self.logger.warning(
                        f"⚠️ Price missing for '{response.meta['title']}' on detail page. HTML dump: {content[:500]}..."
                    )
                    # Save full HTML for inspection
                    with open(f"biletix_detail_{response.meta['title'][:10]}.html", "w", encoding="utf-8") as f:
                        f.write(content)
                except Exception:
                    pass
            else:
                self.logger.info(f"✓ Found price for '{response.meta['title']}': {price}")

            # Yield the final item
            event_item = EventItem(
                title=self.clean_text(response.meta["title"]),
                venue=self.clean_text(response.meta["venue"]) if response.meta["venue"] else None,
                city=self.clean_text(response.meta["city"]) if response.meta["city"] else None,
                date=response.meta["date"],
                price=price,
                url=response.url,
                image_url=response.meta["image_url"],
                category="Tiyatro",
                source="biletix",
            )
            yield event_item

        except Exception as e:
            self.logger.error(f"Error parsing detail page for {response.url}: {e}")
        finally:
            await page.close()

    def extract_title(self, element):
        """Extract event title from element."""
        # Based on actual Biletix HTML structure
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

    def extract_city(self, element):
        """Extract city name from element."""
        # City is in <span class="ln2 searchResultCity">
        # Note: Don't use just "span.ln2" as fallback - it catches "Satışta" (On Sale) text
        city = element.css("span.searchResultCity::text").get()
        if city and city.strip():
            return city.strip()

        return None

    def extract_date(self, element):
        """Extract event date from element."""
        # Date is in <span class="ln1"> like "Sal, 02/12/25"
        date_spans = element.css(".searchResultInfo3 span.ln1::text").getall()

        for date_text in date_spans:
            if date_text and "," in date_text and "/" in date_text:
                # Found date like "Sal, 02/12/25"
                # Clean up trailing dash artifact
                cleaned = date_text.strip().rstrip(" -")
                return cleaned

        # Alternative: just look for any span with date format
        all_text = element.css("span.ln1::text").getall()
        for text in all_text:
            if text and "/" in text:
                # Clean up trailing dash artifact
                cleaned = text.strip().rstrip(" -")
                return cleaned

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
