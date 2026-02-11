from aiogram import types, Router, F, html
import urllib.parse
import logging
from aiogram.filters import CommandStart, Command, StateFilter, ChatMemberUpdatedFilter, KICKED, MEMBER
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from database import ensure_user, is_premium, increment_referral, set_premium, get_setting, get_all_channels, get_user, get_now, get_user_language, get_dashboard_stats, get_top_users, get_user_deadlines, log_user_activity
from config import ADMIN_ID, WEBAPP_URL
from utils.texts import get_text, get_all_translations
from utils.check_sub import is_subscribed
from aiogram.utils.keyboard import InlineKeyboardBuilder
import datetime
import os
import logging

logger = logging.getLogger(__name__)

router = Router()


def get_cancel_kb(user_id: int):
    builder = ReplyKeyboardBuilder()
    builder.row(types.KeyboardButton(text=get_text('cancel', user_id)))
    return builder.as_markup(resize_keyboard=True)

def get_main_menu(user_id: int):
    builder = ReplyKeyboardBuilder()
    
    # Row 1
    builder.row(
        types.KeyboardButton(text=get_text('btn_test', user_id)), 
        types.KeyboardButton(text=get_text('btn_referat', user_id))
    )
    # Row 2
    builder.row(
        types.KeyboardButton(text=get_text('btn_ppt', user_id)),
        types.KeyboardButton(text=get_text('btn_solver', user_id))
    )
    # Row 4
    builder.row(
        types.KeyboardButton(text=get_text('btn_invite', user_id))
    )
    
    # Admin Panel (if admin)
    from database import is_user_admin
    if is_user_admin(user_id):
        builder.row(types.KeyboardButton(text=get_text('btn_admin', user_id)))
    
    # Row 7 (Premium only)
    builder.row(
        types.KeyboardButton(text=get_text('btn_premium', user_id))
    )
    
    # Row 12
    builder.row(
        types.KeyboardButton(text=get_text('btn_about', user_id))
    )
    
    # Leaderboard Injection (Top 5)
    try:
        top_users = get_top_users(limit=5)
        rank_param = ""
        if top_users:
            # Format: Name:Score|Name:Score
            rank_data = "|".join([f"{name}:{score}" for name, score in top_users])
            rank_param = f"&rank={urllib.parse.quote(rank_data)}"
    except Exception as e:
        logging.error(f"Error fetching leaderboard: {e}")
        rank_param = ""
    
    # Deadlines Injection
    try:
        deadlines = get_user_deadlines(user_id)
        dl_param = ""
        if deadlines:
            # Format: Title:Date|Title:Date
            dl_data = "|".join([f"{title}:{date}" for title, date in deadlines])
            dl_param = f"&dl={urllib.parse.quote(dl_data)}"
    except Exception as e:
        logging.error(f"Error fetching deadlines: {e}")
        dl_param = ""
    
    # Premium Status Injection
    premium_param = ""
    try:
        from database import is_user_premium
        if is_user_premium(user_id):
            premium_param = "&premium=true"
    except Exception as e:
        logging.error(f"Error checking premium status: {e}")

    # Admin Params Injection
    admin_params = ""
    stats_param = ""
    from database import is_user_admin
    if is_user_admin(user_id):
        admin_params = "&admin=true"
        try:
            from database import get_detailed_stats
            stats = get_detailed_stats()
            total_users = stats.get('total', 0)
            premium_users = stats.get('premium', 0)
            stats_param = f"&stats={total_users}:{premium_users}"
        except Exception as e:
            logging.error(f"Error fetching admin stats: {e}")

    # Web App Configuration
    lang = get_user_language(user_id) or 'uz'
    base_url = get_setting("webapp_url", WEBAPP_URL or "https://abusaad-0724.github.io/talaba_wep/index.html")
    
    from config import SERVER_URL
    server_param = f"&server={urllib.parse.quote(SERVER_URL)}" if SERVER_URL else ""

    # Build full WebApp Dashboard URL
    full_url = f"{base_url}?lang={lang}{admin_params}{stats_param}{rank_param}{dl_param}{premium_param}{server_param}"
    
    logging.info(f"CRITICAL DEBUG: Final WebApp URL: {full_url}")
    
    try:
        # Ensure URL is valid
        builder.row(types.KeyboardButton(text=get_text('btn_dashboard', user_id), web_app=types.WebAppInfo(url=full_url)))
    except Exception as e:
        logging.error(f"Error creating WebApp button: {e}")
        # Fallback
        builder.row(types.KeyboardButton(text=get_text('btn_dashboard', user_id), web_app=types.WebAppInfo(url=base_url)))

    
    return builder.as_markup(resize_keyboard=True)

