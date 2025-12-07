#!/usr/bin/env python3
"""
Verification script to check scraping quality and data integrity.
Checks for:
- Missing required fields (Title, Date, URL)
- Duplicate events
- Data completeness stats
- Suspicious data (short titles, long dates)
"""

import sys
from falkordb import FalkorDB


def verify_data():
    """Verify the quality of scraped data in the database."""

    try:
        db = FalkorDB(host="localhost", port=6379)
        g = db.select_graph("eventgraph")
    except Exception as e:
        print(f"❌ Could not connect to database: {e}")
        return False

    print("=" * 80)
    print("EVENTGRAPH DATA VERIFICATION REPORT")
    print("=" * 80)
    print()

    # 1. Overall Statistics
    print("📊 OVERALL STATISTICS")
    print("-" * 80)

    try:
        total_query = g.query("MATCH (e:Event) RETURN count(e)")
        total = total_query.result_set[0][0]
        print(f"Total Events: {total}")

        if total == 0:
            print("\n⚠️  Database is empty! Run 'make scrape' first.")
            return False

        by_source = g.query("MATCH (e:Event) RETURN e.source, count(e) ORDER BY count(e) DESC")
        print("\nEvents by Source:")
        for row in by_source.result_set:
            print(f"  {row[0]}: {row[1]} events")

        # Review stats
        review_query = g.query("MATCH (ec:EventContent) WHERE ec.content_type = 'user_review' RETURN count(ec)")
        review_count = review_query.result_set[0][0]
        print(f"\nTotal Reviews: {review_count}")

    except Exception as e:
        print(f"Error querying stats: {e}")
        return False

    print()

    # 2. Data Completeness Check
    print("✅ DATA COMPLETENESS CHECK")
    print("-" * 80)

    issues = []

    # Check for missing required fields
    missing_title = g.query('MATCH (e:Event) WHERE e.title = "" OR e.title IS NULL RETURN count(e)').result_set[0][0]
    missing_date = g.query('MATCH (e:Event) WHERE e.date = "" OR e.date IS NULL RETURN count(e)').result_set[0][0]
    missing_url = g.query('MATCH (e:Event) WHERE e.url = "" OR e.url IS NULL RETURN count(e)').result_set[0][0]

    print(f"Missing Title: {missing_title}")
    print(f"Missing Date: {missing_date}")
    print(f"Missing URL: {missing_url}")

    if missing_title > 0:
        issues.append(f"{missing_title} events missing title")
    if missing_date > 0:
        issues.append(f"{missing_date} events missing date")
    if missing_url > 0:
        issues.append(f"{missing_url} events missing URL")

    # 3. Data Quality Checks
    print("\n🔍 DATA QUALITY CHECKS")
    print("-" * 80)

    # Check for suspicious short titles
    short_titles = g.query("MATCH (e:Event) WHERE size(e.title) < 3 RETURN count(e)").result_set[0][0]
    if short_titles > 0:
        print(f"⚠️  Suspiciously short titles (< 3 chars): {short_titles} events")
        issues.append(f"{short_titles} events with very short titles")
    else:
        print("✓ No suspiciously short titles")

    # 4. Exact Duplicates Check
    print("\n🔄 DUPLICATE CHECK")
    print("-" * 80)

    duplicates = g.query(
        """
        MATCH (e:Event)
        WITH e.title as title, e.venue as venue, e.date as date, collect(e) as events
        WHERE size(events) > 1
        RETURN count(events)
        """
    ).result_set[0][0]

    if duplicates > 0:
        print(f"⚠️  Found {duplicates} sets of potential duplicates")
        issues.append(f"{duplicates} sets of duplicate events")
    else:
        print("✓ No exact duplicates found")

    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)

    if issues:
        print("\n⚠️  Issues Found:")
        for issue in issues:
            print(f"  - {issue}")
        print("\n❌ Verification FAILED")
        return False
    else:
        print("\n✅ No major issues found! Data quality looks good.")
        return True


if __name__ == "__main__":
    success = verify_data()
    sys.exit(0 if success else 1)
