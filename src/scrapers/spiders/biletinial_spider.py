"""
Biletinial spider for scraping events from biletinial.com
"""

import asyncio
import scrapy
from src.scrapers.spiders.base import BaseEventSpider
from src.scrapers.items import EventItem
from src.utils.date_parser import parse_turkish_date_range


class BiletinialSpider(BaseEventSpider):
    """
    Spider for scraping events from Biletinial.
    """

    name = "biletinial"
    allowed_domains = ["biletinial.com"]

    # Istanbul events - multiple categories
    start_urls = [
        # "https://biletinial.com/tr-tr/sehrineozel/istanbul",  # City-specific page SKIP THIS FOR NOW
        "https://biletinial.com/tr-tr/muzik/istanbul",  # Music events in Istanbul
        "https://biletinial.com/tr-tr/tiyatro/istanbul",  # Theater events in Istanbul
        "https://biletinial.com/tr-tr/sinema/istanbul",  # Cinema events in Istanbul
        "https://biletinial.com/tr-tr/opera-bale/istanbul",  # Opera & Ballet events in Istanbul
        "https://biletinial.com/tr-tr/etkinlikleri/stand-up",  # Stand-up comedy events
        "https://biletinial.com/tr-tr/etkinlikleri/senfoni-etkinlikleri",  # Symphony events
    ]

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
            # Check if we need to select a city (for category pages like concerts)
            # Look for city selector dropdown
            try:
                # Try the concerts page city selector first
                city_selector = page.locator("select#citySelect, select.customSelect").first
                is_selector_visible = await city_selector.is_visible(timeout=3000)

                if is_selector_visible:
                    self.logger.info("🔍 Found city selector, selecting İstanbul...")

                    # Select Istanbul from dropdown (value="147" for İstanbul Tümü)
                    await city_selector.select_option(value="147")
                    self.logger.info("✓ Selected İstanbul from city selector")

                    # Wait for the filter to apply (JavaScript onchange event)
                    await asyncio.sleep(5)
                else:
                    # Try the modal-based city selector (yhm_select_city)
                    modal_selector = page.locator("select.yhm_select_city, select[name='city']").first
                    is_modal_visible = await modal_selector.is_visible(timeout=2000)

                    if is_modal_visible:
                        self.logger.info("🔍 Found modal city selector, selecting İstanbul...")
                        await modal_selector.select_option(value="istanbul")

                        save_button = page.locator("button.yhm_save").first
                        if await save_button.is_visible(timeout=2000):
                            await save_button.click()
                            self.logger.info("✓ Clicked save button")
                            await asyncio.sleep(5)
            except Exception as e:
                self.logger.info(f"No city selector found (page may already be city-specific): {e}")

            # Wait for event list to load (different selectors for different page types)
            event_list_selector = None
            try:
                # Try city-specific page layout first
                await page.wait_for_selector("ul.sehir-detay__liste", timeout=5000)
                event_list_selector = "ul.sehir-detay__liste li"
                self.logger.info("✓ Event list loaded (city-specific layout)")
            except Exception:
                try:
                    # Try category page layout (music, theater) - kategori__etkinlikler
                    await page.wait_for_selector("#kategori__etkinlikler ul", timeout=5000)
                    event_list_selector = "#kategori__etkinlikler ul li"
                    self.logger.info("✓ Event list loaded (kategori__etkinlikler layout)")
                except Exception:
                    try:
                        # Try category page layout with resultsGrid (concerts, etc.)
                        await page.wait_for_selector(".resultsGrid", timeout=5000)
                        event_list_selector = ".resultsGrid > a"
                        self.logger.info("✓ Event list loaded (resultsGrid layout)")
                    except Exception:
                        try:
                            # Try older category layout
                            await page.wait_for_selector("ul.yeniArama__sonuc__data", timeout=5000)
                            event_list_selector = "ul.yeniArama__sonuc__data li"
                            self.logger.info("✓ Event list loaded (yeniArama layout)")
                        except Exception as e:
                            self.logger.warning(f"No event list found: {e}")

            # Skip further processing if no event list found
            if not event_list_selector:
                self.logger.error("❌ No event list found, skipping this page")
                return

            # Wait a bit for dynamic content
            await asyncio.sleep(2)

            # Click "Daha Fazla Yükle" (Load More) button multiple times
            max_clicks = 20  # Safety limit
            clicks = 0

            self.logger.info("🔄 Looking for 'Daha Fazla Yükle' button...")

            for i in range(max_clicks):
                try:
                    # Count events before clicking (use the detected selector)
                    events_before = await page.locator(event_list_selector).count()

                    # Look for the load more button
                    # Common selectors for "Load More" buttons on Turkish sites
                    load_more_button = page.locator(
                        "button:has-text('Daha Fazla'), button:has-text('daha fazla'), a:has-text('Daha Fazla'), a:has-text('daha fazla')"
                    ).first

                    # Check if button is visible
                    is_visible = await load_more_button.is_visible(timeout=2000)

                    if not is_visible:
                        self.logger.info(f"✓ No more 'Daha Fazla Yükle' button found after {clicks} clicks")
                        break

                    # Click the button
                    await load_more_button.click()
                    clicks += 1
                    self.logger.info(f"🖱️  Click #{clicks} - Loading more events...")

                    # Wait for new content to load
                    await asyncio.sleep(3)

                    # Count events after clicking
                    events_after = await page.locator(event_list_selector).count()
                    new_events = events_after - events_before

                    self.logger.info(f"   Found {events_after} events total (+{new_events} new)")

                    # If no new events loaded, stop clicking
                    if new_events == 0:
                        self.logger.info("✓ No new events loaded, stopping")
                        break

                except Exception as e:
                    self.logger.info(f"✓ Button not found or error after {clicks} clicks: {e}")
                    break

            if clicks > 0:
                self.logger.info(f"✅ Clicked 'Daha Fazla Yükle' button {clicks} times")

            # Extract page content
            content = await page.content()

            # Save to file for debugging
            with open("biletinial_page_content.html", "w", encoding="utf-8") as f:
                f.write(content)

            self.logger.info(f"Page content: {len(content)} chars")

            # Replace response body
            response = response.replace(body=content.encode("utf-8"))

            # Find all event items in the list (use the detected selector)
            events = response.css(event_list_selector)
            total_on_page = len(events)

            self.logger.info(f"📊 Found {total_on_page} event elements on page")

            events_yielded = 0
            events_skipped = 0

            # Parse each event
            for idx, event in enumerate(events, 1):
                try:
                    # Extract data
                    title = self.extract_title(event)
                    venue = self.extract_venue(event)
                    city = self.extract_city(event)
                    date_string = self.extract_date(event)
                    url = self.extract_url(event, response)
                    image_url = self.extract_image(event)
                    event_type = self.extract_type(event)

                    if title:  # Only yield if we have at least a title
                        # Parse date range into individual dates
                        individual_dates = parse_turkish_date_range(date_string)

                        # Yield separate event for each date
                        for individual_date in individual_dates:
                            event_item = EventItem(
                                title=self.clean_text(title),
                                venue=self.clean_text(venue) if venue else None,
                                city=self.clean_text(city) if city else "İstanbul",  # Default to Istanbul
                                date=individual_date,
                                price=None,  # Price not visible on listing page
                                url=url,
                                image_url=image_url,
                                category=event_type if event_type else "Etkinlik",
                                source="biletinial",
                            )

                            self.log_event(event_item)
                            events_yielded += 1
                            yield event_item
                    else:
                        events_skipped += 1

                except Exception as e:
                    self.logger.warning(f"Error parsing event {idx}: {e}")
                    events_skipped += 1
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
                self.logger.info(
                    f"✅ All {total_on_page} events processed ({events_skipped} skipped due to missing data)"
                )
            else:
                self.logger.info(f"✅ All {total_on_page} events successfully processed!")

        finally:
            await page.close()

    def extract_title(self, element):
        """Extract event title from element."""
        # Try city-specific layout: h2 > a
        title = element.css("h2 a::text").get()
        if title and title.strip():
            return title.strip()

        # Try kategori__etkinlikler layout: h3 > a
        title = element.css("h3 a::text").get()
        if title and title.strip():
            return title.strip()

        # Try concert/category layout: figcaption > span
        title = element.css("figcaption > span::text").get()
        if title and title.strip():
            return title.strip()

        return None

    def extract_venue(self, element):
        """Extract venue from element."""
        # Try city-specific layout
        venue = element.css("div.sehir-detay__liste__alt__adres::text").getall()
        if venue:
            venue_text = " ".join([v.strip() for v in venue if v.strip()])
            return venue_text

        # Try kategori__etkinlikler layout: address
        venue = element.css("address::text").get()
        if venue and venue.strip():
            return venue.strip()

        # Try concert/category layout: p.loca
        venue = element.css("p.loca::text").get()
        if venue and venue.strip():
            return venue.strip()

        return None

    def extract_city(self, element):
        """Extract city name from element."""
        # For now, we know it's Istanbul from the URL
        # Could be extracted from venue/address if needed
        return "İstanbul"

    def extract_date(self, element):
        """Extract event date from element."""
        # Date is in mobile date display with different HTML tags:
        # <span>03</span> <b>Aralık</b> <p>19:30</p>

        # Try city-specific layout first
        day = element.css("div.sehir-detay__liste-mobiltarih span::text").get()
        month = element.css("div.sehir-detay__liste-mobiltarih b::text").get()
        time = element.css("div.sehir-detay__liste-mobiltarih p::text").get()

        if day or month or time:
            # Combine available parts
            parts = [p.strip() for p in [day, month, time] if p and p.strip()]
            return " ".join(parts) if parts else None

        # Try kategori__etkinlikler layout: span after address
        # Date format: "Aralık - 03 - 07" with <br> separating multiple dates
        date_span = element.css("address ~ span::text").getall()
        if date_span:
            # Join all date parts and clean up whitespace
            date_text = " ".join([d.strip() for d in date_span if d.strip()])
            return date_text if date_text else None

        # Try concert/category layout (if different structure exists)
        date_text = element.css("figcaption time::text").get()
        if date_text and date_text.strip():
            return date_text.strip()

        return None

    def extract_url(self, element, response):
        """Extract event URL from element."""
        # Try city-specific layout: h2 > a href
        url = element.css("h2 a::attr(href)").get()
        if url:
            return response.urljoin(url)

        # Try kategori__etkinlikler layout: h3 > a href
        url = element.css("h3 a::attr(href)").get()
        if url:
            return response.urljoin(url)

        # Try concert/category layout: a::attr(href) (element itself is the link)
        url = element.css("::attr(href)").get()
        if url:
            return response.urljoin(url)

        return None

    def extract_image(self, element):
        """Extract event image URL from element."""
        # Image can be in data-src (lazy load) or src
        img_url = element.css("img::attr(data-src)").get() or element.css("img::attr(src)").get()
        if img_url and not img_url.startswith("data:"):
            if img_url.startswith("//"):
                return "https:" + img_url
            elif img_url.startswith("/"):
                return "https://biletinial.com" + img_url
            return img_url
        return None

    def extract_type(self, element):
        """Extract event type/category from element."""
        # Try city-specific layout: badge
        event_type = element.css("span.sehir-detay__liste__ust__tip::text").get()
        if event_type and event_type.strip():
            return event_type.strip()

        # Try concert/category layout: figcaption > small (first one)
        event_type = element.css("figcaption > small::text").get()
        if event_type and event_type.strip():
            return event_type.strip()

        return None

    def clean_text(self, text):
        """Clean and normalize text."""
        if not text:
            return None
        return " ".join(text.split()).strip()

    async def errback_close_page(self, failure):
        """Handle errors by closing the page."""
        page = failure.request.meta.get("playwright_page")
        if page:
            await page.close()
        self.logger.error(f"Request failed: {failure.value}")
