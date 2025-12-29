"""AI-generated event summary model for intelligent recommendations."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from datetime import datetime
from typing import Optional, List, Dict, Any
import json

from src.models.base import Node
from src.database.connection import db_connection


@dataclass
class AISummaryNode(Node):
    """
    AI-generated summary and analysis of an event.

    Stores compressed, intelligent summaries that enable efficient
    AI reasoning over large event datasets.

    Relationship: (Event)-[:HAS_AI_SUMMARY]->(AISummary)
    """

    # Reference to parent event
    event_uuid: str = ""

    # Quality & Importance Assessment
    quality_score: Optional[float] = None  # 0-10 overall quality rating
    importance: Optional[str] = None  # must-see, iconic, popular, niche, seasonal, emerging
    value_rating: Optional[str] = None  # excellent, good, fair, expensive

    # Condensed Insights
    sentiment_summary: Optional[str] = None  # One-line review summary
    key_highlights: Optional[str] = None  # JSON array of 3-5 highlights
    concerns: Optional[str] = None  # JSON array of concerns/drawbacks

    # Audience & Context
    best_for: Optional[str] = None  # Comma-separated audience types
    vibe: Optional[str] = None  # Event atmosphere/feeling
    uniqueness: Optional[str] = None  # What makes this special

    # Educational & Cultural Value
    educational_value: bool = False
    tourist_attraction: bool = False
    bucket_list_worthy: bool = False

    # Embedding for similarity search
    embedding_v4: Optional[List[float]] = None  # Native Vector storage (v4 for fix)

    # Full summary JSON (backup)
    summary_json: Optional[str] = None  # Complete AI response

    # Metadata
    model_version: str = "llama3.2"  # AI model used
    prompt_version: str = "v1"  # Prompt template version
    created_at: datetime = None
    updated_at: datetime = None

    def __post_init__(self):
        """Initialize timestamps."""
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.updated_at is None:
            self.updated_at = datetime.utcnow()

    @property
    def label(self) -> str:
        """Node label for FalkorDB."""
        return "AISummary"

    def _get_properties(self) -> dict:
        """Get node properties for database storage."""
        return {
            "uuid": self.uuid,
            "event_uuid": self.event_uuid,
            "quality_score": self.quality_score,
            "importance": self.importance,
            "value_rating": self.value_rating,
            "sentiment_summary": self.sentiment_summary,
            "key_highlights": self.key_highlights,
            "concerns": self.concerns,
            "best_for": self.best_for,
            "vibe": self.vibe,
            "uniqueness": self.uniqueness,
            "educational_value": self.educational_value,
            "tourist_attraction": self.tourist_attraction,
            "bucket_list_worthy": self.bucket_list_worthy,
            "embedding_v4": self.embedding_v4,
            "summary_json": self.summary_json,
            "model_version": self.model_version,
            "prompt_version": self.prompt_version,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def get_highlights_list(self) -> list[str]:
        """Parse highlights JSON to list."""
        if not self.key_highlights:
            return []
        try:
            return json.loads(self.key_highlights)
        except (json.JSONDecodeError, TypeError):
            return []

    def get_concerns_list(self) -> list[str]:
        """Parse concerns JSON to list."""
        if not self.concerns:
            return []
        try:
            return json.loads(self.concerns)
        except (json.JSONDecodeError, TypeError):
            return []

    def get_embedding_vector(self) -> Optional[List[float]]:
        """Return embedding vector (ALREADY A LIST)."""
        return self.embedding_v4

    def to_compact_dict(self) -> dict:
        """
        Return compact representation for AI reasoning.

        This is the format sent to Gemini for recommendations.
        Keeps token count low while preserving key insights.
        """
        return {
            "event_uuid": self.event_uuid,
            "quality_score": self.quality_score,
            "importance": self.importance,
            "value_rating": self.value_rating,
            "sentiment": self.sentiment_summary,
            "highlights": self.get_highlights_list(),
            "concerns": self.get_concerns_list(),
            "best_for": self.best_for.split(",") if self.best_for else [],
            "vibe": self.vibe,
            "uniqueness": self.uniqueness,
            "special_flags": {
                "educational": self.educational_value,
                "tourist_spot": self.tourist_attraction,
                "bucket_list": self.bucket_list_worthy,
            },
        }

    async def save(self) -> Optional["AISummaryNode"]:
        """
        Save AI summary node to database and create relationship to event.

        Returns:
            AISummaryNode if successful, None if failed
        """
        from src.database.connection import db_connection

        try:
            self.updated_at = datetime.utcnow()
            properties = self._get_properties()

            # Separate embedding to store as Vector (vecf32)
            embedding_val = properties.pop("embedding_v4", None)

            # Build Cypher query for MERGE (create or update)
            # Use SET s += to update properties without wiping existing ones if strictly needed,
            # but here we want to enforce schema, so SET s = might be okay.
            # However, separating embedding means SET s = {...} might REMOVE embedding if we use =.
            # So we should include embedding in the map OR update logic.
            # Pattern: SET s = map (without vector), SET s.vec = vecf32($vec)

            props_str = ", ".join([f"{k}: ${k}" for k in properties.keys()])

            query = f"""
            MERGE (s:AISummary {{uuid: $uuid}})
            SET s = {{{props_str}}}
            """

            if embedding_val is not None:
                query += " SET s.embedding_v4 = vecf32($embedding_vec) "
                properties["embedding_vec"] = embedding_val

            query += """
            WITH s
            MATCH (e:Event {uuid: $event_uuid})
            MERGE (e)-[:HAS_AI_SUMMARY]->(s)
            RETURN s
            """

            result = db_connection.graph.query(query, properties)

            if result.result_set:
                return self
            return None

        except Exception as e:
            print(f"Error saving AI summary: {e}")
            return None

    @staticmethod
    async def get_by_event_uuid(event_uuid: str) -> Optional["AISummaryNode"]:
        """
        Get AI summary for a specific event.

        Args:
            event_uuid: UUID of the event

        Returns:
            AISummaryNode if found, None otherwise
        """
        from src.database.connection import db_connection

        try:
            query = """
            MATCH (e:Event {uuid: $event_uuid})-[:HAS_AI_SUMMARY]->(s:AISummary)
            RETURN s
            LIMIT 1
            """

            result = db_connection.graph.query(query, {"event_uuid": event_uuid})

            if result.result_set:
                node_data = result.result_set[0][0]
                return AISummaryNode(
                    uuid=node_data.properties.get("uuid"),
                    event_uuid=node_data.properties.get("event_uuid"),
                    quality_score=node_data.properties.get("quality_score"),
                    importance=node_data.properties.get("importance"),
                    value_rating=node_data.properties.get("value_rating"),
                    sentiment_summary=node_data.properties.get("sentiment_summary"),
                    key_highlights=node_data.properties.get("key_highlights"),
                    concerns=node_data.properties.get("concerns"),
                    best_for=node_data.properties.get("best_for"),
                    vibe=node_data.properties.get("vibe"),
                    uniqueness=node_data.properties.get("uniqueness"),
                    educational_value=node_data.properties.get("educational_value", False),
                    tourist_attraction=node_data.properties.get("tourist_attraction", False),
                    bucket_list_worthy=node_data.properties.get("bucket_list_worthy", False),
                    embedding_v4=node_data.properties.get("embedding_v4"),
                    summary_json=node_data.properties.get("summary_json"),
                    model_version=node_data.properties.get("model_version", "gemini-1.5-flash"),
                    prompt_version=node_data.properties.get("prompt_version", "v1"),
                    created_at=(
                        datetime.fromisoformat(node_data.properties["created_at"])
                        if node_data.properties.get("created_at")
                        else None
                    ),
                    updated_at=(
                        datetime.fromisoformat(node_data.properties["updated_at"])
                        if node_data.properties.get("updated_at")
                        else None
                    ),
                )

            return None

        except Exception as e:
            print(f"Error getting AI summary: {e}")
            return None

    @staticmethod
    def create_vector_index(dimension: Optional[int] = None):
        """Create vector index on AISummary nodes."""
        from config.settings import settings

        if dimension is None:
            dimension = settings.ai.embedding_dimension

        try:
            # Native Cypher syntax for FalkorDB >= 1.0
            query = f"CREATE VECTOR INDEX FOR (s:AISummary) ON (s.embedding_v4) OPTIONS {{dimension: {dimension}, similarityFunction: 'cosine'}}"
            db_connection.graph.query(query)
            print(f"Vector index created with dimension {dimension}.")
        except Exception as e:
            # Check if index already exists
            if "already indexed" in str(e):
                print(f"Vector index already exists (dim={dimension}).")
            else:
                print(f"Error creating vector index: {e}")

    @staticmethod
    async def get_all_summaries(limit: int = 100) -> list["AISummaryNode"]:
        """
        Get all AI summaries with optional limit.

        Args:
            limit: Maximum number of summaries to return

        Returns:
            List of AISummaryNode objects
        """
        from src.database.connection import db_connection

        try:
            query = f"""
            MATCH (s:AISummary)
            RETURN s
            LIMIT {limit}
            """

            result = db_connection.graph.query(query)

            summaries = []
            if result.result_set:
                for row in result.result_set:
                    node_data = row[0]
                    summaries.append(
                        AISummaryNode(
                            uuid=node_data.properties.get("uuid"),
                            event_uuid=node_data.properties.get("event_uuid"),
                            quality_score=node_data.properties.get("quality_score"),
                            importance=node_data.properties.get("importance"),
                            value_rating=node_data.properties.get("value_rating"),
                            sentiment_summary=node_data.properties.get("sentiment_summary"),
                            key_highlights=node_data.properties.get("key_highlights"),
                            concerns=node_data.properties.get("concerns"),
                            best_for=node_data.properties.get("best_for"),
                            vibe=node_data.properties.get("vibe"),
                            uniqueness=node_data.properties.get("uniqueness"),
                            educational_value=node_data.properties.get("educational_value", False),
                            tourist_attraction=node_data.properties.get("tourist_attraction", False),
                            bucket_list_worthy=node_data.properties.get("bucket_list_worthy", False),
                            embedding_v4=node_data.properties.get("embedding_v4"),
                            summary_json=node_data.properties.get("summary_json"),
                            model_version=node_data.properties.get("model_version", "gemini-1.5-flash"),
                            prompt_version=node_data.properties.get("prompt_version", "v1"),
                            created_at=(
                                datetime.fromisoformat(node_data.properties["created_at"])
                                if node_data.properties.get("created_at")
                                else None
                            ),
                            updated_at=(
                                datetime.fromisoformat(node_data.properties["updated_at"])
                                if node_data.properties.get("updated_at")
                                else None
                            ),
                        )
                    )

            return summaries

        except Exception as e:
            print(f"Error getting AI summaries: {e}")
            return []
