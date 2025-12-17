#!/usr/bin/env python3
"""
Enrich venues with AI intelligence (Indoors/Outdoors, Vibe).
Iterates over all unique venues found in Event nodes and creates/enriches VenueNodes.
"""

import asyncio
from loguru import logger
from src.database.connection import db_connection
from src.services.venue_enricher import VenueEnricher

async def main():
    logger.info("🏟️  Starting venue enrichment...")
    
    # 1. Get all unique venues from events
    query = "MATCH (e:Event) WHERE e.venue IS NOT NULL AND e.venue <> '' RETURN DISTINCT e.venue as venue_name"
    results = db_connection.execute_query(query)
    
    if not results or not results.result_set:
        logger.warning("No venues found in events.")
        return

    venue_names = [r[0] for r in results.result_set]
    logger.info(f"Found {len(venue_names)} unique venues in events.")
    
    enricher = VenueEnricher()
    
    # 2. Process each venue
    enriched_count = 0
    for name in venue_names:
        try:
            # This will create it if missing, and enrich it if new
            # If it already exists, it returns it (we assume existing ones are enriched or we can force update later)
            venue = await enricher.get_or_create_venue(name)
            if venue.is_outdoors is not None: # Check if it has data
                 enriched_count += 1
        except Exception as e:
            logger.error(f"Error processing venue '{name}': {e}")
            
    logger.info(f"✅ Venue enrichment complete. Verified {enriched_count} venues.")

if __name__ == "__main__":
    asyncio.run(main())
