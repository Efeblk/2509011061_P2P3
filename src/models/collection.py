"""Collection model for curated event lists."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List

from src.models.base import Node
from src.database.connection import db_connection


@dataclass
class CollectionNode(Node):
    """
    Represents a curated collection of events (e.g., "Best Value", "Date Night").
    Results from AI Tournaments are stored here.
    """

    name: str = ""
    description: str = ""
    category: str = ""  # internal tag: value, vibe, etc.
    updated_at: datetime = None

    def __post_init__(self):
        if self.updated_at is None:
            self.updated_at = datetime.utcnow()

    @property
    def label(self) -> str:
        return "Collection"

    def _get_properties(self) -> dict:
        return {
            "uuid": self.uuid,
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    async def save(self) -> Optional["CollectionNode"]:
        """Save collection to DB."""
        try:
            self.updated_at = datetime.utcnow()
            properties = self._get_properties()
            
            # Simple merge based on category (unique key)
            query = """
            MERGE (c:Collection {category: $category})
            SET c += $props
            RETURN c
            """
            # We overwrite name/desc if they changed
            params = {"category": self.category, "props": properties}
            
            result = db_connection.graph.query(query, params)
            if result.result_set:
                return self
            return None
        except Exception as e:
            print(f"Error saving collection: {e}")
            return None

    async def add_event(self, event_uuid: str, rank: int, reason: str):
        """Add an event to this collection with ranking."""
        try:
            query = """
            MATCH (c:Collection {category: $category})
            MATCH (e:Event {uuid: $event_uuid})
            MERGE (c)-[r:CONTAINS]->(e)
            SET r.rank = $rank, r.reason = $reason, r.added_at = $now
            """
            params = {
                "category": self.category,
                "event_uuid": event_uuid,
                "rank": rank,
                "reason": reason,
                "now": datetime.utcnow().isoformat()
            }
            db_connection.graph.query(query, params)
        except Exception as e:
            print(f"Error adding event to collection: {e}")

    async def clear_events(self):
        """Remove all events from this collection (before refreshing)."""
        try:
            query = """
            MATCH (c:Collection {category: $category})-[r:CONTAINS]->()
            DELETE r
            """
            db_connection.graph.query(query, {"category": self.category})
        except Exception as e:
            print(f"Error clearing collection: {e}")

    @staticmethod
    async def get_by_category(category: str) -> Optional["CollectionNode"]:
        """Fetch collection by category."""
        try:
            query = "MATCH (c:Collection {category: $cat}) RETURN c"
            res = db_connection.graph.query(query, {"cat": category})
            if res.result_set:
                data = res.result_set[0][0]
                return CollectionNode(
                    uuid=data.properties.get("uuid"),
                    name=data.properties.get("name"),
                    description=data.properties.get("description"),
                    category=data.properties.get("category"),
                    updated_at=datetime.fromisoformat(data.properties["updated_at"])
                )
            return None
        except Exception as e:
             print(f"Error getting collection: {e}")
             return None
