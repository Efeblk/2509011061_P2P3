#!/usr/bin/env python
"""View events from the database with rating and review information."""

from falkordb import FalkorDB

# Connect to database
db = FalkorDB(host="localhost", port=6379)
g = db.select_graph("eventgraph")

# Get total events count
count_r = g.query("MATCH (e:Event) RETURN count(e) as count")
total = count_r.result_set[0][0]

# Get stats by source
biletinial_r = g.query("MATCH (e:Event) WHERE e.source = 'biletinial' RETURN count(e)")
biletinial_count = biletinial_r.result_set[0][0] if biletinial_r.result_set else 0

biletix_r = g.query("MATCH (e:Event) WHERE e.source = 'biletix' RETURN count(e)")
biletix_count = biletix_r.result_set[0][0] if biletix_r.result_set else 0

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

print(f"\n📊 DATABASE STATS")
print(f"Total Events: {total}")
print(f" - Biletinial: {biletinial_count}")
print(f" - Biletix: {biletix_count}")
print(f"Ratings: {total_ratings} | Reviews: {total_reviews}\n")

def print_event(i, row):
    event_uuid = row[0]
    title = row[1]
    venue = row[2]
    city = row[3] or "Unknown"
    price = row[4]
    date = row[5]
    source = row[6]
    rating = row[7]
    rating_count = row[8]
    
    price_str = f"{price} TL" if price is not None else "N/A"

    print(f"{i+1}. {title}")
    print(f"   📍 City: {city}")
    print(f"   🏛️  Venue: {venue}")
    print(f"   💰 Price: {price_str}")
    print(f"   📅 Date: {date}")
    print(f"   🔗 Source: {source}")

    if rating:
        print(f"   ⭐ Rating: {rating}/5 ({rating_count} reviews)")
    else:
        print(f"   ⭐ Rating: N/A")
    print("-" * 40)

# 1. Show Biletinial Samples
print(f"\n🎟️  LATEST 10 FROM BILETINIAL")
r_biletinial = g.query(
    "MATCH (e:Event) WHERE e.source='biletinial' "
    "OPTIONAL MATCH (e)-[:HAS_CONTENT]->(ec:EventContent {content_type: 'platform_rating'}) "
    "RETURN e.uuid, e.title, e.venue, e.city, e.price, e.date, e.source, ec.rating, ec.rating_count "
    "ORDER BY e.date DESC LIMIT 10"
)

for i, row in enumerate(r_biletinial.result_set):
    print_event(i, row)

# 2. Show Biletix Samples
print(f"\n🎟️  LATEST 10 FROM BILETIX")
r_biletix = g.query(
    "MATCH (e:Event) WHERE e.source='biletix' "
    "OPTIONAL MATCH (e)-[:HAS_CONTENT]->(ec:EventContent {content_type: 'platform_rating'}) "
    "RETURN e.uuid, e.title, e.venue, e.city, e.price, e.date, e.source, ec.rating, ec.rating_count "
    "ORDER BY e.date DESC LIMIT 10"
)

for i, row in enumerate(r_biletix.result_set):
    print_event(i, row)



