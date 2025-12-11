import asyncio
from playwright.async_api import async_playwright

async def debug_price():
    url = "https://biletinial.com/tr-tr/opera-bale/la-boheme-idob-akm"
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        print(f"Navigating to {url}...")
        await page.goto(url)
        await page.wait_for_load_state("domcontentloaded")
        
        # Check for price elements
        print("\n--- Debugging Price Elements ---")
        
        # Selector 1: .price-info[itemprop="price"]
        el = await page.query_selector('.price-info[itemprop="price"]')
        if el:
            text = await el.inner_text()
            content = await el.get_attribute("content")
            print(f"Found .price-info[itemprop='price']:")
            print(f"  Inner Text: '{text}'")
            print(f"  Content Attr: '{content}'")
        else:
            print("❌ .price-info[itemprop='price'] NOT FOUND")

        # Selector 2: .bilet-fiyati
        el = await page.query_selector('.bilet-fiyati')
        if el:
            text = await el.inner_text()
            print(f"Found .bilet-fiyati: '{text}'")
        else:
            print("❌ .bilet-fiyati NOT FOUND")

        # Selector 3: .ed-biletler__sehir__gun__fiyat
        el = await page.query_selector('.ed-biletler__sehir__gun__fiyat')
        if el:
            text = await el.inner_text()
            print(f"Found .ed-biletler__sehir__gun__fiyat: '{text}'")
        else:
            print("❌ .ed-biletler__sehir__gun__fiyat NOT FOUND")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(debug_price())
