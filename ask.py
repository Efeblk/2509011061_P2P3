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

from src.ai.gemini_client import GeminiClient
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
    client = GeminiClient(model_name=settings.ai.model_fast) # Use Flash
    
    prompt = f"""
    You are an intent classifier for an event recommendation engine.
    
    Available Categories:
    1. best-value (cheap, good deals, bang for buck)
    2. date-night (romantic, couple, impressive)
    3. hidden-gems (underground, cool, unique, unknown)
    4. this-weekend (general best, popular, weekend)

    User Query: "{query}"

    Task: Return ONLY the exact category slug from the list above that best matches. 
    If nothing matches well, default to 'this-weekend'.
    Output JUST the slug.
    """
    
    try:
        response = await client.generate(prompt)
        slug = response.strip().lower()
        if slug in CATEGORIES:
            return slug
        return "this-weekend"
    except Exception as e:
        # Fallback if AI fails
        return "this-weekend"

async def main():
    parser = argparse.ArgumentParser(description="Ask for event recommendations")
    parser.add_argument("query", type=str, nargs="?", help="Your question (e.g. 'Where can I go on a date?')")
    args = parser.parse_args()

    if not args.query:
        print("\n👋 Hi! I'm your Event AI. Ask me anything like:")
        print("   - 'Plan a date night for me'")
        print("   - 'What's cool and cheap?'")
        print("   - 'Show me hidden gems'")
        print("   - 'What's on this weekend?'\n")
        
        # Interactive mode
        try:
            query = input(">> What are you looking for? ")
        except KeyboardInterrupt:
            return
    else:
        query = args.query

    print(f"\n🤔 Thinking... ('{query}')")
    
    # 1. Route Intent
    category_slug = await identify_intent(query)
    category_name = CATEGORIES.get(category_slug, "Top Picks")
    
    print(f"💡 Aha! You want: {category_slug} ({category_name})")
    print(f"📚 Fetching curated collection from database...\n")

    # 2. Fetch Data
    try:
        # DB connection is auto-initialized on import
        
        # Cypher to get events in the collection, ordered by rank
        query_cypher = """
        MATCH (c:Collection {category: $cat})-[r:CONTAINS]->(e:Event)
        RETURN e.title as title, 
               e.venue as venue, 
               e.date as date, 
               e.price as price, 
               r.reason as reason, 
               r.rank as rank
        ORDER BY r.rank ASC
        LIMIT 5
        """
        
        # FalkorDB query is synchronous
        result = db_connection.graph.query(query_cypher, {"cat": category_slug})
        
        if not result.result_set:
            print("❌ No events found in this collection. (Has the tournament run?)")
            return

        print(f"🎉 Here are the Top 5 {category_name}:\n")
        
        for row in result.result_set:
            # row is [title, venue, date, price, reason, rank]
            title = row[0]
            venue = row[1]
            date = row[2]
            price = row[3]
            reason = row[4]
            # rank = row[5]

            print(f"📍 {title}")
            print(f"   🏠 {venue} | 🗓️ {date} | 💰 {price}")
            print(f"   🤖 AI: {reason}")
            print("-" * 60)
            
        print("\n✨ Enjoy!")

    except Exception as e:
        print(f"❌ Error fetching results: {e}")

if __name__ == "__main__":
    asyncio.run(main())
