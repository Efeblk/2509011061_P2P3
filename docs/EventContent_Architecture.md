# EventContent Node Architecture

## Overview

The EventContent node type stores event-related metadata separately from core Event data. This separation enables clean data architecture optimized for AI processing, user engagement, and content management.

## Architecture Principles

### 1. Separation of Concerns
- **Event Node**: Core, factual event data (title, date, venue, price)
- **EventContent Node**: User-generated and AI-relevant content (reviews, ratings, descriptions)

### 2. Relationship Model
```cypher
(Event)-[:HAS_CONTENT]->(EventContent)
```

- One Event can have multiple EventContent nodes
- Each EventContent node belongs to exactly one Event
- Content types differentiate purpose (reviews, summaries, descriptions)

### 3. Content Types

The `content_type` field enables different kinds of content:

| Type | Purpose | Author | Example |
|------|---------|--------|---------|
| `user_review` | User reviews and ratings | User ID | "Great concert! Highly recommend." |
| `ai_summary` | AI-generated summaries | "AI" | "Classical music performance featuring Beethoven." |
| `description` | Official event description | "editorial" | "Full orchestra performing Beethoven's symphonies." |
| `editorial` | Expert reviews | Editor ID | "A masterful performance that shouldn't be missed." |

## Node Schema

### Core Fields
- `event_uuid` (string, required): Reference to Event node
- `content_type` (string, required): Type of content (see above)

### Content Fields
- `text` (string, optional): Main textual content
- `summary` (string, optional): Short summary for display/AI

### Rating Fields
- `rating` (float, optional): Numerical rating (0.0-5.0)
- `rating_count` (int, optional): Number of ratings aggregated

### Metadata Fields
- `author` (string, optional): Author identifier
- `language` (string, default "tr"): Content language

### AI-Relevant Fields
- `sentiment_score` (float, optional): Sentiment analysis score (-1.0 to 1.0)
- `keywords` (string, optional): Comma-separated keywords
- `embedding_vector` (string, optional): JSON-serialized vector for similarity search

### Engagement Fields
- `likes_count` (int, default 0): Number of likes
- `views_count` (int, default 0): Number of views
- `helpful_count` (int, default 0): "Was this helpful?" count

### Standard Fields (inherited from Node)
- `uuid` (string): Unique identifier
- `created_at` (datetime): Creation timestamp
- `updated_at` (datetime): Last update timestamp

## Usage Examples

### Creating a User Review

```python
from src.models import EventContentNode

review = EventContentNode(
    event_uuid="event-123",
    content_type="user_review",
    text="Amazing concert! The orchestra was phenomenal.",
    rating=5.0,
    author="user-456",
    sentiment_score=0.9,
    keywords="amazing,phenomenal,orchestra",
    language="en"
)

# Save and create relationship to Event
review.save_with_relationship()
```

### Creating an AI Summary

```python
ai_summary = EventContentNode(
    event_uuid="event-123",
    content_type="ai_summary",
    text="Classical music concert featuring Beethoven's Symphony No. 9.",
    summary="Beethoven Symphony No. 9 performance",
    author="AI",
    keywords="classical,beethoven,symphony,orchestra",
    embedding_vector="[0.1, 0.2, 0.3, ...]"  # Vector from embedding model
)

ai_summary.save_with_relationship()
```

### Creating an Event Description

```python
description = EventContentNode(
    event_uuid="event-123",
    content_type="description",
    text="Join us for an evening of classical music as the Istanbul Symphony Orchestra performs Beethoven's complete 9th Symphony.",
    summary="Istanbul Symphony Orchestra - Beethoven's 9th",
    author="editorial",
    language="tr"
)

description.save_with_relationship()
```

## Query Examples

### Get All Content for an Event

```python
# Get all content
all_content = EventContentNode.find_by_event_uuid("event-123")

# Get only user reviews
reviews = EventContentNode.find_by_event_uuid("event-123", content_type="user_review")
```

### Get Average Rating for Event

```python
avg_rating = EventContentNode.get_aggregated_rating("event-123")
print(f"Average rating: {avg_rating}/5.0")
```

### Get Top-Rated Events

```python
top_events = EventContentNode.get_top_rated_events(limit=10)
for event in top_events:
    print(f"Event {event['event_uuid']}: {event['average_rating']}/5.0 ({event['review_count']} reviews)")
```

### Cypher Query Examples

**Get event with all its content:**
```cypher
MATCH (e:Event {uuid: "event-123"})-[:HAS_CONTENT]->(c:EventContent)
RETURN e, c
```

**Get all user reviews for an event:**
```cypher
MATCH (e:Event {uuid: "event-123"})-[:HAS_CONTENT]->(c:EventContent)
WHERE c.content_type = "user_review"
RETURN c.text, c.rating, c.author, c.created_at
ORDER BY c.created_at DESC
```

