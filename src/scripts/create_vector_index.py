import json
import asyncio
import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from src.database.connection import db_connection
from src.models.ai_summary import AISummaryNode
from config.settings import settings

def migrate_embeddings():
    """
    Migrate existing string-based embeddings to native Vector arrays
    and create the vector index.
    """
    print("🚀 Starting Vector Index Migration...")

    # 1. Detect Dimension from Data or Settings
    print("🔍 Detecting embedding dimension...")
    
    # Try to find one real embedding
    dimension = None
    query = "MATCH (s:AISummary) WHERE s.embedding IS NOT NULL RETURN s.embedding LIMIT 1"
    res = db_connection.execute_query(query)
    
    if res and res.result_set:
        sample_emb = res.result_set[0][0]
        if isinstance(sample_emb, str):
            try:
                vec = json.loads(sample_emb)
                dimension = len(vec)
                print(f"✅ Detected dimension from data: {dimension}")
            except:
                pass
        elif isinstance(sample_emb, list):
             dimension = len(sample_emb)
             print(f"✅ Detected dimension from data (already list): {dimension}")

    if not dimension:
        # Fallback to settings
        provider = settings.ai.provider
        # Fallback to settings
        # User confirmed we don't use Gemini, so default to Ollama/mxbai
        dimension = 1024 
        print(f"⚠️ No data found. Defaulting to Ollama (mxbai) dimension: {dimension}")

    # 2. Convert Strings to Vectors in Bulk
    print("🔄 Converting JSON strings to Native Vectors in DB...")
    
    # Fetch all nodes with string embeddings (checking if it starts with '[')
    # Note: FalkorDB doesn't have robust typeof check for properties in Cypher yet easily, 
    # so we fetch all and check in python.
    query_all = "MATCH (s:AISummary) WHERE s.embedding IS NOT NULL RETURN s.uuid, s.embedding"
    res = db_connection.execute_query(query_all)
    
    count = 0
    if res and res.result_set:
        for row in res.result_set:
            uuid = row[0]
            emb = row[1]
            
            if isinstance(emb, str):
                try:
                    vec = json.loads(emb)
                    # Update to list
                    update_query = "MATCH (s:AISummary {uuid: $uuid}) SET s.embedding = $vec"
                    db_connection.execute_query(update_query, {"uuid": uuid, "vec": vec})
                    count += 1
                    if count % 100 == 0:
                        print(f"   Processed {count} nodes...")
                except Exception as e:
                    print(f"   ❌ Error converting node {uuid}: {e}")
    
    print(f"✅ Converted {count} nodes to vector format.")

    # 3. Create Index
    print(f"🏗️ Creating Vector Index (dim={dimension})...")
    AISummaryNode.create_vector_index(dimension)
    
    print("✅ Migration Complete!")

if __name__ == "__main__":
    migrate_embeddings()
