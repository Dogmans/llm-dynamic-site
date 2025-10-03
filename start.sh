#!/bin/bash

# Development startup script for LLM Dynamic Site
# This script starts memcached and the FastAPI application

echo "🚀 Starting LLM Dynamic Site development environment..."

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check if memcached is installed
if ! command_exists memcached; then
    echo "❌ Memcached not found. Please install memcached:"
    echo "   Ubuntu/Debian: sudo apt-get install memcached"
    echo "   CentOS/RHEL: sudo yum install memcached"
    echo "   macOS: brew install memcached"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "❌ Virtual environment not found. Please run setup.py first:"
    echo "   python setup.py"
    exit 1
fi

# Start memcached if not running
if ! pgrep -x "memcached" > /dev/null; then
    echo "🔧 Starting memcached..."
    memcached -d -m 64 -p 11211 -u $(whoami) 2>/dev/null
    sleep 2
    
    if pgrep -x "memcached" > /dev/null; then
        echo "✅ Memcached started successfully"
    else
        echo "❌ Failed to start memcached"
        exit 1
    fi
else
    echo "✅ Memcached is already running"
fi

# Activate virtual environment and start FastAPI
echo "🌐 Starting FastAPI application..."
source .venv/bin/activate

# Check if dependencies are installed
if ! python -c "import fastapi" 2>/dev/null; then
    echo "❌ Dependencies not installed. Installing now..."
    pip install -e .
fi

# Start the application
echo "🎉 LLM Dynamic Site is starting..."
echo "📱 Visit http://localhost:8000/about/ to see the demo"
echo "📚 API docs available at http://localhost:8000/api/docs"
echo ""
echo "Press Ctrl+C to stop the server"

fastapi dev app/main.py