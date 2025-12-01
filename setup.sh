#!/bin/bash

# EventGraph Setup Script
# This script sets up the development environment

set -e

echo "======================================"
echo "EventGraph - Setup Script"
echo "======================================"
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
required_version="3.10"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "Error: Python $required_version or higher is required (found $python_version)"
    exit 1
fi
echo "✓ Python $python_version found"

# Check if Docker is installed
echo "Checking Docker..."
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed"
    echo "Please install Docker from https://www.docker.com/get-started"
    exit 1
fi
echo "✓ Docker found"

# Check if Docker Compose is installed
echo "Checking Docker Compose..."
if ! command -v docker-compose &> /dev/null; then
    echo "Error: Docker Compose is not installed"
    exit 1
fi
echo "✓ Docker Compose found"

# Create virtual environment
echo ""
echo "Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip -q

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt -q
pip install -r requirements-dev.txt -q
echo "✓ Dependencies installed"

# Install Playwright browsers
echo "Installing Playwright browsers..."
playwright install chromium
echo "✓ Playwright browsers installed"

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cp .env.example .env
    echo "✓ .env file created"
    echo "⚠ Please edit .env file and add your API keys"
else
    echo "✓ .env file already exists"
fi

# Create necessary directories
echo "Creating directories..."
mkdir -p logs scraped_data tests/test_data
echo "✓ Directories created"

# Start Docker services
echo ""
echo "Starting Docker services..."
docker-compose up -d
echo "✓ Docker services started"

# Wait for FalkorDB to be ready
echo "Waiting for FalkorDB to be ready..."
sleep 5

# Test database connection
echo "Testing database connection..."
python3 -c "from src.database.connection import db_connection; assert db_connection.health_check(), 'Database connection failed'" && echo "✓ Database connection successful" || echo "✗ Database connection failed"

echo ""
echo "======================================"
echo "Setup Complete!"
echo "======================================"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your API keys"
echo "2. Activate virtual environment: source venv/bin/activate"
echo "3. Run tests: pytest"
echo "4. Start application: python src/main.py"
echo ""
echo "Useful commands:"
echo "- make help          # Show available commands"
echo "- make test          # Run tests"
echo "- make docker-logs   # View Docker logs"
echo ""
