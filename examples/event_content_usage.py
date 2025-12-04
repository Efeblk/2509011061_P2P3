#!/usr/bin/env python3
"""
Example script demonstrating EventContent node usage.
Shows how to create, query, and manage event-related content.
"""

from src.models import EventNode, EventContentNode
from falkordb import FalkorDB


def example_1_create_user_review():
    """Example 1: Create a user review with rating."""
    print("=" * 80)
    print("EXAMPLE 1: Creating User Review")
    print("=" * 80)

    # First, let's find an existing event (or create one for demo)
    # In real usage, you'd get event_uuid from your application logic

    # Create a user review
    review = EventContentNode(
        event_uuid="demo-event-123",  # Replace with actual event UUID
        content_type="user_review",
        text="Amazing concert! The acoustics were perfect and the performance was stunning. Highly recommend!",
        summary="Perfect acoustics, stunning performance",
        rating=5.0,
        author="user-789",
        language="en",
        sentiment_score=0.95,  # Calculated by sentiment analysis
        keywords="amazing,perfect,stunning,acoustics,recommend",
    )

    print(f"Created review: {review}")
    print(f"  Event: {review.event_uuid}")
    print(f"  Rating: {review.rating}/5.0")
    print(f"  Text: {review.text[:50]}...")
    print(f"  Sentiment: {review.sentiment_score}")
    print()

    # To save to database (uncomment when database is running):
    # review.save_with_relationship()
    # print("✅ Review saved to database with relationship to Event")


def example_2_create_ai_summary():
    """Example 2: Create AI-generated summary."""
    print("=" * 80)
    print("EXAMPLE 2: Creating AI-Generated Summary")
    print("=" * 80)

    # AI processes event information and generates summary
    ai_summary = EventContentNode(
        event_uuid="demo-event-123",
        content_type="ai_summary",
        text="This classical music concert features the Istanbul Symphony Orchestra performing Beethoven's Symphony No. 9 in D minor, Op. 125. The performance includes the famous 'Ode to Joy' finale with full choir.",
        summary="Istanbul Symphony Orchestra - Beethoven's 9th Symphony with 'Ode to Joy'",
        author="AI",
        language="en",
        keywords="classical,beethoven,symphony,orchestra,istanbul,ode to joy,choir",
        # In real usage, this would be a vector from an embedding model
        embedding_vector="[0.12, -0.34, 0.56, 0.78, ...]",
    )

    print(f"Created AI summary: {ai_summary}")
    print(f"  Summary: {ai_summary.summary}")
    print(f"  Keywords: {ai_summary.keywords}")
    print(f"  Has embedding: {'Yes' if ai_summary.embedding_vector else 'No'}")
    print()


def example_3_create_editorial_content():
    """Example 3: Create editorial/description content."""
    print("=" * 80)
    print("EXAMPLE 3: Creating Editorial Content")
    print("=" * 80)

    description = EventContentNode(
        event_uuid="demo-event-123",
        content_type="description",
        text="İstanbul Senfoni Orkestrası, Beethoven'in 9. Senfoni'sini seslendirecek. Konser, ünlü 'Neşeye Övgü' finaliyle birlikte tam bir koro performansı içerecektir. Bu eser, klasik müzik tarihinin en önemli eserlerinden biridir.",
        summary="İstanbul Senfoni Orkestrası - Beethoven 9. Senfoni",
        author="editorial",
        language="tr",
    )

    print(f"Created description: {description}")
    print(f"  Language: {description.language}")
    print(f"  Text: {description.text}")
    print()


def example_4_query_content():
    """Example 4: Query EventContent from database."""
    print("=" * 80)
    print("EXAMPLE 4: Querying EventContent")
    print("=" * 80)

    # These require database connection
    # Uncomment when database is running:

    # # Get all content for an event
    # all_content = EventContentNode.find_by_event_uuid("demo-event-123")
    # print(f"Found {len(all_content)} content items")

    # # Get only user reviews
    # reviews = EventContentNode.find_by_event_uuid(
    #     "demo-event-123",
    #     content_type="user_review"
    # )
    # print(f"Found {len(reviews)} user reviews")

    # # Get all AI summaries
    # summaries = EventContentNode.find_by_content_type("ai_summary", limit=10)
    # print(f"Found {len(summaries)} AI summaries")

    print("(Query examples - requires database connection)")
    print()


def example_5_aggregate_ratings():
    """Example 5: Calculate aggregate ratings."""
    print("=" * 80)
    print("EXAMPLE 5: Aggregate Ratings")
    print("=" * 80)

    # Uncomment when database is running:

    # # Get average rating for an event
    # avg_rating = EventContentNode.get_aggregated_rating("demo-event-123")
    # if avg_rating:
    #     print(f"Average rating: {avg_rating:.2f}/5.0")
    # else:
    #     print("No ratings yet")

    # # Get top-rated events
    # top_events = EventContentNode.get_top_rated_events(limit=10)
    # print(f"\nTop {len(top_events)} events:")
    # for i, event in enumerate(top_events, 1):
    #     print(f"  {i}. Event {event['event_uuid']}")
    #     print(f"     Rating: {event['average_rating']:.2f}/5.0")
    #     print(f"     Reviews: {event['review_count']}")

    print("(Aggregate rating examples - requires database connection)")
    print()


