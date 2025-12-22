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
from src.ai.schemas import RerankResponse
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
        from src.ai.schemas import IntentResponse, EventIntent

        # Simple keyword shortcuts removed to prevent false positives for specific queries.
        # We rely on the LLM to decide if it's a general intent or a specific search.

        # Fallback to AI for ambiguous queries
        prompt = f"""
        You are an intent classifier.
        
        Query: "{query}"
        
        Identify the user's PRIMARY intent.
        
        Available Intents:
        - best-value: Vague/general request for cheap/good value events.
        - date-night: Vague/general request for romantic spots.
        - this-weekend: General request for weekend plans.
        - hidden-gems: General request for unique/niche events.
        - search: SPECIFIC request matching a genre, artist, venue, or subject (e.g. "Jazz", "Stand-up", "Rock").

        CRITICAL RULE: 
        If the query specifies a GENRE (Jazz, Rock, Comedy), ARTIST, or TOPIC... ALWAYS classify as SEARCH.
        Even if they mention "value" or "date", if there is a specific subject like "Jazz", it is a SEARCH.

        Examples:
        - "I want cheap events" -> best-value
        - "Cheap Jazz concerts" -> search (Because "Jazz" is specific)
        - "Romantic dinner" -> date-night
        - "Romantic comedy play" -> search (Because "comedy play" is specific)
        """

        try:
            response = await self.client.generate_json(prompt, temperature=0.1, schema=IntentResponse)
            if not response:
                return None

            intent = response.get("intent")
            
            if intent == EventIntent.SEARCH:
                return None
            
            return intent

        except Exception as e:
            logger.error(f"Intent classification failed: {e}")
            return None

    async def extract_filters(self, query: str) -> Dict[str, Any]:
        """
        Extracts structured filters from natural language query.
        """
        from datetime import datetime
        from src.ai.schemas import SearchFilters

        today = datetime.now().strftime("%Y-%m-%d")
        day_name = datetime.now().strftime("%A")

        prompt = f"""
        You are a smart query parser. Extract search filters from the user's query into JSON.
        
        Current Date: {today} ({day_name})
        
        Query: "{query}"
        
        Rules:
        1. max_price: Extract number if user mentions price/budget.
        2. city: Extract city name.
        3. category: Extract event type (e.g. "Jazz", "Theater").
        4. genre: Extract genre. IMPORTANT: Translate common genres to Turkish if possible (e.g. "Comedy" -> "Komedi", "Stand up" -> "Stand up", "Concert" -> "Konser", "Theater" -> "Tiyatro").
        5. duration: Extract duration.
        6. date_range: Calculate start/end dates.
        
        Constraints:
        - Only set fields that are EXPLICITLY mentioned in the query.
        - Do not guess or hallucinate values.
        - If a field is not mentioned, it MUST be skipped or null.

        Examples:
        - "Jazz in Istanbul" -> {{"city": "İstanbul", "category": "Caz"}}
        - "Cheap events" -> {{"max_price": 500}} (implied budget)
        - "Rock concerts under 1000TL" -> {{"category": "Konser", "genre": "Rock", "max_price": 1000}}
        """

        try:
            # Use reasoning client for better instruction following
            response = await self.reasoning_client.generate_json(prompt, schema=SearchFilters)
            if not response:
                return {}

            # Clean up None values
            filters = {k: v for k, v in response.items() if v is not None}
            
            # Flatten date_range if present
            if filters.get("date_range"):
                dr = filters["date_range"]
                # Pydantic model dump might return dict or object, ensure it's dict
                if hasattr(dr, "model_dump"):
                    filters["date_range"] = dr.model_dump()
                
                # Remove if empty
                if not filters["date_range"].get("start") and not filters["date_range"].get("end"):
                    del filters["date_range"]

            return filters
        except Exception as e:
            logger.error(f"Filter extraction failed: {e}")
            return {}

    async def search(self, query: str) -> List[Tuple[float, Any, Dict]]:
        """
        Perform hybrid search:
        1. Extract filters (price, date, city).
        2. Filter candidates via Cypher.
        3. Rank candidates via Vector Search.
        """
        logger.info(f"Searching for: {query}")
        
        # 1. Extract Filters
        filters = await self.extract_filters(query)

        # 2. Build Cypher Filter Query
        cypher_where = []
        params = {}

        if filters.get("max_price"):
            cypher_where.append("e.price <= $max_price")
            params["max_price"] = filters["max_price"]

        if filters.get("city"):
            cypher_where.append("toLower(e.city) CONTAINS toLower($city)")
            params["city"] = filters["city"]

        if filters.get("category"):
            cypher_where.append("toLower(e.category) CONTAINS toLower($category)")
            params["category"] = filters["category"]

        if filters.get("genre"):
            cypher_where.append("toLower(e.genre) CONTAINS toLower($genre)")
            params["genre"] = filters["genre"]

        if filters.get("duration"):
            # Duration is string (e.g. "120 dakika"), simple contains search
            cypher_where.append("toLower(e.duration) CONTAINS toLower($duration)")
            params["duration"] = filters["duration"]

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

        # 4. Vector Search (Database or Hybrid)
        results = []
        semantic_candidates = []

        try:
            # Try Database Vector Search first
            # Syntax: CALL db.idx.vector.queryNodes('AISummary', 'embedding', $k, $vec) YIELD node, score
            # We fetch more than needed (20) to allow for re-ranking
            logger.info("Attempting Database Vector Search...")
            k_neighbors = 20
            
            # Note: We use vecf32() to cast the list to a vector
            vec_query = "CALL db.idx.vector.queryNodes('AISummary', 'embedding', $k, vecf32($vec)) YIELD node, score RETURN node, score"
            vec_params = {'k': k_neighbors, 'vec': query_vec}
            
            res = db_connection.execute_query(vec_query, vec_params)
            
            if res and res.result_set:
                logger.info(f"Database Vector Search returned {len(res.result_set)} results.")
                for row in res.result_set:
                    node_data = row[0] # Node object or node properties
                    score = row[1]
                    
                    # Parse Node Data
                    summary_node = None
                    if hasattr(node_data, 'properties'):
                        # FalkorDB Node object
                        summary_node = AISummaryNode(**node_data.properties)
                        # Fix types if needed (embedding extraction might be string)
                    else:
                        # Assuming dict/map
                        # Only applicable if using older client or weird response
                        pass # TODO: Robust parsing
                        
                    if summary_node:
                        # Filter by Cypher constraints if strictly required?
                        # Vector search is approximate. If we have HARD filters (city, date), 
                        # we should intersect candidate_uuids.
                        if candidate_uuids is not None and summary_node.event_uuid not in candidate_uuids:
                            continue
                            
                        results.append((score, summary_node))

            else:
                logger.warning("Database Vector Search returned empty.")
        
        except Exception as e:
            logger.warning(f"Database Vector Search failed ({e}).")

        # Fallback if no results from DB
        if not results:
            logger.info("Falling back to In-Memory Search.")
            # --- Fallback: In-Memory Search ---
            summaries = await AISummaryNode.get_all_summaries(limit=5000)
            logger.info(f"Fallback: Checking {len(summaries)} summaries...")
            for s in summaries:
                # Filter first
                if candidate_uuids is not None and s.event_uuid not in candidate_uuids:
                    continue
                if not s.embedding:
                    continue

                try:
                    vec = s.get_embedding_vector()
                    if not vec: continue
                    
                    # Ensure it's not a string
                    if isinstance(vec, str):
                         vec = json.loads(vec)

                    # Cosine Similarity
                    score = np.dot(query_vec, vec) / (np.linalg.norm(query_vec) * np.linalg.norm(vec))
                    if score > 0.3: # Lower threshold for debug
                        results.append((score, s))
                except Exception as ex:
                    # logger.warning(f"Math error in fallback: {ex}")
                    continue
            logger.info(f"Fallback: Found {len(results)} matches.")
            # ----------------------------------

        # 5. Sort & Top K
        results.sort(key=lambda x: x[0], reverse=True)
        top_candidates = results[:20] # Take top 20 for re-ranking

        # 6. Re-ranking (LLM Judge)
        # We verify if the event ACTUALLY matches the user query intent beyond keywords.
        final_results = []
        
        # Determine if re-ranking is needed (optimization: skip for simple queries?)
        # For now, always re-rank to ensure quality.
        
        # Prepare candidates for LLM
        # We need event details for the LLM to judge properly
        candidate_details = []
        for score, s in top_candidates:
            details = await self._fetch_event_details(s.event_uuid)
            if details:
                candidate_details.append({
                    "id": s.event_uuid,
                    "title": details['title'],
                    "summary": s.sentiment_summary,
                    "score": score,
                    "summary_obj": s,
                    "details_obj": details
                })

        if candidate_details:
            logger.info(f"Re-ranking {len(candidate_details)} candidates...")
            reranked = await self._rerank_results(query, candidate_details)
            
            # --- DEDUPLICATION LOGIC ---
            grouped_results = {}
            for score, summary_obj, details_obj in reranked:
                key = (details_obj['title'], details_obj.get('venue', ''))
                
                if key not in grouped_results:
                    # New group
                    grouped_results[key] = {
                        "score": score,
                        "summary": summary_obj,
                        "details": details_obj,
                        "dates": [details_obj.get('date')] if details_obj.get('date') else []
                    }
                else:
                    # Existing group - merge
                    group = grouped_results[key]
                    group['score'] = max(group['score'], score) # Best score
                    if details_obj.get('date'):
                         group['dates'].append(details_obj.get('date'))
            
            # Flatten back to list
            final_results_with_details = []
            for item in grouped_results.values():
                d = item['details']
                # clean duplicate dates
                unique_dates = sorted(list(set([x for x in item['dates'] if x])))
                d['dates'] = unique_dates
                
                final_results_with_details.append((
                    item['score'],
                    item['summary'],
                    d
                ))
                
            # Re-sort by score
            final_results_with_details.sort(key=lambda x: x[0], reverse=True)
        else:
            final_results_with_details = []

        return final_results_with_details[:10]

    async def generate_answer(self, query: str, top_results: List[Tuple[float, Any, Dict]]) -> str:
        """
        Generates a conversational answer based on search results (RAG).
        """
        if not top_results:
            return "I couldn't find any events matching your request."

        # Fetch details for context
        events_context = []
        for score, summary, details in top_results[:5]:  # Use top 5 for context, unpack triplet
            if details:
                # Handle grouped dates if present
                date_str = details['date']
                if "dates" in details and len(details["dates"]) > 1:
                     sorted_dates = sorted(details["dates"])
                     date_str = f"{sorted_dates[0]} to {sorted_dates[-1]} ({len(sorted_dates)} shows)"

                events_context.append(
                    f"- {details['title']} @ {details['venue']} ({date_str}, {details['price']} TL): {summary.sentiment_summary}"
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
        query = "MATCH (e:Event {uuid: $uuid}) RETURN e.title, e.venue, e.date, e.price, e.city, e.genre, e.duration"
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
                    "genre": row[5],
                    "duration": row[6],
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

    async def _rerank_results(self, query: str, candidates: List[Dict[str, Any]]) -> List[Tuple[float, Any, Dict]]:
        """
        Re-ranks candidates using LLM to filter irrelevant vector matches.
        """
        if not candidates:
            return []

        # Prepare context for LLM
        # We only send minimal info to keep tokens low
        docs = []
        for i, c in enumerate(candidates):
            docs.append(f"ID {i}: {c['title']} - {c['summary']}")
        
        docs_str = "\n".join(docs)

        prompt = f"""
        Rank the following events based on relevance to the user query.
        
        Query: "{query}"
        
        Events:
        {docs_str}
        
        Task:
        1. Identify events that are RELEVANT to the query.
        2. Assign a relevance score (0.0 to 1.0).
        3. Explain logic briefly.
        
        Return JSON list:
        [{{ "id": 0, "score": 0.9, "reason": "Exact match" }}, ...]
        
        Filter out events with score < 0.4.
        Sort by score descending.
        """

        try:
            # Use reasoning client (Gemini/Mistral)
            from src.ai.schemas import RerankResponse
            response = await self.reasoning_client.generate_json(prompt, schema=RerankResponse)
            
            if not response or "results" not in response:
                # Fallback: maintain original order
                logger.warning("Re-ranking failed format, using original order.")
                # Convert back to tuple format
                return [(c['score'], c['summary_obj'], c['details_obj']) for c in candidates]

            # Process AI rankings
            final_results = []
            
            # Map ID back to candidate
            # response['results'] is list of {id, score}
            for res in response['results']:
                idx = res.get("id")
                score = res.get("score", 0)
                if idx is not None and 0 <= idx < len(candidates) and score >= 0.4:
                    cand = candidates[idx]
                    # Update summary/reason if desired, but here we just re-score
                    final_results.append((score, cand['summary_obj'], cand['details_obj']))
            
            # If AI filtered everything (rare), fallback to top 3 original
            if not final_results:
                logger.warning("Re-ranking filtered all results! Fallback to top 3.")
                return [(c['score'], c['summary_obj'], c['details_obj']) for c in candidates[:3]]

            return final_results

        except Exception as e:
            logger.error(f"Re-ranking error: {e}")
            # Fallback
            return [(c['score'], c['summary_obj'], c['details_obj']) for c in candidates]
