
import asyncio
from src.models.event import EventNode
from loguru import logger

async def main():
    events = await EventNode.get_all_events(limit=20)
    for e in events:
        desc_len = len(e.description) if e.description else 0
        logger.info(f"Event: {e.title[:30]}... | Desc Len: {desc_len}")
        if desc_len > 0:
            logger.info(f"Sample: {e.description[:100]}...")

if __name__ == "__main__":
    asyncio.run(main())
