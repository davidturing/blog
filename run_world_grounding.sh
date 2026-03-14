#!/bin/bash

# World Grounding & Proactive Exploration System
# One-click startup script for Mac mini M4

set -e  # Exit on any error

echo "🚀 Starting World Grounding System..."

# Check if we're in the right directory
if [ ! -f "sensors/external_watcher.py" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

# Create necessary directories
mkdir -p config data memory logs

# Check if Python virtual environment exists
if [ ! -d "venv" ]; then
    echo "🏗️  Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Create log directory with proper permissions
mkdir -p logs
chmod 755 logs

# Run the external watcher
echo "🔍 Starting world perception cycle..."
python -m sensors.external_watcher

echo "✅ World Grounding System completed successfully!"