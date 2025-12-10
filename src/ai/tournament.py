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


async def run_stage_1_filter(events: List[Dict], criteria: str, dry_run: bool = False) -> List[Dict]:
    """
    Stage 1: Fast filtering using Local/Fast Model.
    Input: List of compact event dicts.
    Output: Subset of events that match criteria.
    """

    # Switch to Gemini Flash for filtering (Smart + Cheap)
    # Replaces Llama (Local) as per user request for "Reasoning" quality
    from src.ai.gemini_client import GeminiClient
    
    if dry_run:
        logger.info("[DRY RUN] Simulating Stage 1 filtering (selecting first 2 events)")
        return events[:2] if events else []
    
    
    # Use Flash for high-volume filtering
    # note: ensuring using specific version to avoid 404
    client = GeminiClient(model_name=settings.ai.model_fast) 
    
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
        response = client.generate(prompt)
        # extracting json from response
        clean_json = response.strip()
        if "```json" in clean_json:
            clean_json = clean_json.split("```json")[1].split("```")[0]
        elif "```" in clean_json:
            clean_json = clean_json.split("```")[1].split("```")[0]
            
        uuids = json.loads(clean_json)
        # Filter original list
        winners = [e for e in events if e['uuid'] in uuids]
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
             mock_results.append({
                 "uuid": c['uuid'],
                 "rank": i + 1,
                 "reason": f"[DRY RUN] This is a simulated reason for {c['title']}."
             })
        return mock_results

    # Use Reasoning model (Gemini 3.0 Pro)
    # We need to instantiate Gemini client explicitly if default is Llama
    # But get_ai_client handles provider switching. We need to force provider=gemini and model=reasoning
    
    # Access settings directly or create custom client
    from src.ai.gemini_client import GeminiClient
    client = GeminiClient(model_name=settings.ai.model_reasoning) 
    
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
        response = client.generate(prompt)
        clean_json = response.strip()
        if "```json" in clean_json:
            clean_json = clean_json.split("```json")[1].split("```")[0]
        elif "```" in clean_json:
            clean_json = clean_json.split("```")[1].split("```")[0]
            
        results = json.loads(clean_json)
        return results
    except Exception as e:
        logger.error(f"Stage 2 failed: {e}")
        return []


async def run_tournament(category_slug: str, category_name: str, criteria: str, dry_run: bool = False, candidate_limit: int = 0):
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
            
        all_candidates.append({
            "uuid": row[0],
            "title": row[1],
            "date": row[2],
            "summary": row[3],
            "importance": row[4],
            "value": row[5]
        })
    
    logger.info(f"Found {len(all_candidates)} eligible candidates.")
    
    if not all_candidates:
        logger.warning("No candidates found. Tournament cancelled.")
        return

    # 2. Stage 1: Chunked Filtering
    # Split into chunks of 50
    CHUNK_SIZE = 50
    semi_finalists = []
    
    chunks = [all_candidates[i:i + CHUNK_SIZE] for i in range(0, len(all_candidates), CHUNK_SIZE)]
    
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
        name=category_name,
        description=f"AI Curated selection for {category_name}",
        category=category_slug
    )
    await collection.save()
    await collection.clear_events() # Clear old rankings
    
    for item in final_results:
        await collection.add_event(
            event_uuid=item['uuid'],
            rank=item['rank'],
            reason=item['reason']
        )
        
    logger.info(f"🏆 Tournament Complete! Saved {len(final_results)} winners to '{category_name}'.")

