"""
Talaba Bot - Production-Ready Telegram Bot with Web Dashboard
=============================================================

This module provides:
- Telegram Bot with webhook support (compatible with ngrok)
- FastAPI web server for web dashboard
- Static file serving
- Production-ready configuration

Usage:
    python main.py

For webhook mode (ngrok/production):
    # Set webhook in Telegram:
    # https://api.telegram.org/bot<TOKEN>/setWebhook?url=https://your-domain.com/webhook
    
    # Then run with:
    python main.py --mode webhook
"""

import asyncio
import logging
import os
import sys
import datetime
from pathlib import Path
from typing import Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# ============================================================================
# Configuration
# ============================================================================

# Bot Token from config
try:
    from config import BOT_TOKEN
except ImportError:
    logger.error("config.py not found! Please create config.py with BOT_TOKEN")
    sys.exit(1)

# Database
from database import init_db, DB_PATH

# ============================================================================
# FastAPI App Setup
# ============================================================================

from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Create FastAPI app
app = FastAPI(
    title="Talaba Bot API",
    description="Telegram Student Assistant Bot API",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS middleware for web dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS", "PUT", "DELETE"],
    allow_headers=[
        "Content-Type",
        "Authorization",
        "ngrok-skip-browser-warning",
        "Accept",
        "Origin",
        "X-Requested-With"
    ],
)

# ============================================================================
# Static Files & Static Directory Handling
# ============================================================================

# Define base directory
BASE_DIR = Path(__file__).resolve().parent
WEBAPP_DIR = BASE_DIR / "webapp_src"

# Mount static files from webapp_src root
# FastAPI's StaticFiles serves ALL files in the directory
if WEBAPP_DIR.exists():
    logger.info(f"Serving static files from: {WEBAPP_DIR}")
    app.mount("/static", StaticFiles(directory=str(WEBAPP_DIR), html=True), name="static")
else:
    logger.warning(f"Webapp directory not found: {WEBAPP_DIR}")

# Create uploads directory if it doesn't exist
STATIC_UPLOADS = WEBAPP_DIR / "uploads"
if not STATIC_UPLOADS.exists():
    STATIC_UPLOADS.mkdir(parents=True, exist_ok=True)
    logger.info(f"Created uploads directory: {STATIC_UPLOADS}")

# Mount uploads if needed
if STATIC_UPLOADS.exists():
    app.mount("/static/uploads", StaticFiles(directory=str(STATIC_UPLOADS)), name="uploads")

