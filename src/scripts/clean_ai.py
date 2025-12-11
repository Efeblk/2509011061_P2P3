#!/usr/bin/env python3
"""
Clean AI summaries from the database.
Uses the shared database connection to respect settings.
"""
import sys
import os

# Ensure src is in path
sys.path.append(os.getcwd())

from src.database.connection import db_connection
from loguru import logger

def clean_ai():
    """Remove all AISummary nodes."""
    logger.info(f"🧹 Removing AI summaries from graph '{db_connection.graph.name}'...")
    
    try:
        query = "MATCH (s:AISummary) DETACH DELETE s"
        db_connection.execute_query(query)
        logger.info("✅ AI summaries removed!")
        return True
    except Exception as e:
        logger.error(f"Failed to remove AI summaries: {e}")
        return False

if __name__ == "__main__":
    success = clean_ai()
    sys.exit(0 if success else 1)
