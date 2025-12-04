#!/usr/bin/env python3
"""
Verification script to check scraping quality and test cinema date extraction.
"""

from falkordb import FalkorDB
from collections import Counter
import random
import asyncio
import sys


def verify_scraping():
    """Verify the quality of scraped data."""

    db = FalkorDB(host="localhost", port=6379)
    g = db.select_graph("eventgraph")

    print("=" * 80)
    print("EVENTGRAPH SCRAPING VERIFICATION REPORT")
    print("=" * 80)
    print()

    # 1. Overall Statistics
    print("📊 OVERALL STATISTICS")
    print("-" * 80)

    total_query = g.query("MATCH (e:Event) RETURN count(e)")
    total = total_query.result_set[0][0]
    print(f"Total Events: {total}")

    by_source = g.query("MATCH (e:Event) RETURN e.source, count(e) ORDER BY count(e) DESC")
    print("\nEvents by Source:")
    for row in by_source.result_set:
        print(f"  {row[0]}: {row[1]} events")

    print()

    # 2. Data Completeness Check
    print("✅ DATA COMPLETENESS CHECK")
    print("-" * 80)

    # Check for missing required fields
    missing_title = g.query('MATCH (e:Event) WHERE e.title = "" OR e.title IS NULL RETURN count(e)')
    missing_date = g.query('MATCH (e:Event) WHERE e.date = "" OR e.date IS NULL RETURN count(e)')
    missing_url = g.query('MATCH (e:Event) WHERE e.url = "" OR e.url IS NULL RETURN count(e)')

    print(f"Missing Title: {missing_title.result_set[0][0]} events")
    print(f"Missing Date: {missing_date.result_set[0][0]} events")
    print(f"Missing URL: {missing_url.result_set[0][0]} events")

    # Check for optional fields
    missing_venue = g.query('MATCH (e:Event) WHERE e.venue = "" OR e.venue IS NULL RETURN count(e)')
    missing_image = g.query('MATCH (e:Event) WHERE e.image_url = "" OR e.image_url IS NULL RETURN count(e)')

    print("\nOptional Fields:")
    venue_pct = missing_venue.result_set[0][0] / total * 100
    image_pct = missing_image.result_set[0][0] / total * 100
    print(f"  Missing Venue: {missing_venue.result_set[0][0]} events ({venue_pct:.1f}%)")
    print(f"  Missing Image: {missing_image.result_set[0][0]} events ({image_pct:.1f}%)")

    print()

    # 3. Data Quality Checks
    print("🔍 DATA QUALITY CHECKS")
    print("-" * 80)

    # Check for suspicious short titles (fetch all and check in Python)
    all_events = g.query("MATCH (e:Event) RETURN e.title")
    short_titles = [row[0] for row in all_events.result_set if row[0] and len(row[0]) < 3]

    if short_titles:
        print(f"⚠️  Suspiciously short titles (< 3 chars): {len(short_titles)} events")
        for title in short_titles[:5]:
            print(f"    '{title}'")
    else:
        print("✓ No suspiciously short titles")

    # Check for very long dates (fetch all and check in Python)
    all_dates = g.query("MATCH (e:Event) RETURN e.title, e.date")
    long_dates = [(row[0], row[1]) for row in all_dates.result_set if row[1] and len(row[1]) > 100]

    if long_dates:
        print("\n⚠️  Very long dates (> 100 chars) - might indicate parsing issues:")
        for title, date in long_dates[:5]:
            print(f"    {title}: {date[:80]}...")
    else:
        print("\n✓ No unusually long dates")

    print()

    # 4. Exact Duplicates Check
    print("🔄 DUPLICATE CHECK")
    print("-" * 80)

    # Check for exact duplicates (same title, venue, date)
    duplicates = g.query(
        """
        MATCH (e:Event)
        WITH e.title as title, e.venue as venue, e.date as date, collect(e) as events
        WHERE size(events) > 1
        RETURN title, venue, date, size(events) as count
        ORDER BY count DESC
        LIMIT 10
    """
    )

    if duplicates.result_set:
        print(f"⚠️  Found {len(duplicates.result_set)} sets of potential duplicates:")
        for row in duplicates.result_set:
            print(f"    '{row[0]}' @ {row[1]} on {row[2]}: {row[3]} copies")
    else:
        print("✓ No exact duplicates found")

    print()

    # 5. Sample Events for Manual Inspection
    print("📋 RANDOM SAMPLE EVENTS (Manual Inspection)")
    print("-" * 80)

    # Get random sample from each source
    for source_row in by_source.result_set:
        source = source_row[0]

        print(f"\n{source.upper()} Sample (3 random events):")

        sample = g.query(
            f"""
            MATCH (e:Event)
            WHERE e.source = "{source}"
            RETURN e.title, e.venue, e.date, e.url
            LIMIT 3
        """
        )

        for i, row in enumerate(sample.result_set, 1):
            print(f"\n  {i}. {row[0]}")
            print(f"     Venue: {row[1] or 'N/A'}")
            print(f"     Date: {row[2] or 'N/A'}")
            print(f"     URL: {row[3][:60]}..." if len(row[3]) > 60 else f"     URL: {row[3]}")

    print()

    # 6. Date Format Analysis
    print("📅 DATE FORMAT ANALYSIS")
    print("-" * 80)

    # Sample different date formats
    date_samples = g.query(
        """
        MATCH (e:Event)
        WHERE e.date <> ""
        RETURN DISTINCT e.date
        LIMIT 20
    """
    )

    print("Sample date formats found:")
    for row in date_samples.result_set[:10]:
        print(f"  '{row[0]}'")

    print()

    # 7. URL Validation
    print("🔗 URL VALIDATION")
    print("-" * 80)

    invalid_urls = g.query(
        """
        MATCH (e:Event)
        WHERE e.url <> "" AND NOT e.url STARTS WITH "http"
        RETURN e.title, e.url
        LIMIT 5
    """
    )

    if invalid_urls.result_set:
        print(f"⚠️  Found {len(invalid_urls.result_set)} potentially invalid URLs:")
        for row in invalid_urls.result_set:
            print(f"    {row[0]}: {row[1]}")
    else:
        print("✓ All URLs appear valid (start with http)")

    print()

    # 8. Summary
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)

    issues = []

    if missing_title.result_set[0][0] > 0:
        issues.append(f"{missing_title.result_set[0][0]} events missing titles")

    if missing_date.result_set[0][0] > 0:
        issues.append(f"{missing_date.result_set[0][0]} events missing dates")

    if missing_url.result_set[0][0] > 0:
        issues.append(f"{missing_url.result_set[0][0]} events missing URLs")

    if duplicates.result_set:
        issues.append(f"{len(duplicates.result_set)} sets of duplicates")

    if invalid_urls.result_set:
        issues.append(f"{len(invalid_urls.result_set)} invalid URLs")

    if issues:
        print("\n⚠️  Issues Found:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("\n✅ No major issues found! Data quality looks good.")

    # Calculate completeness: percentage of events with all 3 required fields
    if total > 0:
        # If any field is missing, the event is incomplete
        # Count events that have at least one missing field
        events_with_missing = max(
            missing_title.result_set[0][0], missing_date.result_set[0][0], missing_url.result_set[0][0]
        )
        complete_events = total - events_with_missing
        completeness_score = (complete_events / total) * 100
    else:
        completeness_score = 0.0

    print(f"\nData Completeness Score: {completeness_score:.1f}%")
    print(f"Complete Events: {complete_events}/{total}")
    print(f"Events with missing data: {events_with_missing}")

    print()


async def test_cinema_date_extraction():
    """Test extracting release date from cinema event pages."""
    print()
    print("=" * 80)
    print("CINEMA DATE EXTRACTION TEST")
    print("=" * 80)
    print()

    try:
        from playwright.async_api import async_playwright
    except ImportError:
        print("⚠️  Playwright not available, skipping cinema date extraction test")
        print("   Install with: pip install playwright && playwright install chromium")
        return

    test_urls = [
        "https://biletinial.com/tr-tr/sinema/zootropolis-2",
        "https://biletinial.com/tr-tr/sinema/nasipse-olur-2",
    ]

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        for url in test_urls:
            print(f"Testing: {url}")

            try:
                page = await browser.new_page()
                await page.goto(url, timeout=30000)
                await page.wait_for_load_state("domcontentloaded")
                await asyncio.sleep(2)

                # Try to find release date
                release_date = None

                # Method 1: Look for "Vizyon Tarihi" text
                try:
                    date_element = await page.query_selector("text=Vizyon Tarihi")
                    if date_element:
                        full_text = await date_element.evaluate("el => el.parentElement.textContent")
                        if full_text and "Vizyon Tarihi" in full_text:
                            release_date = full_text.replace("Vizyon Tarihi", "").strip()
                except Exception:
                    pass

                # Method 2: Regex search in page content
                if not release_date:
                    all_text = await page.content()
                    import re

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

                    for month in turkish_months:
                        if "Vizyon Tarihi" in all_text and month in all_text:
                            pattern = r"Vizyon Tarihi\s*([0-9]{1,2}\s+" + month + r"\s+[0-9]{4})"
                            match = re.search(pattern, all_text)
                            if match:
                                release_date = match.group(1).strip()
                                break

                if release_date:
                    print(f"  ✓ Found release date: {release_date}")
                else:
                    print("  ✗ Could not find release date")

                await page.close()

            except Exception as e:
                print(f"  ✗ Error: {e}")

        await browser.close()

    print()
    print("=" * 80)
    print("Cinema date extraction test complete!")
    print("=" * 80)
    print()


if __name__ == "__main__":
    # Check if --test-cinema flag is provided
    if "--test-cinema" in sys.argv:
        asyncio.run(test_cinema_date_extraction())
    else:
        # Run standard verification
        verify_scraping()

        # Optionally run cinema test if requested
        if "--with-cinema-test" in sys.argv:
            asyncio.run(test_cinema_date_extraction())
