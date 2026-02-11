#!/usr/bin/env python3
"""
Bot Connection Test
Tests if bot token is valid and bot can connect to Telegram
"""

import asyncio
from aiogram import Bot
from config import BOT_TOKEN

async def test_bot_connection():
    print("🔍 Testing bot connection...\n")
    
    try:
        bot = Bot(token=BOT_TOKEN)
        
        # Get bot info
        me = await bot.get_me()
        
        print("✅ Bot connection successful!")
        print(f"📱 Bot ID: {me.id}")
        print(f"👤 Bot Username: @{me.username}")
        print(f"📝 Bot Name: {me.first_name}")
        print(f"🤖 Is Bot: {me.is_bot}")
        
        await bot.session.close()
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_bot_connection())
