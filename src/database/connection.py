"""
Database connection module for FalkorDB.
Implements Singleton pattern to ensure single connection instance.
"""

from typing import Optional, Any
import redis
from falkordb import FalkorDB
from loguru import logger
from config.settings import settings


class FalkorDBConnection:
    """
    Singleton class for managing FalkorDB connection.
    Ensures only one connection instance exists throughout the application.
    """

    _instance: Optional["FalkorDBConnection"] = None
    _client: Optional[FalkorDB] = None
    _redis_client: Optional[redis.Redis] = None
    _graph: Optional[Any] = None

    def __new__(cls):
        """
        Implement Singleton pattern.
        Returns the same instance if already created.
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """Initialize connection only once."""
        if self._initialized:
            return

        self._initialized = True
        self._connect()

    def _connect(self):
        """Establish connection to FalkorDB."""
        try:
            # Create Redis client for low-level operations
            self._redis_client = redis.Redis(
                host=settings.falkordb.host,
                port=settings.falkordb.port,
                password=settings.falkordb.password,
                db=settings.falkordb.db,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
            )

            # Test connection
            self._redis_client.ping()
            logger.info(f"Successfully connected to Redis at {settings.falkordb.host}:{settings.falkordb.port}")

            # Create FalkorDB client
            self._client = FalkorDB(
                host=settings.falkordb.host,
                port=settings.falkordb.port,
                password=settings.falkordb.password,
            )

            # Select graph
            self._graph = self._client.select_graph(settings.falkordb.graph_name)
            logger.info(f"Selected graph: {settings.falkordb.graph_name}")

        except redis.ConnectionError as e:
            logger.error(f"Failed to connect to FalkorDB: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during connection: {e}")
            raise

    @property
    def client(self) -> FalkorDB:
        """Get FalkorDB client instance."""
        if self._client is None:
            self._connect()
        return self._client

    @property
    def redis(self) -> redis.Redis:
        """Get Redis client instance for low-level operations."""
        if self._redis_client is None:
            self._connect()
        return self._redis_client

    @property
    def graph(self):
        """Get current graph instance."""
        if self._graph is None:
            self._connect()
        return self._graph

    def execute_query(self, query: str, params: Optional[dict] = None) -> Any:
        """
        Execute a Cypher query on the graph.

        Args:
            query: Cypher query string
            params: Optional query parameters

        Returns:
            Query result
        """
        try:
            logger.debug(f"Executing query: {query}")
            if params:
                logger.debug(f"Query parameters: {params}")

            result = self.graph.query(query, params or {})
            return result

        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            logger.error(f"Query: {query}")
            raise

    def health_check(self) -> bool:
        """
        Check if database connection is healthy.

        Returns:
            True if connection is healthy, False otherwise
        """
        try:
            self.redis.ping()
            return True
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False

    def close(self):
        """Close database connection."""
        try:
            if self._redis_client:
                self._redis_client.close()
                logger.info("Redis connection closed")

            self._client = None
            self._redis_client = None
            self._graph = None
            self._initialized = False

        except Exception as e:
            logger.error(f"Error closing connection: {e}")

    def reset_connection(self):
        """Reset and reconnect to database."""
        logger.info("Resetting database connection...")
        self.close()
        self._connect()

    def create_indexes(self):
        """Create indexes for better query performance."""
        try:
            # Index on Event nodes
            self.execute_query("CREATE INDEX FOR (e:Event) ON (e.uuid)")
            self.execute_query("CREATE INDEX FOR (e:Event) ON (e.title)")
            self.execute_query("CREATE INDEX FOR (e:Event) ON (e.date)")

            # Index on Venue nodes
            self.execute_query("CREATE INDEX FOR (v:Venue) ON (v.uuid)")
            self.execute_query("CREATE INDEX FOR (v:Venue) ON (v.name)")

            # Index on Artist nodes
            self.execute_query("CREATE INDEX FOR (a:Artist) ON (a.uuid)")
            self.execute_query("CREATE INDEX FOR (a:Artist) ON (a.name)")

            # Index on Tag nodes
            self.execute_query("CREATE INDEX FOR (t:Tag) ON (t.name)")

            logger.info("Database indexes created successfully")

        except Exception as e:
            logger.warning(f"Index creation failed (may already exist): {e}")

    def clear_graph(self):
        """
        Clear all data from the graph.
        WARNING: This is destructive and cannot be undone!
        """
        logger.warning("Clearing all graph data...")
        try:
            self.execute_query("MATCH (n) DETACH DELETE n")
            logger.info("Graph cleared successfully")
        except Exception as e:
            logger.error(f"Failed to clear graph: {e}")
            raise

    def get_stats(self) -> dict:
        """
        Get database statistics.

        Returns:
            Dictionary with database statistics
        """
        try:
            stats = {}

            # Count nodes by label
            for label in ["Event", "Venue", "Artist", "Tag"]:
                result = self.execute_query(f"MATCH (n:{label}) RETURN count(n) as count")
                stats[f"{label.lower()}_count"] = result.result_set[0][0] if result.result_set else 0

            # Count relationships
            result = self.execute_query("MATCH ()-[r]->() RETURN count(r) as count")
            stats["relationship_count"] = result.result_set[0][0] if result.result_set else 0

            # Memory info from Redis
            info = self.redis.info("memory")
            stats["memory_used"] = info.get("used_memory_human", "N/A")

            return stats

        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            return {}


# Global connection instance
db_connection = FalkorDBConnection()
