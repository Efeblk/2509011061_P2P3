#!/usr/bin/env python3
"""
Quick check script - works without dependencies.
Shows if scraping worked and what's in database.
"""

import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

print("=" * 60)
print("EventGraph - Quick Check")
print("=" * 60)
print()

# Check if dependencies are installed
try:
    import redis
    from falkordb import FalkorDB
    print("✅ Dependencies installed")
except ImportError as e:
    print("❌ Dependencies not installed!")
    print(f"   Missing: {e}")
    print()
    print("Please run:")
    print("  source venv/bin/activate")
    print("  make install")
    sys.exit(1)

# Check database connection
try:
    client = redis.Redis(host='localhost', port=6379, decode_responses=True)
    client.ping()
    print("✅ Database connected")
except Exception as e:
    print(f"❌ Database connection failed: {e}")
    print()
    print("Please start database:")
    print("  docker compose up -d falkordb")
    sys.exit(1)

# Query database
try:
    db = FalkorDB(host='localhost', port=6379)
    graph = db.select_graph('eventgraph')

    # Count events
    result = graph.query("MATCH (e:Event) RETURN count(e) as count")
    count = result.result_set[0][0] if result.result_set else 0

    print(f"📊 Events in database: {count}")
    print()

    if count == 0:
        print("⚠️  No events found!")
        print()
        print("This could mean:")
        print("  1. Scraper hasn't run yet - run: make scrape")
        print("  2. Scraper ran but couldn't extract data (website structure changed)")
        print("  3. All events were filtered out as duplicates")
        print()
        print("Check scraper logs to see what happened")
    else:
        # Get all events
        result = graph.query("MATCH (e:Event) RETURN e.title, e.venue, e.price, e.source LIMIT 10")

        print("📋 Events found:")
        print("-" * 60)

        if result.result_set:
            for i, row in enumerate(result.result_set, 1):
                title = row[0] or "Unknown"
                venue = row[1] or "N/A"
                price = row[2] or "N/A"
                source = row[3] or "N/A"

                print(f"\n{i}. {title}")
                print(f"   Venue: {venue}")
                print(f"   Price: {price} TL")
                print(f"   Source: {source}")

        print()
        print("-" * 60)
        print(f"Total: {count} events")

except Exception as e:
    print(f"❌ Error querying database: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()
print("=" * 60)