**Get events with highest average ratings:**
```cypher
MATCH (e:Event)-[:HAS_CONTENT]->(c:EventContent)
WHERE c.content_type = "user_review" AND c.rating > 0
WITH e, avg(c.rating) as avg_rating, count(c) as review_count
WHERE review_count >= 3
RETURN e.title, e.venue, avg_rating, review_count
ORDER BY avg_rating DESC
LIMIT 10
```

**Get all content for AI processing:**
```cypher
MATCH (e:Event)-[:HAS_CONTENT]->(c:EventContent)
WHERE c.content_type IN ["ai_summary", "description"]
RETURN e.uuid, e.title, c.text, c.summary, c.keywords, c.embedding_vector
```

## AI Integration

### Sentiment Analysis
Store sentiment scores for user reviews:

```python
# After analyzing review text with sentiment model
review.sentiment_score = 0.85  # Positive sentiment
review.save_with_relationship()
```

### Keyword Extraction
Extract and store keywords for search/recommendations:

```python
# After keyword extraction
content.keywords = "jazz,live,concert,istanbul,amazing"
```

### Embedding Vectors
Store vector embeddings for similarity search:

```python
import json

# After generating embedding with model (e.g., OpenAI, Sentence Transformers)
embedding = [0.1, 0.2, 0.3, ...]  # 768-dim vector
content.embedding_vector = json.dumps(embedding)
content.save_with_relationship()
```

Later, use embeddings for similarity search:
```cypher
// Note: Vector similarity requires custom implementation or extension
MATCH (c:EventContent)
WHERE c.embedding_vector IS NOT NULL
RETURN c
// Apply cosine similarity in application code
```

## Future Enhancements

### 1. User Node Integration
Connect reviews to User nodes:
```cypher
(User)-[:WROTE]->(EventContent)-[:ABOUT]->(Event)
```

### 2. Comment Threading
Support replies to reviews:
```cypher
(EventContent)-[:REPLY_TO]->(EventContent)
```

### 3. Content Moderation
Add moderation fields:
- `moderation_status`: "pending", "approved", "rejected"
- `moderation_notes`: Moderator notes
- `moderated_by`: Moderator ID
- `moderated_at`: Timestamp

### 4. Social Features
- Likes: `(User)-[:LIKED]->(EventContent)`
- Shares: `(User)-[:SHARED]->(EventContent)`
- Bookmarks: `(User)-[:BOOKMARKED]->(EventContent)`

### 5. AI Recommendations
Use content similarity:
```cypher
MATCH (e1:Event)-[:HAS_CONTENT]->(c1:EventContent)
WHERE c1.event_uuid = "target-event"
MATCH (e2:Event)-[:HAS_CONTENT]->(c2:EventContent)
WHERE e1.uuid <> e2.uuid
// Calculate similarity based on keywords, embeddings, sentiment
RETURN e2, similarity_score
ORDER BY similarity_score DESC
LIMIT 10
```

## Testing

Unit tests cover:
- Node creation and field validation
- Different content types
- Engagement field operations
- Rating validation
- Multilingual support
- Dictionary conversion (to_dict/from_dict)

Run tests:
```bash
pytest tests/unit/test_event_content.py -v
```

## Best Practices

1. **Always specify content_type**: Makes filtering and querying efficient
2. **Use save_with_relationship()**: Ensures Event-EventContent relationship is created
3. **Validate ratings**: Keep ratings in 0.0-5.0 range in application logic
4. **Store language**: Enables multilingual content management
5. **Use embedding_vector for AI**: Store as JSON string for flexibility
6. **Aggregate ratings carefully**: Use get_aggregated_rating() to handle edge cases

## Performance Considerations

1. **Index on event_uuid**: Critical for fast lookups
   ```cypher
   CREATE INDEX ON :EventContent(event_uuid)
   ```

2. **Index on content_type**: Enables fast filtering
   ```cypher
   CREATE INDEX ON :EventContent(content_type)
   ```

3. **Index on rating**: For top-rated queries
   ```cypher
   CREATE INDEX ON :EventContent(rating)
   ```

4. **Limit embedding vector size**: Balance between accuracy and storage
   - 384 dims: Fast, good for most tasks
   - 768 dims: Better accuracy, more storage
   - 1536 dims: Highest accuracy (OpenAI), largest storage

## Database Queries Performance

All class methods use optimized Cypher queries:
- `find_by_event_uuid()`: Single index lookup
- `get_aggregated_rating()`: Aggregation with WHERE filter
- `get_top_rated_events()`: Aggregation + ORDER BY + LIMIT

## Summary

EventContent provides a clean, extensible architecture for storing event-related content optimized for:
- ✅ AI processing (embeddings, sentiment, keywords)
- ✅ User engagement (reviews, ratings, likes)
- ✅ Content management (multiple types, multilingual)
- ✅ Social features (ready for User node integration)
- ✅ Scalability (separate from core Event data)
- ✅ Performance (relationship-based queries)
