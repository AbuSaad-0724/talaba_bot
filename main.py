"""
Talaba Bot - Production-Ready Telegram Bot with Web Dashboard
=============================================================

Usage:
    python main.py                    # Bot polling only
    python main.py --web             # Web server only
    python main.py --all            # Both bot and web (default)
"""

import asyncio
import logging
import os
import sys
import datetime
from pathlib import Path
from typing import Optional

# ============================================================================
# Logging Configuration
# ============================================================================

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

try:
    from config import BOT_TOKEN
except ImportError:
    logger.error("config.py not found!")
    sys.exit(1)

from database import init_db, DB_PATH

# ============================================================================
# FastAPI App Setup
# ============================================================================

from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(
    title="Talaba Bot API",
    version="1.0.0",
    docs_url=None,  # Disable docs for production
    redoc_url=None  # Disable redoc for production
)

# ============================================================================
# CORS Middleware
# ============================================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# Directory Configuration
# ============================================================================

BASE_DIR = Path(__file__).resolve().parent
WEBAPP_DIR = BASE_DIR / "webapp_src"

if not WEBAPP_DIR.exists():
    logger.error(f"Webapp directory not found: {WEBAPP_DIR}")
    sys.exit(1)

logger.info(f"Webapp directory: {WEBAPP_DIR}")

# ============================================================================
# Static Files Mount
# ============================================================================

# Mount static files at /static path
app.mount("/static", StaticFiles(directory=str(WEBAPP_DIR), html=True), name="static")

# Create and mount uploads directory
UPLOADS_DIR = WEBAPP_DIR / "uploads"
if not UPLOADS_DIR.exists():
    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/static/uploads", StaticFiles(directory=str(UPLOADS_DIR)), name="uploads")

logger.info(f"Static files mounted: /static -> {WEBAPP_DIR}")
logger.info(f"Uploads mounted: /static/uploads -> {UPLOADS_DIR}")

# ============================================================================
# Root Endpoint - Serve Telegram Web App
# ============================================================================

@app.get("/", response_class=FileResponse)
async def root():
    """
    Serve the main Telegram Web App at root URL.
    This is the entry point for the web application.
    """
    index_path = WEBAPP_DIR / "index.html"
    if index_path.exists():
        logger.info(f"Serving index.html from: {index_path}")
        return FileResponse(index_path)
    else:
        logger.error(f"index.html not found at: {index_path}")
        raise HTTPException(status_code=404, detail="Web App not found")

@app.get("/webapp")
async def webapp():
    """
    Alternative route for web app access.
    """
    return await root()

# ============================================================================
# Health Check Endpoint
# ============================================================================

@app.get("/health")
async def health():
    """
    Health check endpoint for monitoring.
    """
    return {
        "status": "healthy",
        "service": "talaba_bot",
        "version": "1.0.0",
        "timestamp": str(datetime.datetime.now())
    }

# ============================================================================
# Telegram Webhook Endpoint
# ============================================================================

