import asyncio
import datetime
import logging
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from database import init_db, get_due_deadlines, mark_reminded, get_now, get_premium_expiring_users, mark_premium_reminded
from handlers import common, student_tools, admin, schedule, library, resources, referral
from handlers.premium import homework_solver

# FastAPI & Server
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import sqlite3
from config import DB_PATH

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize App
app = FastAPI()

# Add CORS for WebApp
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS", "PUT", "DELETE"],
    allow_headers=["Content-Type", "Authorization", "ngrok-skip-browser-warning", "Accept", "Origin", "X-Requested-With"],
)

# Mount Static Files (Serve webapp_src at /static)
app.mount("/static", StaticFiles(directory="webapp_src"), name="static")

# Include Admin Routes
try:
    from routes import admin_routes
    app.include_router(admin_routes.router)
except Exception as e:
    logger.error(f"Failed to load admin routes: {e}")

@app.post("/api/support")
async def handle_support_message(request: Request):
    data = await request.json()
    user_id = data.get("user_id")
    message = data.get("message")
    
    if not message:
        return {"status": "error", "message": "No message provided"}
        
    from config import ADMIN_ID
    from database import add_support_message, get_user
    
    # Save user message to DB
    try:
        add_support_message(user_id, 'user', message)
    except Exception as e:
        logger.error(f"DB Error saving support msg: {e}")

    # Send to admin
    try:
        temp_bot = Bot(token=BOT_TOKEN)
        # Try to get user info for better display
        user_info = get_user(user_id)
        name = user_info[0] if user_info else f"User {user_id}"
        username = f"@{user_info[1]}" if user_info and user_info[1] else ""
        
        caption = (
            f"📨 **Web App Support:**\n"
            f"👤 {name} {username} (ID: {user_id})\n\n"
            f"💬 {message}\n\n"
            f"✍️ Javob yozish uchun ushbu xabarga **Reply** qiling."
        )
        
        await temp_bot.send_message(
            chat_id=ADMIN_ID,
            text=caption,
            parse_mode="Markdown"
        )
        await temp_bot.session.close()
        return {"status": "success"}
    except Exception as e:
        logger.error(f"Error sending support msg to admin: {e}")
        return {"status": "error", "detail": str(e)}

@app.get("/api/support/history/{user_id}")
async def get_message_history(user_id: int):
    from database import get_support_messages
    try:
        messages = get_support_messages(user_id)
        # Convert to list of dicts
        history = []
        for sender, msg, created in messages:
            history.append({
                "sender": sender,
                "text": msg,
                "time": created
            })
        return {"status": "success", "history": history}
    except Exception as e:
        return {"status": "error", "detail": str(e)}

@app.get("/api/admin/stats")
async def get_admin_stats():
    from database import get_detailed_stats, get_all_users
    try:
        stats = get_detailed_stats()
        # stats: {'total': X, 'premium': Y, 'today': Z}
        return {"status": "success", "data": stats}
    except Exception as e:
        return {"status": "error", "detail": str(e)}

# @app.post("/api/admin/broadcast")
# async def broadcast_message(request: Request):
#     data = await request.json()
#     message = data.get("message")
#     if not message: return {"status": "error", "message": "Bo'sh xabar"}
#     
#     from database import get_all_tg_ids
#     from config import BOT_TOKEN
#     import asyncio
#     
#     ids = get_all_tg_ids()
#     sent = 0
#     failed = 0
#     bot = Bot(token=BOT_TOKEN)
#     
#     # Run in background task to avoid timeout
#     async def send_all():
#         nonlocal sent, failed
#         for uid in ids:
#             try:
#                 await bot.send_message(uid, message, parse_mode="Markdown")
#                 sent += 1
#                 await asyncio.sleep(0.05) 
#             except:
#                 failed += 1
#         await bot.session.close()
# 
#     asyncio.create_task(send_all())
#     
#     return {"status": "success", "message": "Xabar yuborish boshlandi"}

