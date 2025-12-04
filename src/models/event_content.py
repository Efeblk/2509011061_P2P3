"""
EventContent node model for storing event-related metadata.
Stores comments, ratings, and AI-relevant content separately from Event nodes.
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from datetime import datetime
from loguru import logger

from src.models.base import Node
from src.database.connection import db_connection


@dataclass
class EventContentNode(Node):
    """
    EventContent node for storing metadata about events.

    This node stores user-generated and AI-relevant content separately from
    the core Event data, enabling:
    - User comments and reviews
    - Rating aggregation
    - Rich textual descriptions for AI analysis
    - Social features (likes, shares, etc.)

    Architecture:
    - EventContent nodes connect to Event nodes via HAS_CONTENT relationship
    - Multiple EventContent nodes can relate to one Event (for different content types)
    - Content type field allows filtering (e.g., "user_review", "ai_summary", "description")
    """

    # Core fields
    event_uuid: str = ""  # Reference to the Event node this content belongs to
    content_type: str = ""  # e.g., "description", "user_review", "ai_summary", "editorial"

    # Content fields
    text: Optional[str] = None  # Main textual content
    summary: Optional[str] = None  # Short summary for AI/display

    # Rating fields
    rating: Optional[float] = None  # Numerical rating (0.0-5.0)
    rating_count: Optional[int] = None  # Number of ratings aggregated

    # Metadata fields
    author: Optional[str] = None  # Author of content (user_id, "AI", "editorial", etc.)
    language: Optional[str] = "tr"  # Content language (default Turkish)

    # AI-relevant fields
    sentiment_score: Optional[float] = None  # Sentiment analysis (-1.0 to 1.0)
    keywords: Optional[str] = None  # Comma-separated keywords for AI
    embedding_vector: Optional[str] = None  # JSON-serialized embedding for similarity

    # Engagement fields
    likes_count: int = 0
    views_count: int = 0
    helpful_count: int = 0  # For reviews: "Was this helpful?" count

    @property
    def label(self) -> str:
        """Cypher label for this node type."""
        return "EventContent"

    def _get_properties(self) -> Dict[str, Any]:
        """Get node properties for database storage."""
        return {
            "uuid": self.uuid,
            "event_uuid": self.event_uuid,
            "content_type": self.content_type,
            "text": self.text or "",
            "summary": self.summary or "",
            "rating": self.rating or 0.0,
            "rating_count": self.rating_count or 0,
            "author": self.author or "",
            "language": self.language,
            "sentiment_score": self.sentiment_score or 0.0,
            "keywords": self.keywords or "",
            "embedding_vector": self.embedding_vector or "",
            "likes_count": self.likes_count,
            "views_count": self.views_count,
            "helpful_count": self.helpful_count,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat() if self.updated_at else "",
        }

    def save_with_relationship(self) -> bool:
        """
        Save this EventContent node and create relationship to Event.
        Creates: (Event)-[:HAS_CONTENT]->(EventContent)
        """
        try:
            self.updated_at = datetime.utcnow()
            properties = self._get_properties()

            # Build Cypher query that creates/updates node AND relationship
            props_str = ", ".join([f"{k}: ${k}" for k in properties.keys()])
            query = f"""
                MATCH (e:Event {{uuid: $event_uuid}})
                MERGE (c:{self.label} {{uuid: $uuid}})
                SET c = {{{props_str}}}
                MERGE (e)-[:HAS_CONTENT]->(c)
                RETURN c
            """

            db_connection.execute_query(query, properties)
            logger.debug(f"Saved {self.label} node with UUID: {self.uuid} " f"and linked to Event: {self.event_uuid}")
            return True

        except Exception as e:
            logger.error(f"Failed to save {self.label} node with relationship: {e}")
            return False

    @classmethod
    def find_by_event_uuid(cls, event_uuid: str, content_type: Optional[str] = None) -> List["EventContentNode"]:
        """
        Find all EventContent nodes for a specific Event.

        Args:
            event_uuid: UUID of the Event node
            content_type: Optional filter by content type

        Returns:
            List of EventContentNode instances
        """
        try:
            if content_type:
                query = """
                    MATCH (e:Event {uuid: $event_uuid})-[:HAS_CONTENT]->(c:EventContent {content_type: $content_type})
                    RETURN c
                """
                params = {"event_uuid": event_uuid, "content_type": content_type}
            else:
                query = """
                    MATCH (e:Event {uuid: $event_uuid})-[:HAS_CONTENT]->(c:EventContent)
                    RETURN c
                """
                params = {"event_uuid": event_uuid}

            result = db_connection.execute_query(query, params)

            contents = []
            if result.result_set:
                for row in result.result_set:
                    node_data = row[0].properties
                    contents.append(cls.from_dict(node_data))

            return contents

        except Exception as e:
            logger.error(f"Failed to find EventContent by event UUID: {e}")
            return []

    @classmethod
    def find_by_content_type(cls, content_type: str, limit: Optional[int] = None) -> List["EventContentNode"]:
        """
        Find EventContent nodes by content type.

        Args:
            content_type: Type of content to filter (e.g., "user_review", "ai_summary")
            limit: Optional limit on results

        Returns:
            List of EventContentNode instances
        """
        try:
            query = "MATCH (c:EventContent {content_type: $content_type}) RETURN c"
            if limit:
                query += f" LIMIT {limit}"

            result = db_connection.execute_query(query, {"content_type": content_type})

            contents = []
            if result.result_set:
                for row in result.result_set:
                    node_data = row[0].properties
                    contents.append(cls.from_dict(node_data))

            return contents

        except Exception as e:
            logger.error(f"Failed to find EventContent by type: {e}")
            return []

    @classmethod
    def get_aggregated_rating(cls, event_uuid: str) -> Optional[float]:
        """
        Get aggregated rating for an event from all user reviews.

        Args:
            event_uuid: UUID of the Event node

        Returns:
            Average rating or None if no ratings exist
        """
        try:
            query = """
                MATCH (e:Event {uuid: $event_uuid})-[:HAS_CONTENT]->(c:EventContent)
                WHERE c.content_type = 'user_review' AND c.rating > 0
                RETURN avg(c.rating) as avg_rating
            """
            result = db_connection.execute_query(query, {"event_uuid": event_uuid})

            if result.result_set and result.result_set[0][0] is not None:
                return float(result.result_set[0][0])

            return None

        except Exception as e:
            logger.error(f"Failed to get aggregated rating: {e}")
            return None

    @classmethod
    def get_top_rated_events(cls, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get top-rated events based on EventContent ratings.

        Args:
            limit: Number of events to return

        Returns:
            List of dicts with event_uuid and average rating
        """
        try:
            query = """
                MATCH (e:Event)-[:HAS_CONTENT]->(c:EventContent)
                WHERE c.content_type = 'user_review' AND c.rating > 0
                WITH e.uuid as event_uuid, avg(c.rating) as avg_rating, count(c) as review_count
                WHERE review_count >= 3
                RETURN event_uuid, avg_rating, review_count
                ORDER BY avg_rating DESC
                LIMIT $limit
            """
            result = db_connection.execute_query(query, {"limit": limit})

            top_events = []
            if result.result_set:
                for row in result.result_set:
                    top_events.append(
                        {"event_uuid": row[0], "average_rating": float(row[1]), "review_count": int(row[2])}
                    )

            return top_events

        except Exception as e:
            logger.error(f"Failed to get top rated events: {e}")
            return []

    def __repr__(self) -> str:
        """String representation of the EventContent."""
        return (
            f"EventContentNode(event_uuid='{self.event_uuid}', "
            f"content_type='{self.content_type}', rating={self.rating})"
        )
