"""Event enrichment with AI-generated summaries."""

import json
from typing import Optional
from loguru import logger
from config.settings import settings

from src.ai.gemini_client import gemini_client
from src.ai.ollama_client import ollama_client
from src.models.event import EventNode
from src.models.ai_summary import AISummaryNode
from src.database.connection import db_connection


def get_ai_client(use_reasoning: bool = False):
    """Factory to get the configured AI client."""
    # If provider is Ollama, use it for everything (including reasoning)
    if settings.ai.provider == "ollama":
        return ollama_client

    # Reasoning uses Gemini (if not local)
    if use_reasoning:
        from src.ai.gemini_client import GeminiClient

        return GeminiClient(model_name=settings.ai.model_reasoning)

    return gemini_client


SUMMARY_PROMPT_TEMPLATE = """
Analyze this event and create a compact, intelligent summary.

EVENT DETAILS:
Title: {title}
Category: {category}
Genre: {genre}
Duration: {duration}
Description: {description}
Venue: {venue}
City: {city}
Price: ₺{price}
Category Prices: {category_prices}
Rating: {rating}/5 ({review_count} reviews)

{reviews_section}

Create a JSON summary (be concise and honest):
{{
    "quality_score": 0-10,
    "importance": "must-see" | "iconic" | "popular" | "niche" | "seasonal" | "emerging",
    "value_rating": "excellent" | "good" | "fair" | "expensive",
    "sentiment_summary": "Two sentences capturing the essence and vibe of the event. Be descriptive.",
    "key_highlights": ["highlight1", "highlight2", "highlight3"],
    "concerns": ["concern1", "concern2"] or null if none,
    "best_for": ["audience1", "audience2", "audience3"],
    "vibe": "2-3 words describing atmosphere",
    "uniqueness": "what makes this special (one line)",
    "educational_value": true/false,
    "tourist_attraction": true/false,
    "bucket_list_worthy": true/false
}}

Consider:
- Is this a cultural classic everyone should see? (Don Quixote, Nutcracker)
- Is it a legendary artist/show? (Metallica, famous opera)
- Does it offer good value compared to similar events?
- What do reviews consistently praise or criticize?
- Who would most enjoy this?

Be honest - if it's mediocre, say so. If reviews are mixed, reflect that.

CRITICAL:
- The event is happening in {city}.
- If the description mentions other cities (e.g. past tour dates, "Ankara'dan sonra İstanbul'da"), IGNORE those cities.
- Do NOT say "in Ankara" or "in Izmir" if the Event City is {city}.
- Stick strictly to the venue and city provided in EVENT DETAILS above.
"""


