
import asyncio
import json
from loguru import logger
from src.database.connection import db_connection
from src.ai.ollama_client import ollama_client
from config.settings import settings
from datetime import datetime

async def update_embeddings():
    logger.info("Starting embedding update with venue info...")
    
    # Update the query to fetch venue
    query = "MATCH (e:Event) RETURN e.uuid, e.title, e.description, e.category, e.venue"
    result = db_connection.execute_query(query)
    
    if not result or not result.result_set:
        logger.error("No events found!")
        return

    records = result.result_set
    total = len(records)
    logger.info(f"Found {total} events to process.")
    
    updated = 0
    failed = 0
    
    for i, record in enumerate(records):
        uuid = record[0]
        title = record[1]
        description = record[2]
        category = record[3]
        venue = record[4] # Get venue from property

        # Generate embedding text
        embedding_text = f"{title}. {venue or ''}. {category or ''}. {description or ''}"
        
        try:
            # Generate embedding using the configured embedding model
            embedding_vector = ollama_client.embed(embedding_text)
            
            if embedding_vector:
                embedding_json = json.dumps(embedding_vector)
                
                # Update AISummary node with new embedding
                # We target AISummary nodes directly
                update_query = """
                MATCH (e:Event {uuid: $uuid})-[:HAS_AI_SUMMARY]->(s:AISummary)
                SET s.embedding = $embedding, s.updated_at = $timestamp
                """
                
                timestamp = datetime.utcnow().isoformat()
                db_connection.execute_query(update_query, {"uuid": uuid, "embedding": embedding_json, "timestamp": timestamp})
                updated += 1
                if i % 100 == 0:
                    logger.info(f"Processed {i}/{total} events...")
            else:
                failed += 1
                logger.warning(f"Failed to generate embedding for {title}")
                
        except Exception as e:
            failed += 1
            logger.error(f"Error processing {title}: {e}")

    logger.info(f"Finished! Updated: {updated}, Failed: {failed}")

if __name__ == "__main__":
    asyncio.run(update_embeddings())
