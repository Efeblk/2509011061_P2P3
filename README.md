# EventGraph - Event Discovery Scraper

Web scraper for Turkish cultural events (theater, concerts, exhibitions) using graph database storage.

## What It Does

Scrapes events from Biletix and stores them in a FalkorDB graph database with:
- Event title, venue, date, price
- Duplicate detection
- Data validation

## Tech Stack

- **Scrapy + Playwright**: Web scraping with JavaScript rendering
- **FalkorDB**: Graph database (runs in Docker)
- **Python 3.10+**: Core application

## Setup (First Time)

```bash
# 1. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 2. Install dependencies
make install

# 3. Start database and initialize
make up
```

## Usage

```bash
# Always activate venv first
source venv/bin/activate

# Start database
make up

# Scrape events
make scrape

# View events
make view

# Stop database
make down
```

## Available Commands

```bash
make help      # Show all commands
make up        # Start database and initialize
make down      # Stop database
make scrape    # Scrape Biletix events
make view      # View scraped events
make db-shell  # Open database CLI (Cypher queries)
make clean     # Clean Python cache files
```

## Project Structure

```
EventGraph/
├── src/
│   ├── models/          # EventNode model
│   ├── scrapers/        # Scrapy spiders
│   │   ├── spiders/     # biletix_spider.py
│   │   ├── pipelines.py # Validation, duplicates, database
│   │   └── items.py     # EventItem definition
│   └── database/        # FalkorDB connection
├── config/              # Settings and logging
├── docker-compose.yml   # FalkorDB container
└── Makefile            # Command shortcuts
```

## How It Works

1. **Scraping**: Playwright renders JavaScript-heavy pages → Scrapy extracts data
2. **Validation**: Pipeline validates required fields (title, source)
3. **Duplicates**: Checks in-memory and database for existing events
4. **Storage**: Saves to FalkorDB as graph nodes

## Database Queries

```bash
# Open database shell
make db-shell

# Example Cypher queries:
MATCH (e:Event) RETURN e.title, e.venue, e.price LIMIT 10

MATCH (e:Event) WHERE e.price < 500 RETURN e.title, e.price

MATCH (e:Event) WHERE e.venue CONTAINS 'Zorlu' RETURN e
```

## Current Status

✅ **Working Features:**
- Biletix spider operational (12+ events per run)
- Full pipeline: scrape → validate → deduplicate → save
- Graph database storage
- Simple CLI commands

📋 **Roadmap:**
- Additional sources (Biletino, Passo)
- Price extraction from detail pages
- Category detection

## Requirements

- Python 3.10+
- Docker
- 2GB RAM minimum

## License

MIT
