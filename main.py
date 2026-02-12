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

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
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

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(
    title="Talaba Bot API",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# Static Files
# ============================================================================

BASE_DIR = Path(__file__).resolve().parent
WEBAPP_DIR = BASE_DIR / "webapp_src"

if WEBAPP_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(WEBAPP_DIR), html=True), name="static")
    logger.info(f"Static files from: {WEBAPP_DIR}")
else:
    logger.warning(f"Webapp dir not found: {WEBAPP_DIR}")

# Create uploads
UPLOADS_DIR = WEBAPP_DIR / "uploads"
if not UPLOADS_DIR.exists():
    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
if UPLOADS_DIR.exists():
    app.mount("/static/uploads", StaticFiles(directory=str(UPLOADS_DIR)), name="uploads")

# ============================================================================
# Endpoints
# ============================================================================

@app.get("/")
async def root():
    return {
        "status": "ok",
        "message": "Talaba Bot API",
        "webapp": "/static/index.html",
        "admin": "/static/admin_dashboard.html"
    }

@app.get("/health")
async def health():
    return {"status": "healthy", "time": str(datetime.datetime.now())}

@app.get("/favicon.ico")
async def favicon():
    return JSONResponse(status_code=204, content=None)

@app.get("/static/")
async def static_index():
    """Serve index.html for /static/ requests"""
    index_path = WEBAPP_DIR / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    return JSONResponse(status_code=404, content={"error": "index.html not found"})

# ============================================================================
# Admin Routes
# ============================================================================

try:
    from routes import admin_routes
    app.include_router(admin_routes.router, prefix="/api/admin")
except Exception as e:
    logger.error(f"Admin routes error: {e}")

# ============================================================================
# API Routes
# ============================================================================

@app.post("/api/support")
async def support(request: Request):
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
        return {"status": "error", "message": str(e)}

@app.get("/api/user/{user_id}")
async def get_user(user_id: int):
    try:
        from database import get_user_summary
        data = get_user_summary(user_id)
        return {"status": "success", "data": data} if data else {"status": "error", "message": "User not found"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/library/materials")
async def materials(subject: str = None):
    try:
        from database import get_library_materials
        rows = get_library_materials(subject)
        return {"status": "success", "materials": [{"id": r[0], "subject": r[1], "title": r[4]} for r in rows]}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/api/chat")
async def chat(request: Request):
    try:
        data = await request.json()
        from database import log_event
        log_event(data.get("user_id"), 'ai_chat')
        from services.gemini_service import gemini_chat
        response = await gemini_chat(data.get("prompt"))
        return {"status": "success", "response": response}
    except Exception as e:
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

# ============================================================================
# Background Tasks
# ============================================================================

async def reminders_loop():
    from database import get_due_deadlines, mark_reminded, get_now
    while True:
        try:
            for d in get_due_deadlines():
                try:
                    await bot.send_message(d[0], f"Reminder: {d[1]} - {d[3]}")
                    mark_reminded(d[0])
                except: pass
            await asyncio.sleep(300)
        except: await asyncio.sleep(60)

# ============================================================================
# Startup/Shutdown
# ============================================================================

async def on_startup():
    logger.info("Bot starting...")
    asyncio.create_task(reminders_loop())

async def on_shutdown():
    logger.info("Bot shutting down...")
    await bot.session.close()

dp.startup.register(on_startup)
dp.shutdown.register(on_shutdown)

# ============================================================================
# Main
# ============================================================================

import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--web", action="store_true", help="Web server only")
    parser.add_argument("--bot", action="store_true", help="Bot polling only")
    args = parser.parse_args()
    
    init_db()
    logger.info("Database initialized")
    
    if args.web:
        # Web server only
        config = uvicorn.Config(app, host="0.0.0.0", port=8080, log_level="info")
        uvicorn.Server(config).run()
    elif args.bot:
        # Bot polling only
        asyncio.run(dp.start_polling(bot))
    else:
        # Both
        async def run_all():
            # Start bot in background
            bot_task = asyncio.create_task(dp.start_polling(bot))
            await asyncio.sleep(2)  # Give bot time to start
            
            # Start web server
            config = uvicorn.Config(app, host="0.0.0.0", port=8080, log_level="info")
            server = uvicorn.Server(config)
            
            # Run both
            await asyncio.gather(bot_task, server.serve())
        
        asyncio.run(run_all())

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Stopped by user")
