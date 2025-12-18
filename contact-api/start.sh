#!/bin/bash
# Quick start script for Contact API

set -e

echo "==================================="
echo "Triple C Contact API - Starting"
echo "==================================="

# Check if .env exists
if [ ! -f .env ]; then
    echo "ERROR: .env file not found!"
    echo "Please copy .env.example to .env and configure it:"
    echo "  cp .env.example .env"
    echo "  nano .env"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install/upgrade dependencies
echo "Installing dependencies..."
pip install -r requirements.txt --quiet

# Check if database exists
if [ ! -f "contact_submissions.db" ]; then
    echo "Database will be created on first run..."
fi

echo ""
echo "==================================="
echo "Starting API server..."
echo "==================================="
echo ""
echo "API will be available at:"
echo "  http://localhost:8000"
echo ""
echo "API Documentation:"
echo "  http://localhost:8000/docs"
echo ""
echo "Press CTRL+C to stop the server"
echo ""

# Start the server
python main.py
