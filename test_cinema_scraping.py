#!/usr/bin/env python3
"""
Quick test script to verify cinema event date extraction.
Tests the parse_cinema_detail functionality.
"""

import asyncio
from playwright.async_api import async_playwright


async def test_cinema_date_extraction():
    """Test extracting release date from a cinema event page."""

    test_urls = [
        "https://biletinial.com/tr-tr/sinema/zootropolis-2",
        "https://biletinial.com/tr-tr/sinema/nasipse-olur-2",
    ]

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        for url in test_urls:
            print(f"\nTesting: {url}")
            print("=" * 80)

            page = await browser.new_page()
            await page.goto(url)
            await page.wait_for_load_state("domcontentloaded")
            await asyncio.sleep(2)

            # Try to find release date
            release_date = None

            # Method 1: Look for "Vizyon Tarihi" text
            date_element = await page.query_selector("text=Vizyon Tarihi")
            if date_element:
                parent = await date_element.evaluate("el => el.parentElement")
                if parent:
                    full_text = await page.evaluate("el => el.textContent", parent)
                    if "Vizyon Tarihi" in full_text:
                        release_date = full_text.replace("Vizyon Tarihi", "").strip()

            # Method 2: Regex search in page content
            if not release_date:
                all_text = await page.content()
                import re
                turkish_months = ["Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran",
                                  "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"]

                for month in turkish_months:
                    if "Vizyon Tarihi" in all_text and month in all_text:
                        pattern = r'Vizyon Tarihi\s*([0-9]{1,2}\s+' + month + r'\s+[0-9]{4})'
                        match = re.search(pattern, all_text)
                        if match:
                            release_date = match.group(1).strip()
                            break

            if release_date:
                print(f"✓ Found release date: {release_date}")
            else:
                print("✗ Could not find release date")

            await page.close()

        await browser.close()

    print("\n" + "=" * 80)
    print("Test complete!")


if __name__ == "__main__":
    asyncio.run(test_cinema_date_extraction())
