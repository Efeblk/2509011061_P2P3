"""
Unit tests for database connection module.
"""

import pytest
from unittest.mock import MagicMock, patch, call
from src.database.connection import FalkorDBConnection


@pytest.mark.unit
@pytest.mark.database
class TestFalkorDBConnection:
    """Test cases for FalkorDBConnection class."""

    def test_singleton_pattern(self):
        """Test that FalkorDBConnection implements Singleton pattern."""
        with patch("src.database.connection.redis.Redis"), \
             patch("src.database.connection.FalkorDB"):

            conn1 = FalkorDBConnection()
            conn2 = FalkorDBConnection()

            assert conn1 is conn2, "FalkorDBConnection should return same instance"

    def test_connection_initialization(self, mock_redis_client, mock_falkordb_client):
        """Test database connection initialization."""
        with patch("src.database.connection.redis.Redis", return_value=mock_redis_client), \
             patch("src.database.connection.FalkorDB", return_value=mock_falkordb_client):

            # Reset singleton
            FalkorDBConnection._instance = None

            conn = FalkorDBConnection()

            assert conn is not None
            mock_redis_client.ping.assert_called_once()

    def test_health_check_success(self, mock_redis_client):
        """Test successful health check."""
        with patch("src.database.connection.redis.Redis", return_value=mock_redis_client), \
             patch("src.database.connection.FalkorDB"):

            # Reset singleton
            FalkorDBConnection._instance = None

            conn = FalkorDBConnection()
            mock_redis_client.ping.return_value = True

            assert conn.health_check() is True

    def test_health_check_failure(self, mock_redis_client):
        """Test failed health check."""
        with patch("src.database.connection.redis.Redis", return_value=mock_redis_client), \
             patch("src.database.connection.FalkorDB"):

            # Reset singleton
            FalkorDBConnection._instance = None

            conn = FalkorDBConnection()
            mock_redis_client.ping.side_effect = Exception("Connection failed")

            assert conn.health_check() is False

    def test_execute_query(self):
        """Test query execution."""
        mock_graph = MagicMock()
        mock_result = MagicMock()
        mock_graph.query.return_value = mock_result

        with patch("src.database.connection.redis.Redis"), \
             patch("src.database.connection.FalkorDB") as mock_falkordb:

            # Reset singleton
            FalkorDBConnection._instance = None

            mock_client = MagicMock()
            mock_client.select_graph.return_value = mock_graph
            mock_falkordb.return_value = mock_client

            conn = FalkorDBConnection()
            result = conn.execute_query("MATCH (n) RETURN n")

            assert result == mock_result
            mock_graph.query.assert_called_once()

    def test_close_connection(self, mock_redis_client):
        """Test connection closure."""
        with patch("src.database.connection.redis.Redis", return_value=mock_redis_client), \
             patch("src.database.connection.FalkorDB"):

            # Reset singleton
            FalkorDBConnection._instance = None

            conn = FalkorDBConnection()
            conn.close()

            mock_redis_client.close.assert_called_once()
            assert conn._initialized is False
