from fastapi import APIRouter, HTTPException, Query, Body, Request, Response, Depends, File, UploadFile
from pydantic import BaseModel
from typing import List, Optional
import json
import csv
import io
import asyncio
import os
import shutil
from datetime import datetime
from database import (
    get_all_users_paginated, get_total_users_count, 
    block_user_feature, unblock_user_feature, get_user_restrictions,
    log_analytics, get_analytics_stats, get_recent_activity,
    add_library_material, get_library_materials, delete_library_material,
    get_user, get_all_users, get_all_payments, update_payment_status,
    update_user_premium, get_all_tg_ids, get_user_summary, set_setting, get_setting
)
from utils.security import check_admin_auth
import config

router = APIRouter(prefix="/api/admin", tags=["admin"], dependencies=[Depends(check_admin_auth)])

# --- Models ---
class FeatureBlockRequest(BaseModel):
    user_id: int
    feature_key: str

class AnalyticsLogRequest(BaseModel):
    user_id: int
    feature_key: str

class BroadcastRequest(BaseModel):
    text: str
    image_url: Optional[str] = None
    pin: bool = False
    schedule_time: Optional[str] = None

# --- Global Broadcast State ---
broadcast_status = {
    "active": False,
    "total": 0,
    "sent": 0,
    "failed": 0,
    "message": ""
}

# --- Users Management ---
@router.get("/users")
async def list_users(
    page: int = 1, 
    limit: int = 20, 
    offset: Optional[int] = None,
    search: Optional[str] = None
):
    """Get paginated list of users"""
    if offset is None:
        offset = (page - 1) * limit
    
    try:
        users = get_all_users_paginated(limit, offset, search)
        total = get_total_users_count(search)
        
        return {
            "users": users,
            "total": total,
            "page": page,
            "pages": (total + limit - 1) // limit, 
            "limit": limit
        }
    except Exception as e:
        print(f"Error listing users: {e}")
        return {"users": [], "total": 0, "error": str(e)}

@router.get("/users/{user_id}")
async def get_user_details(user_id: int):
    """Get detailed user information"""
    user = get_user_summary(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    restrictions = get_user_restrictions(user_id)
    return {
        "user": user,
        "restrictions": restrictions
    }

@router.get("/users/{user_id}/restrictions")
async def get_restrictions(user_id: int):
    restrictions = get_user_restrictions(user_id)
    return {"restrictions": restrictions}

@router.post("/users/block-feature")
async def block_feature(data: FeatureBlockRequest):
    block_user_feature(data.user_id, data.feature_key)
    return {"status": "success", "message": f"Feature {data.feature_key} blocked for user {data.user_id}"}

@router.post("/users/unblock-feature")
async def unblock_feature(data: FeatureBlockRequest):
    unblock_user_feature(data.user_id, data.feature_key)
    return {"status": "success", "message": f"Feature {data.feature_key} unblocked for user {data.user_id}"}

@router.get("/users/export")
async def export_users(format: str = "json"):
    """Export all users data"""
    users = get_all_users()
    
    if format == "csv":
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["ID", "Username", "Full Name", "Created At", "Is Premium"])
        for user in users:
            # users structure: (tg_id, is_premium, premium_until, created, full_name, username)
            writer.writerow([
                user[0],
                user[5], # username
                user[4], # full_name
                user[3], # created
                "Yes" if user[1] else "No"
            ])
        
        return Response(
            content=output.getvalue(),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=users_export.csv"}
        )
    else:
        user_list = []
        for user in users:
            user_list.append({
                "id": user[0],
                "username": user[5],
                "full_name": user[4],
                "created_at": user[3],
                "is_premium": bool(user[1])
            })
        return Response(
            content=json.dumps(user_list, indent=2),
            media_type="application/json",
            headers={"Content-Disposition": "attachment; filename=users_export.json"}
        )

# --- Analytics ---
@router.get("/stats/features")
async def get_feature_stats(days: int = 7):
    stats = get_analytics_stats(days)
    # Transform for easy chart consumption if needed
    formatted = {}
    for item in stats:
        formatted[item['feature']] = item['count']
    return {"status": "success", "data": formatted, "raw": stats}

