#!/usr/bin/env python3
"""
Interactive Event Assistant CLI.
"""
import sys
import asyncio
import argparse
from loguru import logger

# Disable aggressive logging for CLI experience
logger.remove()
logger.add(sys.stderr, level="ERROR")

from src.ai.assistant import EventAssistant, CATEGORIES


async def main():
    parser = argparse.ArgumentParser(description="Event Assistant")
    parser.add_argument("query", type=str, nargs="?", help="Initial query")
    args = parser.parse_args()

    print("\n👋 Hi! I'm your Event AI. I can help you find events, plan dates, or discover hidden gems.")
    print("   Type 'exit' or 'quit' to stop.\n")

    assistant = EventAssistant()

    # If initial query provided, process it first
    initial_query = args.query

    while True:
        if initial_query:
            query = initial_query
            initial_query = None  # Clear after first run
        else:
            try:
                query = input("\n>> What are you looking for? ").strip()
            except (KeyboardInterrupt, EOFError):
                print("\n👋 Goodbye!")
                break

        if not query:
            continue

        if query.lower() in ["exit", "quit", "q"]:
            print("👋 Goodbye!")
            break

        print(f"🤔 Thinking...")

        # 1. Identify Intent (Collection vs Search)
        intent = await assistant.identify_intent(query)

        if intent and intent != "search":
            # Handle Collection
            cat_name = CATEGORIES.get(intent, intent)
            print(f"💡 Found a curated collection: {cat_name}\n")

            events = await assistant.get_collection(intent)
            if not events:
                print("❌ No events found in this collection.")
            else:
                for e in events:
                    print(f"📍 {e['title']}")
                    print(f"   🏠 {e['venue']} | 🗓️ {e['date']} | 💰 {e['price']}")
                    print(f"   🏆 {e['reason']}")
                    if e.get("summary"):
                        print(f"   📝 {e['summary']}")
                    print("-" * 60)
        else:
            # Handle Search (Hybrid + RAG)
            # 1. Search
            results = await assistant.search(query)

            # 2. Generate Answer
            answer = await assistant.generate_answer(query, results)

            print(f"\n🤖 {answer}\n")

            if results:
                print("📚 Source Events:")
                print("-" * 60)
                # Fetch details for display
                for score, summary in results[:5]:
                    details = await assistant._fetch_event_details(summary.event_uuid)
                    if details:
                        print(f"📍 {details['title']}")
                        print(f"   🏠 {details['venue']} | 🗓️ {details['date']} | 💰 {details['price']}")
                        print(f"   Match: {int(score*100)}%")
                        print("-" * 60)
            else:
                print("❌ No matching events found.")


if __name__ == "__main__":
    asyncio.run(main())
