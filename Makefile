# Makefile for EventGraph project
SHELL := /bin/bash

.PHONY: help install setup clean clean-data fclean docker-up docker-down up down scrape view db-shell

# Python command (use python if in venv, otherwise python3)
PYTHON := $(shell command -v python 2> /dev/null || echo python3)

# Docker Compose command (check for "docker compose" first, then "docker-compose")
DOCKER_COMPOSE := $(shell docker compose version > /dev/null 2>&1 && echo "docker compose" || echo "docker-compose")

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
	@echo "🤖 AI Commands:"
	@echo "  make ask [QUERY=...] - Ask for recommendations (interactive or direct)"
	@echo "  make ai-enrich       - Generate AI summaries and enrich venues"
	@echo "  make ai-embeddings   - Regenerate embeddings only (fast)"
	@echo "  make ai-collections  - Run AI tournaments"
	@echo "  make ai-view         - Audit AI quality"
	@echo ""
	@echo "📦 Setup:"
	@echo "  make install   - Install dependencies"
	@echo "  make setup     - Full first-time setup"

# Installation
install:
	venv/bin/pip install -r requirements.txt
	venv/bin/playwright install
	venv/bin/playwright install-deps

# Full setup
setup: install
	@if [ ! -f .env ]; then cp .env.example .env; echo "Created .env file"; fi
	@mkdir -p logs
	$(DOCKER_COMPOSE) up -d
	@echo "Setup complete!"

# Docker
docker-up:
	$(DOCKER_COMPOSE) up -d

docker-down:
	$(DOCKER_COMPOSE) down

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
	@echo ""
	@venv/bin/python src/scripts/wipe_db.py
	@echo ""
	@echo "Database is now empty. Reinitialize with:"
	@echo "  make up"

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
		$(DOCKER_COMPOSE) down -v 2>/dev/null || true; \
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
	$(DOCKER_COMPOSE) up -d falkordb
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
	$(DOCKER_COMPOSE) down
	@echo "✅ All services stopped"

scrape:
	@echo "🕷️  Running Scrapers (Biletix & Biletinial)..."
	@if [ -n "$(LIMIT)" ]; then \
		echo "🔍 Limit set to $(LIMIT) events per spider"; \
		# venv/bin/scrapy crawl biletix -a limit=$(LIMIT) & \
		venv/bin/scrapy crawl biletinial -a limit=$(LIMIT) & \
		wait; \
	else \
		# venv/bin/scrapy crawl biletix & \
		venv/bin/scrapy crawl biletinial & \
		wait; \
	fi
	@echo "✅ Scraping complete!"

scrape-price:
	@echo "💰 Updating missing prices..."
	@venv/bin/scrapy crawl biletinial_price_updater
	@echo "✅ Price update complete!"
	@echo ""
	@echo "View results with: make view"

scrape-biletix:
	@echo "🕷️  Starting Biletix scraper..."
	@echo ""
	venv/bin/scrapy crawl biletix
	@echo ""
	@echo "✅ Biletix scraping complete!"
	@echo ""
	@echo "View results with: make view"

scrape-biletinial:
	@echo "🕷️  Starting Biletinial scraper..."
	@echo ""
	venv/bin/scrapy crawl biletinial
	@echo ""
	@echo "✅ Biletinial scraping complete!"
	@echo ""
	@echo "View results with: make view"

view:
	@echo "📊 Events in database:"
	@echo ""
	@venv/bin/python src/scripts/view_events.py

# Validation & Testing
test:
	@echo "🧪 Running tests..."
	@venv/bin/pytest

# Helper for CLI
# Helper for CLI
ask:
	@if [ -n "$(QUERY)" ]; then \
		venv/bin/python ask.py "$(QUERY)"; \
	else \
		venv/bin/python ask.py; \
	fi

lint:
	@echo "🔍 Running linters..."
	@echo "Checking with Black..."
	@venv/bin/black --check src tests ask.py
	@echo "Checking with Pylint..."
	@venv/bin/pylint src ask.py || true
	@echo "Checking with Mypy..."
	@venv/bin/mypy src ask.py || true


# Validaton & Testing
clean-ai:
	@echo "🧹 Removing AI summaries..."
	@export PYTHONPATH=. && venv/bin/python src/scripts/clean_ai.py

clean-collections:
	@echo "🧹 Removing Collections..."
	@export PYTHONPATH=. && venv/bin/python src/scripts/clean_collections.py

# Default limit covers all events
LIMIT ?= 10000
FORCE ?= 

ai-enrich:
	@echo "🤖 Generating AI summaries (Limit: $(LIMIT))..."
	@export PYTHONPATH=. && venv/bin/python src/scripts/enrich_events.py --limit $(LIMIT) $(FORCE)
	@make venue-enrich

venue-enrich:
	@echo "🏟️  Enriching venues..."
	@export PYTHONPATH=. && venv/bin/python src/scripts/enrich_venues.py

enrich-entities:
	@echo "🕸️  Enriching entities (Knowledge Graph)..."
	@export PYTHONPATH=. && venv/bin/python src/scripts/enrich_entities.py --limit $(LIMIT)

entity-enrich: enrich-entities

ai-enrich-all:
	@echo "🤖 Regenerating AI summaries for ALL events..."
	@export PYTHONPATH=. && venv/bin/python src/scripts/enrich_events.py --all $(FORCE)
	@make venue-enrich

ai-embeddings:
	@echo "🧠 Regenerating embeddings only..."
	@export PYTHONPATH=. && venv/bin/python src/scripts/update_embeddings_only.py

ai-view:
	@export PYTHONPATH=. && venv/bin/python src/scripts/audit_ai_quality.py

ai-collections:
	@echo "🏆 Running AI Tournaments..."
	@export PYTHONPATH=. && venv/bin/python src/scripts/run_tournaments.py

verify:
	@echo "🔎 Verifying data integrity..."
	@venv/bin/python src/scripts/verify_data.py
