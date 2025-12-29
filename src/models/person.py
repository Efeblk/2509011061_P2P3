"""
Person node model for Knowledge Graph.
Represents an individual (Writer, Director, Actor, etc.) in the graph.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, List
from loguru import logger

from src.models.base import Node
from src.database.connection import db_connection


@dataclass
class PersonNode(Node):
    """
    Person node representing a real-world person.
    Connected to events via relationships like [:WROTE], [:DIRECTED], [:ACTED_IN].
    """

    name: str = ""
    # Optional: context or role commonly associated (e.g., "Writer") - though relationships define this dynamically
    known_for: Optional[str] = None

    @property
    def label(self) -> str:
        return "Person"

    def _get_properties(self) -> Dict[str, Any]:
        return {
            "uuid": self.uuid,
            "name": self.name,
            "known_for": self.known_for or "",
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat() if self.updated_at else "",
        }

    @classmethod
    def find_by_name(cls, name: str) -> Optional["PersonNode"]:
        """Find a person by name."""
        try:
            query = """
                MATCH (p:Person {name: $name})
                RETURN p
                LIMIT 1
            """
            result = db_connection.execute_query(query, {"name": name})

            if result.result_set:
                node_data = result.result_set[0][0].properties
                return cls.from_dict(node_data)

            return None
        except Exception as e:
            logger.error(f"Failed to find person by name '{name}': {e}")
            return None

    def save_relationship(self, event_uuid: str, relationship_type: str) -> bool:
        """
        Create a relationship from this Person to an Event.
        Example: (Person)-[:WROTE]->(Event)
        """
        valid_relationships = ["WROTE", "DIRECTED", "ACTED_IN", "PERFORMED_BY", "COMPOSED", "CONDUCTED", "CREW"]

        if relationship_type not in valid_relationships:
            logger.warning(f"Invalid relationship type: {relationship_type}")
            return False

        try:
            query = f"""
                MATCH (p:Person {{uuid: $person_uuid}})
                MATCH (e:Event {{uuid: $event_uuid}})
                MERGE (p)-[r:{relationship_type}]->(e)
                RETURN r
            """
            db_connection.execute_query(query, {"person_uuid": self.uuid, "event_uuid": event_uuid})
            return True
        except Exception as e:
            logger.error(f"Failed to save relationship {relationship_type}: {e}")
            return False
