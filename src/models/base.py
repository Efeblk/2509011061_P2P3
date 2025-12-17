"""
Base classes for graph models.
Provides common functionality for all node types.
"""

import uuid
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional, Dict, Any, List, Type
from dataclasses import dataclass, field, asdict

from loguru import logger
from src.database.connection import db_connection


@dataclass
class Node(ABC):
    """
    Abstract base class for all graph nodes.
    Implements common fields and methods shared by all node types.
    """

    uuid: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

    @property
    @abstractmethod
    def label(self) -> str:
        """
        The Cypher label for this node type.
        Must be implemented by subclasses.
        """
        pass

    @abstractmethod
    def _get_properties(self) -> Dict[str, Any]:
        """
        Get node properties for database storage.
        Must be implemented by subclasses.
        """
        pass

    def save(self) -> bool:
        """
        Save this node to the graph database.
        Updates updated_at timestamp.
        """
        try:
            self.updated_at = datetime.utcnow()
            properties = self._get_properties()

            # Build Cypher query for MERGE (create or update)
            props_str = ", ".join([f"{k}: ${k}" for k in properties.keys()])
            query = f"""
                MERGE (n:{self.label} {{uuid: $uuid}})
                SET n = {{{props_str}}}
                RETURN n
            """

            db_connection.execute_query(query, properties)
            logger.debug(f"Saved {self.label} node with UUID: {self.uuid}")
            return True

        except Exception as e:
            logger.error(f"Failed to save {self.label} node: {e}")
            return False

    def delete(self) -> bool:
        """
        Delete this node from the graph database.
        Also deletes all relationships.
        """
        try:
            query = f"""
                MATCH (n:{self.label} {{uuid: $uuid}})
                DETACH DELETE n
            """
            db_connection.execute_query(query, {"uuid": self.uuid})
            logger.debug(f"Deleted {self.label} node with UUID: {self.uuid}")
            return True

        except Exception as e:
            logger.error(f"Failed to delete {self.label} node: {e}")
            return False

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert node to dictionary representation.
        Converts datetime objects to ISO format strings.
        """
        data = asdict(self)
        # Convert datetime to ISO format
        if data.get("created_at"):
            data["created_at"] = data["created_at"].isoformat()
        if data.get("updated_at"):
            data["updated_at"] = data["updated_at"].isoformat()
        return data

    @classmethod
    def from_dict(cls: Type["Node"], data: Dict[str, Any]) -> "Node":
        """
        Create node instance from dictionary.
        Converts ISO format strings back to datetime objects.
        """
        # Convert ISO format strings to datetime
        if isinstance(data.get("created_at"), str):
            data["created_at"] = datetime.fromisoformat(data["created_at"])
        if isinstance(data.get("updated_at"), str):
            data["updated_at"] = datetime.fromisoformat(data["updated_at"])

        return cls(**data)

    @classmethod
    def find_by_uuid(cls: Type["Node"], uuid: str) -> Optional["Node"]:
        """
        Find a node by its UUID.
        """
        try:
            # Get label from a temporary instance
            label = cls.__annotations__.get("label", cls.__name__)
            # Try to get label from class if it's a property
            if hasattr(cls, "label"):
                # Create a minimal instance to get the label
                temp_instance = object.__new__(cls)
                label = temp_instance.label

            query = f"""
                MATCH (n:{label} {{uuid: $uuid}})
                RETURN n
            """
            result = db_connection.execute_query(query, {"uuid": uuid})

            if result.result_set:
                node_data = result.result_set[0][0].properties
                return cls.from_dict(node_data)

            return None

        except Exception as e:
            logger.error(f"Failed to find node by UUID: {e}")
            return None

    @classmethod
    async def get_all_events(cls, limit: int = 100) -> List["EventNode"]:
        """
        Get all events (async wrapper around find_all).
        """
        from src.database.connection import db_connection
        import asyncio
        
        # We can implement this as an async wrapper essentially
        # But for now, let's just make a direct cypher query that is efficient
        try:
            query = f"MATCH (n:Event) RETURN n LIMIT {limit}"
            result = await asyncio.to_thread(db_connection.execute_query, query)
            
            nodes = []
            if result.result_set:
                for row in result.result_set:
                    node_data = row[0].properties
                    nodes.append(cls.from_dict(node_data))
            return nodes
        except Exception as e:
            logger.error(f"Failed to get events: {e}")
            return []
        try:
            # Get label
            temp_instance = object.__new__(cls)
            label = temp_instance.label

            query = f"MATCH (n:{label}) RETURN n"
            if limit:
                query += f" LIMIT {limit}"

            result = db_connection.execute_query(query)

            nodes = []
            if result.result_set:
                for row in result.result_set:
                    node_data = row[0].properties
                    nodes.append(cls.from_dict(node_data))

            return nodes

        except Exception as e:
            logger.error(f"Failed to find all nodes: {e}")
            return []

    def __repr__(self) -> str:
        """String representation of the node."""
        return f"{self.__class__.__name__}(uuid={self.uuid})"
