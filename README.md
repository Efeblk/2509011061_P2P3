# EventGraph - AI Powered Event Discovery & Recommendation Engine

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Overview

EventGraph is an intelligent event discovery and recommendation system that aggregates cultural events (concerts, theater, stand-up) from distributed sources in Istanbul, models their semantic relationships using a **Knowledge Graph**, and performs qualitative analysis using **Large Language Models (LLM)**.

Unlike traditional ticket aggregation systems, EventGraph answers not just "What's available?" but also:
- *"Is this price worth it for this event?"*
- *"Which event is actually a hidden gem?"*

The system analyzes event popularity, artist reputation, and user reviews to provide **Value-Based Ranking**.

## Features

- 🕷️ **Advanced Web Scraping**: Dynamic JavaScript-rendered sites using Scrapy + Playwright
- 🔗 **Graph Database**: FalkorDB for modeling complex relationships between events, venues, and artists
- 🤖 **AI Analysis**: Google Gemini API for event quality assessment and recommendations
- 📊 **Value-Based Ranking**: 0-100 scoring based on price/performance and cultural value
- 🏗️ **SOLID Architecture**: Strong OOP design with design patterns (Strategy, Template Method, Singleton)

## Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Web Scraping** | Scrapy + Playwright | Dynamic site crawling with async I/O |
| **Database** | FalkorDB (Graph DB) | Relationship modeling and fast queries |
| **AI Analysis** | Google Gemini 1.5 Flash | Event analysis and reasoning |
| **Backend** | Python 3.10+ | Strong typing with dataclasses and protocols |
| **Infrastructure** | Docker | Environment isolation and portability |

## Project Structure

```
EventGraph/
├── src/
│   ├── models/          # Domain models (EventNode, VenueNode, etc.)
│   ├── scrapers/        # Scrapy spiders for different platforms
│   ├── ai/              # AI analysis and Gemini integration
│   ├── database/        # FalkorDB connection and OGM layer
│   └── utils/           # Helper functions and utilities
├── tests/
│   ├── unit/           # Unit tests
│   └── integration/    # Integration tests
├── config/             # Configuration files
├── docs/              # Documentation
├── docker-compose.yml # Docker services configuration
└── requirements.txt   # Python dependencies
```

## Quick Start

### Prerequisites

- Python 3.10 or higher
- Docker and Docker Compose
- Git

### Installation (One-Time Setup)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd 2509011061_P2P3
   ```

2. **Set up virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   make install
   # OR manually:
   pip install -r requirements.txt
   playwright install
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys (optional for scraping)
   ```

### Daily Usage

```bash
# 1. Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 2. Start the system
make up

# 3. Scrape events
make scrape

# 4. View results
make view

# 5. Stop when done
make down
```

## Usage

### Quick Commands

```bash
make up        # Start everything (Docker + initialize DB)
make scrape    # Scrape events from Biletix
make view      # View scraped events in terminal
make down      # Stop everything
make help      # See all available commands
```

📚 For complete command reference, see [COMMANDS.md](COMMANDS.md)

### Manual Scraping

```bash
# Scrape from Biletix
scrapy crawl biletix
```

### Querying Events (Python)

```python
from src.models.event import EventNode

# Find all events
events = EventNode.find_all()

# Find events by source
events = EventNode.find_by_source("biletix")

# Find events by category
events = EventNode.find_by_category("Tiyatro")
```

## Architecture

### Graph Schema

**Nodes:**
- `(:Event {title, date, price, ai_score, ai_verdict})`
- `(:Venue {name, city, address, capacity})`
- `(:Artist {name, genre, reputation_score})`
- `(:Tag {name})`

**Relationships:**
- `(:Artist)-[:PERFORMS_AT]->(:Event)`
- `(:Event)-[:LOCATED_AT]->(:Venue)`
- `(:Event)-[:HAS_TAG]->(:Tag)`

### AI Analysis

Events are analyzed using Google Gemini API with the following criteria:
- **Price/Performance Ratio** (0-50 points)
- **Cultural Value** (0-50 points)

**Verdicts:**
- `MUST_GO` (90-100): Exceptional value
- `WORTH_IT` (70-89): Good choice
- `MAYBE` (50-69): Consider your preferences
- `SKIP` (0-49): Not recommended

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src tests/

# Run specific test file
pytest tests/unit/test_models.py
```

### Code Quality

```bash
# Format code
black src/ tests/

# Lint
pylint src/

# Type checking
mypy src/
```

## Documentation

- [Software Design Document (SDD)](SDD.md)
- [Development Roadmap](ROADMAP.md)
- [API Documentation](docs/API.md) *(Coming soon)*

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- FalkorDB for graph database technology
- Google Gemini API for AI capabilities
- Scrapy and Playwright communities

## Contact

Project Maintainer: [Your Name]
Project Link: [GitHub Repository URL]

---

**Status:** 🚧 In Development - Phase 1 Complete
