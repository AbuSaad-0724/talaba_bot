#!/usr/bin/env python3
"""
Token Request Test
Tests bot token with various API requests
"""

import asyncio
from aiogram import Bot
from config import BOT_TOKEN, ADMIN_ID

async def test_token_requests():
    """Test various bot API requests"""
    print("🔍 Testing Bot Token Requests...\n")
    
    bot = Bot(token=BOT_TOKEN)
    
    tests_passed = 0
    tests_failed = 0
    
    # Test 1: Get Me
    print("Test 1: getMe")
    print("-" * 60)
    try:
        me = await bot.get_me()
        print(f"✅ Success: @{me.username} (ID: {me.id})")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Failed: {e}")
        tests_failed += 1
    print()
    
    # Test 2: Get Webhook Info
    print("Test 2: getWebhookInfo")
    print("-" * 60)
    try:
        webhook = await bot.get_webhook_info()
        print(f"✅ Success: Webhook URL = {webhook.url or 'None (polling)'}")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Failed: {e}")
        tests_failed += 1
    print()
    
    # Test 3: Get Chat
    print("Test 3: getChat (Admin)")
    print("-" * 60)
    try:
        chat = await bot.get_chat(ADMIN_ID)
        print(f"✅ Success: {chat.first_name} (@{chat.username or 'no username'})")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Failed: {e}")
        tests_failed += 1
    print()
    
    # Test 4: Send Message
    print("Test 4: sendMessage")
    print("-" * 60)
    try:
        msg = await bot.send_message(
            ADMIN_ID,
            "🧪 Token test message\n\n"
            "This is an automated test of bot API requests."
        )
        print(f"✅ Success: Message ID {msg.message_id} sent")
        tests_passed += 1
        
        # Delete test message
        await bot.delete_message(ADMIN_ID, msg.message_id)
        print("   (Test message deleted)")
    except Exception as e:
        print(f"❌ Failed: {e}")
        tests_failed += 1
    print()
    
    # Test 5: Get Updates
    print("Test 5: getUpdates")
    print("-" * 60)
    try:
        updates = await bot.get_updates(limit=1)
        print(f"✅ Success: {len(updates)} updates retrieved")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Failed: {e}")
        tests_failed += 1
    print()
    
    await bot.session.close()
    
    # Summary
    print("=" * 60)
    print(f"Tests Passed: {tests_passed}/5")
    print(f"Tests Failed: {tests_failed}/5")
    print("=" * 60)
    
    if tests_failed == 0:
        print("✅ All tests passed! Token is fully functional.")
    else:
        print("⚠️  Some tests failed. Check token permissions.")

if __name__ == "__main__":
    asyncio.run(test_token_requests())
