#!/usr/bin/env python3
"""
Clean Collections from the database.
Uses the shared database connection to respect settings.
"""
import sys
import os

# Ensure src is in path
sys.path.append(os.getcwd())

from src.database.connection import db_connection
from loguru import logger

def clean_collections():
    """Remove all Collection nodes."""
    logger.info(f"🧹 Removing Collections from graph '{db_connection.graph.name}'...")
    
    try:
        query = "MATCH (c:Collection) DETACH DELETE c"
        db_connection.execute_query(query)
        logger.info("✅ Collections removed!")
        return True
    except Exception as e:
        logger.error(f"Failed to remove Collections: {e}")
        return False

if __name__ == "__main__":
    success = clean_collections()
    sys.exit(0 if success else 1)
