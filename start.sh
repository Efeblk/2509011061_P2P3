#!/bin/bash

# EventGraph - Simple Start Script
# For users who don't have 'make' installed

set -e

echo "🚀 Starting EventGraph..."
echo ""

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Please run setup first:"
    echo "  python -m venv venv"
    echo "  source venv/bin/activate"
    echo "  pip install -r requirements.txt"
    echo "  playwright install"
    exit 1
fi

# Check if venv is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo "⚠️  Virtual environment not activated!"
    echo "Please run: source venv/bin/activate"
    exit 1
fi

echo "📋 Step 1: Starting FalkorDB..."
docker-compose up -d falkordb

echo "⏳ Waiting for database to be ready..."
sleep 5

echo ""
echo "📋 Step 2: Initializing database..."
python src/main.py

echo ""
echo "✅ EventGraph is ready!"
echo ""
echo "Next steps:"
echo "  scrapy crawl biletix   - Scrape events"
echo "  python test_scraper.py - View results"
echo "  docker-compose down    - Stop everything"
