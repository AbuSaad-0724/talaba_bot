import logging
import httpx
from groq import AsyncGroq
from config import GROQ_API_KEY, OPENROUTER_API_KEY, MISTRAL_API_KEY
from services.gemini_service import gemini_generate

logger = logging.getLogger(__name__)

async def groq_generate(prompt: str, system_instruction: str = None, max_tokens: int = 2000):
    """Generate text using Groq (Llama 3.3)"""
    if not GROQ_API_KEY:
        return None
    try:
        client = AsyncGroq(api_key=GROQ_API_KEY)
        messages = []
        if system_instruction:
            messages.append({"role": "system", "content": system_instruction})
        messages.append({"role": "user", "content": prompt})
        
        completion = await client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            max_tokens=max_tokens,
        )
        return completion.choices[0].message.content
    except Exception as e:
        logger.error(f"Groq Error: {e}")
        return None

async def openrouter_generate(prompt: str, system_instruction: str = None, max_tokens: int = 2000):
    """Generate text using OpenRouter (Claude 3.5 Sonnet)"""
    if not OPENROUTER_API_KEY:
        return None
    try:
        async with httpx.AsyncClient() as client:
            headers = {
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "HTTP-Referer": "https://github.com/AbuSaad-0724/talaba_bot",
                "X-Title": "Talaba Bot"
            }
            payload = {
                "model": "anthropic/claude-3.5-sonnet",
                "messages": [],
                "max_tokens": max_tokens
            }
            if system_instruction:
                payload["messages"].append({"role": "system", "content": system_instruction})
            payload["messages"].append({"role": "user", "content": prompt})
            
            response = await client.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload, timeout=60)
            if response.status_code == 200:
                data = response.json()
                return data['choices'][0]['message']['content']
            return None
    except Exception as e:
        logger.error(f"OpenRouter Error: {e}")
        return None

async def mistral_generate(prompt: str, system_instruction: str = None, max_tokens: int = 2000):
    """Generate text using Mistral AI"""
    if not MISTRAL_API_KEY:
        return None
    try:
        async with httpx.AsyncClient() as client:
            headers = {"Authorization": f"Bearer {MISTRAL_API_KEY}"}
            payload = {
                "model": "mistral-small-latest",
                "messages": [],
                "max_tokens": max_tokens
            }
            if system_instruction:
                payload["messages"].append({"role": "system", "content": system_instruction})
            payload["messages"].append({"role": "user", "content": prompt})
            
            response = await client.post("https://api.mistral.ai/v1/chat/completions", headers=headers, json=payload, timeout=60)
            if response.status_code == 200:
                data = response.json()
                return data['choices'][0]['message']['content']
            return None
    except Exception as e:
        logger.error(f"Mistral Error: {e}")
        return None

async def multi_ai_generate(prompt: str, system_instruction: str = None, max_tokens: int = 2000):
    """Unified generator with fallback: Claude -> Gemini -> Groq -> Mistral"""
    # 1. Claude (OpenRouter) - Highest quality
    res = await openrouter_generate(prompt, system_instruction, max_tokens)
    if res: return res
    
    # 2. Gemini - Main free provider
    res = await gemini_generate(prompt, system_instruction, max_tokens)
    if res and "xatolik yuz berdi" not in res.lower() and "limit" not in res.lower():
        return res
        
    # 3. Groq - Fast fallback
    res = await groq_generate(prompt, system_instruction, max_tokens)
    if res: return res
    
    # 4. Mistral - Final fallback
    res = await mistral_generate(prompt, system_instruction, max_tokens)
    if res: return res
    
    return "Xatolik: Barcha AI xizmatlari javob bermadi."
