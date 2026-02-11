from aiogram import Bot
import asyncio
import os
from dotenv import load_dotenv

async def test():
    load_dotenv()
    token = os.getenv("BOT_TOKEN")
    print(f"Token from env: '{token}'")
    bot = Bot(token=token)
    try:
        me = await bot.get_me()
        print(f"Bot: @{me.username}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(test())