async def generate_summary(event: EventNode, force: bool = False) -> Optional[AISummaryNode]:
    """
    Generate AI summary for an event.

    Args:
        event: EventNode to summarize
        force: Process even if low quality

    Returns:
        AISummaryNode with summary, or None if failed
    """
    logger.debug(f"Generating summary for event: {event.title}")

    # Prepare reviews section with AI summary and top reviews
    reviews_section = ""
    reviews = []

    # We need to check for reviews before deciding to skip
    try:
        from src.models.event_content import EventContentNode

        # Get Biletinial's AI summary if available
        ai_contents = EventContentNode.find_by_event_uuid(event.uuid, content_type="ai_summary")

        if ai_contents:
            ai_summary = ai_contents[0].text
            reviews_section = f"BILETINIAL AI SUMMARY:\n{ai_summary}\n\n"

        # Get top 5 user reviews for comprehensive analysis
        user_reviews = EventContentNode.find_by_event_uuid(event.uuid, content_type="user_review")
        if user_reviews:
            # Use up to 500 chars per review for comprehensive quality analysis
            # This allows capturing full user sentiment and detailed feedback
            review_texts = [f"- {r.text[:500]}..." if len(r.text) > 500 else f"- {r.text}" for r in user_reviews[:5]]
            reviews_section += f"TOP USER REVIEWS:\n" + "\n".join(review_texts)
            reviews = user_reviews

    except Exception as e:
        logger.warning(f"Could not fetch content: {e}")

    # SKIP LOGIC REMOVED BY USER REQUEST (process all events)
    # has_description = event.description and len(event.description.strip()) > 10
    # if not has_description and not reviews_section and not force: ...

    # Initialize client first
    client = get_ai_client()

    # Generate embedding for the event (always do this if enabled)
    embedding_json = None
    if settings.ai.enable_embeddings:
        try:
            # Fetch venue name
            venue_query = "MATCH (e:Event {uuid: $uuid})-[:HELD_AT]->(v:Venue) RETURN v.name"
            venue_res = db_connection.execute_query(venue_query, {"uuid": event.uuid})
            venue_name = venue_res.result_set[0][0] if venue_res and venue_res.result_set else ""

            # Use Title + Venue + Category + Description
            embedding_text = f"{event.title}. {venue_name}. {event.category or ''}. {event.description or ''}"
            embedding_vector = client.embed(embedding_text)
            embedding_json = json.dumps(embedding_vector) if embedding_vector else None
        except Exception as e:
            logger.warning(f"Could not generate embedding (quota/rate limit): {e}")

    # Final check: If no description and no reviews/AI summary, SKIP LLM SUMMARY
    # But we still save the embedding if we have one.
    has_description = event.description and len(event.description.strip()) > 10

    summary_data = {}
    skipped_llm = False

    # Fetch graph relationships (Cast, Crew, etc.)
    key_people_section = ""
    try:
        relationships = await event.get_relationships()
        if relationships:
            people_map = {}
            for r in relationships:
                role = r["role"]
                name = r["name"]
                if role not in people_map:
                    people_map[role] = []
                people_map[role].append(name)
            
            key_people_section = "KEY PEOPLE (Verified):\n"
            for role, names in people_map.items():
                key_people_section += f"{role}: {', '.join(names)}\n"
    except Exception as e:
        logger.warning(f"Failed to fetch relationships for summary: {e}")

    if not has_description and not reviews_section and not key_people_section and not force:
        logger.debug(f"Skipping LLM summary for low-quality event: {event.title}")
        skipped_llm = True
        # We will save a partial node with just the embedding
    else:
        # Build prompt
        prompt = SUMMARY_PROMPT_TEMPLATE.format(
            title=event.title or "Unknown",
            category=event.category or "Uncategorized",
            genre=event.genre or "Unknown",
            duration=event.duration or "Unknown",
            description=(event.description[:1000] + "...") if event.description else "No description",
            venue=event.venue or "Unknown venue",
            city=event.city or "Unknown city",
            price=event.price or 0,
            category_prices=event.category_prices or "Not available",
            rating="N/A",
            review_count=len(reviews) if reviews else 0,
            reviews_section=(key_people_section + "\n" + (reviews_section or "No reviews available.")),
        )

        # Generate summary
        summary_data = await client.generate_json(prompt, temperature=0.3)

        if not summary_data:
            logger.error(f"Failed to generate summary for: {event.title}")
            # If we have an embedding, we can still save it?
            # Ideally yes, but let's treat LLM failure as a soft fail for now unless we have embedding.
            if not embedding_json:
                return None

    # If we skipped LLM and have no embedding, then we really have nothing.
    if skipped_llm and not embedding_json:
        return None

    # Create AISummaryNode
    try:
        summary = AISummaryNode(
            event_uuid=event.uuid,
            quality_score=summary_data.get("quality_score"),
            importance=summary_data.get("importance"),
            value_rating=summary_data.get("value_rating"),
            sentiment_summary=summary_data.get("sentiment_summary") or ("Event details available for search." if skipped_llm else None),
            key_highlights=json.dumps(summary_data.get("key_highlights") or []),
            concerns=json.dumps(summary_data.get("concerns") or []),
            best_for=",".join(summary_data.get("best_for") or []),
            vibe=summary_data.get("vibe"),
            uniqueness=summary_data.get("uniqueness"),
            educational_value=summary_data.get("educational_value", False),
            tourist_attraction=summary_data.get("tourist_attraction", False),
            bucket_list_worthy=summary_data.get("bucket_list_worthy", False),
            embedding=embedding_json,
            summary_json=json.dumps(summary_data) if summary_data else None,
            model_version="gemini-1.5-flash",
            prompt_version="v1",
        )

        # Save to database
        saved = await summary.save()

        if saved:
            if skipped_llm:
                logger.debug(f"✓ Embedding created (LLM skipped) for: {event.title}")
            else:
                logger.debug(f"✓ Summary created for: {event.title}")
            return saved
        else:
            logger.error(f"Failed to save summary for: {event.title}")
            return None

    except Exception as e:
        logger.error(f"Error creating summary node: {e}")
        return None


async def batch_generate_summaries(
    events: list[EventNode], delay: float = 1.0, force: bool = False, overwrite: bool = False
) -> dict:
    """
    Generate summaries for multiple events with rate limiting.

    Args:
        events: List of EventNode objects
        delay: Delay between API calls in seconds
        force: If True, process even if low quality
        overwrite: If True, regenerate existing summaries
    """
    import asyncio
    from tqdm import tqdm

    results = {"success": 0, "failed": 0, "skipped": 0, "skipped_low_quality": 0}

    # Limit concurrency for local LLM (or API rate limits)
    # Configurable via AI_CONCURRENCY in .env
    MAX_CONCURRENCY = settings.ai.concurrency
    semaphore = asyncio.Semaphore(MAX_CONCURRENCY)

    async def process_event(event):
        async with semaphore:
            # Update description (approximate since parallel)
            # pbar.set_description(f"🤖 Processing: {event.title[:30]}...")

            # Check existing
            if not overwrite:
                existing = await AISummaryNode.get_by_event_uuid(event.uuid)
                if existing:
                    results["skipped"] += 1
                    pbar.update(1)
                    return

            # Generate
            summary = await generate_summary(event, force=force)
            if summary:
                results["success"] += 1
            elif summary is None:
                # Check if it was skipped due to low quality
                has_description = event.description and len(event.description.strip()) > 10
                try:
                    from src.models.event_content import EventContentNode

                    ai_contents = EventContentNode.find_by_event_uuid(event.uuid, content_type="ai_summary")
                    user_reviews = EventContentNode.find_by_event_uuid(event.uuid, content_type="user_review")
                    has_content = bool(ai_contents or user_reviews)
                except:
                    has_content = False

                if not has_description and not has_content and not force:
                    results["skipped_low_quality"] += 1
                else:
                    results["failed"] += 1

            pbar.update(1)
            pbar.set_postfix(
                success=results["success"], failed=results["failed"], low_quality=results["skipped_low_quality"]
            )

    # Create tasks
    tasks = [process_event(e) for e in events]

    # Run all
    with tqdm(total=len(events), desc="🤖 Enriching Events", unit="event", dynamic_ncols=True) as pbar:
        await asyncio.gather(*tasks)

    logger.info(
        f"Batch complete: {results['success']} success, {results['failed']} failed, "
        f"{results['skipped']} already had summaries, {results['skipped_low_quality']} skipped (low quality)"
    )
    return results
