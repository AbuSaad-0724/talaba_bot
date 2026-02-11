
from fastapi import Request, HTTPException, Security
from fastapi.security import APIKeyHeader
from config import BOT_TOKEN
import hashlib
import hmac
import urllib.parse
import json

api_key_header = APIKeyHeader(name="Authorization", auto_error=False)

async def check_admin_auth(request: Request, api_key_header: str = Security(api_key_header)):
    """
    Verify Telegram WebApp initData or a simple Admin Secret.
    For production, initData validation is best.
    """
    
    # 1. Check for Admin Secret (Simpler for external tools)
    # if api_key_header == "MY_SUPER_SECRET_ADMIN_KEY":
    #     return True

    # 2. Check for Telegram initData (from WebApp)
    # The frontend should send `initData` in a header, e.g., "X-Telegram-Init-Data"
    init_data = request.headers.get("X-Telegram-Init-Data")
    
    if not init_data:
        # Allow localhost for development (optional)
        if request.client.host == "127.0.0.1":
            return True
        raise HTTPException(status_code=403, detail="No authentication data provided")

    if not validate_telegram_init_data(init_data, BOT_TOKEN):
        raise HTTPException(status_code=403, detail="Invalid Telegram data")
        
    return True

def validate_telegram_init_data(init_data: str, bot_token: str) -> bool:
    """
    Validates the initData received from Telegram WebApp.
    """
    try:
        parsed_data = dict(urllib.parse.parse_qsl(init_data))
        if "hash" not in parsed_data:
            return False

        hash_check = parsed_data.pop("hash")
        data_check_string = "\n".join(
            f"{k}={v}" for k, v in sorted(parsed_data.items())
        )
        
        secret_key = hmac.new(
            key=b"WebAppData", 
            msg=bot_token.encode(), 
            digestmod=hashlib.sha256
        ).digest()
        
        calculated_hash = hmac.new(
            key=secret_key, 
            msg=data_check_string.encode(), 
            digestmod=hashlib.sha256
        ).hexdigest()
        
        if calculated_hash != hash_check:
            return False
            
        # Optional: Check auth_date for expiration (e.g. 24h)
        return True
    except Exception:
        return False