@router.message(StateFilter("*"), CommandStart())
async def cmd_start(message: types.Message):
    args = message.text.split()
    referrer_id = None
    source = None
    
    if len(args) > 1:
        arg = args[1]
        if arg.isdigit():
            referrer_id = int(arg)
            # Prevent self-referral
            if referrer_id == message.from_user.id:
                referrer_id = None
        elif arg in ["uni", "bekat", "kocha"]:
            source = arg

    is_new_user = ensure_user(
        message.from_user.id, 
        referrer_id, 
        source, 
        message.from_user.full_name, 
        message.from_user.username
    )
    
    if is_new_user:
        log_user_activity(message.from_user.id, message.from_user.full_name, message.from_user.username, "joined")

    if is_new_user and referrer_id:
        # Increment stats for referrer
        new_count = increment_referral(referrer_id)
        
        # Reward Logic: Every 10 referrals = 30 days
        if new_count > 0 and new_count % 10 == 0:
            set_premium(referrer_id, 30)
            try:
                await message.bot.send_message(
                    referrer_id,
                    f"🎉 **Tabriklaymiz!**\n\nSiz 10-do'stingizni taklif qildingiz.\nMukofot tariqasida sizga **1 oy (30 kun) Premium** berildi! ✅"
                )
            except Exception:
                pass # Can't notify if blocked
        else:
            try:
                await message.bot.send_message(
                    referrer_id,
                    f"👏 Sizning havolangiz orqali yangi foydalanuvchi qo'shildi!\nJami takliflar: {new_count} ta.\nKeyingi mukofotgacha: {10 - (new_count % 10)} ta qoldi."
                )
            except Exception:
                pass
    
    # Mandatory Subscription Check
    MANDATORY_CHANNEL = get_setting("mandatory_channel", "@talaba_uz")
    
    try:
        if not await is_subscribed(message.bot, message.from_user.id, MANDATORY_CHANNEL):
            builder = InlineKeyboardBuilder()
            builder.button(text="📢 Kanalga a'zo bo'lish", url=f"https://t.me/{MANDATORY_CHANNEL.replace('@', '')}")
            builder.button(text="✅ Tekshirish", callback_data="check_sub")
            builder.adjust(1)
            
            return await message.answer(
                "⚠️ <b>Diqqat!</b>\n\nBotdan foydalanish uchun rasmiy kanalimizga a'zo bo'lishingiz shart. "
                "Kanalga a'zo bo'lib, 'Tekshirish' tugmasini bosing:",
                reply_markup=builder.as_markup(),
                parse_mode="HTML"
            )
    except PermissionError:
        return await message.answer(
            "❌ <b>Xatolik!</b>\n\nBot kanal a'zolarini tekshira olmayapti. "
            "Iltimos, botni kanalga <b>Administrator</b> qilib tayinlang!",
            parse_mode="HTML"
        )

    is_prem = is_premium(message.from_user.id)
    
    # Get premium details
    user = get_user(message.from_user.id)
    premium_status = "💎 Premium" if is_prem else "🆓 Bepul"
    premium_info = ""
    
    if is_prem and user and len(user) > 2 and user[2]:  # user[2] is premium_until
        from datetime import datetime
        try:
            premium_until = datetime.fromisoformat(user[2])
            now = get_now()
            
            # Calculate remaining time
            time_left = premium_until - now
            days_left = time_left.days
            hours_left = time_left.seconds // 3600
            
            # Format expiry date
            expiry_date = premium_until.strftime("%d.%m.%Y %H:%M")
            
            # Get user language for localized text
            lang = get_user_language(message.from_user.id)
            
            if lang == 'uz':
                premium_info = f"\n⏳ Qolgan vaqt: {days_left} kun, {hours_left} soat\n📅 Tugash vaqti: {expiry_date}\n"
            elif lang == 'ru':
                premium_info = f"\n⏳ Осталось: {days_left} дней, {hours_left} часов\n📅 Истекает: {expiry_date}\n"
            else:  # en
                premium_info = f"\n⏳ Time left: {days_left} days, {hours_left} hours\n📅 Expires: {expiry_date}\n"
        except Exception as e:
            logger.debug(f"Error calculating premium time: {e}")
    
    trial_text = ""
    if is_new_user:
        lang = get_user_language(message.from_user.id)
        if lang == 'uz':
            trial_text = "🎉 <b>Xushxabar!</b> Sizga 2 kunlik Premium sinov muddati berildi!\n\n"
        elif lang == 'ru':
            trial_text = "🎉 <b>Отличная новость!</b> Вам предоставлен 2-дневный пробный период Premium!\n\n"
        else:  # en
            trial_text = "🎉 <b>Great news!</b> You've been granted a 2-day Premium trial period!\n\n"
    
    welcome_text = get_text('welcome', message.from_user.id, 
                            name=html.quote(message.from_user.full_name),
                            status=premium_status,
                            trial=trial_text)
    
    # Insert premium info after status line
    if premium_info:
        lines = welcome_text.split('\n')
        # Find the Status line and insert premium info after it
        for i, line in enumerate(lines):
            if 'Status:' in line or 'Статус:' in line:
                lines.insert(i + 1, premium_info.strip())
                break
        welcome_text = '\n'.join(lines)

    await message.answer(
        welcome_text,
        reply_markup=get_main_menu(message.from_user.id),
        parse_mode="HTML"
    )

