from aiogram import types, Router, F, html
from aiogram.utils.keyboard import InlineKeyboardBuilder
from database import log_event
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from services.ai_service import ai_generate_referat, ai_generate_test, ai_generate_ppt_content
from database import is_premium, add_deadline, get_due_deadlines, get_user_language
from utils.texts import get_text, get_all_translations
from utils.docx_gen import create_referat_docx
from utils.pptx_gen import create_presentation_pptx
import datetime
import os
import pytz
import json
from config import TEMP_DIR, TIMEZONE

router = Router()

class StudentStates(StatesGroup):
    waiting_for_referat_topic = State()
    waiting_for_test_topic = State()
    waiting_for_deadline_title = State()
    waiting_for_deadline_time = State()
    waiting_for_ppt_topic = State()

# Referat
@router.message(F.text.in_(get_all_translations('btn_referat')))
async def get_referat_topic(message: types.Message, state: FSMContext):
    log_event(message.from_user.id, "AI Referat")
    if not is_premium(message.from_user.id):
        return await message.answer("Referat generatori faqat Premium foydalanuvchilar uchun.")
    
    from .common import get_cancel_kb
    await message.answer(get_text('referat_topic', message.from_user.id), reply_markup=get_cancel_kb(message.from_user.id))
    await state.set_state(StudentStates.waiting_for_referat_topic)

@router.message(StudentStates.waiting_for_referat_topic)
async def handle_referat(message: types.Message, state: FSMContext):
    if message.text in get_all_translations('cancel'):
        from .common import get_main_menu
        await state.clear()
        return await message.answer("Bekor qilindi.", reply_markup=get_main_menu(message.from_user.id))
    
    await message.answer("⏳ Referat yozilmoqda (taxminan 1-2 daqiqa)...")
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
@router.message(F.text.in_(get_all_translations('btn_test')))
async def get_test_topic(message: types.Message, state: FSMContext):
    log_event(message.from_user.id, "Test generator")
    from .common import get_cancel_kb
    await message.answer(get_text('test_topic', message.from_user.id), reply_markup=get_cancel_kb(message.from_user.id))
    await state.set_state(StudentStates.waiting_for_test_topic)

@router.message(StudentStates.waiting_for_test_topic)
async def handle_test(message: types.Message, state: FSMContext):
    if message.text in get_all_translations('cancel'):
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



# Presentation Generator
@router.message(F.text.in_(get_all_translations('btn_ppt')))
async def ask_ppt_topic(message: types.Message, state: FSMContext):
    log_event(message.from_user.id, "AI Prezentatsiya")
    if not is_premium(message.from_user.id):
        return await message.answer("Prezentatsiya generatori faqat Premium foydalanuvchilar uchun.")
    
    from .common import get_cancel_kb
    await message.answer(get_text('ppt_topic', message.from_user.id), reply_markup=get_cancel_kb(message.from_user.id))
    await state.set_state(StudentStates.waiting_for_ppt_topic)

@router.message(StudentStates.waiting_for_ppt_topic)
async def handle_ppt_topic(message: types.Message, state: FSMContext):
    if message.text in get_all_translations('cancel'):
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
    if not category:
        return await callback.answer("Noto'g'ri so'rov.", show_alert=True)
    
    from database import get_templates_by_category
    templates = get_templates_by_category(category)
    
    if not templates:
        return await callback.answer("Ushbu bo'limda shablonlar yo'q.", show_alert=True)
        
    builder = InlineKeyboardBuilder()
    for tid, name, path in templates:
        builder.button(text=name, callback_data=f"ppt_tpl_{tid}")
    
    builder.button(text="🔙 Orqaga", callback_data="ppt_back_to_cats")
    builder.adjust(2)
    
    try:
        await callback.message.edit_text(f"📁 **{category}** bo'limidagi shablonlar:", reply_markup=builder.as_markup(), parse_mode="Markdown")
    except Exception as e:
        # Fallback without Markdown if editing fails
        await callback.message.edit_text(f"📁 {category} bo'limidagi shablonlar:", reply_markup=builder.as_markup())

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
        return await callback.answer("Xatolik: Mavzu topilmadi.", show_alert=True)
    
    tpl_id_str = callback.data.replace("ppt_tpl_", "")
    template_path = None
    
    if tpl_id_str != "default":
        try:
            tpl_id = int(tpl_id_str)
            from database import get_template_by_id
            res = get_template_by_id(tpl_id)
            if res:
                template_path = res[1]
        except ValueError:
            pass  # Invalid template ID
    
    try:
        await callback.message.edit_text(f"⏳ **{topic}** bo'yicha prezentatsiya tayyorlanmoqda...", parse_mode="Markdown")
    except:
        await callback.message.edit_text(f"⏳ {topic} bo'yicha prezentatsiya tayyorlanmoqda...")
    
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