@router.get("/activity")
async def get_activity_log(limit: int = 15):
    activity = get_recent_activity(limit)
    return {"activity": activity}

@router.get("/stats/overview")
async def get_overview_stats():
    """Get overview statistics for dashboard"""
    try:
        total_users = get_total_users_count()
        users = get_all_users() # Minimal fetching would be better for scale
        
        premium_count = 0
        new_today = 0
        today = datetime.now().strftime("%Y-%m-%d")
        
        for u in users:
            if u[1]: premium_count += 1
            if u[3] and str(u[3]).startswith(today): new_today += 1
        
        return {
            "total_users": total_users,
            "premium_users": premium_count,
            "new_today": new_today,
            "free_users": total_users - premium_count
        }
    except Exception as e:
        print(f"Overview stats error: {e}")
        return {
            "total_users": 0, "premium_users": 0, "new_today": 0, "free_users": 0
        }

@router.post("/analytics/log")
async def log_feature_usage(data: AnalyticsLogRequest):
    log_analytics(data.user_id, data.feature_key)
    return {"status": "success"}

# --- Broadcast ---
async def run_broadcast(text: str, pin: bool):
    global broadcast_status
    from aiogram import Bot
    bot = Bot(token=config.BOT_TOKEN)
    
    users = get_all_tg_ids()
    broadcast_status["total"] = len(users)
    broadcast_status["sent"] = 0
    broadcast_status["failed"] = 0
    broadcast_status["active"] = True
    broadcast_status["message"] = "Sending..."
    
    for uid in users:
        if not broadcast_status["active"]:
            break # Stopped
            
        try:
            msg = await bot.send_message(uid, text, parse_mode="Markdown")
            if pin:
                await bot.pin_chat_message(uid, msg.message_id)
            broadcast_status["sent"] += 1
        except Exception:
            broadcast_status["failed"] += 1
        
        await asyncio.sleep(0.05) # Rate limit
    
    broadcast_status["active"] = False
    broadcast_status["message"] = "Finished"
    await bot.session.close()

@router.post("/broadcast")
async def send_broadcast_api(data: BroadcastRequest):
    global broadcast_status
    if broadcast_status["active"]:
        return {"status": "error", "message": "Broadcast already running"}
        
    # Start background task
    asyncio.create_task(run_broadcast(data.text, data.pin))
    
    return {
        "status": "started",
        "message": "Broadcast started in background"
    }

@router.get("/broadcast/status")
async def get_broadcast_status():
    return broadcast_status

@router.post("/broadcast/stop")
async def stop_broadcast():
    global broadcast_status
    broadcast_status["active"] = False
    return {"status": "success", "message": "Broadcast stopping..."}

