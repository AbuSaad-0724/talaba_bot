import logging
from services.multi_ai_service import multi_ai_generate
from services.gemini_service import (
    gemini_summarize, gemini_chat, gemini_solve_homework, gemini_generate_flashcards
)

logger = logging.getLogger(__name__)

async def ai_summarize(text: str):
    return await gemini_summarize(text)

async def ai_generate_referat(topic: str):
    system = "Sen talabalarga referat yozishda yordam berasan. Matn chuqur va akademik uslubda bo'lsin. Mavzu bo'yicha kamida 5 ta bo'limdan iborat reja va batafsil matn tayyorla."
    return await multi_ai_generate(f"Mavzu: {topic}", system, max_tokens=3500)

async def ai_generate_test(topic: str, count: int = 5):
    system = f"Berilgan mavzu bo'yicha aniq {count} ta test (MCQ) yarat. Har bir testda 4 ta variant (A, B, C, D) bo'lsin va oxirida to'g'ri javoblarni ro'yxat ko'rinishida ko'rsat."
    return await multi_ai_generate(f"Mavzu: {topic}", system, max_tokens=2000)

async def ai_generate_ppt_content(topic: str):
    system = "Sen professional prezentatsiya tayyorlovchi yordamchisan. Berilgan mavzu bo'yicha 7-10 ta slayddan iborat reja va har bir slayd uchun qisqa, mazmunli matn yozib ber. Har bir yangi slaydni '|||' belgisi bilan boshla. Format:\n||| Sarlavha\nMatn...\n||| Keyingi Sarlavha\nMatn..."
    return await multi_ai_generate(f"Mavzu: {topic}", system, max_tokens=3000)

async def ai_chat_tutor(user_message: str, chat_history: list = None):
    return await gemini_chat(user_message, chat_history)

async def ai_solve_homework(image_path: str):
    return await gemini_solve_homework(image_path)

async def ai_check_essay(essay_text: str):
    system = "Sen professional insho tekshiruvchisan. Berilgan matnni tahlil qilib: 1. Grammatika xatolarini top 2. Uslub va ifoda tavsiyalari ber 3. Umumiy baho ber (5 ball) 4. Yaxshilash yo'llarini ko'rsat."
    return await multi_ai_generate(f"Insho:\n{essay_text}", system, max_tokens=1500)

async def ai_generate_flashcards(topic: str, count: int = 10):
    return await gemini_generate_flashcards(topic, count)

async def ai_transcribe_audio(file_path: str):
    try:
        import google.generativeai as genai
        with open(file_path, "rb") as f:
            audio_data = f.read()
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content([
            "Ushbu audio faylni so'zma-so'z matnga aylantirib ber (transkripsiya).",
            {"mime_type": "audio/mpeg", "data": audio_data}
        ])
        return response.text
    except Exception as e:
        logger.error(f"Audio Transcription Error: {e}")
        return "Audio faylni tahlil qilishda xatolik yuz berdi."
