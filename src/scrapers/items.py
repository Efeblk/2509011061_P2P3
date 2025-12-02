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
    url = scrapy.Field()
    image_url = scrapy.Field()
    category = scrapy.Field()
    source = scrapy.Field()
