"""
Premium Payment Handler - Telegram Bot
=====================================

Subscription Plans:
- 1 Month: 25,000 UZS
- 3 Months: 60,000 UZS (20% discount)
- 6 Months: 99,000 UZS (34% discount)
"""

from aiogram import types, Router, F
from aiogram.utils.keyboard import InlineKeyboardBuilder
from database import is_premium, set_premium, get_user
from config import ADMIN_ID
import datetime
import uuid

router = Router()

# Subscription prices (in UZS)
SUBSCRIPTION_PLANS = {
    "1_month": {
        "name": "1 Oy",
        "price": 25000,
        "months": 1,
        "discount": 0
    },
    "3_months": {
        "name": "3 Oy",
        "price": 60000,
        "months": 3,
        "discount": 20
    },
    "6_months": {
        "name": "6 Oy",
        "price": 99000,
        "months": 6,
        "discount": 34
    }
}

# Payment states
PAYMENTStates = ["waiting_for_payment"]

def get_premium_kb():
    """Show premium plans with inline buttons"""
    builder = InlineKeyboardBuilder()
    
    # Premium plans
    for plan_id, plan in SUBSCRIPTION_PLANS.items():
        discount_text = f" 🔥 -{plan['discount']}%" if plan['discount'] > 0 else ""
        price_text = f"{plan['price']:,} so'm"
        builder.row(
            types.InlineKeyboardButton(
                text=f"💎 {plan['name']} - {price_text}{discount_text}",
                callback_data=f"premium_select:{plan_id}"
            )
        )
    
    builder.row(
        types.InlineKeyboardButton(
            text="🔙 Orqaga",
            callback_data="premium_back"
        )
    )
    
    return builder.as_markup()

def get_payment_confirmation_kb(plan_id: str, order_id: str):
    """Payment confirmation keyboard"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        types.InlineKeyboardButton(
            text="✅ To'lov qildim",
            callback_data=f"payment_confirm:{order_id}"
        )
    )
    builder.row(
        types.InlineKeyboardButton(
            text="❌ Bekor qilish",
            callback_data="payment_cancel"
        )
    )
    
    return builder.as_markup()

def get_payment_info_text(plan_id: str) -> str:
    """Get payment information text"""
    plan = SUBSCRIPTION_PLANS[plan_id]
    
    original_price = plan['price']
    if plan['discount'] > 0:
        original_price = int(plan['price'] / (1 - plan['discount'] / 100))
    
    text = f"""💎 **Talaba Premium - {plan['name']}**

Imkoniyatlar:
✅ Vazifa Yechuvchi (AI Vision)
✅ Cheksiz foydalanish
✅ Ustuvor qo'llab-quvvatlash
✅ Barcha Premium funksiyalar

💰 Narx: {plan['price']:,} so'm"""
    
    if plan['discount'] > 0:
        text += f"\n💎 {plan['discount']}% chegirma!"
    
    text += f"""

📱 To'lov usuli: Click / Payme
💳 Karta: 8600 **** **** ****

To'lov qilib, "To'lov qildim" tugmasini bosing!"""
    
    return text

@router.message(F.text.in_(["premium", "💎 Premium", "premium sotib olish", "Premium"]))
async def show_premium_plans(message: types.Message):
    """Show premium subscription plans"""
    from ..common import get_main_menu
    
    user_id = message.from_user.id
    
    # Check if user is already premium
    if is_premium(user_id):
        subscription = get_user_subscription(user_id)
        if subscription:
            expire_date = subscription.get('expire_date', 'N/A')
            return await message.answer(
                f"✅ Siz **Premium** foydalanuvchisiz!\n\n"
                f"📅 Amal qilish muddati: {expire_date}\n\n"
                "Boshqa Premium sotib olish uchun kutishingiz mumkin!",
                parse_mode="Markdown",
                reply_markup=get_main_menu(user_id)
            )
    
    await message.answer(
        """💎 **Talaba Premium**

Imkoniyatlaringizni kengaytiring!

✅ Vazifa Yechuvchi - AI bilan masalalaringizni yeching
✅ Cheksiz foydalanish
✅ Tez javob
✅ Premium funksiyalar

**Tariflar:**""",
        reply_markup=get_premium_kb(),
        parse_mode="Markdown"
    )

