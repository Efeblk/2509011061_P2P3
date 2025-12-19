
import pytest
from unittest.mock import Mock, AsyncMock, patch
from src.scrapers.spiders.biletinial_spider import BiletinialSpider

@pytest.mark.asyncio
async def test_parse_event_detail_metadata_extraction():
    """Test extraction of genre, duration, and refined category."""
    spider = BiletinialSpider()
    # spider.logger is a property, cannot be set directly

    
    # Mock Page
    mock_page = Mock()
    mock_page.url = "http://test.com/event"
    mock_page.close = AsyncMock() # Make close awaitable
    
    # Mock Selectors for Genre/Duration
    # We need to configure query_selector to return specific elements based on the selector string
    
    # Mocks for elements
    mock_genre_el = AsyncMock()
    mock_genre_el.inner_text.return_value = "Komedi"
    
    mock_duration_el = AsyncMock()
    mock_duration_el.inner_text.return_value = "120 dakika"
    
    mock_category_el = AsyncMock()
    mock_category_el.inner_text.return_value = "Müzikal Çocuk Oyunu"

    async def side_effect(selector, timeout=None):
        if 'Etkinlik Türü' in selector:
            return mock_genre_el
        if 'Süre' in selector:
            return mock_duration_el
        if('.yds_cinema_movie_thread_info p' in selector): # Adjusted selector matching
            return mock_category_el
        return None

    # Mock wait_for_load_state and wait_for_selector
    mock_page.wait_for_load_state = AsyncMock()
    mock_page.wait_for_selector = AsyncMock()
    mock_page.query_selector_all = AsyncMock(return_value=[])

    # Ensure elements returned by query_selector can also be used as scopes (have query_selector)
    mock_genre_el.query_selector = AsyncMock(return_value=None)
    mock_duration_el.query_selector = AsyncMock(return_value=None)
    mock_category_el.query_selector = AsyncMock(return_value=None)
    
    # query_selector needs to be AsyncMock to be awaited
    mock_page.query_selector = AsyncMock(side_effect=side_effect)
    
    # Mock Response meta
    response = Mock()
    response.meta = {
        "playwright_page": mock_page,
        "title": "Test Event",
        "venue": "Test Venue",
        "city": "Test City",
        "date_string": "01.01.2025",
        "price": None,
        "uuid": "test-uuid"
    }
    response.url = "http://test.com/event"
    
    # We need to mock extract_description and extract_entities since they are awaited
    with patch.object(spider, 'extract_description', new_callable=AsyncMock) as mock_desc:
        mock_desc.return_value = "Test Description"
        
        with patch.object(spider, 'extract_entities', new_callable=AsyncMock) as mock_ent:
            mock_ent.return_value = []
            
            # Run the generator
            items = []
            async for item in spider.parse_event_detail(response):
                items.append(item)
                
            # Verification
            assert len(items) >= 1
            event = items[0]
            
            assert event["genre"] == "Komedi"
            assert event["duration"] == "120 dakika"
            assert event["category"] == "Müzikal Çocuk Oyunu"
