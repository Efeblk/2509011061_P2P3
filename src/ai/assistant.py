"""
Event Assistant module.
Handles user queries, intent classification, and hybrid search.
"""

import json
import asyncio
from typing import Optional, List, Dict, Any, Tuple
import numpy as np
from loguru import logger

from src.ai.enrichment import get_ai_client
from src.database.connection import db_connection
from src.models.ai_summary import AISummaryNode
from src.models.event import EventNode

CATEGORIES = {
    "best-value": "High quality events with great value for money.",
    "date-night": "Romantic, intimate, impressive date spots.",
    "hidden-gems": "Unique, niche, off-the-beaten-path cool events.",
    "this-weekend": "The absolute best things happening this upcoming weekend.",
}


class EventAssistant:
    """
    AI Assistant for Event Discovery.
    Combines vector search, Cypher queries, and LLM reasoning.
    """

    def __init__(self):
        self.client = get_ai_client(use_reasoning=False)
        self.reasoning_client = get_ai_client(use_reasoning=True)
        self.history = []  # Store conversation history

    async def identify_intent(self, query: str) -> Optional[str]:
        """Classifies user query into one of the known categories."""

        # Simple keyword shortcuts for speed/cost
        q = query.lower()
        if "date" in q or "romantic" in q:
            return "date-night"
        if "weekend" in q:
            return "this-weekend"
        if "cheap" in q or "value" in q or "budget" in q:
            return "best-value"
        if "hidden" in q or "unique" in q or "niche" in q:
            return "hidden-gems"

        # Fallback to AI for ambiguous queries
        prompt = f"""
        You are an intent classifier.
        
        STRICT Categories:
        - best-value: ONLY for "cheap", "budget", "free", "value".
        - date-night: ONLY for "date", "romantic", "couple".
        - this-weekend: ONLY for "weekend", "friday", "saturday", "sunday".
        - hidden-gems: ONLY for "hidden", "secret", "underground".
        
        - search: EVERYTHING ELSE. Use this for specific topics (jazz, kids, workshops, atölye), vibes (dark, happy), or general questions.
        
        Query: "{query}"
        
        Task: Return ONLY the category slug. 
        If in doubt, return "search".
        """

        try:
            response = await self.client.generate(prompt, temperature=0.1)
            if not response:
                return None

            # Clean response
            slug = response.strip().lower()

            # Extract slug if embedded in text
            for cat in CATEGORIES:
                if cat in slug:
                    return cat

            if "search" in slug:
                return None

            # If the query contains specific constraints (price, city, specific topic), prefer search
            # unless it's a very generic "what to do this weekend" query.
            complex_keywords = [
                "istanbul",
                "ankara",
                "tl",
                "concert",
                "jazz",
                "workshop",
                "atölye",
                "sinema",
                "tiyatro",
            ]
            is_complex = any(k in slug for k in complex_keywords) or any(k in query.lower() for k in complex_keywords)

            if is_complex and slug in CATEGORIES:
                # If it matches a category but has specific constraints, force search
                # e.g. "Jazz concerts this weekend" -> should be search, not just generic "this-weekend" collection
                return None

            if slug in CATEGORIES:
                return slug

            return None  # Trigger search
        except Exception as e:
            logger.error(f"Intent classification failed: {e}")
            return None

    async def extract_filters(self, query: str) -> Dict[str, Any]:
        """
        Extracts structured filters from natural language query.
        Returns JSON: {
            "max_price": float | None,
            "city": str | None,
            "date_range": {"start": str, "end": str} | None, # ISO format
            "category": str | None
        }
        """
        from datetime import datetime

        today = datetime.now().strftime("%Y-%m-%d")
        day_name = datetime.now().strftime("%A")

        prompt = f"""
        You are a query parser. Extract filters from the user's search query.
        
        Current Date: {today} ({day_name})
        
        Query: "{query}"
        
        Task: Return a JSON object with these keys (use null if not specified):
        - max_price: number (e.g. 500)
        - city: string (e.g. "Istanbul", "Ankara")
        - category: string (e.g. "Jazz", "Theater", "Workshop")
        - date_range: object with "start" and "end" in YYYY-MM-DD format.
          - "this weekend": next Friday to Sunday.
          - "tomorrow": {today} + 1 day.
          - "next week": next Monday to Sunday.
        
        IMPORTANT:
        - ONLY extract filters explicitly mentioned in the query.
        - If the user does NOT mention a date/time, set date_range to null.
        - If the user does NOT mention a city, set city to null.
        - If the user mentions a city NOT in Turkey (e.g. "Mars", "London"), extract it anyway as "city".
        - Handle Turkish date terms: "hafta sonu" -> "this weekend", "yarın" -> "tomorrow".
        
        Return ONLY valid JSON.
        """

        try:
            # Use reasoning client for better instruction following
            response = await self.reasoning_client.generate_json(prompt)
            if not response:
                return {}

            # Code-level Safeguard: Discard date_range if no date keywords found
            # This prevents "implicit" date filters (hallucinations)
            q_lower = query.lower()
            date_keywords = [
                "today",
                "tomorrow",
                "tonight",
                "weekend",
                "week",
                "month",
                "year",
                "bugün",
                "yarın",
                "akşam",
                "gece",
                "hafta",
                "ay",
                "yıl",
                "monday",
                "tuesday",
                "wednesday",
                "thursday",
                "friday",
                "saturday",
                "sunday",
                "pazartesi",
                "salı",
                "çarşamba",
                "perşembe",
                "cuma",
                "cumartesi",
                "pazar",
                "ocak",
                "şubat",
                "mart",
                "nisan",
                "mayıs",
                "haziran",
                "temmuz",
                "ağustos",
                "eylül",
                "ekim",
                "kasım",
                "aralık",
                "jan",
                "feb",
                "mar",
                "apr",
                "may",
                "jun",
                "jul",
                "aug",
                "sep",
                "oct",
                "nov",
                "dec",
            ]

            has_date_keyword = any(k in q_lower for k in date_keywords)

            # Also check for specific date formats (2024, 12.12, etc)
            import re

            has_date_format = re.search(r"\d{1,2}[./-]\d{1,2}", q_lower) or re.search(r"\d{4}", q_lower)

            if response.get("date_range") and not (has_date_keyword or has_date_format):
                logger.warning(f"Discarding hallucinated date range: {response['date_range']}")
                response["date_range"] = None

            return response
        except Exception as e:
            logger.error(f"Filter extraction failed: {e}")
            return {}

    async def search(self, query: str) -> List[Tuple[float, Any]]:
        """
        Perform hybrid search:
        1. Extract filters (price, date, city).
        2. Filter candidates via Cypher.
        3. Rank candidates via Vector Search.
        """
        logger.info(f"Searching for: {query}")

        # 1. Extract Filters
        filters = await self.extract_filters(query)
        logger.info(f"Extracted filters: {filters}")

        # 2. Build Cypher Filter Query
        cypher_where = []
        params = {}

        if filters.get("max_price"):
            cypher_where.append("e.price <= $max_price")
            params["max_price"] = filters["max_price"]

        if filters.get("city"):
            cypher_where.append("toLower(e.city) CONTAINS toLower($city)")
            params["city"] = filters["city"]

        if filters.get("date_range"):
            dr = filters["date_range"]
            if dr.get("start"):
                cypher_where.append("e.date >= $start_date")
                params["start_date"] = dr["start"]
            if dr.get("end"):
                cypher_where.append("e.date <= $end_date")
                params["end_date"] = dr["end"]

        # If we have filters, get candidate UUIDs
        candidate_uuids = None
        if cypher_where:
            where_clause = " AND ".join(cypher_where)
            query_cypher = f"MATCH (e:Event) WHERE {where_clause} RETURN e.uuid"
            logger.info(f"Cypher Filter: {where_clause}")

            try:
                res = db_connection.execute_query(query_cypher, params)
                if res and res.result_set:
                    candidate_uuids = set(row[0] for row in res.result_set)
                    logger.info(f"Found {len(candidate_uuids)} candidates matching filters.")
                else:
                    logger.warning("No events match the filters.")
                    return []
            except Exception as e:
                logger.error(f"Cypher filter failed: {e}")
                # Fallback to full search? Or return empty?
                # Let's return empty to respect constraints
                return []

        # 3. Embed Query
        query_vec = self.client.embed(query)

        if not query_vec:
            logger.error("Could not generate embedding for query.")
            return []

        # 4. Fetch Summaries & Rank
        # Optimization: If candidate_uuids is small, we could fetch only those.
        # But get_all_summaries is cached/fast enough for now.
        summaries = await AISummaryNode.get_all_summaries(limit=5000)

        results = []

        for s in summaries:
            # Filter by candidates if filters exist
            if candidate_uuids is not None and s.event_uuid not in candidate_uuids:
                continue

            if not s.embedding:
                continue

            try:
                vec = json.loads(s.embedding)
                # Cosine Similarity
                score = np.dot(query_vec, vec) / (np.linalg.norm(query_vec) * np.linalg.norm(vec))

                results.append((score, s))
            except Exception:
                continue

        # 5. Sort
        results.sort(key=lambda x: x[0], reverse=True)
        return results[:10]

    async def generate_answer(self, query: str, top_results: List[Tuple[float, Any]]) -> str:
        """
        Generates a conversational answer based on search results (RAG).
        """
        if not top_results:
            return "I couldn't find any events matching your request."

        # Fetch details for context
        events_context = []
        for score, summary in top_results[:5]:  # Use top 5 for context
            details = await self._fetch_event_details(summary.event_uuid)
            if details:
                events_context.append(
                    f"- {details['title']} @ {details['venue']} ({details['date']}, {details['price']} TL): {summary.sentiment_summary}"
                )

        context_str = "\n".join(events_context)

        # Format history
        history_str = ""
        if self.history:
            history_str = "Conversation History:\n" + "\n".join([f"{role}: {msg}" for role, msg in self.history[-6:]])

        prompt = f"""
        You are a helpful event assistant.
        
        {history_str}
        
        User Query: "{query}"
        
        Found Events:
        {context_str}
        
        Task: Answer the user's query based on these events. 
        - Be conversational and helpful.
        - Recommend specific events from the list.
        - If the user asked for a plan (e.g. "date night"), propose a plan.
        - Mention prices and dates where relevant.
        - Do NOT make up events not in the list.
        - If the user refers to previous events (e.g. "the first one"), use the history to understand context.
        """

        try:
            response = await self.reasoning_client.generate(prompt)
            answer = response or "Here are the events I found."

            # Update history
            self.history.append(("User", query))
            self.history.append(("AI", answer))

            return answer
        except Exception as e:
            logger.error(f"Answer generation failed: {e}")
            return "Here are the events I found."

    async def _fetch_event_details(self, uuid: str) -> Optional[Dict[str, Any]]:
        """Helper to fetch event details by UUID."""
        query = "MATCH (e:Event {uuid: $uuid}) RETURN e.title, e.venue, e.date, e.price, e.city"
        try:
            res = db_connection.execute_query(query, {"uuid": uuid})
            if res and res.result_set:
                row = res.result_set[0]
                return {
                    "title": row[0],
                    "venue": row[1],
                    "date": row[2],
                    "price": row[3],
                    "city": row[4],
                }
            return None
        except Exception:
            return None

    async def get_collection(self, category_slug: str) -> List[Dict[str, Any]]:
        """Fetch events from a curated collection."""
        query_cypher = """
        MATCH (c:Collection {category: $cat})-[r:CONTAINS]->(e:Event)
        OPTIONAL MATCH (e)-[:HAS_AI_SUMMARY]->(s:AISummary)
        RETURN e.title as title, 
               e.venue as venue, 
               e.date as date, 
               e.price as price, 
               r.reason as reason, 
               r.rank as rank,
               s.sentiment_summary as summary
        ORDER BY r.rank ASC
        LIMIT 5
        """

        try:
            res = db_connection.execute_query(query_cypher, {"cat": category_slug})
            results = []
            if res and res.result_set:
                for row in res.result_set:
                    results.append(
                        {
                            "title": row[0],
                            "venue": row[1],
                            "date": row[2],
                            "price": row[3],
                            "reason": row[4],
                            "summary": row[6],
                        }
                    )
            return results
        except Exception as e:
            logger.error(f"Collection fetch failed: {e}")
            return []
