from aiogram import types, Router, F, html
from database import log_event
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from services.ai_service import ai_generate_referat, ai_generate_test, ai_generate_ppt_content
from database import is_premium, add_deadline, get_due_deadlines
from utils.docx_gen import create_referat_docx
from utils.pptx_gen import create_presentation_pptx
import datetime
import os
import pytz
from config import TEMP_DIR, TIMEZONE

router = Router()

class StudentStates(StatesGroup):
    waiting_for_referat_topic = State()
    waiting_for_test_topic = State()
    waiting_for_deadline_title = State()
    waiting_for_deadline_time = State()
    waiting_for_gpa_data = State()
    waiting_for_ppt_topic = State()

# Referat
@router.message(F.text == "🧾 Referat (AI)")
async def get_referat_topic(message: types.Message, state: FSMContext):
    log_event(message.from_user.id, "AI Referat")
    if not is_premium(message.from_user.id):
        return await message.answer("Referat generatori faqat Premium foydalanuvchilar uchun.")
    
    from .konspekt import get_cancel_kb
    await message.answer("Referat mavzusini yozing:", reply_markup=get_cancel_kb())
    await state.set_state(StudentStates.waiting_for_referat_topic)

@router.message(StudentStates.waiting_for_referat_topic)
async def handle_referat(message: types.Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        from .common import get_main_menu
        await state.clear()
        return await message.answer("Bekor qilindi.", reply_markup=get_main_menu(message.from_user.id))
    
    await message.answer("⏳ AI referat yozmoqda (taxminan 1-2 daqiqa)...")
    from .common import get_main_menu
    res = await ai_generate_referat(message.text)
    
    # Generate and send DOCX
    safe_topic = "".join([c for c in message.text if c.isalnum() or c==' ']).strip()[:30]
    filename = f"referat_{message.from_user.id}_{safe_topic}.docx"
    filepath = os.path.join(TEMP_DIR, filename)
    
    try:
        create_referat_docx(message.text, res, filepath)
        await message.answer_document(
            types.FSInputFile(filepath),
            caption=f"📄 **Mavzu:** {message.text}\n\nTayyor referatni yuklab oling!",
            parse_mode="Markdown",
            reply_markup=get_main_menu(message.from_user.id)
        )
    except Exception as e:
        await message.answer(f"Xato yuz berdi: {e}")
        # Fallback to text if docx fails
        for i in range(0, len(res), 4000):
            await message.answer(res[i:i+4000], reply_markup=get_main_menu(message.from_user.id) if i+4000 >= len(res) else None)
    finally:
        if os.path.exists(filepath):
            os.remove(filepath)
            
    await state.clear()

# Test Generator
@router.message(F.text == "📚 Test generator")
async def get_test_topic(message: types.Message, state: FSMContext):
    log_event(message.from_user.id, "Test generator")
    from .konspekt import get_cancel_kb
    await message.answer("Test mavzusini va savollar sonini yuboring (Masalan: Informatika 10):", reply_markup=get_cancel_kb())
    await state.set_state(StudentStates.waiting_for_test_topic)

@router.message(StudentStates.waiting_for_test_topic)
async def handle_test(message: types.Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        from .common import get_main_menu
        await state.clear()
        return await message.answer("Bekor qilindi.", reply_markup=get_main_menu(message.from_user.id))
    
    text = message.text.strip()
    count = 5
    topic = text
    
    # Try different separators
    if ";" in text:
        parts = text.split(";")
        topic = parts[0].strip()
        if parts[1].strip().isdigit():
            count = int(parts[1].strip())
    else:
        parts = text.split()
        if len(parts) > 1 and parts[-1].isdigit():
            count = int(parts.pop())
            topic = " ".join(parts)
    
    await message.answer(f"⏳ <b>{html.quote(topic)}</b> bo'yicha {count} ta test tayyorlanmoqda...", parse_mode="HTML")
    from .common import get_main_menu
    res = await ai_generate_test(topic, count)
    
    # Split response if too long
    for i in range(0, len(res), 4000):
        # AI output typically contains markdown, but since we use HTML mode, we should be careful.
        # Actually, for test generation, the AI usually returns Markdown. 
        # Safest is to disable parsing for the big block or try to convert.
        # Let's use Markdown parsing for the content if it's markdown, but be careful with the initial message.
        # Wait, if AI returns Markdown (**bold**), and we use HTML, it won't render.
        # We should keep Markdown for the AI response part IF we trust the AI output.
        # But previous errors were due to user input/filenames.
        # For this specific block, let's stick to Markdown but ensure previous messages were safe.
        # Actually, let's just use NO parse_mode for the big content block to be safe, 
        # or Markdown if we are confident. AI models adhere to markdown well usually.
        # The crash happens when we mix user input with markdown characters.
        await message.answer(res[i:i+4000], reply_markup=get_main_menu(message.from_user.id) if i+4000 >= len(res) else None)
    await state.clear()

# GPA Hisoblash
@router.message(F.text == "🧮 GPA hisoblash")
async def ask_gpa(message: types.Message, state: FSMContext):
    log_event(message.from_user.id, "GPA hisoblash")
    from .konspekt import get_cancel_kb
    await message.answer(
        "📊 **GPA hisoblash (HEMIS tizimi)**\n\n"
        "Baholaringizni quyidagi formatda yuboring:\n"
        "`Fan_nomi  Baho  Kredit` (har birini yangi qatorda)\n\n"
        "**Misol:**\n"
        "Matematika 95 5\n"
        "Ingliz tili 4 3\n"
        "Tarix 75 4\n\n"
        "💡 *Baho sifatida raqam (90, 85) yoki 5 ballik baho (5, 4, 3) kiritishingiz mumkin.*",
        parse_mode="Markdown",
        reply_markup=get_cancel_kb()
    )
    await state.set_state(StudentStates.waiting_for_gpa_data)

@router.message(StudentStates.waiting_for_gpa_data)
async def handle_gpa(message: types.Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        from .common import get_main_menu
        await state.clear()
        return await message.answer("Bekor qilindi.", reply_markup=get_main_menu(message.from_user.id))
    
    lines = message.text.strip().splitlines()
    total_points = 0.0
    total_credits = 0.0
    errors = []
    processed_count = 0

    for i, line in enumerate(lines, 1):
        line = line.strip()
        if not line: continue
        
        parts = line.split()
        if len(parts) < 2:
            errors.append(f"{i}-qator: Ma'lumot yetarli emas (Baho va Kredit bo'lishi shart).")
            continue
            
        try:
            # Parse from right to left
            # Format: Subject Name Score Credit
            # Example: Mathematics 90 5 or History of Art 85 4
            if len(parts) < 2:
                errors.append(f"{i}-qator: Ma'lumot yetarli emas.")
                continue
                
            credit_str = parts[-1].replace(",", ".")
            score_str = parts[-2].replace(",", ".")
            
            credit = float(credit_str)
            score = float(score_str)
            
            # Handle score/grade
            if score <= 5: 
                # Direct 5-point scale (standard grade)
                if score >= 4.5: grade = 4.0
                elif score >= 3.5: grade = 3.0
                elif score >= 2.5: grade = 2.0
                else: grade = 0.0
            else:
                # 100-point scale (HEMIS system)
                if 90 <= score <= 100: grade = 4.0
                elif 80 <= score < 90: grade = 3.0
                elif 60 <= score < 80: grade = 2.0
                else: grade = 0.0
            
            total_points += grade * credit
            total_credits += credit
            processed_count += 1
        except ValueError:
             errors.append(f"{i}-qator: Baho yoki Kredit raqam bo'lishi kerak.")

    from .common import get_main_menu
    from aiogram import html
    if errors:
        error_text = "\n".join(errors[:5])
        if len(errors) > 5: error_text += "\n..."
        await message.answer(f"⚠️ <b>Ba'zi qatorlarda xatolik aniqlandi:</b>\n\n{html.quote(error_text)}\n\nIltimos, formatni tekshirib qaytadan urinib ko'ring.", parse_mode="HTML")
        # Don't clear state, let user try again or cancel
    elif processed_count == 0:
        await message.answer("❌ Hech qanday ma'lumot qayta ishlanmadi. Iltimos, namunadagidek yuboring.")
    else:
        gpa = total_points / total_credits
        await message.answer(
            f"✅ <b>GPA hisoblandi!</b>\n\n"
            f"📚 Fanlar soni: {processed_count}\n"
            f"🔢 Jami kreditlar: {total_credits}\n"
            f"📊 Sizning GPA: <b>{gpa:.2f}</b>", 
            parse_mode="HTML", 
            reply_markup=get_main_menu(message.from_user.id)
        )
        await state.clear()

# Deadline
@router.message(F.text == "⏰ Deadline qo'shish")
async def ask_deadline_title(message: types.Message, state: FSMContext):
    from .konspekt import get_cancel_kb
    await message.answer("📌 **Vazifa nomini kiriting:**\n\n(Masalan: Matematika nazorat ishi)", parse_mode="Markdown", reply_markup=get_cancel_kb())
    await state.set_state(StudentStates.waiting_for_deadline_title)

@router.message(StudentStates.waiting_for_deadline_title)
async def handle_deadline_title(message: types.Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        from .common import get_main_menu
        await state.clear()
        return await message.answer("Bekor qilindi.", reply_markup=get_main_menu(message.from_user.id))
    
    await state.update_data(title=message.text)
    
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    builder = InlineKeyboardBuilder()
    builder.button(text="Bugun", callback_data="dl_date_today")
    builder.button(text="Ertaga", callback_data="dl_date_tomorrow")
    builder.button(text="Dushanba", callback_data="dl_date_monday")
    builder.button(text="Boshqa sana...", callback_data="dl_date_custom")
    builder.adjust(2)
    
    await message.answer(
        "📅 **Muddatni tanlang yoki kiriting:**\n\n"
        "Format: `KK.OO.YYYY` (Masalan: `15.01.2026`)",
        parse_mode="Markdown",
        reply_markup=builder.as_markup()
    )
    await state.set_state(StudentStates.waiting_for_deadline_time)

@router.callback_query(F.data.startswith("dl_date_"), StudentStates.waiting_for_deadline_time)
async def handle_deadline_date_callback(callback: types.CallbackQuery, state: FSMContext):
    date_type = callback.data.replace("dl_date_", "")
    tz = pytz.timezone(TIMEZONE)
    now = datetime.datetime.now(tz)
    
    target_date = now
    if date_type == "today":
        target_date = now
    elif date_type == "tomorrow":
        target_date = now + datetime.timedelta(days=1)
    elif date_type == "monday":
        days_ahead = 0 - now.weekday()
        if days_ahead <= 0: days_ahead += 7
        target_date = now + datetime.timedelta(days=days_ahead)
    elif date_type == "custom":
        await callback.message.answer("Sana kiriting (format: `KK.OO.YYYY`):", parse_mode="Markdown")
        await callback.answer()
        return

    await state.update_data(date=target_date.strftime("%d.%m.%Y"))
    
    # Show time options
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    builder = InlineKeyboardBuilder()
    for t in ["09:00", "12:00", "15:00", "18:00", "21:00"]:
        builder.button(text=t, callback_data=f"dl_time_{t}")
    builder.adjust(3)
    
    await callback.message.edit_text(
        f"🕒 **Vaqtni tanlang:**\n(Sana: {target_date.strftime('%d.%m.%Y')})",
        reply_markup=builder.as_markup()
    )
    await callback.answer()

@router.callback_query(F.data.startswith("dl_time_"), StudentStates.waiting_for_deadline_time)
async def handle_deadline_time_callback(callback: types.CallbackQuery, state: FSMContext):
    time_val = callback.data.replace("dl_time_", "")
    data = await state.get_data()
    date_str = data.get("date")
    
    full_str = f"{date_str} {time_val}"
    try:
        tz = pytz.timezone(TIMEZONE)
        due = datetime.datetime.strptime(full_str, "%d.%m.%Y %H:%M")
        due = tz.localize(due)
        
        from database import add_deadline
        from .common import get_main_menu
        from aiogram import html
        
        safe_title = html.quote(data.get('title', 'Vazifa'))
        add_deadline(callback.from_user.id, data['title'], due.isoformat())
        
        await callback.message.edit_text(
            f"✅ **Deadline saqlandi!**\n\n"
            f"📌 **Vazifa:** {safe_title}\n"
            f"⏰ **Muddat:** {due.strftime('%d.%m.%Y %H:%M')}\n\n"
            f"Sizga muddat yaqinlashganda eslatma yuboramiz."
        )
        await callback.message.answer("Asosiy menyu:", reply_markup=get_main_menu(callback.from_user.id))
        await state.clear()
    except Exception as e:
        await callback.message.answer(f"❌ Xatolik yuz berdi: {str(e)}")
    await callback.answer()

@router.message(StudentStates.waiting_for_deadline_time)
async def handle_deadline_time_manual(message: types.Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        from .common import get_main_menu
        await state.clear()
        return await message.answer("Bekor qilindi.", reply_markup=get_main_menu(message.from_user.id))
    
    data = await state.get_data()
    text = message.text.strip()
    tz = pytz.timezone(TIMEZONE)
    now = datetime.datetime.now(tz)
    
    try:
        # Case 1: HH:MM (Assume today/tomorrow)
        if len(text) <= 5 and ":" in text:
            tm = datetime.datetime.strptime(text, "%H:%M")
            due = now.replace(hour=tm.hour, minute=tm.minute, second=0, microsecond=0)
            if due < now:
                due += datetime.timedelta(days=1)
        # Case 2: DD.MM.YYYY
        elif len(text) <= 10 and text.count(".") == 2:
            await state.update_data(date=text)
            builder = InlineKeyboardBuilder()
            for t in ["09:00", "12:00", "15:00", "18:00", "21:00"]:
                builder.button(text=t, callback_data=f"dl_time_{t}")
            builder.adjust(3)
            return await message.answer(f"🕒 **Sana qabul qilindi ({text}). Endi vaqtni tanlang:**", reply_markup=builder.as_markup(), parse_mode="Markdown")
        # Case 3: DD.MM.YYYY HH:MM
        else:
            for fmt in ["%d.%m.%Y %H:%M", "%Y-%m-%d %H:%M"]:
                try:
                    due = datetime.datetime.strptime(text, fmt)
                    due = tz.localize(due)
                    break
                except: continue
            else:
                raise ValueError("Format error")

        from database import add_deadline
        from .common import get_main_menu
        from aiogram import html
        
        safe_title = html.quote(data.get('title', 'Vazifa'))
        add_deadline(message.from_user.id, data['title'], due.isoformat())
        
        await message.answer(
            f"✅ **Deadline saqlandi!**\n\n"
            f"📌 **Vazifa:** {safe_title}\n"
            f"⏰ **Muddat:** {due.strftime('%d.%m.%Y %H:%M')}\n\n"
            f"Sizga muddat yaqinlashganda eslatma yuboramiz.",
            reply_markup=get_main_menu(message.from_user.id),
            parse_mode="HTML"
        )
        await state.clear()
    except Exception:
        await message.answer("❌ Noto'g'ri format. Iltimos, `30.12.2025 18:00` kabi kiriting yoki tugmalardan foydalaning.")

@router.message(F.text == "📋 Mening deadline'larim")
async def show_deadlines(message: types.Message):
    from database import get_user_deadlines
    rows = get_user_deadlines(message.from_user.id)
    
    if not rows:
        return await message.answer("Sizda hozircha faol deadline'lar yo'q.")
    
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    text = "📋 **Sizning deadline'laringiz:**\n\n"
    builder = InlineKeyboardBuilder()
    
    for rid, title, due in rows:
        dt = datetime.datetime.fromisoformat(due)
        text += f"🔹 **{title}**\n   📅 {dt.strftime('%d.%m.%Y %H:%M')}\n\n"
        builder.button(text=f"🗑 {title[:15]}...", callback_data=f"dl_del_{rid}")
    
    builder.adjust(1)
    await message.answer(text, reply_markup=builder.as_markup(), parse_mode="Markdown")

@router.callback_query(F.data.startswith("dl_del_"))
async def process_dl_delete(callback: types.CallbackQuery):
    from database import delete_deadline
    dl_id = int(callback.data.replace("dl_del_", ""))
    delete_deadline(dl_id)
    await callback.answer("O'chirildi.")
    await callback.message.edit_text("✅ Tanlangan deadline o'chirildi.")

# Presentation Generator
@router.message(F.text == "📊 Prezentatsiya (AI)")
async def ask_ppt_topic(message: types.Message, state: FSMContext):
    log_event(message.from_user.id, "AI Prezentatsiya")
    if not is_premium(message.from_user.id):
        return await message.answer("Prezentatsiya generatori faqat Premium foydalanuvchilar uchun.")
    
    from .konspekt import get_cancel_kb
    await message.answer("Slaydlar uchun mavzuni kiriting:", reply_markup=get_cancel_kb())
    await state.set_state(StudentStates.waiting_for_ppt_topic)

@router.message(StudentStates.waiting_for_ppt_topic)
async def handle_ppt_topic(message: types.Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        from .common import get_main_menu
        await state.clear()
        return await message.answer("Bekor qilindi.", reply_markup=get_main_menu(message.from_user.id))
    
    await state.update_data(ppt_topic=message.text)
    
    from database import get_template_categories
    categories = get_template_categories()
    
    if not categories:
        # If no custom categories, show default directly or fallback to "all templates"
        from database import get_all_templates
        templates = get_all_templates()
        if not templates:
            return await start_ppt_generation(message, state, None)
            
        builder = InlineKeyboardBuilder()
        for tid, name, cat, path in templates:
            builder.button(text=name, callback_data=f"ppt_tpl_{tid}")
        builder.button(text="Standart (Ko'k)", callback_data="ppt_tpl_default")
        builder.adjust(2)
        await message.answer("Prezentatsiya uchun dizaynni tanlang:", reply_markup=builder.as_markup())
    else:
        builder = InlineKeyboardBuilder()
        for cat in categories:
            builder.button(text=cat, callback_data=f"ppt_cat_{cat}")
        builder.button(text="Standart (Ko'k)", callback_data="ppt_tpl_default")
        builder.adjust(2)
        await message.answer("Prezentatsiya uchun bo'limni tanlang:", reply_markup=builder.as_markup())

@router.callback_query(F.data.startswith("ppt_cat_"))
async def handle_ppt_category_selection(callback: types.CallbackQuery, state: FSMContext):
    category = callback.data.replace("ppt_cat_", "")
    from database import get_templates_by_category
    templates = get_templates_by_category(category)
    
    if not templates:
        return await callback.answer("Ushbu bo'limda shablonlar yo'q.")
        
    builder = InlineKeyboardBuilder()
    for tid, name, path in templates:
        builder.button(text=name, callback_data=f"ppt_tpl_{tid}")
    
    builder.button(text="🔙 Orqaga", callback_data="ppt_back_to_cats")
    builder.adjust(2)
    
    await callback.message.edit_text(f"📁 **{category}** bo'limidagi shablonlar:", reply_markup=builder.as_markup(), parse_mode="Markdown")

@router.callback_query(F.data == "ppt_back_to_cats")
async def handle_ppt_back_to_cats(callback: types.CallbackQuery, state: FSMContext):
    from database import get_template_categories
    categories = get_template_categories()
    
    builder = InlineKeyboardBuilder()
    for cat in categories:
        builder.button(text=cat, callback_data=f"ppt_cat_{cat}")
    builder.button(text="Standart (Ko'k)", callback_data="ppt_tpl_default")
    builder.adjust(2)
    await callback.message.edit_text("Prezentatsiya uchun bo'limni tanlang:", reply_markup=builder.as_markup())

@router.callback_query(F.data.startswith("ppt_tpl_"))
async def handle_ppt_template_selection(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    topic = data.get('ppt_topic')
    if not topic:
        return await callback.answer("Xatolik: Mavzu topilmadi.")
    
    tpl_id_str = callback.data.replace("ppt_tpl_", "")
    template_path = None
    
    if tpl_id_str != "default":
        from database import get_template_by_id
        res = get_template_by_id(int(tpl_id_str))
        if res:
            template_path = res[1]
    
    await callback.message.edit_text(f"⏳ **{topic}** bo'yicha prezentatsiya tayyorlanmoqda...")
    await start_ppt_generation(callback.message, state, template_path, topic)
    await callback.answer()

async def start_ppt_generation(message: types.Message, state: FSMContext, template_path: str, topic: str = None):
    if not topic:
        data = await state.get_data()
        topic = data.get('ppt_topic')
    
    content = await ai_generate_ppt_content(topic)
    
    filename = f"presentation_{message.chat.id}.pptx"
    filepath = os.path.join(TEMP_DIR, filename)
    
    try:
        from .common import get_main_menu
        create_presentation_pptx(topic, content, filepath, template_path)
        await message.answer_document(
            types.FSInputFile(filepath),
            caption=f"📊 **Mavzu:** {topic}\n\nSizning prezentatsiyangiz tayyor!",
            reply_markup=get_main_menu(message.chat.id)
        )
    except Exception as e:
        await message.answer(f"Xato yuz berdi: {e}")
    finally:
        if os.path.exists(filepath):
            os.remove(filepath)
            
    await state.clear()