@router.callback_query(StateFilter("*"), F.data == "check_sub")
async def check_sub_callback(callback: types.CallbackQuery):
    MANDATORY_CHANNEL = get_setting("mandatory_channel", "@talaba_uz")
    try:
        subscribed = await is_subscribed(callback.bot, callback.from_user.id, MANDATORY_CHANNEL)
        if subscribed:
            await callback.answer("✅ Rahmat! Endi botdan foydalanishingiz mumkin.", show_alert=True)
            await callback.message.delete()
            
            # Get premium details
            is_prem = is_premium(callback.from_user.id)
            user = get_user(callback.from_user.id)
            premium_status = "💎 Premium" if is_prem else "🆓 Bepul"
            premium_info = ""
            
            if is_prem and user and len(user) > 2 and user[2]:
                from datetime import datetime
                try:
                    premium_until = datetime.fromisoformat(user[2])
                    now = get_now()
                    
                    time_left = premium_until - now
                    days_left = time_left.days
                    hours_left = time_left.seconds // 3600
                    expiry_date = premium_until.strftime("%d.%m.%Y %H:%M")
                    
                    lang = get_user_language(callback.from_user.id)
                    
                    if lang == 'uz':
                        premium_info = f"\n⏳ Qolgan vaqt: {days_left} kun, {hours_left} soat\n📅 Tugash vaqti: {expiry_date}\n"
                    elif lang == 'ru':
                        premium_info = f"\n⏳ Осталось: {days_left} дней, {hours_left} часов\n📅 Истекает: {expiry_date}\n"
                    else:
                        premium_info = f"\n⏳ Time left: {days_left} days, {hours_left} hours\n📅 Expires: {expiry_date}\n"
                except Exception as e:
                    logger.debug(f"Error calculating premium time: {e}")
            
            welcome_text = get_text('welcome', callback.from_user.id,
                                   name=html.quote(callback.from_user.full_name),
                                   status=premium_status,
                                   trial="")
            
            # Insert premium info
            if premium_info:
                lines = welcome_text.split('\n')
                for i, line in enumerate(lines):
                    if 'Status:' in line or 'Статус:' in line:
                        lines.insert(i + 1, premium_info.strip())
                        break
                welcome_text = '\n'.join(lines)
            
            await callback.message.answer(
                welcome_text,
                reply_markup=get_main_menu(callback.from_user.id),
                parse_mode="HTML"
            )
        else:
            await callback.answer("❌ Siz hali kanalga a'zo bo'lmadingiz!", show_alert=True)
    except PermissionError:
        await callback.message.answer(
            "❌ <b>Xatolik!</b>\n\nBot kanal a'zolarini tekshira olmayapti. "
            "Iltimos, botni kanalga <b>Administrator</b> qilib tayinlang!",
            parse_mode="HTML"
        )
        await callback.answer()

