"""
Venue node model for storing venue intelligence data.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any
from loguru import logger

from src.models.base import Node


@dataclass
class VenueNode(Node):
    """
    Venue node representing a physical location where events are held.
    Stores intelligence about the venue (outdoors, capacity, etc.).
    """

    name: str = ""
    city: str = "İstanbul"
    address: Optional[str] = None
    coordinates: Optional[str] = None  # "lat,lon"
    is_outdoors: bool = False
    capacity: Optional[int] = None
    vibe: Optional[str] = None  # e.g., "Historical", "Modern", "Intimate"

    @property
    def label(self) -> str:
        """Cypher label for this node type."""
        return "Venue"

    def _get_properties(self) -> Dict[str, Any]:
        """Get node properties for database storage."""
        return {
            "uuid": self.uuid,
            "name": self.name,
            "city": self.city,
            "address": self.address or "",
            "coordinates": self.coordinates or "",
            "is_outdoors": self.is_outdoors,
            "capacity": self.capacity or 0,
            "vibe": self.vibe or "",
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat() if self.updated_at else "",
        }

    @classmethod
    def find_by_name(cls, name: str) -> Optional["VenueNode"]:
        """Find a venue by its name."""
        from src.database.connection import db_connection

        try:
            query = """
                MATCH (v:Venue {name: $name})
                RETURN v
                LIMIT 1
            """
            result = db_connection.execute_query(query, {"name": name})

            if result.result_set:
                node_data = result.result_set[0][0].properties
                return cls.from_dict(node_data)

            return None

        except Exception as e:
            logger.error(f"Failed to find venue by name: {e}")
            return None
