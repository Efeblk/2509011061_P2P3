# Makefile for EventGraph project

.PHONY: help install install-dev setup test test-unit test-integration coverage lint format clean docker-up docker-down

# Default target
help:
	@echo "EventGraph - Available Commands:"
	@echo "  make install         - Install production dependencies"
	@echo "  make install-dev     - Install development dependencies"
	@echo "  make setup           - Full setup (install + docker + .env)"
	@echo "  make test            - Run all tests"
	@echo "  make test-unit       - Run unit tests only"
	@echo "  make test-integration - Run integration tests only"
	@echo "  make coverage        - Run tests with coverage report"
	@echo "  make lint            - Run linters (pylint, flake8, mypy)"
	@echo "  make format          - Format code with black"
	@echo "  make clean           - Clean cache and build files"
	@echo "  make docker-up       - Start Docker services"
	@echo "  make docker-down     - Stop Docker services"
	@echo "  make docker-logs     - Show Docker logs"

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
	docker-compose up -d
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
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

docker-restart:
	docker-compose restart

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
	python -c "from src.database.connection import db_connection; print(db_connection.get_stats())"