@app.post("/webhook")
async def telegram_webhook(request: Request):
    """
    Telegram webhook endpoint for receiving updates.
    """
    try:
        from aiogram import Bot, types
        from aiogram.methods import GetMe
        
        data = await request.json()
        logger.info(f"Webhook received: {data.get('update_id', 'unknown')}")
        
        # Initialize bot to process update
        bot = Bot(token=BOT_TOKEN)
        
        # Convert dict to Update object
        update = types.Update(**data)
        
        # Process the update through dispatcher
        await dp.feed_update(bot, update)
        
        return {"status": "ok"}
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.get("/webhook")
async def webhook_info():
    """
    Webhook status endpoint.
    """
    try:
        from aiogram import Bot
        bot = Bot(token=BOT_TOKEN)
        webhook_info = await bot.get_webhook_info()
        return {
            "status": "ok",
            "webhook_url": webhook_info.url,
            "has_custom_certificate": webhook_info.has_custom_certificate,
            "pending_update_count": webhook_info.pending_update_count
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

# ============================================================================
# Favicon Endpoint
# ============================================================================

@app.get("/favicon.ico")
async def favicon():
    """
    Return empty response for favicon requests.
    """
    return JSONResponse(status_code=204, content=None)

# ============================================================================
# Admin Routes
# ============================================================================

try:
    from routes import admin_routes
    app.include_router(admin_routes.router, prefix="/api/admin")
    logger.info("Admin routes registered: /api/admin")
except Exception as e:
    logger.error(f"Admin routes error: {e}")

# ============================================================================
# Library Routes
# ============================================================================

try:
    from routes import library_routes
    app.include_router(library_routes.router)
    logger.info("Library routes registered: /api/library")
except Exception as e:
    logger.error(f"Library routes error: {e}")

# ============================================================================
# API Routes
# ============================================================================

@app.post("/api/support")
async def support(request: Request):
    """
    Support message endpoint.
    """
    try:
        data = await request.json()
        from config import ADMIN_ID
        from database import add_support_message
        add_support_message(data.get("user_id"), 'user', data.get("message"))
        
        from aiogram import Bot
        bot = Bot(token=BOT_TOKEN)
        await bot.send_message(ADMIN_ID, f"Support: {data.get('message')}")
        await bot.session.close()
        return {"status": "success"}
    except Exception as e:
        logger.error(f"Support error: {e}")
        return {"status": "error", "message": str(e)}

@app.get("/api/user/{user_id}")
async def get_user(user_id: int):
    """
    Get user information by ID.
    """
    try:
        from database import get_user_summary
        data = get_user_summary(user_id)
        return {"status": "success", "data": data} if data else {"status": "error", "message": "User not found"}
    except Exception as e:
        logger.error(f"Get user error: {e}")
        return {"status": "error", "message": str(e)}

@app.get("/api/library/materials")
async def materials(subject: str = None):
    """
    Get library materials.
    """
    try:
        from database import get_library_materials
        rows = get_library_materials(subject)
        return {"status": "success", "materials": [{"id": r[0], "subject": r[1], "title": r[4]} for r in rows]}
    except Exception as e:
        logger.error(f"Materials error: {e}")
        return {"status": "error", "message": str(e)}

@app.get("/api/deadlines/{user_id}")
async def get_deadlines(user_id: int):
    """
    Get user deadlines.
    """
    try:
        from database import get_due_deadlines
        deadlines = get_due_deadlines()
        result = []
        for d in deadlines:
            result.append({
                "id": d[0],
                "title": d[1],
                "subject": d[2],
                "due_date": d[3],
                "days_left": 2
            })
        return {"status": "success", "deadlines": result}
    except Exception as e:
        logger.error(f"Deadlines error: {e}")
        return {"status": "error", "message": str(e)}

@app.post("/api/chat")
async def chat(request: Request):
    """
    AI chat endpoint.
    """
    try:
        data = await request.json()
        from database import log_event
        log_event(data.get("user_id"), 'ai_chat')
        from services.gemini_service import gemini_chat
        response = await gemini_chat(data.get("prompt"))
        return {"status": "success", "response": response}
    except Exception as e:
        logger.error(f"Chat error: {e}")
        return {"status": "error", "response": str(e)}

# ============================================================================
# Telegram Bot
# ============================================================================

from aiogram import Bot, Dispatcher, types

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Import handlers
from handlers import admin, common, student_tools, library, resources, referral
from handlers.premium import homework_solver

dp.include_router(admin.router)
dp.include_router(common.router)
dp.include_router(referral.router)
dp.include_router(student_tools.router)
dp.include_router(library.router)
dp.include_router(resources.router)
dp.include_router(homework_solver.router)

logger.info("Telegram handlers registered")

# ============================================================================
# Background Tasks
# ============================================================================

async def reminders_loop():
    """
    Background task for sending reminders.
    """
    from database import get_due_deadlines, mark_reminded
    while True:
        try:
            for d in get_due_deadlines():
                try:
                    await bot.send_message(d[0], f"Reminder: {d[1]} - {d[3]}")
                    mark_reminded(d[0])
                except Exception as e:
                    logger.error(f"Reminder error: {e}")
            await asyncio.sleep(300)
        except Exception as e:
            logger.error(f"Reminders loop error: {e}")
            await asyncio.sleep(60)

# ============================================================================
# Startup/Shutdown
# ============================================================================

async def on_startup():
    logger.info("Bot starting...")
    asyncio.create_task(reminders_loop())
    logger.info("Background tasks started")

async def on_shutdown():
    logger.info("Bot shutting down...")
    await bot.session.close()

dp.startup.register(on_startup)
dp.shutdown.register(on_shutdown)

# ============================================================================
# Main Entry Point
# ============================================================================

import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--web", action="store_true", help="Web server only")
    parser.add_argument("--bot", action="store_true", help="Bot polling only")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8080, help="Port to bind to")
    args = parser.parse_args()
    
    init_db()
    logger.info("Database initialized")
    
    if args.web:
        # Web server only
        config = uvicorn.Config(app, host=args.host, port=args.port, log_level="info")
        logger.info(f"Starting web server on {args.host}:{args.port}")
        uvicorn.Server(config).run()
    elif args.bot:
        # Bot polling only
        logger.info("Starting bot polling...")
        asyncio.run(dp.start_polling(bot))
    else:
        # Both
        async def run_all():
            # Start bot in background
            bot_task = asyncio.create_task(dp.start_polling(bot))
            await asyncio.sleep(2)
            
            # Start web server
            config = uvicorn.Config(app, host=args.host, port=args.port, log_level="info")
            server = uvicorn.Server(config)
            
            logger.info(f"Starting web server on {args.host}:{args.port}")
            await asyncio.gather(bot_task, server.serve())
        
        logger.info("Starting bot and web server...")
        asyncio.run(run_all())

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)
