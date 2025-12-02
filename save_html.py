"""Save Biletix HTML to file for inspection."""
import asyncio
from playwright.async_api import async_playwright

async def save_html():
    url = "https://www.biletix.com/search/TURKIYE/tr?category_sb=-1&date_sb=next14days&city_sb=İstanbul"

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        print(f"Loading: {url}")
        await page.goto(url, wait_until="domcontentloaded", timeout=60000)

        print("Waiting for content...")
        await asyncio.sleep(5)

        # Save HTML
        html = await page.content()
        with open("biletix_page.html", "w", encoding="utf-8") as f:
            f.write(html)

        print(f"✅ Saved HTML ({len(html)} chars)")

        # Count searchResultEvent divs
        count = html.count('class="grid_21 alpha omega listevent searchResultEvent"')
        print(f"Found {count} occurrences of searchResultEvent")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(save_html())
