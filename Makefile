# Makefile for EventGraph project

.PHONY: help install install-dev setup test test-unit test-integration coverage lint format clean docker-up docker-down up down scrape view

# Python command (use python if in venv, otherwise python3)
PYTHON := $(shell command -v python 2> /dev/null || echo python3)

# Default target
help:
	@echo "EventGraph - Available Commands:"
	@echo ""
	@echo "🚀 Quick Start:"
	@echo "  make up              - Start everything (Docker + init database)"
	@echo "  make down            - Stop everything"
	@echo "  make scrape          - Run Biletix scraper"
	@echo "  make view            - View scraped events"
	@echo ""
	@echo "📦 Setup:"
	@echo "  make install         - Install production dependencies"
	@echo "  make install-dev     - Install development dependencies"
	@echo "  make setup           - Full setup (install + docker + .env)"
	@echo ""
	@echo "🧪 Testing:"
	@echo "  make test            - Run all tests"
	@echo "  make test-unit       - Run unit tests only"
	@echo "  make test-integration - Run integration tests only"
	@echo "  make coverage        - Run tests with coverage report"
	@echo ""
	@echo "🔍 Code Quality:"
	@echo "  make lint            - Run linters (pylint, flake8, mypy)"
	@echo "  make format          - Format code with black"
	@echo "  make clean           - Clean cache and build files"
	@echo ""
	@echo "🐳 Docker:"
	@echo "  make docker-up       - Start Docker services"
	@echo "  make docker-down     - Stop Docker services"
	@echo "  make docker-logs     - Show Docker logs"
	@echo ""
	@echo "💾 Database:"
	@echo "  make db-shell        - Open database CLI"
	@echo "  make db-stats        - Show database statistics"

# Installation
install:
	pip install -r requirements.txt
	playwright install

install-dev:
	pip install -r requirements-dev.txt
	playwright install

# Full setup
setup: install-dev
	@if [ ! -f .env ]; then cp .env.example .env; echo "Created .env file"; fi
	@mkdir -p logs scraped_data
	docker compose up -d
	@echo "Setup complete! Edit .env file with your API keys."

# Testing
test:
	pytest

test-unit:
	pytest tests/unit -m unit

test-integration:
	pytest tests/integration -m integration

coverage:
	pytest --cov=src --cov-report=html --cov-report=term

# Code Quality
lint:
	pylint src/
	flake8 src/
	mypy src/

format:
	black src/ tests/

# Docker
docker-up:
	docker compose up -d

docker-down:
	docker compose down

docker-logs:
	docker compose logs -f

docker-restart:
	docker compose restart

# Clean
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf dist/
	rm -rf build/

# Database
db-shell:
	docker exec -it eventgraph-falkordb redis-cli

db-stats:
	$(PYTHON) -c "from src.database.connection import db_connection; print(db_connection.get_stats())"

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

scrape-test:
	@echo "🧪 Running test scraper (creates dummy events)..."
	@echo ""
	scrapy crawl test
	@echo ""
	@echo "✅ Test scraping complete!"
	@echo ""
	@echo "View results with: make view"

view:
	@echo "📊 Viewing scraped events..."
	@echo ""
	$(PYTHON) quick_check.py
