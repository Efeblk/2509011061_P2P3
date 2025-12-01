"""
Protocol definitions for graph models.
Defines interfaces that all graph models must implement.
"""

from typing import Protocol, Optional, Dict, Any, List
from datetime import datetime


class GraphModel(Protocol):
    """
    Protocol (Interface) that all graph database models must implement.
    This ensures consistent behavior across all node types.
    """

    uuid: str
    created_at: datetime
    updated_at: Optional[datetime]

    def save(self) -> bool:
        """
        Save the model to the graph database.

        Returns:
            True if successful, False otherwise
        """
        ...

    def delete(self) -> bool:
        """
        Delete the model from the graph database.

        Returns:
            True if successful, False otherwise
        """
        ...

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert model to dictionary representation.

        Returns:
            Dictionary with all model fields
        """
        ...

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GraphModel":
        """
        Create model instance from dictionary.

        Args:
            data: Dictionary with model fields

        Returns:
            New model instance
        """
        ...

    @classmethod
    def find_by_uuid(cls, uuid: str) -> Optional["GraphModel"]:
        """
        Find a model by its UUID.

        Args:
            uuid: The UUID to search for

        Returns:
            Model instance if found, None otherwise
        """
        ...

    @classmethod
    def find_all(cls, limit: Optional[int] = None) -> List["GraphModel"]:
        """
        Find all instances of this model.

        Args:
            limit: Optional limit on number of results

        Returns:
            List of model instances
        """
        ...
