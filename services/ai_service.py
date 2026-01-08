"""
AI Service - Gemini API (BEPUL!)

Bu fayl Gemini API'ni ishlatadi (OpenAI o'rniga)
Afzalliklari:
- 100% BEPUL (1,500 req/kun)
- 2x tezroq
- Vision bor
- Yaxshi sifat
"""

from services.gemini_service import (
    gemini_summarize,
    gemini_generate_referat,
    gemini_generate_test,
    gemini_generate_ppt_content,
    gemini_chat,
    gemini_solve_homework,
    gemini_check_essay,
    gemini_generate_flashcards
)
import logging

logger = logging.getLogger(__name__)

# ===== BASIC FUNCTIONS =====

async def ai_summarize(text: str):
    """Summarize text using Gemini"""
    return await gemini_summarize(text)

async def ai_generate_referat(topic: str):
    """Generate referat using Gemini"""
    return await gemini_generate_referat(topic)

async def ai_generate_test(topic: str, count: int = 5):
    """Generate test using Gemini"""
    return await gemini_generate_test(topic, count)

async def ai_generate_ppt_content(topic: str):
    """Generate presentation content using Gemini"""
    return await gemini_generate_ppt_content(topic)

# ===== PREMIUM FEATURES =====

async def ai_chat_tutor(user_message: str, chat_history: list = None):
    """AI Tutor - Chat with context using Gemini"""
    return await gemini_chat(user_message, chat_history)

async def ai_solve_homework(image_path: str):
    """Homework Solver - Solve problems from image using Gemini Vision"""
    return await gemini_solve_homework(image_path)

async def ai_check_essay(essay_text: str):
    """Essay Checker using Gemini"""
    return await gemini_check_essay(essay_text)

async def ai_generate_flashcards(topic: str, count: int = 10):
    """Generate flashcards using Gemini"""
    return await gemini_generate_flashcards(topic, count)


# ===== AUDIO TRANSCRIPTION (Removed to eliminate OpenAI costs) =====

async def ai_transcribe_audio(file_path: str):
    """
    Audio transcription using Gemini (Multimodal)
    """
    try:
        from services.gemini_service import gemini_vision # Or a generic gemini_multimodal
        # Re-using gemini_vision logic for audio if mime_type is set correctly
        import google.generativeai as genai
        from config import GEMINI_API_KEY
        
        with open(file_path, "rb") as f:
            audio_data = f.read()
        
        model = genai.GenerativeModel('models/gemini-2.5-flash-lite')
        response = model.generate_content([
            "Ushbu audio faylni so'zma-so'z matnga aylantirib ber (transkripsiya).",
            {"mime_type": "audio/mpeg", "data": audio_data}
        ])
        return response.text
    except Exception as e:
        logger.error(f"Audio Transcription Error: {e}")
        return "Audio faylni tahlil qilishda xatolik yuz berdi."

