# Makefile for EventGraph project

.PHONY: help install setup clean clean-data fclean docker-up docker-down up down scrape scrape-reviews view db-shell

# Python command (use python if in venv, otherwise python3)
PYTHON := $(shell command -v python 2> /dev/null || echo python3)

# Default target
help:
	@echo "EventGraph - Event Discovery Scraper"
	@echo ""
	@echo "🚀 Commands:"
	@echo "  make up           - Start database and initialize"
	@echo "  make down         - Stop database"
	@echo "  make scrape       - Scrape events from all sources (Biletix + Biletinial)"
	@echo "  make scrape-biletix    - Scrape events from Biletix only"
	@echo "  make scrape-biletinial - Scrape events from Biletinial only"
	@echo "  make view         - View scraped events"
	@echo "  make verify       - Verify data integrity"
	@echo "  make test         - Run tests"
	@echo "  make clean        - Clean cache files"
	@echo "  make clean-data   - Wipe database data (keeps Docker running)"
	@echo "  make fclean       - Full clean (removes venv, database, cache)"
	@echo ""
	@echo "📦 Setup:"
	@echo "  make install   - Install dependencies"
	@echo "  make setup     - Full first-time setup"

# Installation
install:
	pip install -r requirements.txt
	playwright install

# Full setup
setup: install
	@if [ ! -f .env ]; then cp .env.example .env; echo "Created .env file"; fi
	@mkdir -p logs
	docker compose up -d
	@echo "Setup complete!"

# Docker
docker-up:
	docker compose up -d

docker-down:
	docker compose down

# Clean
clean:
	@echo "🧹 Cleaning cache files..."
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type f -name "*.pyo" -delete 2>/dev/null || true
	@find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	@rm -rf htmlcov/ .coverage dist/ build/ 2>/dev/null || true
	@echo "✅ Cache cleaned"

clean-data:
	@echo "🗑️  Wiping database data..."
	@echo ""
	@if docker ps | grep -q eventgraph-falkordb; then \
		docker exec eventgraph-falkordb redis-cli FLUSHALL > /dev/null 2>&1 && \
			echo "✅ Database wiped successfully!" && \
			echo "" && \
			echo "Database is now empty. Reinitialize with:" && \
			echo "  make up"; \
	else \
		echo "❌ Database container is not running!" && \
		echo "" && \
		echo "Start the database first:" && \
		echo "  make up" && \
		exit 1; \
	fi

fclean: clean
	@echo "🗑️  Full cleanup - removing everything..."
	@echo ""
	@echo "This will remove:"
	@echo "  - Virtual environment (venv/)"
	@echo "  - Docker containers and volumes"
	@echo "  - All database data"
	@echo "  - Log files"
	@echo ""
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		echo "Stopping Docker containers..."; \
		docker compose down -v 2>/dev/null || true; \
		echo "Removing virtual environment..."; \
		rm -rf venv/; \
		echo "Removing logs..."; \
		rm -rf logs/; \
		echo "Removing debug files..."; \
		rm -f *.html *.png scrapy_page_content.html 2>/dev/null || true; \
		echo ""; \
		echo "✅ Full cleanup complete!"; \
		echo ""; \
		echo "To start fresh:"; \
		echo "  python3 -m venv venv"; \
		echo "  source venv/bin/activate"; \
		echo "  make setup"; \
	else \
		echo "Cancelled."; \
	fi

# Database
db-shell:
	docker exec -it eventgraph-falkordb redis-cli

