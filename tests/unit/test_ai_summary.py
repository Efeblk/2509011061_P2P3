
import pytest
from datetime import datetime
from src.models.ai_summary import AISummaryNode

class TestAISummaryDatabase:
    def test_embedding_optional(self):
        """Test optional embedding initialization"""
        summary = AISummaryNode(
            uuid="uuid-1",
            event_uuid="event-1",
            sentiment_summary="Summary"
        )
        assert summary.embedding_v4 is None

    def test_embedding_parsing(self):
        """Test embedding parsing"""
        summary = AISummaryNode(
            uuid="uuid-1",
            event_uuid="event-1",
            sentiment_summary="Summary",
            embedding_v4=[0.1, 0.2]
        )
        assert summary.embedding_v4 == [0.1, 0.2]
