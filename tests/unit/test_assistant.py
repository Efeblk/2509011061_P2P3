import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from src.ai.assistant import EventAssistant


@pytest.fixture
def mock_ai_client():
    with patch("src.ai.assistant.get_ai_client") as mock:
        client = AsyncMock()
        # Mock generate and generate_json to be async
        client.generate = AsyncMock()
        client.generate_json = AsyncMock()
        client.embed = MagicMock()  # embed is usually synchronous in my client, check implementation

        mock.return_value = client
        yield client


@pytest.fixture
def mock_db():
    with patch("src.ai.assistant.db_connection") as mock:
        yield mock


@pytest.mark.asyncio
async def test_identify_intent_keyword(mock_ai_client):
    assistant = EventAssistant()

    # Test keyword matching
    assert await assistant.identify_intent("cheap events") == "best-value"
    assert await assistant.identify_intent("romantic dinner") == "date-night"
    assert await assistant.identify_intent("this weekend") == "this-weekend"


@pytest.mark.asyncio
async def test_identify_intent_ai_fallback(mock_ai_client):
    assistant = EventAssistant()

    # Mock AI response
    assistant.client.generate.return_value = "hidden-gems"

    intent = await assistant.identify_intent("what should I do?")
    assert intent == "hidden-gems"

    # Verify AI was called
    assistant.client.generate.assert_called_once()


@pytest.mark.asyncio
async def test_extract_filters_valid(mock_ai_client):
    assistant = EventAssistant()

    # Mock AI response
    assistant.reasoning_client.generate_json.return_value = {"max_price": 500, "city": "Istanbul", "date_range": None}

    filters = await assistant.extract_filters("events in Istanbul under 500 tl")

    assert filters["max_price"] == 500
    assert filters["city"] == "Istanbul"


@pytest.mark.asyncio
async def test_extract_filters_date_safeguard(mock_ai_client):
    assistant = EventAssistant()

    # Mock AI returning a date even though query has none
    assistant.reasoning_client.generate_json.return_value = {"date_range": {"start": "2025-01-01", "end": "2025-01-02"}}

    # Query without date keywords
    filters = await assistant.extract_filters("events in Istanbul")

    # Should discard date_range
    assert filters["date_range"] is None


@pytest.mark.asyncio
async def test_search_hybrid(mock_ai_client, mock_db):
    assistant = EventAssistant()

    # 1. Mock Filter Extraction
    # We mock the method on the instance
    assistant.extract_filters = AsyncMock(return_value={"max_price": 500, "city": "Istanbul"})

    # 2. Mock Cypher Result (Candidates)
    mock_db.execute_query.return_value.result_set = [["uuid-1"], ["uuid-2"]]

    # 3. Mock Embeddings
    assistant.client.embed.return_value = [0.1, 0.2, 0.3]

    # 4. Mock Summaries
    with patch("src.models.ai_summary.AISummaryNode.get_all_summaries", new_callable=AsyncMock) as mock_get_summaries:
        mock_summary1 = MagicMock()
        mock_summary1.event_uuid = "uuid-1"
        mock_summary1.embedding = "[0.1, 0.2, 0.3]"  # Perfect match

        mock_summary2 = MagicMock()
        mock_summary2.event_uuid = "uuid-3"  # Not in candidates
        mock_summary2.embedding = "[0.1, 0.2, 0.3]"

        mock_get_summaries.return_value = [mock_summary1, mock_summary2]

        results = await assistant.search("query")

        # Should only return uuid-1 because uuid-3 was filtered out by Cypher
        assert len(results) == 1
        assert results[0][1].event_uuid == "uuid-1"


@pytest.mark.asyncio
async def test_generate_answer(mock_ai_client, mock_db):
    assistant = EventAssistant()

    # Mock AI response
    assistant.reasoning_client.generate.return_value = "Here is a plan."

    # Mock Event Details
    assistant._fetch_event_details = AsyncMock(
        return_value={"title": "Event 1", "venue": "Venue 1", "date": "2025-01-01", "price": 100}
    )

    mock_summary = MagicMock()
    mock_summary.sentiment_summary = "Good event"
    mock_summary.event_uuid = "uuid-1"

    top_results = [(0.9, mock_summary)]

    answer = await assistant.generate_answer("plan a date", top_results)

    assert answer == "Here is a plan."
    assistant.reasoning_client.generate.assert_called_once()
