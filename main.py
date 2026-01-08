import asyncio
import datetime
import logging
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from database import init_db, get_due_deadlines, mark_reminded, get_now, get_premium_expiring_users, mark_premium_reminded
from handlers import common, konspekt, student_tools, admin, schedule, library, university, channels, grants, quiz, resources, referral
from handlers.premium import ai_tutor, homework_solver, flashcards, essay_checker

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

async def main():
    init_db()
    
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    
    # Include routers (Order matters!)
    dp.include_router(common.router)
    dp.include_router(referral.router)
    dp.include_router(konspekt.router)
    dp.include_router(student_tools.router)
    dp.include_router(schedule.router)
    dp.include_router(library.router)
    dp.include_router(university.router)
    dp.include_router(channels.router)
    dp.include_router(grants.router)
    dp.include_router(quiz.router)
    dp.include_router(resources.router)
    # Premium routers
    dp.include_router(ai_tutor.router)
    dp.include_router(homework_solver.router)
    dp.include_router(flashcards.router)
    dp.include_router(essay_checker.router)
    # Admin router (last)
    dp.include_router(admin.router)
    
    # Start reminders
    asyncio.create_task(reminders_loop(bot))
    
    logger.info("Talaba Bot ishga tushirildi.")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
