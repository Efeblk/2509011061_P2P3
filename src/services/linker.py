
import difflib
from datetime import datetime
from typing import List, Dict, Tuple, Set
from loguru import logger
from src.models.event import EventNode
from src.database.connection import db_connection

class EventLinker:
    """
    Service to associate identical events from different sources using fuzzy matching.
    Creates [:SAME_AS] relationships between duplicate event nodes.
    """

    def __init__(self, check_score_threshold: float = 0.85):
        self.threshold = check_score_threshold

    def calculate_similarity(self, s1: str, s2: str) -> float:
        """Calculate normalized similarity score between two strings (0.0 to 1.0)."""
        if not s1 or not s2:
            return 0.0
        return difflib.SequenceMatcher(None, s1.lower(), s2.lower()).ratio()

    async def link_duplicates(self, dry_run: bool = False) -> Dict[str, int]:
        """
        Find and link duplicate events.
        Strategy: Group by (Date, City) -> Compare Titles Fuzzy.
        """
        stats = {"groups_checked": 0, "links_found": 0, "links_created": 0}
        
        # 1. Fetch all events (optimized: could filter by date range in production)
        logger.info("Fetching all events for linking analysis...")
        events = await EventNode.get_all_events(limit=5000)
        
        # 2. Group by Date + City
        grouped_events: Dict[str, List[EventNode]] = {}
        for event in events:
            # Skip if critical metadata missing
            if not event.date or not event.city:
                continue
                
            # Key: YYYY-MM-DD|City (assuming date is ISO)
            key = f"{event.date}|{event.city.lower()}"
            if key not in grouped_events:
                grouped_events[key] = []
            grouped_events[key].append(event)

        logger.info(f"Grouped events into {len(grouped_events)} clusters based on Date/City.")
        stats["groups_checked"] = len(grouped_events)

        # 3. Compare within groups
        for key, group in grouped_events.items():
            if len(group) < 2:
                continue

            # Compare every pair in the group
            checked_pairs = set()
            for i in range(len(group)):
                for j in range(i + 1, len(group)):
                    e1 = group[i]
                    e2 = group[j]
                    
                    # Avoid checking self or already checked (if logic changes)
                    if e1.uuid == e2.uuid:
                        continue
                        
                    # Calculate Title Similarity
                    similarity = self.calculate_similarity(e1.title, e2.title)
                    
                    if similarity >= self.threshold:
                        logger.info(f"🔗 MATCH FOUND ({similarity:.2f}): '{e1.title}' <-> '{e2.title}'")
                        stats["links_found"] += 1
                        
                        if not dry_run:
                            created = await self.create_same_as_link(e1.uuid, e2.uuid, similarity)
                            if created:
                                stats["links_created"] += 1
        
        return stats

    async def create_same_as_link(self, uuid1: str, uuid2: str, score: float) -> bool:
        """Create bidirectional SAME_AS relationship."""
        query = """
        MATCH (e1:Event {uuid: $uuid1}), (e2:Event {uuid: $uuid2})
        MERGE (e1)-[r:SAME_AS]-(e2)
        SET r.score = $score, r.updated_at = $timestamp
        RETURN r
        """
        try:
            # We use MERGE undirected or directed? 
            # In Neo4j/RedisGraph, relationships are directed but can be traversed both ways.
            # MERGE (a)-[:REL]-(b) is safer to avoid duplication if direction doesn't matter.
            res = db_connection.execute_query(query, {
                "uuid1": uuid1, 
                "uuid2": uuid2, 
                "score": score,
                "timestamp": datetime.utcnow().isoformat()
            })
            if res and res.result_set:
                return True
        except Exception as e:
            logger.error(f"Failed to link events {uuid1} <-> {uuid2}: {e}")
        return False