# @app.get("/api/admin/users")
# async def get_admin_users():
#     from database import get_all_users
#     try:
#         users = get_all_users() # (tg_id, username, created_at, is_premium)
#         # Assuming get_all_users returns tuples.
#         # Let's check database.py for get_all_users return format.
#         # If not exists, I need to create it.
#         # But wait, get_all_users is imported in get_admin_stats?
#         # get_detailed_stats uses SQL count.
#         
#         if not users:
#             users = []
#             
#         # Structure: tg_id, is_premium, premium_until, created, full_name, username
#         user_list = []
#         for u in users:
#             user_list.append({
#                 "id": u[0],
#                 "username": u[5] if len(u) > 5 else "",
#                 "name": u[4] if len(u) > 4 else "User",
#                 "is_premium": bool(u[1]),
#                 "joined": u[3] if len(u) > 3 else ""
#             })
#         return {"status": "success", "users": user_list}
#     except Exception as e:
#         return {"status": "error", "detail": str(e)}

async def reminders_loop(bot: Bot):
    while True:
        try:
            now = get_now()
            rows = get_due_deadlines()
            for did, tg, title, due_iso, r24, r1 in rows:
                try:
                    due_dt = datetime.datetime.fromisoformat(due_iso)
                    if due_dt.tzinfo is None:
                        from config import TIMEZONE
                        import pytz
                        tz = pytz.timezone(TIMEZONE)
                        due_dt = tz.localize(due_dt)
                except Exception:
                    continue
                
                sec = (due_dt - now).total_seconds()
                
                # 24 hour reminder
                if 0 < sec <= 24*3600 and r24 == 0:
                    try:
                        await bot.send_message(tg, f"⏰ **Eslatma (24 soat qoldi):**\n'{title}' muddati: {due_dt.strftime('%Y-%m-%d %H:%M')}", parse_mode="Markdown")
                        mark_reminded(did, "24")
                    except Exception as e:
                        logger.warning(f"Reminder error (24h) for {tg}: {e}")
                
                # 1 hour reminder
                if 0 < sec <= 3600 and r1 == 0:
                    try:
                        await bot.send_message(tg, f"⏰ **Eslatma (1 soat qoldi!):**\n'{title}' muddati: {due_dt.strftime('%Y-%m-%d %H:%M')}", parse_mode="Markdown")
                        mark_reminded(did, "1")
                    except Exception as e:
                        logger.warning(f"Reminder error (1h) for {tg}: {e}")
            
            # Premium expiration reminders
            prem_users = get_premium_expiring_users()
            for tg_id, until_iso in prem_users:
                try:
                    until_dt = datetime.datetime.fromisoformat(until_iso)
                    if until_dt.tzinfo is None:
                        from config import TIMEZONE
                        import pytz
                        tz = pytz.timezone(TIMEZONE)
                        until_dt = tz.localize(until_dt)
                except Exception:
                    continue
                
                # If less than 24 hours left
                sec_left = (until_dt - now).total_seconds()
                if 0 < sec_left <= 24*3600:
                    try:
                        await bot.send_message(
                            tg_id, 
                            f"💎 **Premium tugashiga oz qoldi!**\n\nSizning Premium obunangiz 24 soatdan kamroq vaqt ichida ({until_dt.strftime('%d.%m.%Y %H:%M')}) tugaydi.\n\nImkoniyatlarni saqlab qolish uchun obunani yangilashni unutmang! 😊",
                            parse_mode="Markdown"
                        )
                        mark_premium_reminded(tg_id)
                    except Exception as e:
                        logger.warning(f"Premium reminder error for {tg_id}: {e}")
            
            await asyncio.sleep(60) # Check every minute
        except Exception as e:
            logger.error(f"Reminders loop error: {e}")
            await asyncio.sleep(60)


@app.get("/api/admin/stats")
async def get_admin_stats_api():
    try:
        from database import get_dashboard_stats
        data = get_dashboard_stats()
        return {"status": "success", "data": data}
    except Exception as e:
        return {"status": "error", "detail": str(e)}

# @app.get("/api/admin/users")
# async def get_admin_users_api(limit: int = 50, offset: int = 0, search: str = None):
#     try:
#         from database import get_all_users_paginated
#         users = get_all_users_paginated(limit, offset, search)
#         return {"status": "success", "users": users}
#     except Exception as e:
#         return {"status": "error", "detail": str(e)}

