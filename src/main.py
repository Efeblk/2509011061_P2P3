"""
Main entry point for EventGraph application.
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from loguru import logger
from config.logging_config import setup_logging
from config.settings import settings
from src.database.connection import db_connection


def initialize_app():
    """Initialize the application."""
    logger.info("="*60)
    logger.info("EventGraph - AI Powered Event Discovery")
    logger.info("="*60)
    logger.info(f"Environment: {settings.app.environment}")
    logger.info(f"Log Level: {settings.app.log_level}")

    # Test database connection
    logger.info("Testing database connection...")
    if db_connection.health_check():
        logger.info("✓ Database connection successful")

        # Get and display stats
        stats = db_connection.get_stats()
        logger.info(f"Database Stats: {stats}")

        # Create indexes
        logger.info("Creating database indexes...")
        db_connection.create_indexes()
        logger.info("✓ Database indexes created")
    else:
        logger.error("✗ Database connection failed")
        logger.error("Please ensure FalkorDB is running: docker-compose up -d")
        sys.exit(1)


def main():
    """Main application entry point."""
    try:
        initialize_app()

        logger.info("\n" + "="*60)
        logger.info("Application initialized successfully!")
        logger.info("="*60)
        logger.info("\nNext steps:")
        logger.info("1. Configure your .env file with API keys")
        logger.info("2. Run scrapers: scrapy crawl biletix")
        logger.info("3. View results in FalkorDB")
        logger.info("\nFor help, see: README.md")

    except KeyboardInterrupt:
        logger.info("\nApplication interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.exception(f"Fatal error: {e}")
        sys.exit(1)
    finally:
        logger.info("Cleaning up...")


if __name__ == "__main__":
    main()
