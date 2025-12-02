# EventGraph - Usage Guide

## 🎯 Three Ways to Run

### Method 1: Using Make (Recommended) ⭐

```bash
source venv/bin/activate
make up          # Start everything
make scrape      # Scrape events
make view        # View results
make down        # Stop
```

### Method 2: Using Start Script

```bash
source venv/bin/activate
./start.sh                  # Start
scrapy crawl biletix        # Scrape
python test_scraper.py      # View
docker-compose down         # Stop
```

### Method 3: Manual Commands

```bash
source venv/bin/activate
docker-compose up -d falkordb
sleep 5
python src/main.py
scrapy crawl biletix
python test_scraper.py
docker-compose down
```

---

## 📊 What Happens When You Run

### `make up`
```
🚀 Starting EventGraph...
📋 Step 1: Starting FalkorDB...         ← Docker container starts
⏳ Waiting for database to be ready...  ← Wait 5 seconds
📋 Step 2: Initializing database...     ← Create indexes
✅ EventGraph is ready!                 ← Ready to scrape
```

### `make scrape`
```
🕷️  Starting Biletix scraper...
[biletix] INFO: Spider opened             ← Connects to Biletix
[biletix] INFO: Scraped event #1: Kel Diva
[biletix] INFO: ✓ Saved to database      ← Saves to FalkorDB
[biletix] INFO: Scraped event #2: Kral Lear
...
[biletix] INFO: Total events scraped: 10
✅ Scraping complete!
```

### `make view`
```
📊 Viewing scraped events...

📊 Current Database Stats:
   Events: 10                            ← Number of events
   Total nodes: 10
   Memory: 2.5M

📋 Found 10 events:                      ← Lists all events

1. Kel Diva
   Venue: Zorlu PSM
   Date: 2024-12-15
   Price: 850.0 TL
   Category: Tiyatro
   Source: biletix
   URL: https://biletix.com/...
```

---

## 🔄 Complete Workflow Diagram

```
┌─────────────────────────────────────────────────┐
│  1. make up                                     │
│     ↓                                           │
│  Start FalkorDB Container                       │
│     ↓                                           │
│  Initialize Database (create indexes)           │
│     ↓                                           │
│  ✅ System Ready                                │
└─────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────┐
│  2. make scrape                                 │
│     ↓                                           │
│  Open Biletix.com/tiyatro                       │
│     ↓                                           │
│  Playwright renders JavaScript                  │
│     ↓                                           │
│  Extract: title, venue, date, price             │
│     ↓                                           │
│  Validate data                                  │
│     ↓                                           │
│  Check for duplicates                           │
│     ↓                                           │
│  Save as EventNode in FalkorDB                  │
│     ↓                                           │
│  ✅ 10 events saved                             │
└─────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────┐
│  3. make view                                   │
│     ↓                                           │
│  Query FalkorDB: MATCH (e:Event) RETURN e       │
│     ↓                                           │
│  Display events in terminal                     │
│     ↓                                           │
│  ✅ See all scraped events                      │
└─────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────┐
│  4. make down                                   │
│     ↓                                           │
│  Stop FalkorDB container                        │
│     ↓                                           │
│  ✅ System stopped (data persists!)             │
└─────────────────────────────────────────────────┘
```

---

## 🗂️ Data Flow

```
Biletix.com
    ↓
[BiletixSpider]
    ↓
{EventItem}
    title: "Kel Diva"
    venue: "Zorlu PSM"
    price: 850.0
    ↓
[ValidationPipeline] → ✅ Valid
    ↓
[DuplicatesPipeline] → ✅ Unique
    ↓
[FalkorDBPipeline]
    ↓
FalkorDB Graph:
    (:Event {
        uuid: "123-456-789",
        title: "Kel Diva",
        venue: "Zorlu PSM",
        price: 850.0,
        source: "biletix"
    })
```

---

## 🎓 Understanding Each Component

### FalkorDB (Graph Database)
- Runs in Docker container
- Port: 6379 (same as Redis)
- Stores events as graph nodes
- Data persists even after `make down`

### Scrapy Spider
- Uses Playwright for JavaScript rendering
- Extracts data using CSS selectors
- Returns EventItem objects

### Pipelines (3 stages)
1. **Validation**: Checks data quality
2. **Duplicates**: Prevents duplicate events
3. **FalkorDB**: Saves to database

### EventNode Model
- Python dataclass
- Maps to graph node
- Has CRUD methods (save, delete, find)

---

## 💡 Common Tasks

### Scrape More Events
```bash
make scrape    # Run multiple times
```

### View Specific Category
```python
from src.models.event import EventNode
events = EventNode.find_by_category("Tiyatro")
```

### Count Events
```bash
make db-stats
```

### Clear All Data
```python
from src.database.connection import db_connection
db_connection.clear_graph()  # ⚠️ Destructive!
```

### Query with Cypher
```bash
make db-shell
GRAPH.QUERY eventgraph "MATCH (e:Event) RETURN e.title, e.price"
```

---

## 🐛 Debugging

### Check if Database is Running
```bash
docker-compose ps
# Should show: eventgraph-falkordb   running
```

### View Database Logs
```bash
docker-compose logs -f falkordb
```

### Test Database Connection
```bash
python src/main.py
# Should show: ✓ Database connection successful
```

### Check Spider Logs
```bash
scrapy crawl biletix --loglevel=DEBUG
```

---

## 📈 Performance

| Metric | Value |
|--------|-------|
| Events per run | ~10 (limited for testing) |
| Scraping time | ~30-60 seconds |
| Database size | ~2-5 MB for 100 events |
| Memory usage | <100 MB |

---

## 🎯 Next Steps

1. ✅ **You are here**: Basic scraper working
2. 📊 Add more data sources (Biletino, etc.)
3. 🤖 Integrate AI analysis (Phase 3)
4. 🔗 Add Venue/Artist nodes and relationships
5. 📈 Build recommendation engine
6. 🌐 Create API/Web interface

---

## 🆘 Quick Help

```bash
make help          # See all commands
make view          # View scraped data
make db-stats      # Database statistics
make db-shell      # Open database CLI
make clean         # Clean cache files
```

For detailed troubleshooting, see [COMMANDS.md](COMMANDS.md)

---

**Ready to try it?**

```bash
source venv/bin/activate
make up
make scrape
make view
```

🎉 That's it! You now have working event scraper with graph database!
