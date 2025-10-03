@echo off
REM Development startup script for LLM Dynamic Site on Windows
REM This script starts memcached and the FastAPI application

echo 🚀 Starting LLM Dynamic Site development environment...

REM Check if virtual environment exists
if not exist ".venv" (
    echo ❌ Virtual environment not found. Please run setup.py first:
    echo    python setup.py
    exit /b 1
)

REM Note about memcached on Windows
echo 🔧 Note: Please ensure memcached is installed and running on Windows
echo    Download from: https://memcached.org/downloads
echo    Or use Docker: docker run -d -p 11211:11211 memcached
echo.

REM Activate virtual environment
echo 🌐 Activating virtual environment...
call .venv\Scripts\activate

REM Check if dependencies are installed
python -c "import fastapi" 2>nul
if errorlevel 1 (
    echo ❌ Dependencies not installed. Installing now...
    pip install -e .
)

REM Start the application
echo 🎉 LLM Dynamic Site is starting...
echo 📱 Visit http://localhost:8000/about/ to see the demo
echo 📚 API docs available at http://localhost:8000/api/docs
echo.
echo Press Ctrl+C to stop the server

fastapi dev app/main.py