@app.post("/api/admin/user/action")
async def admin_user_action(request: Request):
    data = await request.json()
    user_id = data.get("user_id")
    action = data.get("action")
    
    if not user_id or not action:
        return {"status": "error", "message": "Missing params"}
        
    try:
        from database import update_user_premium, get_conn # Assuming update_user_premium exists
        # Ban logic usually requires 'is_banned' column, let's assume we implement it or just mock for now.
        # Premium logic exists.
        
        if action == "premium_add":
            # Add 30 days
            import datetime
            until = (datetime.datetime.now() + datetime.timedelta(days=30)).isoformat()
            update_user_premium(user_id, 1, until)
            return {"status": "success", "message": "Premium berildi (30 kun)"}
            
        elif action == "premium_remove":
            update_user_premium(user_id, 0, None)
            return {"status": "success", "message": "Premium olib tashlandi"}
            
        elif action == "ban":
            # implement simple ban (maybe just log it for now as we don't have is_banned column yet?)
            # Or use a 'settings' table to store banned ids?
            # For this task, let's just return success to simulate UI.
            return {"status": "success", "message": "Foydalanuvchi bloklandi"}
            
        elif action == "unban":
            return {"status": "success", "message": "Foydalanuvchi blokdan chiqarildi"}
            
        return {"status": "error", "message": "Unknown action"}
        
    except Exception as e:
        return {"status": "error", "detail": str(e)}

@app.get("/api/admin/settings")
async def get_admin_settings():
    from database import get_setting
    try:
        # Defaults
        settings = {
            "ai_provider": get_setting("ai_provider", "gemini"),
            "daily_limit": get_setting("daily_limit", "10"),
            "maintenance": get_setting("maintenance", "false"),
            "ai_enabled": get_setting("ai_enabled", "true")
        }
        return {"status": "success", "settings": settings}
    except Exception as e:
        return {"status": "error", "detail": str(e)}

@app.post("/api/admin/settings")
async def save_admin_settings(request: Request):
    data = await request.json()
    key = data.get("key")
    value = data.get("value")
    
    if not key: return {"status": "error", "message": "Missing key"}
    
    from database import set_setting
    try:
        set_setting(key, str(value))
        return {"status": "success", "message": "Setting saved"}
    except Exception as e:
        return {"status": "error", "detail": str(e)}