# Quick Start Commands
up:
	@echo "🚀 Starting EventGraph..."
	@echo ""
	@if [ ! -d "venv" ]; then \
		echo "⚠️  Virtual environment not found!"; \
		echo ""; \
		echo "Please run first-time setup:"; \
		echo "  python3 -m venv venv"; \
		echo "  source venv/bin/activate"; \
		echo "  make install"; \
		echo ""; \
		exit 1; \
	fi
	@if [ -z "$$VIRTUAL_ENV" ]; then \
		echo "⚠️  Virtual environment not activated!"; \
		echo ""; \
		echo "Please activate venv:"; \
		echo "  source venv/bin/activate"; \
		echo ""; \
		exit 1; \
	fi
	@echo "📋 Step 1: Starting FalkorDB..."
	docker compose up -d falkordb
	@echo "⏳ Waiting for database to be ready..."
	@sleep 5
	@echo ""
	@echo "📋 Step 2: Initializing database..."
	$(PYTHON) src/main.py
	@echo ""
	@echo "✅ EventGraph is ready!"
	@echo ""
	@echo "Next steps:"
	@echo "  make scrape              - Scrape from all sources"
	@echo "  make scrape-biletix      - Scrape from Biletix"
	@echo "  make scrape-biletinial   - Scrape from Biletinial"
	@echo "  make view                - View scraped events"
	@echo "  make down                - Stop everything"

down:
	@echo "🛑 Stopping EventGraph..."
	docker compose down
	@echo "✅ All services stopped"

scrape:
	@echo "🕷️  Starting scrapers for all sources..."
	@echo ""
	@echo "📍 Scraping Biletix..."
	scrapy crawl biletix
	@echo ""
	@echo "📍 Scraping Biletinial..."
	scrapy crawl biletinial
	@echo ""
	@echo "✅ All scraping complete!"
	@echo ""
	@echo "View results with: make view"

scrape-biletix:
	@echo "🕷️  Starting Biletix scraper..."
	@echo ""
	scrapy crawl biletix
	@echo ""
	@echo "✅ Biletix scraping complete!"
	@echo ""
	@echo "View results with: make view"

scrape-biletinial:
	@echo "🕷️  Starting Biletinial scraper..."
	@echo ""
	scrapy crawl biletinial
	@echo ""
	@echo "✅ Biletinial scraping complete!"
	@echo ""
	@echo "View results with: make view"

view:
	@echo "📊 Events in database:"
	@echo ""
	@bash -c 'source venv/bin/activate && python src/scripts/view_events.py'

# Validation & Testing
test:
	@echo "🧪 Running tests..."
	@bash -c 'source venv/bin/activate && pytest'

# Helper for CLI
ask:
	@bash -c 'source venv/bin/activate && python ask.py'

lint:
	@echo "🔍 Running linters..."
	@echo "Checking with Black..."
	@bash -c 'source venv/bin/activate && black --check src tests ask.py'
	@echo "Checking with Pylint..."
	@bash -c 'source venv/bin/activate && pylint src ask.py || true'
	@echo "Checking with Mypy..."
	@bash -c 'source venv/bin/activate && mypy src ask.py || true'


# Validaton & Testing
clean-ai:
	@echo "🧹 Removing AI summaries..."
	@docker exec eventgraph-falkordb redis-cli GRAPH.QUERY eventgraph "MATCH (s:AISummary) DETACH DELETE s" > /dev/null
	@echo "✅ AI summaries removed!"

# Default limit covers all events
LIMIT ?= 10000
FORCE ?= 

ai-enrich:
	@echo "🤖 Generating AI summaries (Limit: $(LIMIT))..."
	@bash -c 'unset GEMINI_API_KEY && source venv/bin/activate && PYTHONPATH=. python src/scripts/enrich_events.py --limit $(LIMIT) $(FORCE)'

ai-enrich-all:
	@echo "🤖 Regenerating AI summaries for ALL events..."
	@bash -c 'unset GEMINI_API_KEY && source venv/bin/activate && PYTHONPATH=. python src/scripts/enrich_events.py --all $(FORCE)'

ai-audit:
	@bash -c 'source venv/bin/activate && PYTHONPATH=. python src/scripts/audit_ai_quality.py'

ai-collections:
	@echo "🏆 Running AI Tournaments..."
	@bash -c 'unset GEMINI_API_KEY && source venv/bin/activate && PYTHONPATH=. python src/scripts/run_tournaments.py'

verify:
	@echo "🔎 Verifying data integrity..."
	@bash -c 'source venv/bin/activate && python src/scripts/verify_data.py'
