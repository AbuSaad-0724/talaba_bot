#!/bin/bash
# Linux/Mac Setup Script for Talaba Bot
# Run this script to set up the bot on Linux/Mac

echo "🤖 Talaba Bot - Linux/Mac Setup Script"
echo "======================================="
echo ""

# Check Python installation
echo "Checking Python installation..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo "✅ Python found: $PYTHON_VERSION"
else
    echo "❌ Python3 not found! Please install Python 3.8 or higher."
    exit 1
fi

# Check if venv exists
echo ""
echo "Checking virtual environment..."
if [ -d "venv" ]; then
    echo "✅ Virtual environment exists"
else
    echo "⚠️  Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
fi

# Activate venv
echo ""
echo "Activating virtual environment..."
source venv/bin/activate
echo "✅ Virtual environment activated"

# Install requirements
echo ""
echo "Installing dependencies..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    echo "✅ Dependencies installed"
else
    echo "⚠️  requirements.txt not found, skipping..."
fi

# Check .env file
echo ""
echo "Checking configuration..."
if [ -f ".env" ]; then
    echo "✅ .env file exists"
else
    echo "❌ .env file not found!"
    echo "Please create .env file with:"
    echo "  BOT_TOKEN=your_bot_token_here"
    echo "  ADMIN_ID=your_telegram_id"
    echo "  GEMINI_API_KEY=your_gemini_key"
    exit 1
fi

# Initialize database
echo ""
echo "Initializing database..."
python3 -c "from database import init_db; init_db()"
echo "✅ Database initialized"

# Test bot connection
echo ""
echo "Testing bot connection..."
python3 test_ping.py

# Done
echo ""
echo "======================================="
echo "✅ Setup completed successfully!"
echo ""
echo "To start the bot, run:"
echo "  python3 main.py"
echo ""
