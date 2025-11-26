#!/bin/bash
# Start backend on port 8001

cd backend

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
source .venv/bin/activate

# Install dependencies if needed
if [ ! -f ".venv/installed" ]; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
    touch .venv/installed
fi

# Check if knowledge base is preprocessed
if [ ! -d "app/data/embeddings" ]; then
    echo "⚠️  Warning: Knowledge base not preprocessed!"
    echo "Run: python preprocess_kb.py"
    echo ""
fi

# Start server on port 8001
echo "🚀 Starting backend on http://localhost:8001"
uvicorn app.main:app --reload --port 8001