def example_6_engagement_tracking():
    """Example 6: Track engagement metrics."""
    print("=" * 80)
    print("EXAMPLE 6: Engagement Tracking")
    print("=" * 80)

    review = EventContentNode(
        event_uuid="demo-event-123",
        content_type="user_review",
        text="Great show!",
        rating=4.5,
        likes_count=10,
        views_count=150,
        helpful_count=8,
    )

    print(f"Engagement metrics:")
    print(f"  Likes: {review.likes_count}")
    print(f"  Views: {review.views_count}")
    print(f"  Helpful votes: {review.helpful_count}")
    print()

    # Simulate user interactions
    review.likes_count += 1
    review.views_count += 1
    review.helpful_count += 1

    print(f"After user interactions:")
    print(f"  Likes: {review.likes_count}")
    print(f"  Views: {review.views_count}")
    print(f"  Helpful votes: {review.helpful_count}")
    print()


def example_7_multilingual_content():
    """Example 7: Store multilingual content."""
    print("=" * 80)
    print("EXAMPLE 7: Multilingual Content")
    print("=" * 80)

    # Turkish review
    turkish_review = EventContentNode(
        event_uuid="demo-event-123",
        content_type="user_review",
        text="Harika bir konser! Akustik mükemmeldi ve performans muhteşemdi.",
        rating=5.0,
        language="tr",
        sentiment_score=0.92,
    )

    # English review
    english_review = EventContentNode(
        event_uuid="demo-event-123",
        content_type="user_review",
        text="Fantastic concert! The acoustics were perfect and the performance was amazing.",
        rating=5.0,
        language="en",
        sentiment_score=0.95,
    )

    print(f"Turkish review:")
    print(f"  Language: {turkish_review.language}")
    print(f"  Text: {turkish_review.text}")
    print()

    print(f"English review:")
    print(f"  Language: {english_review.language}")
    print(f"  Text: {english_review.text}")
    print()


def example_8_direct_cypher_queries():
    """Example 8: Direct Cypher queries for advanced use cases."""
    print("=" * 80)
    print("EXAMPLE 8: Advanced Cypher Queries")
    print("=" * 80)

    # These are example queries you can run when database is up:

    queries = {
        "Get event with all content": """
            MATCH (e:Event {uuid: "demo-event-123"})-[:HAS_CONTENT]->(c:EventContent)
            RETURN e, c
        """,
        "Get all reviews sorted by rating": """
            MATCH (e:Event)-[:HAS_CONTENT]->(c:EventContent)
            WHERE c.content_type = "user_review"
            RETURN e.title, c.text, c.rating, c.author, c.created_at
            ORDER BY c.rating DESC
        """,
        "Get events with most reviews": """
            MATCH (e:Event)-[:HAS_CONTENT]->(c:EventContent)
            WHERE c.content_type = "user_review"
            WITH e, count(c) as review_count
            RETURN e.title, e.venue, review_count
            ORDER BY review_count DESC
            LIMIT 10
        """,
        "Get content for AI processing": """
            MATCH (e:Event)-[:HAS_CONTENT]->(c:EventContent)
            WHERE c.content_type IN ["ai_summary", "description"]
            RETURN e.uuid, e.title, c.text, c.keywords, c.embedding_vector
        """,
        "Find similar events by keywords": """
            MATCH (e1:Event {uuid: "target-event"})-[:HAS_CONTENT]->(c1:EventContent)
            MATCH (e2:Event)-[:HAS_CONTENT]->(c2:EventContent)
            WHERE e1.uuid <> e2.uuid
              AND c1.keywords IS NOT NULL
              AND c2.keywords IS NOT NULL
            // Use application logic to calculate keyword similarity
            RETURN e2.title, c2.keywords
            LIMIT 10
        """,
    }

    for query_name, query in queries.items():
        print(f"\n{query_name}:")
        print(query.strip())
        print()


def main():
    """Run all examples."""
    print("\n")
    print("█" * 80)
    print("EventContent Node - Usage Examples")
    print("█" * 80)
    print()

    # Run all examples
    example_1_create_user_review()
    example_2_create_ai_summary()
    example_3_create_editorial_content()
    example_4_query_content()
    example_5_aggregate_ratings()
    example_6_engagement_tracking()
    example_7_multilingual_content()
    example_8_direct_cypher_queries()

    print("=" * 80)
    print("Examples Complete!")
    print("=" * 80)
    print()
    print("To use EventContent in your application:")
    print("  1. Start database: make up")
    print("  2. Import models: from src.models import EventContentNode")
    print("  3. Create content: review = EventContentNode(...)")
    print("  4. Save with relationship: review.save_with_relationship()")
    print()
    print("For more details, see: docs/EventContent_Architecture.md")
    print()


if __name__ == "__main__":
    main()
