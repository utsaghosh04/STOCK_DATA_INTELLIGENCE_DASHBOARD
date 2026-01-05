#!/bin/bash

# Setup script for the financial data platform

echo "🚀 Setting up Financial Data Platform..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.9 or higher."
    exit 1
fi

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Initialize database
echo "🗄️  Initializing database..."
python scripts/init_db.py

# Collect initial data
echo "📊 Collecting stock market data (this may take a few minutes)..."
python scripts/collect_data.py --all

echo "✅ Setup complete!"
echo ""
echo "To start the server, run:"
echo "  source venv/bin/activate"
echo "  uvicorn app.main:app --reload"
echo ""
echo "Or use Docker:"
echo "  docker-compose up"

