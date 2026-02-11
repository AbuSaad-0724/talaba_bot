#!/usr/bin/env python3
"""
Bot Token Checker
Verifies bot token validity and shows bot information
"""

import asyncio
from aiogram import Bot
from config import BOT_TOKEN
import sys

async def check_token():
    """Check if bot token is valid"""
    print("🔍 Checking Bot Token...\n")
    print("=" * 70)
    
    # Mask token for security
    masked_token = BOT_TOKEN[:10] + "..." + BOT_TOKEN[-10:] if len(BOT_TOKEN) > 20 else "***"
    print(f"Token: {masked_token}")
    print("=" * 70)
    print()
    
    try:
        bot = Bot(token=BOT_TOKEN)
        
        print("📡 Connecting to Telegram...")
        me = await bot.get_me()
        
        print("✅ Connection successful!\n")
        print("🤖 Bot Information:")
        print("-" * 70)
        print(f"  ID: {me.id}")
        print(f"  Username: @{me.username}")
        print(f"  Name: {me.first_name}")
        print(f"  Is Bot: {me.is_bot}")
        print(f"  Can Join Groups: {me.can_join_groups}")
        print(f"  Can Read Messages: {me.can_read_all_group_messages}")
        print(f"  Supports Inline: {me.supports_inline_queries}")
        print("-" * 70)
        
        # Get webhook info
        print("\n📬 Webhook Information:")
        print("-" * 70)
        webhook_info = await bot.get_webhook_info()
        
        if webhook_info.url:
            print(f"  URL: {webhook_info.url}")
            print(f"  Has Custom Certificate: {webhook_info.has_custom_certificate}")
            print(f"  Pending Updates: {webhook_info.pending_update_count}")
        else:
            print("  ✅ No webhook set (using polling)")
        print("-" * 70)
        
        # Test sending message to admin
        print("\n📤 Testing Message Send...")
        print("-" * 70)
        try:
            from config import ADMIN_ID
            await bot.send_message(
                ADMIN_ID,
                "✅ Bot token check successful!\n\n"
                f"Bot: @{me.username}\n"
                f"ID: {me.id}"
            )
            print(f"  ✅ Test message sent to admin (ID: {ADMIN_ID})")
        except Exception as e:
            print(f"  ⚠️  Could not send test message: {e}")
        print("-" * 70)
        
        await bot.session.close()
        
        print("\n" + "=" * 70)
        print("✅ Token is valid and bot is operational!")
        print("=" * 70)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}\n")
        print("=" * 70)
        print("Possible issues:")
        print("  1. Invalid bot token")
        print("  2. Network connection problem")
        print("  3. Bot was deleted by @BotFather")
        print("=" * 70)
        
        return False

if __name__ == "__main__":
    result = asyncio.run(check_token())
    sys.exit(0 if result else 1)
