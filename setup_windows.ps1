# Windows PowerShell Setup Script for Talaba Bot
# Run this script to set up the bot on Windows

Write-Host "🤖 Talaba Bot - Windows Setup Script" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Check Python installation
Write-Host "Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found! Please install Python 3.8 or higher." -ForegroundColor Red
    exit 1
}

# Check if venv exists
Write-Host ""
Write-Host "Checking virtual environment..." -ForegroundColor Yellow
if (Test-Path "venv") {
    Write-Host "✅ Virtual environment exists" -ForegroundColor Green
} else {
    Write-Host "⚠️  Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
    Write-Host "✅ Virtual environment created" -ForegroundColor Green
}

# Activate venv
Write-Host ""
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"
Write-Host "✅ Virtual environment activated" -ForegroundColor Green

# Install requirements
Write-Host ""
Write-Host "Installing dependencies..." -ForegroundColor Yellow
if (Test-Path "requirements.txt") {
    pip install -r requirements.txt
    Write-Host "✅ Dependencies installed" -ForegroundColor Green
} else {
    Write-Host "⚠️  requirements.txt not found, skipping..." -ForegroundColor Yellow
}

# Check .env file
Write-Host ""
Write-Host "Checking configuration..." -ForegroundColor Yellow
if (Test-Path ".env") {
    Write-Host "✅ .env file exists" -ForegroundColor Green
} else {
    Write-Host "❌ .env file not found!" -ForegroundColor Red
    Write-Host "Please create .env file with:" -ForegroundColor Yellow
    Write-Host "  BOT_TOKEN=your_bot_token_here" -ForegroundColor White
    Write-Host "  ADMIN_ID=your_telegram_id" -ForegroundColor White
    Write-Host "  GEMINI_API_KEY=your_gemini_key" -ForegroundColor White
    exit 1
}

# Initialize database
Write-Host ""
Write-Host "Initializing database..." -ForegroundColor Yellow
python -c "from database import init_db; init_db()"
Write-Host "✅ Database initialized" -ForegroundColor Green

# Test bot connection
Write-Host ""
Write-Host "Testing bot connection..." -ForegroundColor Yellow
python test_ping.py

# Done
Write-Host ""
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "✅ Setup completed successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "To start the bot, run:" -ForegroundColor Yellow
Write-Host "  python main.py" -ForegroundColor White
Write-Host ""
