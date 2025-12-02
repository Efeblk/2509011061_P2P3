# Quick Start - See Scraper in Action! 🚀

## Setup (One-time)

### 1. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # Mac/Linux
# or
venv\Scripts\activate  # Windows
```

### 2. Install Dependencies
```bash
make setup
# or manually:
pip install -r requirements.txt
playwright install
```

### 3. Start FalkorDB
```bash
docker-compose up -d falkordb
```

### 4. Configure Environment
```bash
cp .env.example .env
# Edit .env if needed (Gemini API key not required for scraping)
```

## Run Scraper 🕷️

### Scrape Events from Biletix
```bash
scrapy crawl biletix
```

You should see:
- ✅ Spider connecting to Biletix
- ✅ Events being scraped
- ✅ Data validation
- ✅ Saving to FalkorDB

### View Scraped Data
```bash
python test_scraper.py
```

This will show:
- 📊 Database statistics
- 📋 List of all scraped events
- 🎭 Event details (title, venue, price, etc.)

## Verify in Database

### Option 1: Using Python
```bash
python test_scraper.py
```

### Option 2: Using Redis CLI
```bash
make db-shell
# Then in redis-cli:
GRAPH.QUERY eventgraph "MATCH (e:Event) RETURN e LIMIT 5"
```

### Option 3: View Stats
```bash
make db-stats
```

## Troubleshooting

### "Database connection failed"
```bash
docker-compose up -d falkordb
# Wait 10 seconds for it to start
docker-compose ps  # Should show falkordb as "running"
```

### "No module named 'src'"
```bash
# Make sure you're in the project root
pwd  # Should show: .../2509011061_P2P3

# Make sure venv is activated
which python  # Should show: .../venv/bin/python
```

### "Playwright not installed"
```bash
playwright install chromium
```

## What's Happening? 🔍

1. **Biletix Spider** visits biletix.com/tiyatro
2. **Playwright** renders the JavaScript page
3. **Parser** extracts event data (title, venue, date, price)
4. **Validation Pipeline** checks data quality
5. **Duplicates Pipeline** prevents duplicates
6. **FalkorDB Pipeline** saves events as nodes in the graph

## Next Steps

- Add more spiders for different sites
- Implement AI analysis (Phase 3)
- Query relationships in the graph
- Build recommendation system

## Current Limitations

- Only scrapes theater category
- Limited to first 10 events (for testing)
- No AI scoring yet
- No venue/artist nodes yet (just events)

Ready to see it work? Run: `scrapy crawl biletix` 🎭
