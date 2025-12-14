"""Tests for AI summary generation and quality validation."""

import json
import pytest
import os
from falkordb import FalkorDB
from src.models.ai_summary import AISummaryNode


class TestAISummarySchema:
    """Test AI summary data schema and validation."""

    def test_quality_score_range(self):
        """Quality score should be between 0 and 10."""
        summary = AISummaryNode(
            event_uuid="test-uuid",
            quality_score=7.5,
        )
        assert 0 <= summary.quality_score <= 10

    def test_importance_valid_values(self):
        """Importance should be one of predefined values."""
        valid_importance = ["must-see", "iconic", "popular", "niche", "seasonal", "emerging"]

        for importance in valid_importance:
            summary = AISummaryNode(
                event_uuid="test-uuid",
                importance=importance,
            )
            assert summary.importance in valid_importance

    def test_value_rating_valid_values(self):
        """Value rating should be one of predefined values."""
        valid_ratings = ["excellent", "good", "fair", "expensive"]

        for rating in valid_ratings:
            summary = AISummaryNode(
                event_uuid="test-uuid",
                value_rating=rating,
            )
            assert summary.value_rating in valid_ratings

    def test_highlights_json_format(self):
        """Key highlights should be valid JSON array."""
        highlights = ["Great music", "Amazing venue", "Good value"]
        summary = AISummaryNode(
            event_uuid="test-uuid",
            key_highlights=json.dumps(highlights),
        )

        parsed = summary.get_highlights_list()
        assert isinstance(parsed, list)
        assert len(parsed) == 3
        assert parsed[0] == "Great music"

    def test_concerns_json_format(self):
        """Concerns should be valid JSON array or None."""
        concerns = ["Long queues", "Expensive drinks"]
        summary = AISummaryNode(
            event_uuid="test-uuid",
            concerns=json.dumps(concerns),
        )

        parsed = summary.get_concerns_list()
        assert isinstance(parsed, list)
        assert len(parsed) == 2

    def test_concerns_can_be_empty(self):
        """Concerns can be empty array."""
        summary = AISummaryNode(
            event_uuid="test-uuid",
            concerns=json.dumps([]),
        )

        parsed = summary.get_concerns_list()
        assert parsed == []

    def test_best_for_comma_separated(self):
        """Best_for should be comma-separated audiences."""
        summary = AISummaryNode(
            event_uuid="test-uuid",
            best_for="families,music lovers,tourists",
        )

        compact = summary.to_compact_dict()
        assert isinstance(compact["best_for"], list)
        assert "families" in compact["best_for"]
        assert "music lovers" in compact["best_for"]

    def test_boolean_flags(self):
        """Boolean flags should be true/false."""
        summary = AISummaryNode(
            event_uuid="test-uuid",
            educational_value=True,
            tourist_attraction=True,
            bucket_list_worthy=False,
        )

        assert summary.educational_value is True
        assert summary.tourist_attraction is True
        assert summary.bucket_list_worthy is False


class TestAISummaryQuality:
    """Test quality and consistency of AI summaries."""

    def test_compact_dict_structure(self):
        """Compact dict should have all required fields."""
        summary = AISummaryNode(
            event_uuid="test-uuid",
            quality_score=8.5,
            importance="must-see",
            value_rating="excellent",
            sentiment_summary="Highly recommended event",
            key_highlights=json.dumps(["Great", "Amazing", "Perfect"]),
            concerns=json.dumps(["Crowded"]),
            best_for="families,tourists",
            vibe="energetic fun",
            uniqueness="One of a kind experience",
            educational_value=True,
            tourist_attraction=True,
            bucket_list_worthy=True,
        )

        compact = summary.to_compact_dict()

        assert "event_uuid" in compact
        assert "quality_score" in compact
        assert "importance" in compact
        assert "value_rating" in compact
        assert "sentiment" in compact
        assert "highlights" in compact
        assert "concerns" in compact
        assert "best_for" in compact
        assert "vibe" in compact
        assert "uniqueness" in compact
        assert "special_flags" in compact

    def test_highlights_count_reasonable(self):
        """Highlights should have 3-5 items typically."""
        summary = AISummaryNode(
            event_uuid="test-uuid",
            key_highlights=json.dumps(["Point 1", "Point 2", "Point 3", "Point 4"]),
        )

        highlights = summary.get_highlights_list()
        assert 2 <= len(highlights) <= 6, "Should have reasonable number of highlights"

    def test_sentiment_summary_not_empty(self):
        """Sentiment summary should be meaningful."""
        summary = AISummaryNode(
            event_uuid="test-uuid",
            sentiment_summary="Great event with positive reviews",
        )

        assert summary.sentiment_summary
        assert len(summary.sentiment_summary) > 10, "Should be descriptive"

    def test_consistency_high_quality_positive_sentiment(self):
        """High quality score should correlate with positive sentiment."""
        summary = AISummaryNode(
            event_uuid="test-uuid",
            quality_score=9.0,
            sentiment_summary="Absolutely amazing experience",
            importance="must-see",
        )

        # High quality events should be must-see or iconic
        assert summary.importance in ["must-see", "iconic"]
        assert summary.quality_score >= 8.0

    def test_consistency_low_quality_concerns(self):
        """Low quality events should have concerns."""
        summary = AISummaryNode(
            event_uuid="test-uuid",
            quality_score=4.0,
            concerns=json.dumps(["Poor organization", "Not worth the price"]),
        )

        concerns = summary.get_concerns_list()
        if summary.quality_score < 5.0:
            assert len(concerns) > 0, "Low quality should have concerns"


