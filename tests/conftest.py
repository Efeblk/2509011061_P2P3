"""
Pytest configuration and fixtures for EventGraph tests.
"""

import pytest
import os
from pathlib import Path
from unittest.mock import MagicMock, patch


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Set up test environment variables."""
    os.environ["ENVIRONMENT"] = "testing"
    os.environ["LOG_LEVEL"] = "DEBUG"
    os.environ["FALKORDB_HOST"] = "localhost"
    os.environ["FALKORDB_PORT"] = "6379"
    os.environ["FALKORDB_GRAPH_NAME"] = "test_eventgraph"
    os.environ["GEMINI_API_KEY"] = "test_api_key"


@pytest.fixture(scope="session")
def test_data_dir():
    """Return path to test data directory."""
    return Path(__file__).parent / "test_data"


@pytest.fixture
def mock_db_connection():
    """Mock FalkorDB connection for unit tests."""
    with patch("src.database.connection.FalkorDBConnection") as mock:
        mock_instance = MagicMock()
        mock.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def mock_redis_client():
    """Mock Redis client."""
    with patch("redis.Redis") as mock:
        mock_client = MagicMock()
        mock.return_value = mock_client
        mock_client.ping.return_value = True
        yield mock_client


@pytest.fixture
def mock_falkordb_client():
    """Mock FalkorDB client."""
    with patch("falkordb.FalkorDB") as mock:
        mock_client = MagicMock()
        mock.return_value = mock_client
        yield mock_client


@pytest.fixture
def mock_gemini_api():
    """Mock Google Gemini API."""
    with patch("google.generativeai.GenerativeModel") as mock:
        mock_model = MagicMock()
        mock.return_value = mock_model
        yield mock_model


@pytest.fixture
def sample_event_data():
    """Sample event data for testing."""
    return {
        "title": "Kel Diva - Haluk Bilginer",
        "date": "2025-12-15",
        "price": 1200.0,
        "venue": "Zorlu PSM",
        "description": "Absürd tiyatronun kült eseri",
        "url": "https://example.com/event/123"
    }


@pytest.fixture
def sample_venue_data():
    """Sample venue data for testing."""
    return {
        "name": "Zorlu PSM",
        "city": "Istanbul",
        "address": "Levazım Mahallesi, Koru Sokağı No:2",
        "capacity": 2000
    }


@pytest.fixture
def sample_artist_data():
    """Sample artist data for testing."""
    return {
        "name": "Haluk Bilginer",
        "genre": "Tiyatro",
        "reputation_score": 95
    }


@pytest.fixture
def sample_ai_analysis():
    """Sample AI analysis result."""
    return {
        "score": 92,
        "verdict": "MUST_GO",
        "reasoning": "Haluk Bilginer ve Zuhal Olcay gibi usta oyuncuları bir araya getiren absürd tiyatronun kült eseri.",
        "tags": ["Tiyatro", "Absürd", "Yıldız Kadro", "Kült Eser"]
    }


@pytest.fixture(scope="function")
def clean_test_graph(mock_db_connection):
    """Clean test graph before and after each test."""
    # Setup: clear graph
    yield mock_db_connection
    # Teardown: clear graph
    mock_db_connection.clear_graph()


@pytest.fixture
def mock_scrapy_response():
    """Mock Scrapy response object."""
    class MockResponse:
        def __init__(self, url="https://example.com", body="<html></html>"):
            self.url = url
            self.body = body
            self.text = body
            self.status = 200

        def css(self, selector):
            return MagicMock()

        def xpath(self, selector):
            return MagicMock()

    return MockResponse()
