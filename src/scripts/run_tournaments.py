#!/usr/bin/env python3
"""
Run AI Tournaments to generate curated collections.
"""
import asyncio
from loguru import logger
from src.ai.tournament import run_tournament

TOURNAMENTS = [
    {
        "slug": "best-value",
        "name": "Best Value Events",
        "criteria": "High quality events with reasonable or low ticket prices. Focus on 'bang for your buck'. Avoid very expensive VIP events unless the value is extraordinary."
    },
    {
        "slug": "date-night",
        "name": "Perfect Date Night",
        "criteria": "Romantic, intimate, or impressive atmosphere. Good for couples. Acoustic concerts, jazz, theater, or unique cultural experiences. Avoid loud/aggressive settings."
    },
    {
        "slug": "hidden-gems",
        "name": "Hidden Gems",
        "criteria": "High quality but less mainstream. Unique venues, emerging artists, or niche genres that deserve more attention. 'I saw them before they were famous' vibes."
    },
    {
        "slug": "this-weekend",
        "name": "Top Picks This Weekend",
        "criteria": "The absolute best events happening this coming weekend (Friday-Sunday). diverse mix of genres."
    }
]

import argparse

async def main():
    parser = argparse.ArgumentParser(description="Run AI Tournaments")
    parser.add_argument("--limit", type=int, default=1000, help="Max candidates per tournament")
    parser.add_argument("--dry-run", action="store_true", help="Simulate without API calls")
    args = parser.parse_args()

    logger.info(f"🚀 Starting AI Summarization Tournaments (Limit: {args.limit}, Dry Run: {args.dry_run})...")
    
    for t in TOURNAMENTS:
        logger.info(f"\n>>> Running Tournament: {t['name']}")
        await run_tournament(t['slug'], t['name'], t['criteria'], dry_run=args.dry_run, candidate_limit=args.limit)
        
    logger.info("\n✅ All Tournaments Complete.")

if __name__ == "__main__":
    from src.database.connection import db_connection
    # Ensure DB is connected
    # db_connection.connect() # Removed explicit connect as per fix
    
    asyncio.run(main())