# ============================================================================
# Health Check & Root Endpoints
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint - returns API info"""
    return {
        "status": "ok",
        "message": "Talaba Bot API is running",
        "version": "1.0.0",
        "docs": "/api/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {"status": "healthy", "timestamp": str(datetime.datetime.now())}

@app.get("/favicon.ico")
async def favicon():
    """Handle favicon requests gracefully"""
    # Return a simple response or a default icon
    return FileResponse(WEBAPP_DIR / "favicon.ico") if (WEBAPP_DIR / "favicon.ico").exists() else JSONResponse(
        status_code=204,
        content=None
    )

# ============================================================================
# Telegram Webhook Endpoint
# ============================================================================

from aiogram import Bot, Dispatcher, types
from aiogram.types import Update

# Initialize bot and dispatcher
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@app.post("/webhook")
async def telegram_webhook(request: Request):
    """
    Telegram webhook endpoint.
    
    This endpoint receives all Telegram updates (messages, callbacks, etc.)
    Configure via: https://api.telegram.org/bot<TOKEN>/setWebhook
    
    Args:
        request: FastAPI request with Telegram update
        
    Returns:
        dict: Status message
    """
    try:
        # Get the raw update data
        update_data = await request.json()
        logger.debug(f"Received update: {update_data.get('update_id', 'unknown')}")
        
        # Create Update object
        update = Update(**update_data)
        
        # Process the update through dispatcher
        await dp.feed_update(bot, update)
        
        return {"status": "ok", "message": "Update processed"}
        
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        # Return 200 to prevent Telegram from retrying
        return JSONResponse(
            status_code=200,
            content={"status": "error", "message": str(e)}
        )

@app.get("/webhook")
async def webhook_verify():
    """Verify webhook is set up correctly"""
    return {
        "status": "ok",
        "message": "Webhook endpoint is active",
        "endpoint": "/webhook",
        "method": "POST"
    }

# ============================================================================
# Include API Routes
# ============================================================================

try:
    from routes import admin_routes
    app.include_router(admin_routes.router, prefix="/api/admin")
    logger.info("Admin routes loaded successfully")
except Exception as e:
    logger.error(f"Failed to load admin routes: {e}")

# ============================================================================
# API Endpoints
# ============================================================================

import datetime
import sqlite3
from database import get_user_summary, get_library_materials, get_support_messages
from config import ADMIN_ID

@app.post("/api/support")
async def handle_support_message(request: Request):
    """Handle support messages from web app"""
    try:
        data = await request.json()
        user_id = data.get("user_id")
        message = data.get("message")
        
        if not message:
            return {"status": "error", "message": "No message provided"}
        
        # Save to database
        from database import add_support_message, get_user
        try:
            add_support_message(user_id, 'user', message)
        except Exception as e:
            logger.error(f"DB Error: {e}")
        
        # Send to admin via Telegram
        temp_bot = Bot(token=BOT_TOKEN)
        try:
            user_info = get_user(user_id)
            name = user_info[0] if user_info else f"User {user_id}"
            username = f"@{user_info[1]}" if user_info and user_info[1] else ""
            
            caption = (
                f"📨 **Web App Support:**\n"
                f"👤 {name} {username} (ID: {user_id})\n\n"
                f"💬 {message}\n\n"
                f"✍️ Reply to this message to respond."
            )
            
            await temp_bot.send_message(chat_id=ADMIN_ID, text=caption, parse_mode="Markdown")
            await temp_bot.session.close()
            return {"status": "success"}
        except Exception as e:
            logger.error(f"Error sending to admin: {e}")
            return {"status": "error", "detail": str(e)}
            
    except Exception as e:
        logger.error(f"Support endpoint error: {e}")
        return {"status": "error", "message": str(e)}

@app.get("/api/support/history/{user_id}")
async def get_support_history(user_id: int):
    """Get support message history for a user"""
    try:
        messages = get_support_messages(user_id)
        history = []
        for sender, msg, created in messages:
            history.append({"sender": sender, "text": msg, "time": created})
        return {"status": "success", "history": history}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/user/{user_id}")
async def get_user_data(user_id: int):
    """Get user data by ID"""
    try:
        data = get_user_summary(user_id)
        if not data:
            return {"status": "error", "message": "User not found"}
        return {"status": "success", "data": data}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/library/materials")
async def library_materials(subject: str = None, level: str = None, type_: str = None):
    """Get library materials with optional filters"""
    try:
        rows = get_library_materials(subject, level, type_)
        materials = []
        for r in rows:
            materials.append({
                "id": r[0], "subject": r[1], "level": r[2], "type": r[3],
                "title": r[4], "duration": r[5], "url": r[6], "desc": r[7],
                "views": r[8], "date": r[9]
            })
        return {"status": "success", "materials": materials}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/library/subjects")
async def library_subjects():
    """Get list of available subjects"""
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT DISTINCT subject FROM library_materials WHERE is_active=1")
        subjects = [r[0] for r in c.fetchall()]
        conn.close()
        return {"status": "success", "subjects": subjects}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/api/chat")
async def chat_api(request: Request):
    """AI Chat endpoint"""
    try:
        data = await request.json()
        prompt = data.get("prompt")
        user_id = data.get("user_id")
        
        if not prompt:
            return {"status": "error", "response": "Prompt is empty"}
        
        # Log the event
        from database import log_event
        log_event(user_id, 'ai_chat')
        
        # Get AI response
        from services.gemini_service import gemini_chat
        response = await gemini_chat(prompt)
        return {"status": "success", "response": response}
        
    except Exception as e:
        logger.error(f"Chat API Error: {e}")
        return {"status": "error", "response": str(e)}

# ============================================================================
# Bot Handler Setup (Routers)
# ============================================================================

# Import handlers
from handlers import admin, common, student_tools, schedule, library, resources, referral
from handlers.premium import homework_solver

# Register routers - order matters (admin first for command priority)
dp.include_router(admin.router)
dp.include_router(common.router)
dp.include_router(referral.router)
dp.include_router(student_tools.router)
dp.include_router(library.router)
dp.include_router(resources.router)
dp.include_router(homework_solver.router)

logger.info("Bot routers registered successfully")

# ============================================================================
# Background Tasks
# ============================================================================

async def reminders_loop(bot: Bot):
    """Send deadline reminders to users"""
    from database import get_due_deadlines, mark_reminded, get_now
    
    while True:
        try:
            now = get_now()
            deadlines = get_due_deadlines()
            
            for d in deadlines:
                user_id, title, subject, due_date = d
                try:
                    await bot.send_message(
                        user_id,
                        f"📅 **Eslatma:** \\{title}\\ - {due_date}\\n\\nIltimos, muddatida topshiring!",
                        parse_mode="Markdown"
                    )
                    mark_reminded(d[0])
                except Exception as e:
                    logger.error(f"Reminder failed for {user_id}: {e}")
            
            await asyncio.sleep(300)  # Check every 5 minutes
            
        except Exception as e:
            logger.error(f"Reminders error: {e}")
            await asyncio.sleep(60)

async def cleanup_loop():
    """Clean up old temporary files"""
    from utils.cleanup import cleanup_old_files
    
    while True:
        try:
            await asyncio.sleep(3600)  # Every hour
            deleted, size = cleanup_old_files(max_age_hours=24)
            if deleted > 0:
                logger.info(f"Cleanup: {deleted} files deleted, {size/1024:.2f} KB freed")
        except Exception as e:
            logger.error(f"Cleanup error: {e}")
            await asyncio.sleep(300)

# ============================================================================
# Bot Startup/Shutdown
# ============================================================================

async def on_startup(bot: Bot):
    """Called when bot starts"""
    logger.info("🤖 Bot starting up...")
    
    # Start background tasks
    asyncio.create_task(reminders_loop(bot))
    asyncio.create_task(cleanup_loop())
    
    logger.info("Bot startup complete")

async def on_shutdown(bot: Bot):
    """Called when bot shuts down"""
    logger.info("🤖 Bot shutting down...")
    await bot.session.close()
    logger.info("Bot shutdown complete")

# Register startup/shutdown handlers
dp.startup.register(on_startup)
dp.shutdown.register(on_shutdown)

# ============================================================================
# Server Modes
# ============================================================================

async def start_polling():
    """Start bot in polling mode (local development)"""
    logger.info("🔄 Starting bot in POLLING mode...")
    try:
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Polling error: {e}")
    finally:
        await bot.session.close()

async def start_webhook_mode():
    """Start bot in webhook mode (production/ngrok)"""
    # Get webhook URL from environment or config
    webhook_url = os.environ.get("WEBHOOK_URL", "").rstrip("/")
    
    if not webhook_url:
        logger.warning("WEBHOOK_URL not set! Using default...")
        webhook_url = "https://your-ngrok-url.ngrok-free.app"
    
    logger.info(f"Setting webhook to: {webhook_url}/webhook")
    
    try:
        await bot.set_webhook(
            url=f"{webhook_url}/webhook",
            drop_pending_updates=True
        )
        logger.info("Webhook set successfully!")
        
        # Start FastAPI server
        config = uvicorn.Config(
            app,
            host="0.0.0.0",
            port=8080,
            log_level="info"
        )
        server = uvicorn.Server(config)
        await server.serve()
        
    except Exception as e:
        logger.error(f"Webhook setup error: {e}")
        raise
    finally:
        await bot.session.close()

async def start_server_only():
    """Start only the web server (no bot polling)"""
    logger.info("Starting web server only (webhook mode)...")
    config = uvicorn.Config(app, host="0.0.0.0", port=8080, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()

# ============================================================================
# Main Entry Point
# ============================================================================

import argparse

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Talaba Bot")
    parser.add_argument(
        "--mode",
        choices=["polling", "webhook", "server"],
        default="polling",
        help="Run mode: polling (default), webhook (production), server (web only)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8080,
        help="Port for web server (default: 8080)"
    )
    args = parser.parse_args()
    
    # Initialize database
    init_db()
    logger.info("Database initialized")
    
    # Run based on mode
    if args.mode == "polling":
        # Bot polling + web server
        asyncio.run(start_polling())
    elif args.mode == "webhook":
        # Webhook mode
        asyncio.run(start_webhook_mode())
    elif args.mode == "server":
        # Web server only (bot handles webhooks)
        asyncio.run(start_server_only())

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("👋 Application stopped by user")
    except Exception as e:
        logger.error(f"Application error: {e}")
        sys.exit(1)