@router.message(StateFilter("*"), F.text.contains("Asosiy menyu"))
async def back_to_main(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Asosiy menyu:",
        reply_markup=get_main_menu(message.from_user.id)
    )

@router.message(StateFilter("*"), F.text.in_(get_all_translations('btn_about')))
async def about_bot_combined(message: types.Message):
    text = get_text('about_text', message.from_user.id)
    await message.answer(text, parse_mode="Markdown")

@router.message(StateFilter("*"), Command("ping"))
async def cmd_ping(message: types.Message):
    await message.answer("Bot ishlamoqda! ✅ (Versiya: 2.1.3)")



@router.message(StateFilter("*"), F.text.in_(get_all_translations('btn_premium')))
async def start_premium(message: types.Message):
    # Text from texts.py (already formatted with prices)
    text = get_text('premium_info', message.from_user.id)
    
    builder = InlineKeyboardBuilder()
    # Row 1: 1 Month and 3 Months
    builder.button(text=get_text('btn_1month', message.from_user.id), callback_data="buy_premium_1")
    builder.button(text=get_text('btn_3months', message.from_user.id), callback_data="buy_premium_3")
    # Row 2: 6 Months
    builder.button(text=get_text('btn_6months', message.from_user.id), callback_data="buy_premium_6")
    
    # Adjust layout: 2 buttons in first row, 1 in second (row widths: 2, 1)
    builder.adjust(2, 1)
    
    await message.answer(text, reply_markup=builder.as_markup(), parse_mode="Markdown")

@router.callback_query(F.data.startswith("buy_premium_"))
async def handle_premium_buy(callback: types.CallbackQuery, state: FSMContext):
    from config import HUMO_CARD
    from handlers.admin import PaymentStates
    
    parts = callback.data.split("_")
    try:
        months = int(parts[2])
    except:
        months = 1
    
    prices = {
        1: "25 000",
        3: "60 000",
        6: "99 000"
    }
    amount = prices.get(months, "25 000")
    
    # Get card
    card = get_setting("humo_card", HUMO_CARD)
    
    text = get_text('payment_info', callback.from_user.id, card=card, amount=amount)
    
    # Add instruction for sending proof
    text += f"\n\n💳 **To'lovni amalga oshirgach, chekni (rasm yoki fayl) shu yerga yuboring.**\n"
    text += "Admin tekshiruvidan so'ng Premium statusi avtomatik faollashadi."
    
    kb = InlineKeyboardBuilder()
    # Add back button to premium selection
    kb.button(text=get_text('btn_back', callback.from_user.id), callback_data="back_to_premium")
    
    await callback.message.edit_text(text, reply_markup=kb.as_markup(), parse_mode="Markdown")
    await callback.answer()
    
    # Set state to wait for payment proof
    await state.set_state(PaymentStates.waiting_for_proof)
    # Store payment info in state
    await state.update_data(months=months, amount=amount)

@router.callback_query(F.data == "back_to_premium")
async def back_to_premium(callback: types.CallbackQuery):
    # Re-show premium selection
    text = get_text('premium_info', callback.from_user.id)
    
    builder = InlineKeyboardBuilder()
    builder.button(text=get_text('btn_1month', callback.from_user.id), callback_data="buy_premium_1")
    builder.button(text=get_text('btn_3months', callback.from_user.id), callback_data="buy_premium_3")
    builder.button(text=get_text('btn_6months', callback.from_user.id), callback_data="buy_premium_6")
    builder.adjust(2, 1)
    
    await callback.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="Markdown")
    await callback.answer()

@router.callback_query(F.data == "delete_msg")
async def delete_msg(callback: types.CallbackQuery):
    await callback.message.delete()

@router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=KICKED))
async def user_blocked_bot(event: types.ChatMemberUpdated):
    log_user_activity(event.from_user.id, event.from_user.full_name, event.from_user.username, "left")

@router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=MEMBER))
async def user_unblocked_bot(event: types.ChatMemberUpdated):
    # Only log if they were KICKED/LEFT before, or just log everything.
    # To avoid double logging 'joined' on /start (since /start implies MEMBER),
    # we might want to be careful. But 'joined' log is good anyway.
    # The /start handler handles BRAND NEW users. This handler handles existing users unblocking.
    log_user_activity(event.from_user.id, event.from_user.full_name, event.from_user.username, "joined")

