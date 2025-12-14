#!/usr/bin/env python3
"""
CLI Tool to ask for event recommendations.
Routes queries to the appropriate pre-computed Collection using AI.
"""
import sys
import os
import asyncio
import argparse
from typing import Optional
from loguru import logger

from src.ai.enrichment import get_ai_client
from config import settings
from src.database.connection import db_connection
from src.models.collection import CollectionNode

# Disable aggressive logging for CLI experience
logger.remove()
logger.add(sys.stderr, level="ERROR")

CATEGORIES = {
    "best-value": "High quality events with great value for money.",
    "date-night": "Romantic, intimate, impressive date spots.",
    "hidden-gems": "Unique, niche, off-the-beaten-path cool events.",
    "this-weekend": "The absolute best things happening this upcoming weekend."
}

async def identify_intent(query: str) -> Optional[str]:
    """Classifies user query into one of the known categories."""
    
    # Simple keyword shortcuts for speed/cost
    q = query.lower()
    if "date" in q or "romantic" in q: return "date-night"
    if "weekend" in q: return "this-weekend"
    if "cheap" in q or "value" in q or "budget" in q: return "best-value"
    if "hidden" in q or "unique" in q or "niche" in q: return "hidden-gems"

    # Fallback to AI for ambiguous queries
    # Use fast model (local or cloud)
    client = get_ai_client(use_reasoning=False)
    
    prompt = f"""
    You are an intent classifier.
    
    Categories:
    - best-value
    - date-night
    - hidden-gems
    - this-weekend
    - search (use this for specific topics like 'jazz', 'mozart', 'workshops', 'cinema')
    
    Query: "{query}"
    
    Task: Return ONLY the category slug. 
    If the query is for a specific topic rather than a vibe, return "search".
    """
    
    try:
        response = await client.generate(prompt, temperature=0.1)
        if not response:
            return None
            
        # Clean response (local models can be chatty)
        slug = response.strip().lower()
        
        # Extract slug if embedded in text
        for cat in CATEGORIES:
            if cat in slug:
                return cat
                
        if "search" in slug:
            return None
            
        if slug in CATEGORIES:
            return slug
            
        return None # Trigger search
    except Exception as e:
        # Fallback if AI fails
        return None

from src.models.ai_summary import AISummaryNode
import numpy as np
import json

async def search_events(query: str):
    """Perform semantic search using vector embeddings."""
    print(f"🔎 No category matched. Searching for '{query}'...")
    
    # 1. Embed Query
    client = get_ai_client(use_reasoning=False)
    query_vec = client.embed(query)
    
    if not query_vec:
        print("❌ Could not generate embedding for query.")
        return

    # 2. Fetch All Summaries (with embeddings)
    # Note: In production, use a Vector DB index. For <10k events, in-memory is fine.
    summaries = await AISummaryNode.get_all_summaries(limit=5000)
    
    results = []
    
    for s in summaries:
        if not s.embedding:
            continue
            
        try:
            vec = json.loads(s.embedding)
            # Cosine Similarity
            score = np.dot(query_vec, vec) / (np.linalg.norm(query_vec) * np.linalg.norm(vec))
            results.append((score, s))
        except Exception:
            continue
            
    # 3. Sort and Show
    results.sort(key=lambda x: x[0], reverse=True)
    top_results = results[:5]
    
    if not top_results:
        print("❌ No matching events found.")
        return
        
    print(f"🎉 Found {len(top_results)} matches:\n")
    
    from src.models.event import EventNode
    
    for score, summary in top_results:
        # Fetch event details
        # We need a way to get event by UUID efficiently, or just trust the summary?
        # Summary doesn't have title/venue/date/price directly stored as props in Node object (it does in DB)
        # But AISummaryNode object has them if we fetched them? No, it only has summary props.
        # We need to fetch the event.
        
        # Quick hack: Fetch event by UUID
        # Ideally we'd do a JOIN in Cypher, but we are doing Python-side vector search.
        query_cypher = "MATCH (e:Event {uuid: $uuid}) RETURN e.title, e.venue, e.date, e.price"
        res = db_connection.graph.query(query_cypher, {"uuid": summary.event_uuid})
        
        if res.result_set:
            row = res.result_set[0]
            title = row[0]
            venue = row[1]
            date = row[2]
            price = row[3]
            
            print(f"📍 {title}")
            print(f"   🏠 {venue} | 🗓️ {date} | 💰 {price}")
            print(f"   🤖 Match: {int(score*100)}% | {summary.sentiment_summary}")
            print("-" * 60)

async def main():
    parser = argparse.ArgumentParser(description="Ask for event recommendations")
    parser.add_argument("query", type=str, nargs="?", help="Your question (e.g. 'Where can I go on a date?')")
    args = parser.parse_args()

    if not args.query:
        print("\n👋 Hi! I'm your Event AI. Ask me anything like:")
        print("   - 'Plan a date night for me'")
        print("   - 'What's cool and cheap?'")
        print("   - 'Show me hidden gems'")
        print("   - 'Any jazz concerts this week?'\n")
        
        try:
            query = input(">> What are you looking for? ")
        except KeyboardInterrupt:
            return
    else:
        query = args.query

    print(f"\n🤔 Thinking... ('{query}')")
    
    # 1. Route Intent
    category_slug = await identify_intent(query)
    
    if category_slug and category_slug != "search":
        category_name = CATEGORIES.get(category_slug, "Top Picks")
        print(f"💡 Aha! You want: {category_slug} ({category_name})")
        print(f"📚 Fetching curated collection from database...\n")

        # 2. Fetch Data (Collection)
        try:
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
            
            result = db_connection.graph.query(query_cypher, {"cat": category_slug})
            
            if not result.result_set:
                print("❌ No events found in this collection. (Has the tournament run?)")
                return

            print(f"🎉 Here are the Top 5 {category_name}:\n")
            
            for row in result.result_set:
                title = row[0]
                venue = row[1]
                date = row[2]
                price = row[3]
                reason = row[4]
                summary = row[6]

                print(f"📍 {title}")
                print(f"   🏠 {venue} | 🗓️ {date} | 💰 {price}")
                print(f"   🏆 Why: {reason}")
                if summary:
                    print(f"   📝 Summary: {summary}")
                print("-" * 60)
                
            print("\n✨ Enjoy!")

        except Exception as e:
            print(f"❌ Error fetching results: {e}")
            
    else:
        # 3. General Search
        await search_events(query)

if __name__ == "__main__":
    asyncio.run(main())
