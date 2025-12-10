#!/usr/bin/env python3
"""
Script to forcefully wipe the FalkorDB database.
Uses the Python client to ensure the graph is actually deleted.
"""
from falkordb import FalkorDB

def wipe_database():
    print("🗑️  Connecting to FalkorDB...")
    try:
        db = FalkorDB(host="localhost", port=6379)
        graph = db.select_graph("eventgraph")
        
        print("💥 Deleting graph 'eventgraph'...")
        try:
            graph.delete()
            print("✅ Graph deleted successfully via Python client.")
        except Exception as e:
            if "Graph definition not found" in str(e):
                print("✅ Graph was already empty/non-existent.")
            else:
                print(f"⚠️  Error deleting graph: {e}")
                
        # Double check
        try:
            # Re-select to check
            g = db.select_graph("eventgraph")
            count = g.query("MATCH (n) RETURN count(n)").result_set[0][0]
            if count == 0:
                 print("✅ Verified: 0 nodes remaining.")
                 return True
            else:
                 print(f"❌ FAIL: {count} nodes still exist!")
                 return False
        except Exception:
            # If graph is gone, selecting/querying might fail or return 0, which is good
            print("✅ Verified: Graph is gone.")
            return True

    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

if __name__ == "__main__":
    import sys
    success = wipe_database()
    sys.exit(0 if success else 1)
