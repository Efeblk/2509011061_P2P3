from falkordb import FalkorDB

def show_missing_prices():
    try:
        db = FalkorDB(host="localhost", port=6379)
        g = db.select_graph("eventgraph")
        
        query = "MATCH (e:Event) WHERE e.price IS NULL RETURN e.title, e.url, e.date LIMIT 5"
        result = g.query(query)
        
        print("Events with Missing Prices (Potential Sold Out/Free):")
        print("-" * 80)
        for row in result.result_set:
            print(f"Title: {row[0]}")
            print(f"Date:  {row[2]}")
            print(f"URL:   {row[1]}")
            print("-" * 80)
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    show_missing_prices()
