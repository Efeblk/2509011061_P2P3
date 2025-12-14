"""
Tournament AI Engine.
Runs multi-stage selection process to find best events.
"""

import asyncio
import json
from loguru import logger
from typing import List, Dict

from src.models.event import EventNode
from src.models.ai_summary import AISummaryNode
from src.models.collection import CollectionNode
from src.ai.enrichment import get_ai_client
from config.settings import settings


def extract_list_from_response(data: any) -> list:
    """
    Robustly extract a list from AI response data.
    Handles direct lists, or lists wrapped in dicts (common with local models).
    """
    if isinstance(data, list):
        return data

    if isinstance(data, dict):
        # Common keys used by models
        for key in ["uuids", "events", "results", "rankings", "candidates", "winners"]:
            if key in data and isinstance(data[key], list):
                return data[key]

        # Fallback: find ANY list value
        for value in data.values():
            if isinstance(value, list):
                return value

    return []


async def run_stage_1_filter(events: List[Dict], criteria: str, dry_run: bool = False) -> List[Dict]:
    """
    Stage 1: Fast filtering using Local/Fast Model.
    Input: List of compact event dicts.
    Output: Subset of events that match criteria.
    """

    # Use configured AI client (Local or Cloud)
    client = get_ai_client(use_reasoning=False)

    prompt = f"""
    You are a strict event curator. 
    Filter the following list of events based on this criteria: "{criteria}".
    
    Rules:
    1. Select ONLY events that strongly match the criteria.
    2. Reject generic or irrelevant events.
    3. Return a JSON array of event_uuids for the winners.
    
    Events:
    {json.dumps(events, indent=2)}
    
    Return JSON format only: ["uuid1", "uuid2"]
    """

    try:
        # Use generate_json for robust parsing (works with both clients)
        response_data = await client.generate_json(prompt, temperature=0.1)

        uuids = extract_list_from_response(response_data)

        if not uuids:
            if response_data:
                logger.warning(f"Stage 1: Could not find list in response: {type(response_data)}")
            return []

        # Filter original list
        winners = [e for e in events if e["uuid"] in uuids]
        return winners
    except Exception as e:
        logger.error(f"Stage 1 failed: {e}")
        return []


async def run_stage_2_finals(candidates: List[Dict], category_name: str, criteria: str, dry_run: bool = False):
    """
    Stage 2: Final selection using Reasoning Model (Gemini 3.0 Pro).
    Input: Shortlisted candidates.
    Output: Top 10 ranked with reasons.
    """

    if dry_run:
        logger.info("[DRY RUN] Simulating Stage 2 finals (ranking top 3)")
        mock_results = []
        for i, c in enumerate(candidates[:3]):
            mock_results.append(
                {"uuid": c["uuid"], "rank": i + 1, "reason": f"[DRY RUN] This is a simulated reason for {c['title']}."}
            )
        return mock_results

    # Use Reasoning model (or Local equivalent)
    client = get_ai_client(use_reasoning=True)

    prompt = f"""
    You are an expert lifestyle editor for a premium city guide.
    Task: Select the Top 10 events for the collection: "{category_name}".
    Criteria: {criteria}
    
    You have {len(candidates)} finalists. 
    Compare them based on value, uniqueness, vibe, and "once-in-a-lifetime" factor.
    
    Candidates:
    {json.dumps(candidates, indent=2)}
    
    Output Format (JSON):
    [
      {{
        "uuid": "event_uuid",
        "rank": 1,
        "reason": "Compelling reason why this is #1..."
      }},
      ...
    ]
    """

    try:
        # Use reasoning model for Stage 2
        model_override = None
        if settings.ai.provider == "ollama":
            model_override = settings.ollama.model_reasoning

        results = await client.generate_json(prompt, temperature=0.4, model=model_override)

        final_list = extract_list_from_response(results)

        if not final_list:
            if results:
                logger.warning(f"Stage 2: Could not find list in response: {type(results)}")
            return []

        return final_list
    except Exception as e:
        logger.error(f"Stage 2 failed: {e}")
        return []


async def run_tournament(
    category_slug: str, category_name: str, criteria: str, dry_run: bool = False, candidate_limit: int = 0
):
    """Run full tournament."""
    logger.info(f"🏆 Starting Tournament: {category_name} (Dry Run: {dry_run}, Limit: {candidate_limit})")

    # 1. Fetch Candidates (Events with AI Summaries)
    # We get compact data to save tokens
    from src.database.connection import db_connection

    # Connection is implicit

    limit_clause = f"LIMIT {candidate_limit}" if candidate_limit > 0 else ""

    query = f"""
    MATCH (e:Event)-[:HAS_AI_SUMMARY]->(s:AISummary)
    RETURN e.uuid, e.title, e.date, s.sentiment_summary, s.importance, s.value_rating, s.quality_score
    {limit_clause}
    """
    res = db_connection.graph.query(query).result_set

    all_candidates = []
    for row in res:
        # Filter out very low quality scores before even trying
        quality = row[6]
        if quality and quality < 3:
            continue

        all_candidates.append(
            {"uuid": row[0], "title": row[1], "date": row[2], "summary": row[3], "importance": row[4], "value": row[5]}
        )

    logger.info(f"Found {len(all_candidates)} eligible candidates.")

    if not all_candidates:
        logger.warning("No candidates found. Tournament cancelled.")
        return

    # 2. Stage 1: Chunked Filtering
    # Split into chunks of 50
    CHUNK_SIZE = 50
    semi_finalists = []

    chunks = [all_candidates[i : i + CHUNK_SIZE] for i in range(0, len(all_candidates), CHUNK_SIZE)]

    logger.info(f"Stage 1: Filtering {len(chunks)} chunks...")

    # Run chunks (could be parallelized)
    for i, chunk in enumerate(chunks):
        logger.info(f"Processing chunk {i+1}/{len(chunks)}...")
        winners = await run_stage_1_filter(chunk, criteria, dry_run=dry_run)
        semi_finalists.extend(winners)

    logger.info(f"Stage 1 Complete. {len(semi_finalists)} Semi-Finalists selected.")

    # 3. Stage 2: The Finals
    if not semi_finalists:
        logger.warning("No semi-finalists. Tournament failed.")
        return

    logger.info("Stage 2: The Finals (Reasoning)...")
    final_results = await run_stage_2_finals(semi_finalists, category_name, criteria, dry_run=dry_run)

    # 4. Save Results
    collection = CollectionNode(
        name=category_name, description=f"AI Curated selection for {category_name}", category=category_slug
    )
    await collection.save()
    await collection.clear_events()  # Clear old rankings

    for item in final_results:
        await collection.add_event(event_uuid=item["uuid"], rank=item["rank"], reason=item["reason"])

    logger.info(f"🏆 Tournament Complete! Saved {len(final_results)} winners to '{category_name}'.")
