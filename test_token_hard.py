from aiogram import Bot
import asyncio

async def test():
    # Hardcoded from .env to test
    token = "7794011784:AAH1ka3R9sx5MgZTCFmWKX2ZeHk0h2g7MYg"
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
