import google.generativeai as genai
from groq import Groq
import httpx
from config import GEMINI_API_KEY, GROQ_API_KEY, OPENROUTER_API_KEY, MISTRAL_API_KEY, TIMEZONE
import logging
import datetime
import pytz

logger = logging.getLogger(__name__)

# System Instructions
SYSTEM_PROMPT = """Sen 'Talaba Servis Bot'ning aqlli va kishiga do'stona munosabatda bo'luvchi AI yordamchisisan. 
Sening vazifang talabalarga o'qishda, masalalar yechishda va savollarga javob berishda yordam berish.
Javoblaring:
- O'zbek tilida, aniq va batafsil bo'lsin.
- Agar foydalanuvchi "salom" desa, samimiy javob ber. 
- Ma'lumotlarni chiroyli formatda (markdown) taqdim et.
- Hech qachon javobni "Xayr" yoki ma'nosiz so'zlar bilan asossiz boshlama.
"""

def get_current_context():
    tz = pytz.timezone(TIMEZONE)
    now = datetime.datetime.now(tz)
    return f"\nHozirgi vaqt: {now.strftime('%Y-%m-%d %H:%M:%S')}, kun: {now.strftime('%A')}."

# Providers setup
gemini_keys = [k.strip() for k in GEMINI_API_KEY.split(",")] if GEMINI_API_KEY else []
current_gemini_index = 0

def configure_gemini():
    if gemini_keys:
        genai.configure(api_key=gemini_keys[current_gemini_index])

configure_gemini()

async def gemini_chat_logic(message: str, history: list = None):
    try:
        model = genai.GenerativeModel(
            model_name='gemini-1.5-flash',
            system_instruction=SYSTEM_PROMPT + get_current_context()
        )
        
        formatted_history = []
        if history:
            for msg in history[-6:]:
                role = "user" if msg.get("role") == "user" else "model"
                formatted_history.append({"role": role, "parts": [msg.get("content", "")]})
        
        chat = model.start_chat(history=formatted_history)
        response = chat.send_message(message)
        return response.text
    except Exception as e:
        logger.error(f"Gemini Logic Error: {e}")
        raise e

async def groq_chat_logic(message: str, history: list = None):
    if not GROQ_API_KEY:
        raise Exception("Groq API key missing")
    
    client = Groq(api_key=GROQ_API_KEY)
    messages = [{"role": "system", "content": SYSTEM_PROMPT + get_current_context()}]
    
    if history:
        for msg in history[-6:]:
            messages.append({"role": msg.get("role", "user"), "content": msg.get("content", "")})
    
    messages.append({"role": "user", "content": message})
    
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        temperature=0.7,
        max_tokens=2048
    )
    return completion.choices[0].message.content

async def openrouter_chat_logic(message: str, history: list = None):
    if not OPENROUTER_API_KEY:
        raise Exception("OpenRouter key missing")
        
    async with httpx.AsyncClient() as client:
        full_prompt = f"{SYSTEM_PROMPT}\n{get_current_context()}\n\nUser: {message}"
        response = await client.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "HTTP-Referer": "https://github.com/AbuSaad-0724/talaba_bot",
            },
            json={
                "model": "google/gemini-2.0-flash-exp:free", # Eng yaxshi bepul model
                "messages": [{"role": "user", "content": full_prompt}]
            },
            timeout=20.0
        )
        data = response.json()
        if 'choices' in data:
            return data['choices'][0]['message']['content']
        raise Exception(f"OpenRouter Error: {data}")

async def gemini_chat(user_message: str, chat_history: list = None):
    # 1. Try Gemini
    try:
        return await gemini_chat_logic(user_message, chat_history)
    except Exception:
        pass
        
    # 2. Try Groq (Super fast fallback)
    try:
        return await groq_chat_logic(user_message, chat_history)
    except Exception:
        pass

    # 3. Try OpenRouter (Final fallback)
    try:
        return await openrouter_chat_logic(user_message, chat_history)
    except Exception as e:
        logger.error(f"All AI providers failed: {e}")
        return "Hozirda tizimda texnik ishlar ketmoqda. Iltimos, birozdan so'ng savol bering."

# Helper functions
async def gemini_summarize(text: str): return await gemini_chat(f"Ushbu matnni batafsil konspekt qil:\n\n{text}")
async def gemini_generate_referat(topic: str): return await gemini_chat(f"'{topic}' mavzusida akademik referat yoz.")
async def gemini_generate_test(topic: str, count: int = 5): return await gemini_chat(f"'{topic}' mavzusida {count} ta murakkab test savollarini yarat.")
async def gemini_solve_homework(image_path: str):
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        with open(image_path, "rb") as f:
            img = [{"mime_type": "image/jpeg", "data": f.read()}]
        response = model.generate_content([SYSTEM_PROMPT + "\nUshbu rasmdagi masalani yech.", img[0]])
        return response.text
    except:
        return "Rasm tahlilida xatolik. Iltimos, matn ko'rinishida yozing."

async def gemini_generate_flashcards(topic: str, count: int = 10): return await gemini_chat(f"'{topic}' mavzusida {count} ta flashcard yarat.")
async def gemini_generate_ppt_content(topic: str): return await gemini_chat(f"'{topic}' mavzusida slaydlar uchun reja va matn tayyorla.")

async def gemini_generate(prompt: str, system_instruction: str = None, max_tokens: int = 500):
    """Alias for gemini_chat to support existing code"""
    return await gemini_chat(prompt)
