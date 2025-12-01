"""
Database package for EventGraph.
Provides connection management and OGM functionality.
"""

from src.database.connection import FalkorDBConnection, db_connection

__all__ = ["FalkorDBConnection", "db_connection"]
