"""
Entity Extraction Service.
Extracts structured entities (Person, Organization) from event text.
"""

import json
from loguru import logger
from src.models.event import EventNode
from src.models.person import PersonNode
from src.ai.enrichment import get_ai_client

class EntityExtractor:
    """
    Extracts knowledge graph entities from event data.
    """
    
    def __init__(self):
        self.client = get_ai_client(use_reasoning=False) # Fast model is enough

    async def extract_and_link(self, event: EventNode):
        """
        Extract entities from event description and link them in the graph.
        """
        if not event.description or len(event.description) < 20:
            logger.warning(f"Skipping extraction for {event.title}: Description too short.")
            return

        prompt = f"""
        Extract the key people and their specific roles from this event description.
        
        Event: "{event.title}"
        Description: "{event.description[:2000]}"
        
        Return a JSON list of objects. Each object must have:
        - "name": Full name of the person (normalized, e.g. "William Shakespeare").
        - "role": ONE of the following precise relationship types:
            - "WROTE" (for writer, author, playwright, libretto)
            - "DIRECTED" (for director, sahneye koyan, reji)
            - "ACTED_IN" (for actors, cast, oyuncular)
            - "COMPOSED" (for composer, besteci)
            - "CONDUCTED" (for conductor, orkestra şefi)
            - "PERFORMED_BY" (for musician, soloist, orchestra member if named)
            
        Ignore generic roles like "Lighting", "Costume", "Producer" unless they are very famous.
        Focus on the CREATIVE CORE (Writer, Director, Composer, Main Cast).
        
        Example JSON:
        [
            {{"name": "Wolfgang Amadeus Mozart", "role": "COMPOSED"}},
            {{"name": "Lorenzo Da Ponte", "role": "WROTE"}}
        ]
        """
        
        try:
            # First, try to get raw text to see what it says
            # response = await self.client.generate_json(prompt, temperature=0.0) 
            # We temporarily switch to generate_text to debug JSON issues if generate_json is swallowing errors
            
            # Using generate_json directly
            response = await self.client.generate_json(prompt, temperature=0.0)
            
            # Normalize response to list
            entities = []
            if isinstance(response, list):
                entities = response
            elif isinstance(response, dict):
                # Handle single object
                if "name" in response and "role" in response:
                    entities = [response]
                # Handle wrapped list (e.g. {"key_people": [...]})
                else:
                    for key in ["people", "key_people", "entities", "results"]:
                        if key in response and isinstance(response[key], list):
                            entities = response[key]
                            break
            
            if not entities:
                # logger.warning(f"No entities found for {event.title}. Raw: {response}")
                return

            saved_count = 0
            for item in entities:
                name = item.get("name")
                role = item.get("role")
                
                if name and role:
                    # 1. Find or create Person
                    person = PersonNode.find_by_name(name)
                    if not person:
                        person = PersonNode(name=name)
                        person.save()
                        # logger.info(f"🆕 Created Person: {name}")
                    
                    # 2. Link to Event
                    success = person.save_relationship(event.uuid, role)
                    if success:
                        saved_count += 1
                        
            if saved_count > 0:
                logger.info(f"🔗 Linked {saved_count} entities for '{event.title}'")

        except Exception as e:
            logger.error(f"Error extracting entities for {event.title}: {e}")
