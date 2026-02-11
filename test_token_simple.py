#!/usr/bin/env python3
"""
Simple Token Test
Quick and simple bot token validation
"""

import asyncio
from aiogram import Bot
from config import BOT_TOKEN

async def simple_test():
    """Simple token test"""
    print("🔍 Simple Token Test\n")
    
    try:
        bot = Bot(token=BOT_TOKEN)
        me = await bot.get_me()
        
        print("✅ Token is VALID!\n")
        print(f"Bot Username: @{me.username}")
        print(f"Bot ID: {me.id}")
        print(f"Bot Name: {me.first_name}")
        
        await bot.session.close()
        return True
        
    except Exception as e:
        print(f"❌ Token is INVALID!\n")
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    result = asyncio.run(simple_test())
    exit(0 if result else 1)
