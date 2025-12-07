"""
Biletinial spider for scraping events from biletinial.com
"""

import asyncio
import scrapy
from src.scrapers.spiders.base import BaseEventSpider
from src.scrapers.items import EventItem
from src.utils.date_parser import parse_turkish_date_range, extract_date_from_title


class BiletinialSpider(BaseEventSpider):
    """
    Spider for scraping events from Biletinial.
    Extracts ratings directly from listing pages for efficiency.
    Visits detail pages to extract reviews and dates when needed.
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
        "https://biletinial.com/tr-tr/gosteri/istanbul",  # Show/Performance events in Istanbul
        "https://biletinial.com/tr-tr/egitim/istanbul",  # Education/Workshop events in Istanbul
        "https://biletinial.com/tr-tr/seminer/istanbul",  # Seminar/Conference events in Istanbul
        "https://biletinial.com/tr-tr/etkinlik/istanbul",  # General events in Istanbul
        "https://biletinial.com/tr-tr/eglence/istanbul",  # Entertainment events in Istanbul
        "https://biletinial.com/tr-tr/etkinlikleri/stand-up",  # Stand-up comedy events
        "https://biletinial.com/tr-tr/etkinlikleri/senfoni-etkinlikleri",  # Symphony events
    ]

    custom_settings = {
        **BaseEventSpider.custom_settings,
        "PLAYWRIGHT_PROCESS_REQUEST_HEADERS": None,
        "DOWNLOAD_DELAY": 3,
        "CONCURRENT_REQUESTS": 4,
        "RETRY_TIMES": 2,
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
                    "playwright_page_init_callback": self.init_page,
                    "playwright_page_goto_kwargs": {
                        "wait_until": "domcontentloaded",
                        "timeout": 60000,
                    },
                },
                errback=self.errback_close_page,
            )

    async def init_page(self, page, request):
        """Initialize page with resource blocking."""
        await page.route("**/*", self.route_handler)

    async def route_handler(self, route):
        """Block unnecessary resources to speed up scraping."""
        if route.request.resource_type in ["image", "media", "font", "stylesheet"]:
            await route.abort()
        else:
            await route.continue_()

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
                    rating, rating_count = self.extract_rating(event)

                    if title:  # Only yield if we have at least a title
                        # If no date found, try to extract from title
                        if not date_string or not date_string.strip():
                            date_from_title = extract_date_from_title(title)
                            if date_from_title:
                                self.logger.debug(f"Extracted date from title '{title}': {date_from_title}")
                                date_string = date_from_title

                        # Decide whether to visit detail page
                        needs_date = not date_string or not date_string.strip()
                        has_reviews = rating_count and rating_count > 0

                        if (needs_date or has_reviews) and url:
                            reason = []
                            if needs_date:
                                reason.append("missing date")
                            if has_reviews:
                                reason.append(f"has {rating_count} reviews")
                            self.logger.debug(f"Will visit detail page for '{title}': {', '.join(reason)}")

                            # Yield a request to parse the detail page
                            yield scrapy.Request(
                                url=url,
                                callback=self.parse_event_detail,
                                meta={
                                    "playwright": True,
                                    "playwright_include_page": True,
                                    "playwright_page_init_callback": self.init_page,
                                    "playwright_page_goto_kwargs": {
                                        "wait_until": "domcontentloaded",
                                        "timeout": 60000,
                                    },
                                    "title": title,
                                    "venue": venue,
                                    "city": city,
                                    "url": url,
                                    "image_url": image_url,
                                    "event_type": event_type,
                                    "date_string": date_string,  # Pass date if we have it
                                    "rating": rating,
                                    "rating_count": rating_count,
                                },
                                dont_filter=True,
                                errback=self.errback_close_page,
                            )
                            events_yielded += 1
                        else:
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
                                    rating=rating,
                                    rating_count=rating_count,
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

    async def parse_event_detail(self, response):
        """
        Parse event detail page to extract event date.
        This is called for events that don't have dates on the listing page.
        Handles cinema (Vizyon Tarihi), stand-up, concerts, and other event types.
        """
        page = response.meta["playwright_page"]

        try:
            # Wait for page to load
            await page.wait_for_load_state("domcontentloaded")
            await asyncio.sleep(2)  # Wait for dynamic content

            # Extract event date from detail page
            # Try multiple methods as the date might be in different places/formats
            event_date = response.meta.get("date_string")  # Use date from listing if available

            # Get rating from listing page metadata (already extracted)
            rating = response.meta.get("rating")
            rating_count = response.meta.get("rating_count")

            # Only extract date if not already provided from listing
            if not event_date or not event_date.strip():
                # Method 1: Look for "Vizyon Tarihi" text (for cinema events)
                try:
                    date_element = await page.query_selector("text=Vizyon Tarihi")
                    if date_element:
                        full_text = await date_element.evaluate("el => el.parentElement.textContent")
                        # Extract date from "Vizyon Tarihi 28 Kasım 2025 Cuma"
                        if full_text and "Vizyon Tarihi" in full_text:
                            event_date = full_text.replace("Vizyon Tarihi", "").strip()
                except Exception:
                    pass

                # Method 2: Direct CSS selector if there's a specific class
                if not event_date:
                    try:
                        date_text = await page.text_content(".vizyon-tarihi, .release-date, .event-date", timeout=2000)
                        if date_text:
                            event_date = date_text.strip()
                    except Exception:
                        pass

                # Method 3: Search page content for Turkish date patterns
                if not event_date:
                    all_text = await page.content()
                    # Look for Turkish month names in the content
                    turkish_months = [
                        "Ocak",
                        "Şubat",
                        "Mart",
                        "Nisan",
                        "Mayıs",
                        "Haziran",
                        "Temmuz",
                        "Ağustos",
                        "Eylül",
                        "Ekim",
                        "Kasım",
                        "Aralık",
                    ]

                    import re

                    # Try cinema-specific pattern first
                    for month in turkish_months:
                        if "Vizyon Tarihi" in all_text and month in all_text:
                            pattern = r"Vizyon Tarihi\s*([0-9]{1,2}\s+" + month + r"\s+[0-9]{4})"
                            match = re.search(pattern, all_text)
                            if match:
                                event_date = match.group(1).strip()
                                break

                    # If not found, try general date pattern (DD Month YYYY or DD - DD Month YYYY)
                    if not event_date:
                        for month in turkish_months:
                            if month in all_text:
                                # Pattern: "DD Month YYYY" or "DD - DD Month YYYY"
                                pattern = r"(\d{1,2}(?:\s*-\s*\d{1,2})?\s+" + month + r"\s+\d{4})"
                                match = re.search(pattern, all_text)
                                if match:
                                    event_date = match.group(1).strip()
                                    break

                    # If still not found, try without year
                    if not event_date:
                        for month in turkish_months:
                            if month in all_text:
                                # Pattern: "DD Month" without year
                                pattern = r"(\d{1,2}\s+" + month + r")(?!\s+\d{4})"
                                match = re.search(pattern, all_text)
                                if match:
                                    event_date = match.group(1).strip()
                                    # Add year 2024 as default
                                    event_date += " 2024"
                                    break

            # Extract reviews from detail page
            reviews = await self.extract_reviews(page)
            if reviews:
                self.logger.info(f"✓ Found {len(reviews)} reviews for '{response.meta.get('title')}'")
            else:
                # Save page HTML for debugging if no reviews found (only once)
                import os

                debug_file = "biletinial_detail_page.html"
                if not os.path.exists(debug_file):
                    content = await page.content()
                    with open(debug_file, "w", encoding="utf-8") as f:
                        f.write(content)
                    self.logger.info(f"Saved detail page HTML to {debug_file} for review structure analysis")

            # Get metadata from the request
            title = response.meta.get("title")
            venue = response.meta.get("venue")
            city = response.meta.get("city", "İstanbul")
            url = response.meta.get("url")
            image_url = response.meta.get("image_url")
            event_type = response.meta.get("event_type", "Etkinlik")

            # Store reviews to be saved after event is created
            response.meta["reviews"] = reviews

            if event_date:
                self.logger.info(f"✓ Found date for '{title}': {event_date}")

                # Parse date range into individual dates (in case there's a range)
                individual_dates = parse_turkish_date_range(event_date)

                # Yield event for each date
                for individual_date in individual_dates:
                    event_item = EventItem(
                        title=self.clean_text(title),
                        venue=self.clean_text(venue) if venue else None,
                        city=self.clean_text(city) if city else "İstanbul",
                        date=individual_date,
                        price=None,
                        url=url,
                        image_url=image_url,
                        category=event_type,
                        source="biletinial",
                        rating=rating,
                        rating_count=rating_count,
                        reviews=reviews,
                    )

                    self.log_event(event_item)
                    yield event_item
            else:
                self.logger.warning(f"⚠️  Could not find date for event: {title}")
                # Still yield the event but with empty date
                event_item = EventItem(
                    title=self.clean_text(title),
                    venue=self.clean_text(venue) if venue else None,
                    city=self.clean_text(city) if city else "İstanbul",
                    date=None,
                    price=None,
                    url=url,
                    image_url=image_url,
                    category=event_type,
                    source="biletinial",
                )
                yield event_item

        except Exception as e:
            self.logger.error(f"Error parsing event detail page: {e}")
            # Yield event with no date rather than losing it completely
            event_item = EventItem(
                title=self.clean_text(response.meta.get("title")),
                venue=self.clean_text(response.meta.get("venue")) if response.meta.get("venue") else None,
                city=response.meta.get("city", "İstanbul"),
                date=None,
                price=None,
                url=response.meta.get("url"),
                image_url=response.meta.get("image_url"),
                category=response.meta.get("event_type", "Etkinlik"),
                source="biletinial",
            )
            yield event_item

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

    def extract_rating(self, element):
        """Extract rating and review count from listing page element."""
        try:
            # Look for rating container: <div class="etkinlikler_container_puan_list">
            rating_container = element.css("div.etkinlikler_container_puan_list")

            if not rating_container:
                return None, None

            # Extract rating: <strong>"4,7"</strong>
            rating_text = rating_container.css("strong::text").get()
            if rating_text:
                rating_text = rating_text.strip().strip('"')
                # Convert Turkish decimal (comma) to float
                rating = float(rating_text.replace(",", "."))
            else:
                rating = None

            # Extract review count: <span>(1121 Yorum)</span>
            review_text = rating_container.css("span::text").get()
            if review_text:
                # Extract number from "(1121 Yorum)"
                import re

                match = re.search(r"\((\d+)\s*Yorum\)", review_text)
                rating_count = int(match.group(1)) if match else None
            else:
                rating_count = None

            return rating, rating_count

        except Exception as e:
            self.logger.debug(f"Error extracting rating: {e}")
            return None, None

    async def extract_reviews(self, page):
        """
        Extract reviews and AI summary from event detail page.
        Returns list of review dicts with: author, text, rating, content_type
        """
        try:
            reviews = []

            # First, click the "Yorumlar" (Comments) tab to load reviews
            try:
                comments_tab = await page.query_selector('a.goComments[title="Yorumlar"]')
                if comments_tab:
                    await comments_tab.click()
                    await asyncio.sleep(2)  # Wait for reviews to load
                    self.logger.debug("Clicked on Comments tab")
            except Exception as e:
                self.logger.debug(f"Could not click Comments tab: {e}")

            # Click "Daha Fazla Yorum" (Load More Comments) button repeatedly to load all reviews
            max_clicks = 10  # Prevent infinite loop
            clicks = 0
            while clicks < max_clicks:
                try:
                    # Look for "Daha Fazla Yorum" button
                    load_more_button = await page.query_selector("text=Daha Fazla Yorum")
                    if load_more_button:
                        # Check if button is visible and clickable
                        is_visible = await load_more_button.is_visible()
                        if is_visible:
                            try:
                                # Add timeout to prevent hanging on click
                                await load_more_button.click(timeout=5000)
                                await asyncio.sleep(1.5)  # Wait for new reviews to load
                                clicks += 1
                                self.logger.debug(f"Clicked 'Load More' button ({clicks} times)")
                            except Exception as click_err:
                                self.logger.debug(f"Timeout or error clicking load more: {click_err}")
                                break
                        else:
                            break
                    else:
                        break
                except Exception as e:
                    self.logger.debug(f"No more reviews to load: {e}")
                    break

            if clicks > 0:
                self.logger.info(f"Loaded additional reviews by clicking 'Load More' {clicks} times")

            # Get page HTML content after loading all reviews
            content = await page.content()

            import re
            from scrapy.selector import Selector

            sel = Selector(text=content)

            # Extract AI-generated summary first
            # Pattern: <div class="yds_cinema_movie_yorum_person comment_editor comment_AI">
            #          <mark>biletinial AI</mark>
            #          <p>AI summary text...</p>
            ai_summary_container = sel.css(".comment_editor.comment_AI, .yds_cinema_movie_yorum_person.comment_AI")
            if ai_summary_container:
                ai_text = ai_summary_container.css("p::text").get()
                if ai_text and len(ai_text.strip()) > 20:
                    reviews.append({"author": "biletinial AI", "text": ai_text.strip(), "content_type": "ai_summary"})
                    self.logger.debug(f"Extracted AI summary: {ai_text[:80]}...")

            # Extract user reviews from comment containers
            # Pattern: <div class="yds_comment_container" id="comment_container">
            #          <div class="yds_cinema_movie_yorum_person">...</div>
            comment_containers = sel.css(".yds_comment_container .yds_cinema_movie_yorum_person")

            # Filter out AI comments (already extracted)
            user_comment_containers = [c for c in comment_containers if "comment_AI" not in c.get()]

            self.logger.debug(f"Found {len(user_comment_containers)} user comment elements")

            for comment_el in user_comment_containers:
                review_data = {}

                # Extract author name from various possible locations
                # Try: .yds_cinema_movie_yorum_person_attribute_name_rank, strong, mark tags
                author = comment_el.css(
                    ".yds_cinema_movie_yorum_person_attribute_name_rank::text, strong::text, mark::text"
                ).get()
                if author:
                    review_data["author"] = author.strip()

                # Extract review text from specific container
                # The first <p> often contains "SEYİRCİ" (Spectator) label, so we target the comment body
                text = comment_el.css(".yds_cinema_movie_yorum_person_attribute_satir p::text").get()

                if not text:
                    # Fallback: Try all paragraphs but filter out known labels
                    text_parts = comment_el.css("p::text").getall()
                    valid_parts = [t.strip() for t in text_parts if t.strip() and "SEYİRCİ" not in t]
                    text = " ".join(valid_parts).strip() if valid_parts else None

                if text:
                    review_data["text"] = text.strip()
                    review_data["content_type"] = "user_review"

                # Extract rating if available (some reviews may have individual ratings)
                rating_el = comment_el.css(
                    ".rating::text, .stars::text, .puan::text, .yds_cinema_movie_yorum_person_attribute_satir::text"
                ).get()
                if rating_el:
                    rating_match = re.search(r"(\d+[,\.]?\d*)", rating_el)
                    if rating_match:
                        review_data["rating"] = float(rating_match.group(1).replace(",", "."))

                # Only add review if it has actual text (more than 10 chars to avoid noise)
                if review_data.get("text") and len(review_data.get("text", "")) > 10:
                    reviews.append(review_data)
                    self.logger.debug(
                        f"Extracted user review from {review_data.get('author', 'Unknown')}: {review_data.get('text')[:50]}..."
                    )
                else:
                    self.logger.debug(
                        f"Skipping review from {review_data.get('author', 'Unknown')}: Text too short/empty (len={len(review_data.get('text', '')) if review_data.get('text') else 0})"
                    )

            if reviews:
                self.logger.info(f"Total extracted: {len(reviews)} reviews (AI summaries + user reviews)")

            return reviews if reviews else None

        except Exception as e:
            self.logger.warning(f"Error extracting reviews: {e}")
            import traceback

            self.logger.debug(f"Traceback: {traceback.format_exc()}")
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
