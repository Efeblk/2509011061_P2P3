"""
Scrapy middlewares for EventGraph.
"""

from scrapy import signals


class EventGraphSpiderMiddleware:
    """Spider middleware for EventGraph."""

    @classmethod
    def from_crawler(cls, crawler):
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        return None

    async def process_spider_output(self, response, result, spider):
        async for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        pass

    def spider_opened(self, spider):
        spider.logger.info(f"Spider opened: {spider.name}")


class EventGraphDownloaderMiddleware:
    """Downloader middleware for EventGraph."""

    @classmethod
    def from_crawler(cls, crawler):
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        return None

    def process_response(self, request, response, spider):
        return response

    def process_exception(self, request, exception, spider):
        pass

    def spider_opened(self, spider):
        spider.logger.info(f"Spider opened: {spider.name}")
