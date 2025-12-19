
import asyncio
import argparse
import sys
from loguru import logger
from src.services.linker import EventLinker

# Configure logger
logger.remove()
logger.add(sys.stderr, level="INFO")

async def main():
    parser = argparse.ArgumentParser(description="Link duplicate events in the Knowledge Graph.")
    parser.add_argument("--dry-run", action="store_true", help="Find matches without creating relationships.")
    parser.add_argument("--threshold", type=float, default=0.85, help="Similarity threshold (0.0 - 1.0).")
    
    args = parser.parse_args()

    logger.info("Starting Event Resolution...")
    logger.info(f"Mode: {'DRY RUN' if args.dry_run else 'LIVE'}")
    logger.info(f"Similarity Threshold: {args.threshold}")

    linker = EventLinker(check_score_threshold=args.threshold)
    
    try:
        stats = await linker.link_duplicates(dry_run=args.dry_run)
        
        logger.info("-" * 40)
        logger.info("✅ Linking Complete")
        logger.info(f"Groups Analyzed: {stats['groups_checked']}")
        logger.info(f"Matches Found:   {stats['links_found']}")
        logger.info(f"Links Created:   {stats['links_created']}")
        logger.info("-" * 40)

    except Exception as e:
        logger.exception(f"Detailed Error: {e}")
        logger.error(f"Failed to link events: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
