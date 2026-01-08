from aiogram import types, Router, F, html
from aiogram.filters import CommandStart, Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from database import ensure_user, is_premium, increment_referral, set_premium, get_setting, get_all_channels, get_user, get_now
from config import ADMIN_ID
from utils.check_sub import is_subscribed
from aiogram.utils.keyboard import InlineKeyboardBuilder
import datetime

router = Router()

def get_main_menu(user_id: int = None):
    builder = ReplyKeyboardBuilder()
    
    # Row 1
    builder.row(types.KeyboardButton(text="🧮 GPA hisoblash"), types.KeyboardButton(text="🧾 Referat (AI)"))
    # Row 2
    builder.row(types.KeyboardButton(text="📚 Test generator"), types.KeyboardButton(text="📊 Prezentatsiya (AI)"))
    # Row 3 (Direct access to Konspekt actons)
    builder.row(types.KeyboardButton(text="📂 Fayl → Konspekt"), types.KeyboardButton(text="📸 Foto → Konspekt"))
    # Row 4
    builder.row(types.KeyboardButton(text="⏰ Deadline qo'shish"), types.KeyboardButton(text="📝 Vazifa Yechuvchi"))
    # Row 5
    builder.row(types.KeyboardButton(text="📋 Mening deadline'larim"), types.KeyboardButton(text="✍️ Insho Tekshiruvchi"))
    # Row 6
    builder.row(types.KeyboardButton(text="📚 Onlayn kutubxona"), types.KeyboardButton(text="🤖 AI Tutor"))
    # Row 7
    builder.row(types.KeyboardButton(text="🎯 Kunlik quiz"), types.KeyboardButton(text="🎴 Flashcards"))
    
    # General / Other Free (Centered/Grouped)
    builder.row(types.KeyboardButton(text="🗣 Do'stlarni taklif qilish"), types.KeyboardButton(text="📚 Bepul manbalar"))
    builder.row(types.KeyboardButton(text="📢 Foydali kanallar"), types.KeyboardButton(text="🏢 Universitet yangiliklari"))
    builder.row(types.KeyboardButton(text="🏆 Grantlar"))
    
    # Admin & Info
    builder.row(types.KeyboardButton(text="📖 Malumotnoma"))
    
    # Admin Panel & Premium Status
    if user_id:
        if user_id == ADMIN_ID:
            builder.row(types.KeyboardButton(text="🔑 Boshqaruv Paneli"))
        
        if not is_premium(user_id):
            builder.row(types.KeyboardButton(text="🌟 Premium sotib olish"))
    
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
    premium_status = "💎 Premium" if is_prem else "🆓 Bepul"
    
    # Base welcome message
    welcome_text = f"Assalomu alaykum, {html.quote(message.from_user.full_name)}!\n\n"
    welcome_text += f"Status: {premium_status}\n"
    
    if is_new_user:
        welcome_text += "🎉 <b>Xushxabar!</b> Sizga barcha Premium funksiyalardan foydalanish uchun <b>2 kunlik bepul sinov muddati</b> berildi!\n\n"
    
    if is_prem:
        # Get expiration date
        user_data = get_user(message.from_user.id)
        if user_data and user_data[2]:
            try:
                until_dt = datetime.datetime.fromisoformat(user_data[2])
                now = get_now()
                diff = until_dt - now
                
                if diff.total_seconds() > 0:
                    days = diff.days
                    hours = diff.seconds // 3600
                    minutes = (diff.seconds % 3600) // 60
                    
                    if days > 0:
                        time_left = f"{days} kun, {hours} soat"
                    elif hours > 0:
                        time_left = f"{hours} soat, {minutes} daqiqa"
                    else:
                        time_left = f"{minutes} daqiqa"
                    
                    welcome_text += f"⏳ Qolgan vaqt: <b>{time_left}</b>\n"
                    welcome_text += f"📅 Tugash vaqti: <b>{until_dt.strftime('%d.%m.%Y %H:%M')}</b>\n\n"
                else:
                    if not is_new_user: # Should not happen for new user
                        welcome_text += "⚠️ Premium muddati tugagan.\n\n"
            except Exception:
                welcome_text += "Sizda Premium imkoniyatlari faol! ✅\n\n"
        else:
            welcome_text += "Sizda Premium imkoniyatlari faol! ✅\n\n"
    else:
        if not is_new_user:
            welcome_text += "\n"

    welcome_text += (
        "Talaba Service Botga xush kelibsiz. Men sizga o'qishingizda yordam beraman. "
        "Marhamat, kerakli bo'limni tanlang:"
    )

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
            # Send start menu
            premium_status = "💎 Premium" if is_premium(callback.from_user.id) else "🆓 Bepul"
            await callback.message.answer(
                f"Assalomu alaykum, {html.quote(callback.from_user.full_name)}!\n\n"
                f"Status: {premium_status}\n\n"
                "Marhamat, kerakli bo'limni tanlang:",
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

@router.message(StateFilter("*"), F.text.contains("Malumotnoma"))
async def about_bot_combined(message: types.Message):
    text = (
        "🤖 **Talaba Service Bot — Sizning shaxsiy yordamchingiz!**\n\n"
        "Ushbu bot talabalar uchun o'qish jarayonini osonlashtirish va samaradorlikni oshirish uchun yaratilgan. Bot quyidagi barcha funksiyalarni o'z ichiga oladi:\n\n"
        
        "🛠 **1. O'quv qurollari:**\n"
        "• 🧮 **GPA hisoblash** — Baholaringizni va kreditlaringizni kiriting, bot o'rtacha balingizni avtomatik hisoblab beradi.\n"
        "• ⏰ **Deadline boshqaruvi** — Muhim vazifalaringizni saqlang. Bot sizga 24 soat va 1 soat qolganda eslatma yuboradi.\n"
        "• 🎯 **Kunlik quiz** — Bilimingizni sinash uchun har kuni yangi qiziqarli testlar.\n\n"
        
        "🧠 **2. Sun'iy intellekt (AI) imkoniyatlari:**\n"
        "• 🧾 **AI Referat** — Istalgan mavzuda to'liq, sifatli referat yozdiring va tayyor **Word (.docx)** faylni yuklab oling.\n"
        "• 📊 **AI Prezentatsiya** — Mavzuni yozing, bot slaydlar rejasini tuzadi va tayyor **PowerPoint (.pptx)** dizaynda taqdim etadi.\n"
        "• 📚 **Test generator** — Mavzu bo'yicha mustaqil ishlash uchun AI orqali test savollarini yarating.\n"
        "• 🤖 **AI Tutor** — Har qanday fan bo'yicha savollaringizga real vaqtda javob beruvchi shaxsiy repititor.\n\n"
        
        "📑 **3. Matn va vazifalar bilan ishlash:**\n"
        "• 📸 **Foto → Konspekt** — Qo'lyozma yoki kitob rasmini yuboring, AI uni raqamli matnga aylantirib beradi.\n"
        "• 📂 **Fayl → Konspekt** — Uzun PDF yoki hujjatlarni qisqacha mazmunini chiqaradi.\n"
        "• 📝 **Vazifa yechuvchi** — Murakkab masalalar va topshiriqlarni bosqichma-bosqich yechib beradi.\n"
        "• ✍️ **Insho tekshiruvi** — Yozgan matnlaringizni grammatik va mantiqiy xatolarini tekshiradi.\n\n"
        
        "📖 **4. Resurslar va ma'lumotlar:**\n"
        "• 📚 **Onlayn kutubxona** — Minglab bepul PDF va audio kitoblar bazasi.\n"
        "• 🏆 **Grantlar** — Mahalliy va xalqaro grantlar, stipendiyalar haqida doimiy yangiliklar.\n"
        "• 🏢 **Universitet yangiliklari** — O'zbekiston oliy ta'lim tizimidagi eng so'nggi xabarlar.\n"
        "• 📢 **Foydali kanallar** — Talabalar uchun kerakli bo'lgan saralangan kanallar to'plami.\n\n"
        
        "🚀 **Texnologiya:** Gemini 2.1 Flash\n"
        "✅ **Versiya:** 2.1.6 (Stable)\n\n"
        "O'qishingizda omad tilaymiz! ✨"
    )
    await message.answer(text, parse_mode="Markdown")

@router.message(StateFilter("*"), Command("ping"))
async def cmd_ping(message: types.Message):
    await message.answer("Bot ishlamoqda! ✅ (Versiya: 2.1.3)")



@router.message(StateFilter("*"), F.text == "🌟 Premium sotib olish")
async def start_premium(message: types.Message):
    from config import HUMO_CARD, PREMIUM_PRICE
    
    # Get current values from DB or defaults from config
    card = get_setting("humo_card", HUMO_CARD)
    price = get_setting("premium_price", str(PREMIUM_PRICE))
    
    text = (
        f"💎 **Premium Obuna**\n\n"
        f"Premium obuna narxi: **{price} so'm / oy**\n\n"
        f"💳 **To'lov uchun karta:**\n"
        f"`{card}`\n"
        f"(Humo/Uzcard)\n\n"
        f"❗️ To'lov qilganingizdan so'ng, chekni (skrinshot) shu yerga yuboring.\n"
        f"To'lov tasdiqlangach, Premium avtomatik tarzda faollashadi."
    )
    await message.answer(text, reply_markup=types.ReplyKeyboardMarkup(keyboard=[[types.KeyboardButton(text="❌ Bekor qilish")]], resize_keyboard=True), parse_mode="Markdown")
