import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from src.ai.assistant import EventAssistant
from src.ai.schemas import EventIntent


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
async def test_identify_intent_ai_fallback(mock_ai_client):
    assistant = EventAssistant()

    # Mock AI response (generate_json, not generate)
    assistant.client.generate_json.return_value = {"intent": "hidden-gems"}

    intent = await assistant.identify_intent("what should I do?")
    assert intent == "hidden-gems"

    # Verify AI was called
    assistant.client.generate_json.assert_called_once()


@pytest.mark.asyncio
async def test_extract_filters_valid(mock_ai_client):
    assistant = EventAssistant()

    # Mock AI response
    assistant.reasoning_client.generate_json.return_value = {"max_price": 500, "city": "Istanbul", "date_range": None}

    filters = await assistant.extract_filters("events in Istanbul under 500 tl")

    assert filters["max_price"] == 500
    assert filters["city"] == "Istanbul"


@pytest.mark.asyncio
async def test_search_hybrid(mock_ai_client, mock_db):
    assistant = EventAssistant()

    # 1. Mock Filter Extraction
    assistant.extract_filters = AsyncMock(return_value={"max_price": 500, "city": "Istanbul"})

    # 2. Mock DB Query Results
    # We expect 2 calls:
    # 1st call: Cypher Filter -> returns [uuid-1, uuid-2]
    # 2nd call: Vector Search -> returns [(node, score), (node, score)]
    
    mock_cypher_result = MagicMock()
    mock_cypher_result.result_set = [["uuid-1"], ["uuid-2"]]
    
    # Vector Search Result
    # Each row is [node_data, score]
    mock_node1 = MagicMock()
    mock_node1.properties = {"embedding_v4": [], "uuid": "summary-uuid-1", "event_uuid": "uuid-1"}
    
    mock_node2 = MagicMock() # uuid-3 (not in candidates)
    mock_node2.properties = {"embedding_v4": [], "uuid": "summary-uuid-3", "event_uuid": "uuid-3"}
    
    mock_vec_result = MagicMock()
    mock_vec_result.result_set = [[mock_node1, 0.9], [mock_node2, 0.8]]
    
    mock_db.execute_query.side_effect = [mock_cypher_result, mock_vec_result]

    # 3. Mock Embeddings
    assistant.client.embed.return_value = [0.1, 0.2, 0.3]

    # 4. Mock AISummaryNode construction (since logic does AISummaryNode(**props))
    # We verify logic via search results filtering
    
    # 5. Mock fetch_event_details AND rerank to avoid errors later in the pipeline
    assistant._fetch_event_details = AsyncMock(return_value={"title": "Test", "venue": "V", "date": "2025"})
    assistant._rerank_results = AsyncMock(return_value=[(0.9, MagicMock(), {"title": "Test"})])

    # We only care about step 4 (Filtering)
    # But search() now runs the whole pipeline including re-ranking.
    # To test filtering, we can check arguments to _rerank_results?
    # Or just check final result.
    
    # Let's simplify: search() calls extract_filters -> cypher -> vector -> filter -> fetch -> rerank.
    # The filtering of uuid-3 happens BEFORE fetch/rerank.
    # So _fetch_event_details should be called ONLY for uuid-1.
    
    results = await assistant.search("query")
    
    # Verify we filtered out uuid-3 (Logic: if candidate_uuids is set, filter)
    # _fetch_event_details should be called once for uuid-1
    assistant._fetch_event_details.assert_called_once_with("uuid-1")


@pytest.mark.asyncio
async def test_generate_answer(mock_ai_client, mock_db):
    assistant = EventAssistant()

    # Mock AI response
    assistant.reasoning_client.generate.return_value = "Here is a plan."

    mock_summary = MagicMock()
    mock_summary.sentiment_summary = "Good event"
    mock_summary.event_uuid = "uuid-1"
    
    mock_details = {"title": "Event 1", "venue": "Venue 1", "date": "2025-01-01", "price": 100}

    # Tuple size 3: (score, summary, details)
    top_results = [(0.9, mock_summary, mock_details)]

    answer = await assistant.generate_answer("plan a date", top_results)

    assert answer == "Here is a plan."
    assistant.reasoning_client.generate.assert_called_once()
