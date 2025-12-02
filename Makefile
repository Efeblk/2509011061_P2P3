# Makefile for EventGraph project

.PHONY: help install setup clean fclean docker-up docker-down up down scrape view db-shell

# Python command (use python if in venv, otherwise python3)
PYTHON := $(shell command -v python 2> /dev/null || echo python3)

# Default target
help:
	@echo "EventGraph - Event Discovery Scraper"
	@echo ""
	@echo "🚀 Commands:"
	@echo "  make up        - Start database and initialize"
	@echo "  make down      - Stop database"
	@echo "  make scrape    - Scrape events from Biletix"
	@echo "  make view      - View scraped events"
	@echo "  make db-shell  - Open database CLI (Cypher queries)"
	@echo "  make clean     - Clean cache files"
	@echo "  make fclean    - Full clean (removes venv, database, cache)"
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
	@echo "  make scrape    - Scrape events from Biletix"
	@echo "  make view      - View scraped events"
	@echo "  make down      - Stop everything"

down:
	@echo "🛑 Stopping EventGraph..."
	docker compose down
	@echo "✅ All services stopped"

scrape:
	@echo "🕷️  Starting Biletix scraper..."
	@echo ""
	scrapy crawl biletix
	@echo ""
	@echo "✅ Scraping complete!"
	@echo ""
	@echo "View results with: make view"

view:
	@echo "📊 Events in database:"
	@echo ""
	@$(PYTHON) -c "import redis; from falkordb import FalkorDB; db = FalkorDB(host='localhost', port=6379); g = db.select_graph('eventgraph'); r = g.query('MATCH (e:Event) RETURN e.title, e.venue, e.price, e.date, e.source ORDER BY e.title LIMIT 50'); print(f'\nTotal: {len(r.result_set)} events\n'); [print(f'{i+1}. {row[0]}\n   Venue: {row[1]}\n   Price: {row[2] or \"N/A\"} TL\n   Date: {row[3]}\n   Source: {row[4]}\n') for i, row in enumerate(r.result_set)]"