@router.callback_query(F.data.startswith("premium_select:"))
async def select_plan(callback: types.CallbackQuery):
    """Handle plan selection"""
    plan_id = callback.data.split(":")[1]
    plan = SUBSCRIPTION_PLANS[plan_id]
    
    # Generate order ID
    order_id = f"order_{callback.from_user.id}_{uuid.uuid4().hex[:8]}"
    
    # Store order info in database (simplified)
    await callback.message.edit_text(
        get_payment_info_text(plan_id),
        reply_markup=get_payment_confirmation_kb(plan_id, order_id),
        parse_mode="Markdown"
    )
    await callback.answer()

@router.callback_query(F.data == "premium_back")
async def go_back(callback: types.CallbackQuery):
    """Go back to premium plans"""
    await show_premium_plans(callback.message)
    await callback.message.delete()
    await callback.answer()

@router.callback_query(F.data.startswith("payment_confirm:"))
async def confirm_payment(callback: types.CallbackQuery):
    """Handle payment confirmation (admin approval required)"""
    order_id = callback.data.split(":")[1]
    user_id = callback.from_user.id
    
    # In production, verify payment with payment gateway
    # For now, notify admin for manual verification
    
    await callback.message.edit_text(
        "⏳ **To'lov tekshirilmoqda...**\n\n"
        "Iltimos, 5-10 daqiqa kuting.\n"
        "Admin tasdiqlagan so'ng Premium avtomatik faollashadi!\n\n"
        "Agar muammo bo'lsa: @admin",
        parse_mode="Markdown"
    )
    
    # Notify admin
    try:
        from aiogram import Bot
        bot = Bot(token=callback.bot.token)
        await bot.send_message(
            ADMIN_ID,
            f"💎 **Yangi to'lov so'rovi**\n\n"
            f"👤 Foydalanuvchi: {callback.from_user.full_name}\n"
            f"🆔 User ID: {user_id}\n"
            f"📋 Order ID: {order_id}\n\n"
            "Tasdiqlash uchun /verify_order buyrug'ini ishlating!"
        )
    except Exception as e:
        print(f"Admin notification failed: {e}")
    
    await callback.answer()

@router.callback_query(F.data == "payment_cancel")
async def cancel_payment(callback: types.CallbackQuery):
    """Cancel payment"""
    await callback.message.edit_text(
        "❌ To'lov bekor qilindi.\n\n"
        "Boshqa reja tanlash uchun /premium buyrug'ini yuboring!"
    )
    await callback.answer()

# Admin commands for payment verification
@router.message(F.text.startswith("/verify_order"))
async def verify_order(message: types.Message):
    """Admin: Verify and activate premium"""
    from aiogram import Bot
    
    if message.from_user.id != ADMIN_ID:
        return
    
    # Parse order info (format: /verify_order user_id plan_id months)
    parts = message.text.split()
    if len(parts) < 4:
        return await message.answer(
            "Format: /verify_order user_id plan_id months\n\n"
            "Misol: /verify_order 123456 1_month 1"
        )
    
    try:
        target_user_id = int(parts[1])
        plan_id = parts[2]
        months = int(parts[3])
        
        # Calculate days from months
        days = months * 30
        
        # Activate premium
        set_premium(target_user_id, days)
        
        # Notify user
        bot = Bot(token=message.bot.token)
        await bot.send_message(
            target_user_id,
            f"🎉 **Tabriklayman!**\n\n"
            f"Sizning Premiumingiz faollashdi!\n"
            f"📅 Muddati: {months} oy\n\n"
            "Barcha Premium funksiyalardan foydalanishingiz mumkin! 💎"
        )
        
        await message.answer(f"✅ Premium faollashtrildi! User: {target_user_id}")
        
    except Exception as e:
        await message.answer(f"❌ Xatolik: {e}")

@router.message(F.text.startswith("/check_premium"))
async def check_premium_status(message: types.Message):
    """Check user premium status"""
    from aiogram import Bot
    
    if message.from_user.id != ADMIN_ID:
        return
    
    parts = message.text.split()
    if len(parts) < 2:
        return await message.answer("Format: /check_premium user_id")
    
    try:
        target_user_id = int(parts[1])
        is_user_premium = is_premium(target_user_id)
        user = get_user(target_user_id)
        
        status = "✅ Premium" if is_user_premium else "❌ Oddiy"
        expire = user[2] if user else 'N/A'
        
        await message.answer(
            f"👤 User: {target_user_id}\n"
            f"Status: {status}\n"
            f"Muddati: {expire}"
        )
        
    except Exception as e:
        await message.answer(f"❌ Xatolik: {e}")