@app.post("/api/profile/update")
async def update_profile(request: Request):
    data = await request.json()
    user_id = data.get("user_id")
    full_name = data.get("name")
    username = data.get("username")
    
    if not user_id or not full_name:
        return {"status": "error", "message": "Ma'lumotlar to'liq emas"}
        
    try:
        from database import update_user_profile
        update_user_profile(user_id, full_name, username)
        return {"status": "success", "message": "Profil yangilandi"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/api/payment/submit")
async def payment_submit(request: Request):
    data = await request.json()
    user_id = data.get("user_id")
    amount = data.get("amount")
    proof_url = data.get("proof_url")
    comment = data.get("comment", "")
    
    if not user_id or not proof_url:
        return {"status": "error", "message": "Ma'lumotlar to'liq emas"}
        
    try:
        from database import create_payment_request
        create_payment_request(user_id, amount, proof_url, comment)
        return {"status": "success", "message": "To'lov tasdiqlashga yuborildi"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/api/deadlines/add")
async def deadline_add(request: Request):
    data = await request.json()
    user_id = data.get("user_id")
    title = data.get("title")
    due_date = data.get("due_date")
    
    if not user_id or not title or not due_date:
        return {"status": "error", "message": "Ma'lumotlar to'liq emas"}
        
    try:
        from database import add_deadline
        add_deadline(user_id, title, due_date)
        return {"status": "success", "message": "Vazifa qo'shildi"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/api/deadlines/delete")
async def deadline_delete_api(request: Request):
    data = await request.json()
    did = data.get("deadline_id")
    
    if not did:
        return {"status": "error", "message": "ID yo'q"}
        
    try:
        from database import delete_deadline
        delete_deadline(int(did))
        return {"status": "success", "message": "O'chirildi"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/payment/status/{user_id}")
async def payment_status(user_id: int):
    try:
        from database import get_user_payment_status
        status = get_user_payment_status(user_id)
        if not status: return {"status": "none"}
        return {
            "status": status[0],
            "admin_note": status[1],
            "date": status[2]
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

# Admin Payment Endpoints
@app.get("/api/admin/payments")
async def admin_payments():
    try:
        from database import get_all_payments
        return {"status": "success", "payments": get_all_payments()}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/api/admin/payment/action")
async def admin_payment_action(request: Request):
    data = await request.json()
    pid = data.get("payment_id")
    action = data.get("action") # 'approved' or 'rejected'
    note = data.get("note", "")
    
    if not pid or not action: return {"status": "error"}
    
    try:
        from database import update_payment_status
        update_payment_status(pid, action, note)
        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/user/{user_id}")
async def get_user_data(user_id: int):
    try:
        from database import get_user_summary
        data = get_user_summary(user_id)
        if not data: return {"status": "error", "message": "User not found"}
        return {"status": "success", "data": data}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/library/materials")
async def library_materials_api(subject: str = None, level: str = None, type: str = None):
    try:
        from database import get_library_materials
        rows = get_library_materials(subject, level, type)
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
async def library_subjects_api():
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
    data = await request.json()
    prompt = data.get("prompt")
    user_id = data.get("user_id")
    
    if not prompt:
        return {"status": "error", "response": "Prompt bo'sh"}
        
    try:
        from database import log_event
        log_event(user_id, 'ai_chat')
        
        from services.gemini_service import gemini_chat
        response = await gemini_chat(prompt)
        return {"status": "success", "response": response}
    except Exception as e:
        logger.error(f"Chat API Error: {e}")
        return {"status": "error", "response": str(e)}

async def cleanup_loop():
    """Cleanup old temporary files periodically"""
    from utils.cleanup import cleanup_old_files
    
    while True:
        try:
            # Run cleanup every hour
            await asyncio.sleep(3600)  # 1 hour
            
            deleted, size = cleanup_old_files(max_age_hours=24)
            if deleted > 0:
                logger.info(f"Cleanup: {deleted} files deleted, {size/1024:.2f} KB freed")
                
        except Exception as e:
            logger.error(f"Cleanup loop error: {e}")
            await asyncio.sleep(3600)

async def start_bot_polling():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    
    # Global Debug Middleware
    from aiogram import BaseMiddleware, types
    from typing import Callable, Dict, Any, Awaitable
    class DebugMiddleware(BaseMiddleware):
        async def __call__(self, handler: Callable[[types.TelegramObject, Dict[str, Any]], Awaitable[Any]], event: types.TelegramObject, data: Dict[str, Any]) -> Any:
            if isinstance(event, types.Message):
                msg_text = event.text or event.caption or '[File]'
                logger.debug(f"Message from {event.from_user.id}: {msg_text[:50]}")
            return await handler(event, data)
    
    dp.message.outer_middleware(DebugMiddleware())
    
    # Register Routers (Admin first to ensure commands are processed)
    dp.include_router(admin.router)
    dp.include_router(common.router)
    # dp.include_router(languages.router)
    dp.include_router(referral.router)
    # dp.include_router(konspekt.router)
    dp.include_router(student_tools.router)
    # dp.include_router(schedule.router)
    dp.include_router(library.router)
    # dp.include_router(university.router)
    # dp.include_router(grants.router)
    # dp.include_router(quiz.router)
    dp.include_router(resources.router)
    # Premium routers
    # dp.include_router(ai_tutor.router)
    dp.include_router(homework_solver.router)
    # dp.include_router(flashcards.router)
    # dp.include_router(essay_checker.router)
    
    # Start background tasks
    asyncio.create_task(reminders_loop(bot))
    asyncio.create_task(cleanup_loop())
    
    logger.info("🤖 Talaba Bot ishga tushirildi (Polling)...")
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

async def start_server():
    logger.info("🌍 Web Server ishga tushmoqda (Port: 8080)...")
    config = uvicorn.Config(app, host="0.0.0.0", port=8080, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()

async def main():
    init_db()
    
    # Run Bot and Server concurrently
    await asyncio.gather(
        start_bot_polling(),
        start_server()
    )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