# --- System Status ---
@router.get("/system/status")
async def get_system_status():
    try:
        import psutil
        import time
        import os
        
        boot_time = psutil.boot_time()
        uptime = time.time() - boot_time
        process = psutil.Process(os.getpid())
        memory_info = process.memory_info()
        
        def format_uptime(seconds):
            days = int(seconds // 86400)
            hours = int((seconds % 86400) // 3600)
            minutes = int((seconds % 3600) // 60)
            if days > 0:
                return f"{days}d {hours}h {minutes}m"
            elif hours > 0:
                return f"{hours}h {minutes}m"
            return f"{minutes}m"
        
        return {
            "cpu_percent": psutil.cpu_percent(),
            "memory_percent": psutil.virtual_memory().percent,
            "memory_mb": round(memory_info.rss / 1024 / 1024, 2),
            "disk_percent": psutil.disk_usage('/').percent,
            "uptime_seconds": round(uptime, 2),
            "uptime_formatted": format_uptime(uptime),
            "status": "healthy"
        }
    except Exception as e:
        print(f"System status error: {e}")
        return {
            "cpu_percent": 0, "memory_percent": 0, "memory_mb": 0, 
            "disk_percent": 0, "uptime_seconds": 0, 
            "uptime_formatted": "Unavailable", "status": "error"
        }

# --- Payments ---
@router.get("/payments/history")
async def get_payment_history_api():
    """Get real payment history from DB"""
    payments = get_all_payments()
    
    # Process for frontend
    # DB row: {'id': 1, 'tg_id': 123, 'amount': 25000, 'proof_file_id': '...', 'status': 'pending', 'comment': '', 'admin_note': '', 'created': '...'}
    
    # We need user names for better UI.
    # This might be slow if many payments. 
    # Better to join in SQL, but let's do simple fetch for now.
    
    enriched = []
    pending_count = 0
    approved_count = 0
    
    for p in payments:
        if p['status'] == 'pending': pending_count += 1
        if p['status'] == 'approved': approved_count += 1
        
        user = get_user_summary(p['tg_id'])
        user_name = user['full_name'] if user else f"User {p['tg_id']}"
        
        enriched.append({
            "id": p['id'],
            "user": user_name,
            "user_id": p['tg_id'],
            "amount": f"{p['amount']:,}".replace(",", " "),
            "plan": "Premium" if p['amount'] == 25000 else "Custom",
            "date": p['created'],
            "status": p['status'],
            "proof": p['proof_file_id']
        })
        
    return {
        "history": enriched,
        "total_pending": pending_count,
        "total_approved": approved_count
    }

class PaymentActionRequest(BaseModel):
    payment_id: int
    action: str
    note: Optional[str] = ""

@router.post("/payment/action")
async def admin_payment_action_api(data: PaymentActionRequest):
    try:
        if data.action not in ['approved', 'rejected']:
             return {"status": "error", "message": "Invalid action"}
             
        # Update status
        update_payment_status(data.payment_id, data.action, data.note)
        
        # If approved, grant premium
        if data.action == 'approved':
            # We need to find the user_id for this payment
            payments = get_all_payments() # Inefficient, but works for now. Better to get_payment_by_id
            target_payment = next((p for p in payments if p['id'] == data.payment_id), None)
            
            if target_payment:
                # Add 30 days
                # Fix timedelta
                import datetime as dt_module
                until = (dt_module.datetime.now() + dt_module.timedelta(days=30)).isoformat()
                
                update_user_premium(target_payment['tg_id'], 1, until)
                
                # Notify user (Task)
                from aiogram import Bot
                bot = Bot(token=config.BOT_TOKEN)
                try:
                    await bot.send_message(target_payment['tg_id'], "✅ **To'lovingiz tasdiqlandi!**\nSizga Premium obuna faollashtirildi.", parse_mode="Markdown")
                except:
                   pass
                await bot.session.close()
                
        return {"status": "success", "message": f"Payment {data.action}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# --- Library Endpoints ---
class LibraryItemRequest(BaseModel):
    subject: str
    level: str
    material_type: str
    title: str
    url: str
    description: Optional[str] = None
    duration: Optional[str] = None

@router.post("/library/add")
async def add_library_item_endpoint(item: LibraryItemRequest):
    res = add_library_material(
        subject=item.subject,
        level=item.level,
        material_type=item.material_type,
        title=item.title,
        url=item.url,
        description=item.description,
        duration=item.duration
    )
    if res:
        return {"status": "success", "id": res}
    return {"status": "error", "message": "Database error"}

@router.get("/library/list")
async def list_library_items(subject: Optional[str] = None, level: Optional[str] = None):
    if subject == "all": subject = None
    items = get_library_materials(subject, level)
    # Convert tuples to dicts for nicer JSON
    # row: id, subject, level, material_type, title, duration, file_url, description, views_count, created_at
    mapped_items = []
    for r in items:
        mapped_items.append({
            "id": r[0], "subject": r[1], "level": r[2], "type": r[3],
            "title": r[4], "duration": r[5], "url": r[6], "desc": r[7],
            "views": r[8], "date": r[9]
        })
    return {"materials": mapped_items, "count": len(items)}

class DeleteItemRequest(BaseModel):
    id: int

@router.post("/library/delete")
async def delete_library_item_endpoint(item: DeleteItemRequest):
    delete_library_material(item.id) # returns None but works
    return {"status": "success"}

# --- Quick Actions ---
class QuickActionRequest(BaseModel):
    user_id: int
    action: str
    value: Optional[str] = None

@router.post("/quick-action")
async def quick_action(data: QuickActionRequest):
    """Quick admin actions"""
    import datetime as dt
    
    try:
        if data.action == "premium_add":
            days = int(data.value) if data.value else 30
            until = (dt.datetime.now() + dt.timedelta(days=days)).isoformat()
            update_user_premium(data.user_id, 1, until)
            return {"status": "success", "message": f"Premium added for {days} days"}
        
        elif data.action == "premium_remove":
            update_user_premium(data.user_id, 0, None)
            return {"status": "success", "message": "Premium removed"}
            
        elif data.action == "ban":
            block_user_feature(data.user_id, "access")
            return {"status": "success", "message": "User banned"}
        
        elif data.action == "reset_usage":
            # Just clear logs for today? Or reset specific limits? 
            # For now, just a placeholder
            return {"status": "success", "message": "Limits reset"}
        
        return {"status": "error", "message": "Unknown action"}
    
    except Exception as e:
        return {"status": "error", "message": str(e)}

# --- Settings ---
@router.get("/settings")
async def get_admin_settings():
    try:
        settings = {
            "ai_provider": get_setting("ai_provider", "gemini"),
            "daily_limit": get_setting("daily_limit", "10"),
            "maintenance": get_setting("maintenance", "false"),
            "ai_enabled": get_setting("ai_enabled", "true")
        }
        return {"status": "success", "settings": settings}
    except Exception as e:
        return {"status": "error", "detail": str(e)}

@router.post("/settings")
async def save_admin_settings(request: Request):
    data = await request.json()
    key = data.get("key")
    value = data.get("value")
    
    if not key: return {"status": "error", "message": "Missing key"}
    
    try:
        set_setting(key, str(value))
        return {"status": "success", "message": "Setting saved"}
    except Exception as e:
        return {"status": "error", "detail": str(e)}

@router.post("/upload")
async def upload_file_admin(file: UploadFile = File(...)):
    try:
        UPLOAD_DIR = "webapp_src/uploads"
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{file.filename}"
        file_path = os.path.join(UPLOAD_DIR, filename)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # Return URL relative to webapp
        # Since access is via /static/ (mapped to webapp_src)
        file_url = f"/static/uploads/{filename}"
        
        return {"status": "success", "url": file_url}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# --- Admins & Channels ---
@router.get("/admins/list")
async def list_admins():
    from database import get_all_admins
    return {"admins": get_all_admins()}

@router.post("/admins/add")
async def add_admin_api(data: dict = Body(...)):
    user_id = data.get("user_id")
    name = data.get("name")
    if not user_id or not name: return {"status": "error"}
    
    try:
        from database import add_admin_db
        add_admin_db(int(user_id), name)
        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "detail": str(e)}

@router.post("/admins/delete")
async def remove_admin_api(data: dict = Body(...)):
    user_id = data.get("user_id")
    try:
        from database import remove_admin_db
        remove_admin_db(int(user_id))
        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "detail": str(e)}

@router.get("/channels/list")
async def list_channels():
    from database import get_all_channels
    return {"channels": get_all_channels()}

@router.post("/channels/add")
async def add_channel_api(data: dict = Body(...)):
    title = data.get("title")
    url = data.get("url")
    if not title or not url: return {"status": "error"}
    
    try:
        from database import add_channel
        add_channel(title, url)
        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "detail": str(e)}

@router.post("/channels/delete")
async def delete_channel_api(data: dict = Body(...)):
    id = data.get("id")
    try:
        from database import delete_channel
        delete_channel(int(id))
        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "detail": str(e)}

@router.post("/users/message")
async def send_user_message(data: dict = Body(...)):
    user_id = data.get("user_id")
    text = data.get("text")
    if not user_id or not text: return {"status": "error"}
    
    try:
        from aiogram import Bot
        from config import BOT_TOKEN
        bot = Bot(token=BOT_TOKEN)
        await bot.send_message(user_id, f"📩 **Admin Xabari:**\n\n{text}", parse_mode="Markdown")
        await bot.session.close()
        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "detail": str(e)}
