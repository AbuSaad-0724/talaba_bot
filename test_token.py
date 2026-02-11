from aiogram import Bot
import asyncio
from config import BOT_TOKEN

async def test():
    bot = Bot(token=BOT_TOKEN)
    try:
        me = await bot.get_me()
        print(f"Bot: @{me.username}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(test())
