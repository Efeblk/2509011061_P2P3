"""
Quick script to diagnose Biletix page structure.
Run this to see what selectors we need.
"""

import asyncio
from playwright.async_api import async_playwright

async def diagnose():
    url = "https://www.biletix.com/search/TURKIYE/tr?category_sb=-1&date_sb=next14days&city_sb=İstanbul"

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        print(f"🔍 Loading: {url}")
        await page.goto(url, wait_until="domcontentloaded", timeout=60000)

        # Wait a bit for JavaScript to load
        await asyncio.sleep(5)

        print("\n📊 Page Analysis:")
        print("="*60)

        # Get page title
        title = await page.title()
        print(f"Title: {title}")

        # Check for common event container classes
        selectors_to_try = [
            ".event-card",
            ".event-item",
            "[class*='event']",
            "[class*='card']",
            "article",
            ".search-result",
            "[class*='result']",
            "[class*='list-item']",
        ]

        print("\n🔍 Trying common selectors:")
        for selector in selectors_to_try:
            try:
                elements = await page.query_selector_all(selector)
                if elements:
                    print(f"  ✓ Found {len(elements)} elements with: {selector}")

                    # Get first element's outer HTML
                    if elements:
                        html = await elements[0].evaluate("el => el.outerHTML")
                        print(f"    Sample HTML (first 200 chars):")
                        print(f"    {html[:200]}...")
            except:
                pass

        # Get all class names on the page
        print("\n📋 Top 20 most common class names:")
        classes = await page.evaluate("""
            () => {
                const allElements = document.querySelectorAll('*');
                const classCount = {};
                allElements.forEach(el => {
                    if (el.className && typeof el.className === 'string') {
                        el.className.split(' ').forEach(cls => {
                            if (cls) classCount[cls] = (classCount[cls] || 0) + 1;
                        });
                    }
                });
                return Object.entries(classCount)
                    .sort((a, b) => b[1] - a[1])
                    .slice(0, 20)
                    .map(([name, count]) => `${name} (${count})`);
            }
        """)

        for cls in classes:
            print(f"  - {cls}")

        # Save screenshot
        await page.screenshot(path="biletix_page.png")
        print("\n📸 Screenshot saved: biletix_page.png")

        await browser.close()

        print("\n" + "="*60)
        print("✅ Diagnosis complete!")
        print("\nNext steps:")
        print("1. Check biletix_page.png to see the page")
        print("2. Update biletix_spider.py with correct selectors")

if __name__ == "__main__":
    asyncio.run(diagnose())
