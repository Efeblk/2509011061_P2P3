"""
Logging configuration for EventGraph.
Uses loguru for advanced logging capabilities.
"""

import sys
from pathlib import Path
from loguru import logger
from config.settings import settings


def setup_logging():
    """
    Configure application logging with loguru.
    Creates both console and file handlers with appropriate formatting.
    """
    # Remove default handler
    logger.remove()

    # Create logs directory if it doesn't exist
    log_path = Path(settings.app.log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    # Console handler with colorized output
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=settings.app.log_level,
        colorize=True,
    )

    # File handler with rotation
    logger.add(
        settings.app.log_file,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level=settings.app.log_level,
        rotation="10 MB",  # Rotate when file reaches 10MB
        retention="1 week",  # Keep logs for 1 week
        compression="zip",  # Compress rotated logs
        enqueue=True,  # Thread-safe logging
    )

    # Add exception catching
    logger.add(
        "logs/errors.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="ERROR",
        rotation="10 MB",
        retention="1 month",
        compression="zip",
        backtrace=True,  # Include traceback
        diagnose=True,  # Include variable values
    )

    logger.info(f"Logging initialized - Level: {settings.app.log_level}, Environment: {settings.app.environment}")

    return logger


# Initialize logging on import
app_logger = setup_logging()
