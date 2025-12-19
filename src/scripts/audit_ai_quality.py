#!/usr/bin/env python3
"""
Audit AI Summary Quality.
Analyzes existing summaries for data quality, score distributions, and boilerplate detection.
"""

import asyncio
from loguru import logger
from collections import Counter
from statistics import mean

from src.models.ai_summary import AISummaryNode
from src.database.connection import db_connection


async def main():
    """Run the audit."""
    print("🔎 Auditing AI Summary Quality...\n")

    # Connect DB (implicitly via property access)
    print("✓ Connected to Database")

    # Fetch ALL summaries
    # Note: get_all_summaries limits to 100 by default, we need a custom query for stats
    # to avoid loading 4000 objects into memory if possible, but for analysis objects are fine for now.

    # Let's use a direct Cypher aggregation query for efficiency first
    try:
        # 1. General Stats
        query = """
        MATCH (s:AISummary)
        RETURN count(s) as total, 
               avg(s.quality_score) as avg_score, 
               min(s.quality_score) as min_score, 
               max(s.quality_score) as max_score
        """
        res = db_connection.graph.query(query).result_set[0]
        total, avg_score, min_score, max_score = res

        if total == 0:
            print("⚠️  No AI summaries found in the database.")
            return

        print(f"📊 Total Summaries: {total}")
        print(f"⭐ Average Quality Score: {avg_score:.2f} (Range: {min_score}-{max_score})")

        # 1b. Metadata Coverage Check (Genre/Duration)
        query_meta = """
        MATCH (s:AISummary)<-[:HAS_AI_SUMMARY]-(e:Event)
        WHERE e.genre IS NOT NULL OR e.duration IS NOT NULL
        RETURN count(s) as enriched_summaries
        """
        enriched_count = db_connection.graph.query(query_meta).result_set[0][0]
        print(f"🎭 Summaries with Source Metadata (Genre/Duration): {enriched_count}/{total} ({enriched_count/total*100:.1f}%)")

        # 2. Boilerplate / Low Quality Detection
        # Check for summaries that mention "No content" or "No reviews"
        # We'll need to fetch the actual text for this.
        # Fetching uuid and sentiment_summary is lighter than full objects
        query_text = "MATCH (s:AISummary) RETURN s.sentiment_summary, s.importance"
        res_text = db_connection.graph.query(query_text).result_set

        low_quality_count = 0
        importance_counts = Counter()

        for row in res_text:
            sentiment = row[0] or ""
            importance = row[1] or "Unknown"

            importance_counts[importance] += 1

            # Heuristic for "empty" summaries
            if (
                "no reviews available" in sentiment.lower()
                or "impossible to gauge" in sentiment.lower()
                or "no description" in sentiment.lower()
            ):
                low_quality_count += 1

        print("\n📉 Quality Issues:")
        print(f"   Low Content / Empty Summaries: {low_quality_count} ({low_quality_count/total*100:.1f}%)")
        print("   (Events with missing description/reviews that AI couldn't summarize meaningfully)")

        print("\n🏷️  Importance Distribution:")
        for imp, count in importance_counts.most_common():
            print(f"   - {imp}: {count}")

        # 3. Pricing & Value Analysis
        query_value = """
        MATCH (s:AISummary)<-[:HAS_AI_SUMMARY]-(e:Event)
        RETURN s.value_rating, e.category_prices
        """
        res_value = db_connection.graph.query(query_value).result_set

        value_counts = Counter()
        priced_events = 0

        for row in res_value:
            rating = row[0] or "Unknown"
            prices = row[1]

            value_counts[rating] += 1
            if prices and len(prices) > 5:  # Basic check if JSON/string is not empty
                priced_events += 1

        print("\n💰 Value & Pricing:")
        print(f"   Events with Category Prices: {priced_events}/{total} ({priced_events/total*100:.1f}%)")
        print("   Value Ratings:")
        for rating, count in value_counts.most_common():
            print(f"   - {rating}: {count}")

        # 4. Progress & Forecast
        # Detailed backlog analysis
        # Find events WITHOUT summary to classify them
        query_total = "MATCH (e:Event) RETURN count(e)"
        total_events = db_connection.graph.query(query_total).result_set[0][0]

        # Get pending events (no summary) to check their quality
        # We fetch ID and description to check eligibility
        query_pending = """
        MATCH (e:Event) 
        WHERE NOT (e)-[:HAS_AI_SUMMARY]->()
        RETURN e.description
        """
        res_pending = db_connection.graph.query(query_pending).result_set

        pending_total = len(res_pending)
        total_summarized = total_events - pending_total

        # Analyze pending backlog
        actionable_pending = 0
        likely_skipped = 0

        for row in res_pending:
            desc = row[0]
            # Match the logic in enrichment.py (len > 10)
            if desc and len(desc.strip()) > 10:
                actionable_pending += 1
            else:
                likely_skipped += 1

        progress = (total_summarized / total_events) * 100 if total_events > 0 else 0

        print(f"\n🚀 Progress: {total_summarized}/{total_events} ({progress:.1f}%)")
        print(f"   Shape of Backlog ({pending_total} pending):")
        print(f"   ✅ Actionable:     {actionable_pending} (Ready to enrich)")
        print(f"   🚫 Likely Skipped: {likely_skipped} (Empty description, skipped in fast mode)")

        if actionable_pending > 0:
            # Estimates (Updated for Parallel Processing)
            # Cloud (Gemini): ~0.2s/event effective (batch/parallel)
            # Local (Ollama): ~1.5s/event effective (8x parallel)
            est_cloud = actionable_pending * 0.2 / 60  # minutes
            est_local = actionable_pending * 1.5 / 60  # minutes

            print(f"\n⏱️  Est. Time for Actionable Events (Parallel):")
            print(f"   - Cloud (Gemini): ~{est_cloud:.1f} mins")
            print(f"   - Local (Ollama): ~{est_local:.1f} mins")
        elif likely_skipped > 0:
            est_cloud = likely_skipped * 0.2 / 60
            est_local = likely_skipped * 1.5 / 60

            print(f"\n⏱️  Est. Time to FORCE Process (Likely Skipped):")
            print(f"   - Cloud (Gemini): ~{est_cloud:.1f} mins")
            print(f"   - Local (Ollama): ~{est_local:.1f} mins")
        else:
            print("\n🎉 All Done!")

        # 5. Recommendations
        print("\n💡 Recommendations:")
        if low_quality_count / (total or 1) > 0.5:
            print("   ⚠️  High rate of low-quality summaries.")
            print("      Consider filtering scrapers or improving source data quality.")
        else:
            print("   ✅ Quality looks healthy.")

    except Exception as e:
        logger.error(f"Audit failed: {e}")
    finally:
        db_connection.close()


if __name__ == "__main__":
    asyncio.run(main())
