#!/usr/bin/env python3
"""
Enrich events with entities (Person).
Iterates over events and uses EntityExtractor to find people and create relationships.
"""

import asyncio
import argparse
import sys
from loguru import logger
from tqdm.asyncio import tqdm

from src.models.event import EventNode
from src.services.entity_extractor import EntityExtractor
from config.settings import settings


async def enrich_single_event(extractor, event, semaphore):
    """Enrich a single event with concurrency control."""
    async with semaphore:
        try:
            await extractor.extract_and_link(event)
        except Exception as e:
            logger.error(f"Failed to enrich event {event.uuid}: {e}")


async def main():
    parser = argparse.ArgumentParser(description="Enrich events with entities")
    parser.add_argument("--limit", type=int, default=1000, help="Number of events to process")
    parser.add_argument("--concurrency", type=int, default=10, help="Concurrent requests limit")
    args = parser.parse_args()

    logger.info(f"🕸️  Starting entity enrichment (Knowledge Graph) with limit={args.limit}...")

    # Get all events
    # For now, let's limit to events that have descriptions but might not be enriched
    events = await EventNode.get_all_events(limit=args.limit)  # Process a batch

    if not events:
        logger.warning("No events found.")
        return

    logger.info(f"Found {len(events)} events. Extracting entities with concurrency={args.concurrency}...")

    extractor = EntityExtractor()
    semaphore = asyncio.Semaphore(args.concurrency)

    # Create tasks for all events
    tasks = [enrich_single_event(extractor, event, semaphore) for event in events]

    # Execute with progress bar
    await tqdm.gather(*tasks, desc="Enriching Entities")

    logger.info("✅ Entity enrichment complete.")


if __name__ == "__main__":
    asyncio.run(main())
