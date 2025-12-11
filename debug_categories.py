import asyncio
from playwright.async_api import async_playwright
import json

async def debug_categories():
    # La Boheme URL
    url = "https://biletinial.com/tr-tr/opera-bale/la-boheme-idob-akm"
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        print(f"Navigating to {url}...")
        await page.goto(url)
        await page.wait_for_load_state("domcontentloaded")
        
        # Check for ticket_price_tooltip
        print("\n--- Debugging Category Prices ---")
        
        el = await page.query_selector('.ticket_price_tooltip')
        if el:
            data_attr = await el.get_attribute("data-ticketprices")
            print(f"Found .ticket_price_tooltip")
            print(f"data-ticketprices length: {len(data_attr) if data_attr else 0}")
            if data_attr:
                try:
                    data = json.loads(data_attr)
                    print("JSON parsed successfully.")
                    if "prices" in data:
                        print("Prices list found:")
                        print(json.dumps(data["prices"], indent=2, ensure_ascii=False))
                    else:
                        print("No 'prices' key in JSON.")
                        print(json.dumps(data, indent=2, ensure_ascii=False))
                except Exception as e:
                    print(f"JSON parse error: {e}")
                    print(f"Raw data: {data_attr[:100]}...")
        else:
            print("❌ .ticket_price_tooltip NOT FOUND")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(debug_categories())
