"""
Event node model for storing event data in the graph database.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any, List
from loguru import logger

from src.models.base import Node


@dataclass
class EventNode(Node):
    """
    Event node representing a cultural event (concert, theater, etc.).
    """

    title: str = ""
    description: Optional[str] = None
    date: Optional[str] = None  # Store as ISO format string
    venue: Optional[str] = None
    city: Optional[str] = None
    price: Optional[float] = None
    price_range: Optional[str] = None  # e.g., "100-500 TL"
    url: Optional[str] = None
    image_url: Optional[str] = None
    category: Optional[str] = None  # e.g., "Concert", "Theater", "Stand-up"
    source: Optional[str] = None  # e.g., "biletix", "biletino"

    # AI analysis fields (to be filled later)
    ai_score: Optional[float] = None
    ai_verdict: Optional[str] = None
    ai_reasoning: Optional[str] = None

    @property
    def label(self) -> str:
        """Cypher label for this node type."""
        return "Event"

    def _get_properties(self) -> Dict[str, Any]:
        """Get node properties for database storage."""
        return {
            "uuid": self.uuid,
            "title": self.title,
            "description": self.description or "",
            "date": self.date or "",
            "venue": self.venue or "",
            "city": self.city or "",
            "price": self.price,
            "price_range": self.price_range or "",
            "url": self.url or "",
            "image_url": self.image_url or "",
            "category": self.category or "",
            "source": self.source or "",
            "ai_score": self.ai_score or 0.0,
            "ai_verdict": self.ai_verdict or "",
            "ai_reasoning": self.ai_reasoning or "",
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat() if self.updated_at else "",
        }

    @classmethod
    def find_by_title(cls, title: str) -> Optional["EventNode"]:
        """Find an event by its title."""
        from src.database.connection import db_connection

        try:
            query = """
                MATCH (e:Event {title: $title})
                RETURN e
                LIMIT 1
            """
            result = db_connection.execute_query(query, {"title": title})

            if result.result_set:
                node_data = result.result_set[0][0].properties
                return cls.from_dict(node_data)

            return None

        except Exception as e:
            logger.error(f"Failed to find event by title: {e}")
            return None

    @classmethod
    def find_by_title_and_venue(cls, title: str, venue: str) -> Optional["EventNode"]:
        """Find an event by its title and venue (unique combination)."""
        from src.database.connection import db_connection

        try:
            query = """
                MATCH (e:Event {title: $title, venue: $venue})
                RETURN e
                LIMIT 1
            """
            result = db_connection.execute_query(query, {"title": title, "venue": venue})

            if result.result_set:
                node_data = result.result_set[0][0].properties
                return cls.from_dict(node_data)

            return None

        except Exception as e:
            logger.error(f"Failed to find event by title and venue: {e}")
            return None

    @classmethod
    def find_by_title_venue_and_date(cls, title: str, venue: str, date: str) -> Optional["EventNode"]:
        """Find an event by its title, venue, and date (unique combination for multi-date events)."""
        from src.database.connection import db_connection

        try:
            query = """
                MATCH (e:Event {title: $title, venue: $venue, date: $date})
                RETURN e
                LIMIT 1
            """
            result = db_connection.execute_query(query, {"title": title, "venue": venue, "date": date})

            if result.result_set:
                node_data = result.result_set[0][0].properties
                return cls.from_dict(node_data)

            return None

        except Exception as e:
            logger.error(f"Failed to find event by title, venue, and date: {e}")
            return None

    @classmethod
    def find_by_source(cls, source: str, limit: Optional[int] = None) -> List["EventNode"]:
        """Find events by their source (e.g., 'biletix')."""
        from src.database.connection import db_connection

        try:
            query = "MATCH (e:Event {source: $source}) RETURN e"
            if limit:
                query += f" LIMIT {limit}"

            result = db_connection.execute_query(query, {"source": source})

            events = []
            if result.result_set:
                for row in result.result_set:
                    node_data = row[0].properties
                    events.append(cls.from_dict(node_data))

            return events

        except Exception as e:
            logger.error(f"Failed to find events by source: {e}")
            return []

    @classmethod
    def find_by_category(cls, category: str, limit: Optional[int] = None) -> List["EventNode"]:
        """Find events by category."""
        from src.database.connection import db_connection

        try:
            query = "MATCH (e:Event {category: $category}) RETURN e"
            if limit:
                query += f" LIMIT {limit}"

            result = db_connection.execute_query(query, {"category": category})

            events = []
            if result.result_set:
                for row in result.result_set:
                    node_data = row[0].properties
                    events.append(cls.from_dict(node_data))

            return events

        except Exception as e:
            logger.error(f"Failed to find events by category: {e}")
            return []

    @staticmethod
    async def get_all_events(limit: int = 100) -> List["EventNode"]:
        """Get all events with optional limit."""
        from src.database.connection import db_connection

        try:
            query = f"MATCH (e:Event) RETURN e LIMIT {limit}"
            result = db_connection.execute_query(query)

            events = []
            if result.result_set:
                for row in result.result_set:
                    node_data = row[0].properties
                    events.append(EventNode.from_dict(node_data))

            logger.info(f"Retrieved {len(events)} events from database")
            return events

        except Exception as e:
            logger.error(f"Failed to get all events: {e}")
            return []

    async def get_reviews(self, limit: int = 10) -> List[Any]:
        """Get reviews for this event."""
        from src.database.connection import db_connection

        try:
            query = """
                MATCH (e:Event {uuid: $uuid})-[:HAS_REVIEW]->(r:Review)
                RETURN r
                LIMIT $limit
            """
            result = db_connection.execute_query(query, {"uuid": self.uuid, "limit": limit})

            reviews = []
            if result.result_set:
                for row in result.result_set:
                    reviews.append(row[0])

            return reviews

        except Exception as e:
            logger.warning(f"Failed to get reviews for event {self.title}: {e}")
            return []

    def __repr__(self) -> str:
        """String representation of the event."""
        return f"EventNode(title='{self.title}', date='{self.date}', venue='{self.venue}')"
