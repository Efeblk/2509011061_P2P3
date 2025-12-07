#!/usr/bin/env python
"""View events from the database with rating and review information."""

from falkordb import FalkorDB

# Connect to database
db = FalkorDB(host="localhost", port=6379)
g = db.select_graph("eventgraph")

# Get total events count
count_r = g.query("MATCH (e:Event) RETURN count(e) as count")
total = count_r.result_set[0][0]

# Get total ratings count
rating_r = g.query(
    "MATCH (e:Event)-[:HAS_CONTENT]->(ec:EventContent) "
    'WHERE ec.content_type = "platform_rating" '
    "RETURN count(ec) as count"
)
total_ratings = rating_r.result_set[0][0] if rating_r.result_set else 0

# Get total reviews count
reviews_r = g.query(
    "MATCH (e:Event)-[:HAS_CONTENT]->(ec:EventContent) "
    'WHERE ec.content_type = "user_review" '
    "RETURN count(ec) as count"
)
total_reviews = reviews_r.result_set[0][0] if reviews_r.result_set else 0

# Get events with ratings
r = g.query(
    "MATCH (e:Event) "
    "OPTIONAL MATCH (e)-[:HAS_CONTENT]->(ec:EventContent) "
    'WHERE ec.content_type = "platform_rating" '
    "RETURN e.uuid, e.title, e.venue, e.city, e.price, e.date, e.source, ec.rating, ec.rating_count "
    "ORDER BY e.city, e.title LIMIT 20"
)

print(f"\nTotal: {total} events | Ratings: {total_ratings} | Reviews: {total_reviews}\n")

for i, row in enumerate(r.result_set):
    event_uuid = row[0]
    title = row[1]
    venue = row[2]
    city = row[3] or "Unknown"
    price = row[4] or "N/A"
    date = row[5]
    source = row[6]
    rating = row[7]
    rating_count = row[8]

    print(f"{i+1}. {title}")
    print(f"   📍 City: {city}")
    print(f"   🏛️  Venue: {venue}")
    print(f"   💰 Price: {price} TL")
    print(f"   📅 Date: {date}")
    print(f"   🔗 Source: {source}")

    if rating:
        print(f"   ⭐ Rating: {rating}/5 ({rating_count} reviews)")
    else:
        print(f"   ⭐ Rating: N/A")

    # Get reviews for this event
    reviews_q = g.query(
        "MATCH (e:Event {uuid: $uuid})-[:HAS_CONTENT]->(r:EventContent) "
        'WHERE r.content_type = "user_review" '
        "RETURN r.author, r.text, r.rating LIMIT 3",
        {"uuid": event_uuid},
    )

    if reviews_q.result_set:
        print(f"   💬 User Reviews ({len(reviews_q.result_set)}):")
        for review_row in reviews_q.result_set:
            author = review_row[0] or "Anonymous"
            text = review_row[1][:80] + "..." if review_row[1] and len(review_row[1]) > 80 else review_row[1]
            review_rating = review_row[2]
            rating_str = f" ({review_rating}/5)" if review_rating else ""
            print(f"      - {author}{rating_str}: {text}")

    print()
