#!/usr/bin/env python3
"""
Generate AI summaries for events.

Usage:
    python src/scripts/enrich_events.py              # Process all events without summaries
    python src/scripts/enrich_events.py --limit 10   # Process only 10 events
    python src/scripts/enrich_events.py --all        # Re-process all events (regenerate)
"""

import asyncio
import argparse
from loguru import logger

from src.models.event import EventNode
from src.ai.enrichment import batch_generate_summaries
from config.settings import settings


async def main():
    """Main enrichment script."""
    parser = argparse.ArgumentParser(description="Generate AI summaries for events")
    parser.add_argument("--limit", type=int, help="Limit number of events to process")
    parser.add_argument("--all", action="store_true", help="Re-process all events (regenerate summaries)")
    parser.add_argument("--force", action="store_true", help="Process even low-quality events")
    args = parser.parse_args()

    logger.info("🤖 Starting event enrichment...")

    # Get events to process
    if args.all:
        logger.info("Re-processing ALL events (regenerating summaries)")
        events = await EventNode.get_all_events(limit=args.limit or 10000)
    else:
        logger.info("Processing events without summaries")
        # Default limit increased to cover full dataset (was 100)
        events = await EventNode.get_all_events(limit=args.limit or 10000)

    if not events:
        logger.warning("No events found to process")
        return

    logger.info(f"Found {len(events)} events to process")

    # Generate summaries
    results = await batch_generate_summaries(
        events, 
        delay=settings.ai.rate_limit_delay, 
        force=args.force,
        overwrite=args.all
    )

    # Summary
    logger.info("\n" + "=" * 50)
    logger.info("📊 ENRICHMENT COMPLETE")
    logger.info("=" * 50)
    logger.info(f"✓ Success: {results['success']}")
    logger.info(f"✗ Failed (API errors): {results['failed']}")
    logger.info(f"⊘ Already had summaries: {results['skipped']}")
    logger.info(f"⊘ Skipped (low quality, no content): {results.get('skipped_low_quality', 0)}")
    logger.info(f"Total processed: {sum(results.values())}")

    if results['failed'] > 0:
        logger.warning("\n⚠️  Some events failed to generate summaries.")
        logger.warning("Common causes:")
        logger.warning("  1. Ollama not running or not accessible")
        logger.warning("  2. Model (llama3.2) not installed")
        logger.warning("  3. Ollama connection timeout or network issues")
        logger.warning("\nTroubleshooting:")
        logger.warning("  - Check Ollama status: ollama list")
        logger.warning("  - Start Ollama: ollama serve")
        logger.warning("  - Pull model: ollama pull llama3.2")
        logger.warning("\nTo process low-quality events (no description/reviews), use:")
        logger.warning("  make ai-enrich FORCE=--force")


if __name__ == "__main__":
    asyncio.run(main())
