"""
Pytest configuration and shared fixtures.
"""

import pytest
from datetime import datetime
from unittest.mock import Mock


@pytest.fixture
def sample_event_data():
    """Sample event data for testing."""
    return {
        "title": "Test Concert",
        "description": "A great test concert",
        "date": "2025-12-15 20:00",
        "venue": "Test Arena",
        "city": "Istanbul",
        "price": 150.0,
        "price_range": "100-200 TL",
        "url": "https://example.com/event",
        "image_url": "https://example.com/image.jpg",
        "category": "Concert",
        "source": "biletix",
    }


@pytest.fixture
def mock_spider():
    """Mock Scrapy spider for testing."""
    spider = Mock()
    spider.name = "test_spider"
    spider.logger = Mock()
    return spider


@pytest.fixture
def mock_response():
    """Mock Scrapy response for testing."""
    response = Mock()
    response.url = "https://example.com/events"
    response.urljoin = lambda url: f"https://example.com{url}" if url.startswith("/") else url
    return response


@pytest.fixture
def biletix_event_html():
    """Sample Biletix event HTML."""
    return """
    <div class="searchResultEvent">
        <a href="/etkinlik/12345/TURKIYE/tr">
            <img src="https://example.com/image.jpg" alt="Test Event">
        </a>
        <div class="event-title">Test Concert</div>
        <div class="event-location">Test Arena</div>
        <div class="event-city">Istanbul</div>
        <div class="event-date">Cum, 15/12/25</div>
    </div>
    """


@pytest.fixture
def biletinial_event_html():
    """Sample Biletinial event HTML."""
    return """
    <li>
        <figure>
            <a href="/tr-tr/muzik/test-concert">
                <img src="https://example.com/image.jpg">
            </a>
        </figure>
        <h3><a href="/tr-tr/muzik/test-concert">Test Concert</a></h3>
        <address>Test Arena</address>
        <span>Aralık - 15</span>
    </li>
    """
