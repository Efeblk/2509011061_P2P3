"""
Scrapy settings for EventGraph project.
"""
import os
from dotenv import load_dotenv

load_dotenv()

BOT_NAME = "eventgraph"

SPIDER_MODULES = ["src.scrapers.spiders"]
NEWSPIDER_MODULE = "src.scrapers.spiders"

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests (can be overridden via .env)
CONCURRENT_REQUESTS = int(os.getenv("SCRAPY_CONCURRENT_REQUESTS", "256"))

# Configure a delay for requests for the same website (can be overridden via .env)
DOWNLOAD_DELAY = float(os.getenv("SCRAPY_DOWNLOAD_DELAY", "0"))

# Disable cookies (enabled by default)
COOKIES_ENABLED = True

# Disable Telemetry stats
TELNETCONSOLE_ENABLED = False

# Override the default request headers
DEFAULT_REQUEST_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
}

# Enable or disable spider middlewares
SPIDER_MIDDLEWARES = {
    "src.scrapers.middlewares.EventGraphSpiderMiddleware": 543,
}

# Enable or disable downloader middlewares
DOWNLOADER_MIDDLEWARES = {
    "src.scrapers.middlewares.EventGraphDownloaderMiddleware": 543,
}

# Configure item pipelines
ITEM_PIPELINES = {
    "src.scrapers.pipelines.ValidationPipeline": 100,
    "src.scrapers.pipelines.DuplicatesPipeline": 200,
    "src.scrapers.pipelines.FalkorDBPipeline": 300,
}

# Enable and configure Playwright
DOWNLOAD_HANDLERS = {
    "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
    "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
}

PLAYWRIGHT_BROWSER_TYPE = "chromium"
PLAYWRIGHT_LAUNCH_OPTIONS = {
    "headless": os.getenv("PLAYWRIGHT_HEADLESS", "true").lower() == "true",
    "timeout": int(os.getenv("PLAYWRIGHT_TIMEOUT", "60000")),
    "args": ["--disable-gpu", "--no-sandbox", "--disable-dev-shm-usage"],  # Optimizations
}

# Increase thread pool for high concurrency (matches CONCURRENT_REQUESTS)
REACTOR_THREADPOOL_MAXSIZE = int(os.getenv("SCRAPY_CONCURRENT_REQUESTS", "256"))

# Set settings whose default value is deprecated to a future-proof value
REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"

# Logging (can be overridden via .env)
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
