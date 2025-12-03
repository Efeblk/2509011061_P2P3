# EventGraph - Event Discovery Scraper

[![CI](https://github.com/USERNAME/eventgraph/workflows/CI/badge.svg)](https://github.com/USERNAME/eventgraph/actions)
[![codecov](https://codecov.io/gh/USERNAME/eventgraph/branch/master/graph/badge.svg)](https://codecov.io/gh/USERNAME/eventgraph)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

Web scraper for Turkish cultural events (theater, concerts, exhibitions) using graph database storage.

## What It Does

Scrapes events from **Biletix** and **Biletinial** and stores them in a FalkorDB graph database with:
- Event title, venue, date, city, price, image
- Multi-date event support (same event, different performances)
- Duplicate detection (title + venue + date)
- Data validation and quality checks

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
make help               # Show all commands
make up                 # Start database and initialize
make down               # Stop database
make scrape             # Scrape from all sources (Biletix + Biletinial)
make scrape-biletix     # Scrape from Biletix only
make scrape-biletinial  # Scrape from Biletinial only
make view               # View scraped events
make db-shell           # Open database CLI (Cypher queries)
make clean              # Clean Python cache files
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

## Testing

Run the test suite:

```bash
# Activate venv
source venv/bin/activate

# Run all unit tests
pytest tests/unit/ -v

# Run with coverage
pytest tests/unit/ --cov=src --cov-report=term-missing

# Run specific test file
pytest tests/unit/test_pipelines.py -v

# Run specific test
pytest tests/unit/test_event_model.py::TestEventNode::test_event_creation -v
```

### Test Structure

```
tests/
├── unit/
│   ├── test_event_model.py    # EventNode model tests (10 tests)
│   └── test_pipelines.py       # Pipeline tests (18 tests)
├── integration/                 # Integration tests (future)
└── conftest.py                 # Shared fixtures
```

### CI/CD

- **GitHub Actions**: Automated testing on push/PR
- **Multiple Python versions**: Tests run on Python 3.10, 3.11, 3.12
- **Code coverage**: Tracked with Codecov
- **Code quality**: Linting with flake8, black, mypy

## Data Verification

Verify scraping quality:

```bash
source venv/bin/activate
python verify_scraping.py
```

This generates a comprehensive report with:
- Event counts by source
- Data completeness checks
- Duplicate detection
- Sample events for manual inspection
- Date format analysis
- URL validation

## Current Status

✅ **Working Features:**
- **Two sources**: Biletix (229 events) + Biletinial (1,207 events)
- **Multi-date support**: Same event with different dates stored separately
- **Duplicate detection**: Works across scraper runs (title + venue + date)
- **Full pipeline**: scrape → validate → deduplicate → save
- **Graph database storage**: FalkorDB with Cypher queries
- **Simple CLI commands**: Make-based workflow
- **Unit tests**: 28 tests with 100% pass rate
- **CI/CD**: GitHub Actions with automated testing
- **Data verification**: Quality checking script

📋 **Roadmap:**
- Integration tests with database
- AI-powered event recommendations
- Additional sources (Passo, Mobilet)
- Price extraction from detail pages
- Web API for event queries

## Requirements

- Python 3.10+
- Docker
- 2GB RAM minimum
- Playwright browsers (installed automatically)

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Run tests (`pytest tests/unit/ -v`)
4. Commit your changes (`git commit -m 'Add amazing feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

## License

MIT
