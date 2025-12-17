"""
Venue enrichment service.
Uses AI to determine venue characteristics (indoors/outdoors, vibe).
"""

import asyncio
import json
from loguru import logger
from typing import Optional

from src.models.venue import VenueNode
from src.ai.enrichment import get_ai_client
from src.database.connection import db_connection


class VenueEnricher:
    """
    Service to enrich venues with intelligence.
    """

    def __init__(self):
        self.client = get_ai_client(use_reasoning=False)  # Use fast model

    async def get_or_create_venue(self, venue_name: str, city: str = "İstanbul") -> VenueNode:
        """
        Get existing venue or create a new one and enrich it.
        """
        # Check if exists
        venue = VenueNode.find_by_name(venue_name)
        if venue:
            return venue

        # Create new
        logger.info(f"🆕 New venue detected: {venue_name}")
        venue = VenueNode(name=venue_name, city=city)
        
        # Enrich immediately
        await self.enrich_venue(venue)
        
        # Save
        venue.save()
        return venue

    async def enrich_venue(self, venue: VenueNode):
        """
        Enrich venue with AI data.
        """
        prompt = f"""
        You are a venue intelligence expert for {venue.city}.
        
        Venue: "{venue.name}"
        
        Task: Analyze this venue and return a JSON object.
        
        Fields:
        - is_outdoors: boolean (true if primarily outdoors/open-air, false if indoors)
        - vibe: string (e.g. "Historical", "Modern", "Intimate", "Grand", "Underground")
        - capacity: integer estimate (approximate)
        
        Rules:
        - "Harbiye Cemil Topuzlu" -> is_outdoors: true
        - "Maximum Uniq Açıkhava" -> is_outdoors: true
        - "Zorlu PSM" -> is_outdoors: false
        - If unsure, guess based on the name (e.g. "Açıkhava" means Open Air).
        
        Return ONLY valid JSON.
        """

        try:
            response = await self.client.generate_json(prompt, temperature=0.1)
            
            if response:
                venue.is_outdoors = response.get("is_outdoors", False)
                venue.vibe = response.get("vibe", "Unknown")
                venue.capacity = response.get("capacity", 0)
                
                logger.info(f"✨ Enriched '{venue.name}': Outdoors={venue.is_outdoors}, Vibe={venue.vibe}")
            else:
                logger.warning(f"Failed to enrich venue: {venue.name}")

        except Exception as e:
            logger.error(f"Error enriching venue {venue.name}: {e}")