class TestAISummaryDatabase:
    """Test database operations for AI summaries."""

    @pytest.mark.asyncio
    async def test_summary_has_timestamps(self):
        """Summary should have created_at and updated_at."""
        summary = AISummaryNode(event_uuid="test-uuid")

        assert summary.created_at is not None
        assert summary.updated_at is not None

    def test_model_version_tracking(self):
        """Summary should track model and prompt version."""
        summary = AISummaryNode(
            event_uuid="test-uuid",
            model_version="gemini-2.5-flash",
            prompt_version="v1",
        )

        assert summary.model_version == "gemini-2.5-flash"
        assert summary.prompt_version == "v1"

    def test_embedding_optional(self):
        """Embedding can be None (optional)."""
        summary = AISummaryNode(
            event_uuid="test-uuid",
            embedding=None,
        )

        assert summary.get_embedding_vector() is None

    def test_embedding_parsing(self):
        """Embedding should parse to float array."""
        embedding = [0.1, 0.2, 0.3, 0.4, 0.5]
        summary = AISummaryNode(
            event_uuid="test-uuid",
            embedding=json.dumps(embedding),
        )

        parsed = summary.get_embedding_vector()
        assert isinstance(parsed, list)
        assert len(parsed) == 5
        assert all(isinstance(x, float) for x in parsed)


class TestAISummaryEdgeCases:
    """Test edge cases and error handling."""

    def test_invalid_json_highlights(self):
        """Invalid JSON should return empty list."""
        summary = AISummaryNode(
            event_uuid="test-uuid",
            key_highlights="not valid json",
        )

        highlights = summary.get_highlights_list()
        assert highlights == []

    def test_invalid_json_concerns(self):
        """Invalid JSON concerns should return empty list."""
        summary = AISummaryNode(
            event_uuid="test-uuid",
            concerns="invalid",
        )

        concerns = summary.get_concerns_list()
        assert concerns == []

    def test_none_values_handled(self):
        """None values should be handled gracefully."""
        summary = AISummaryNode(
            event_uuid="test-uuid",
            quality_score=None,
            importance=None,
            sentiment_summary=None,
        )

        compact = summary.to_compact_dict()
        assert compact["quality_score"] is None
        assert compact["importance"] is None

    def test_empty_best_for(self):
        """Empty best_for should return empty list."""
        summary = AISummaryNode(
            event_uuid="test-uuid",
            best_for="",
        )

        compact = summary.to_compact_dict()
        assert compact["best_for"] == []

    def test_quality_score_boundaries(self):
        """Test quality score at boundaries."""
        # Test min
        summary_min = AISummaryNode(event_uuid="test", quality_score=0.0)
        assert summary_min.quality_score == 0.0

        # Test max
        summary_max = AISummaryNode(event_uuid="test", quality_score=10.0)
        assert summary_max.quality_score == 10.0

        # Test decimal
        summary_decimal = AISummaryNode(event_uuid="test", quality_score=7.5)
        assert summary_decimal.quality_score == 7.5


@pytest.mark.integration
class TestLiveAISummaryVerification:
    """
    Integration tests to verify actual data in the database.
    Requires running database.
    """

    @pytest.fixture
    def db_graph(self):
        """Connect to database graph."""
        try:
            db = FalkorDB(host="localhost", port=6379)
            g = db.select_graph("eventgraph")
            # Test connection
            g.query("RETURN 1")
            return g
        except Exception:
            pytest.skip("Database not available - skipping integration tests")

    def test_summaries_exist_in_db(self, db_graph):
        """Verify that AI summaries have been generated and saved."""
        res = db_graph.query("MATCH (s:AISummary) RETURN count(s)")
        count = res.result_set[0][0]

        if count == 0:
            pytest.skip("No AI summaries found in database. Enrichment process hasn't run.")
            
        assert count > 0
        print(f"\nFound {count} AI summaries in database.")

    def test_summary_content_quality(self, db_graph):
        """Verify quality of generated summaries using a sample."""
        # Get up to 5 summaries to check
        query = """
        MATCH (e:Event)-[:HAS_AI_SUMMARY]->(s:AISummary)
        WHERE s.quality_score IS NOT NULL
        RETURN e.title, s.quality_score, s.summary_json, s.concerns
        LIMIT 5
        """
        res = db_graph.query(query)

        if len(res.result_set) == 0:
            pytest.skip("No linked summaries found in database.")

        for row in res.result_set:
            title = row[0]
            score = row[1]
            summary_json_str = row[2]
            concerns_str = row[3]

            # 1. Basic integrity
            assert title, "Event must have a title"
            assert isinstance(score, (int, float)), "Score must be numeric"
            assert 0 <= score <= 10, "Score must be 0-10"

            # 2. JSON validity
            try:
                data = json.loads(summary_json_str)
                assert "quality_score" in data
            except json.JSONDecodeError:
                pytest.fail(f"Invalid JSON in summary for event: {title}")

            # 3. Logic check: Low score should have concerns
            if score < 5:
                concerns = json.loads(concerns_str) if concerns_str else []
                assert len(concerns) > 0, f"Low quality event '{title}' (score {score}) should have concerns listed"
