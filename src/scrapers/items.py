"""
Scrapy items for EventGraph.
"""

import scrapy


class EventItem(scrapy.Item):
    """Item for storing scraped event data."""

    title = scrapy.Field()
    description = scrapy.Field()
    date = scrapy.Field()
    venue = scrapy.Field()
    city = scrapy.Field()
    price = scrapy.Field()
    price_range = scrapy.Field()
    category_prices = scrapy.Field()  # List of dicts: [{'name': '1. Kategori', 'price': 1200.0}, ...]
    url = scrapy.Field()
    image_url = scrapy.Field()
    category = scrapy.Field()
    source = scrapy.Field()
    genre = scrapy.Field()
    duration = scrapy.Field()

    # EventContent fields
    rating = scrapy.Field()
    rating_count = scrapy.Field()
    reviews = scrapy.Field()  # List of review dicts from detail page
    uuid = scrapy.Field()  # For updating existing events
    is_update_job = scrapy.Field()  # Flag for partial updates
    extracted_entities = scrapy.Field()  # List of dicts: [{'name': '...', 'role': '...'}]
