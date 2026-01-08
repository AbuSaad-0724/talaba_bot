from aiogram import types, Router, F
from database import log_event
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from services.ai_service import ai_summarize
from services.file_parser import extract_from_docx, extract_from_pdf, extract_from_image
from database import is_premium
from config import TEMP_DIR
import os

router = Router()

class KonspektStates(StatesGroup):
    waiting_for_file = State()
    waiting_for_photo = State()
    waiting_for_audio = State()

def get_cancel_kb():
    builder = ReplyKeyboardBuilder()
    builder.row(types.KeyboardButton(text="❌ Bekor qilish"))
    return builder.as_markup(resize_keyboard=True)



@router.message(F.text == "📂 Fayl → Konspekt")
async def ask_file(message: types.Message, state: FSMContext):
    log_event(message.from_user.id, "Fayl -> Konspekt")
    await message.answer("Iltimos, PDF yoki DOCX faylni yuboring:", reply_markup=get_cancel_kb())
    await state.set_state(KonspektStates.waiting_for_file)

@router.message(F.text == "📸 Foto → Konspekt")
async def ask_photo(message: types.Message, state: FSMContext):
    log_event(message.from_user.id, "Foto -> Konspekt")
    await message.answer("Matn tushirilgan rasmni yuboring:", reply_markup=get_cancel_kb())
    await state.set_state(KonspektStates.waiting_for_photo)


@router.message(F.text == "🔙 Orqaga")
async def back_to_main_menu(message: types.Message, state: FSMContext):
    from .common import get_main_menu
    await state.clear()
    await message.answer("Asosiy menyu:", reply_markup=get_main_menu(message.from_user.id))

@router.message(F.text == "❌ Bekor qilish")
async def cancel_handler(message: types.Message, state: FSMContext):
    from .common import get_main_menu
    await state.clear()
    await message.answer("Amal bekor qilindi.", reply_markup=get_main_menu(message.from_user.id))

@router.message(KonspektStates.waiting_for_file, F.document)
async def handle_konspekt_file(message: types.Message, state: FSMContext):
    doc = message.document
    fn = doc.file_name.lower()
    
    if not (fn.endswith(".pdf") or fn.endswith(".docx")):
        return await message.answer("Faqat .pdf va .docx formatlar qabul qilinadi.")
    
    await message.answer("Fayl qabul qilindi, o'qilmoqda...")
    path = os.path.join(TEMP_DIR, f"{doc.file_id}_{fn}")
    await message.bot.download(doc, destination=path)
    
    text = ""
    if fn.endswith(".pdf"):
        text = extract_from_pdf(path)
    else:
        text = extract_from_docx(path)
    
    if os.path.exists(path): os.remove(path)
    
    if not text.strip():
        return await message.answer("Faylni o'qishda muammo bo'ldi yoki fayl bo'sh.")
    
    await message.answer("⏳ Tahlil qilinmoqda...")
    from .common import get_main_menu
    res = await ai_summarize(text)
    await message.answer(f"📄 **Fayldan konspekt:**\n\n{res}", parse_mode="Markdown", reply_markup=get_main_menu(message.from_user.id))
    await state.clear()

@router.message(KonspektStates.waiting_for_photo, F.photo)
async def handle_konspekt_photo(message: types.Message, state: FSMContext):
    photo = message.photo[-1]
    path = os.path.join(TEMP_DIR, f"{photo.file_id}.jpg")
    await message.bot.download(photo, destination=path)
    
    await message.answer("⏳ Rasm Gemini AI orqali tahlil qilinmoqda...")
    
    from services.gemini_service import gemini_vision
    # Using a specialized prompt for conspekt from image
    prompt = "Ushbu rasmdagi matnni o'qib chiq va uni chiroyli, mazmunli konspekt (summary) ko'rinishida yozib ber. O'zbek tilida."
    res = await gemini_vision(path, prompt)
    
    if os.path.exists(path): os.remove(path)
    
    from handlers.common import get_main_menu
    await message.answer(f"📄 **Rasmdan konspekt:**\n\n{res}", parse_mode="Markdown", reply_markup=get_main_menu(message.from_user.id))
    await state.clear()

