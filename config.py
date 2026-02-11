import os
from dotenv import load_dotenv

load_dotenv(override=True)

# Telegram Bot Token
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Admin ID
ADMIN_ID = int(os.getenv("ADMIN_ID", 0))

# OpenAI API Key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Gemini API Key (BEPUL!)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Groq API Key
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# OpenRouter API Key
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# Mistral API Key
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

# WebApp URL
WEBAPP_URL = os.getenv("WEBAPP_URL")

# Backend API Server URL (Ngrok or Public IP)
SERVER_URL = os.getenv("SERVER_URL", "")

# Payment Details
HUMO_CARD = os.getenv("HUMO_CARD", "9860 1201 1367 9696")
PREMIUM_PRICE = int(os.getenv("PREMIUM_PRICE", 25000))
DEFAULT_PREMIUM_DAYS = 30

# Timezone
TIMEZONE = "Asia/Tashkent"

# Database
DB_PATH = "talaba_superbot.db"

# Folders
TEMP_DIR = "temp"
if not os.path.exists(TEMP_DIR):
    os.makedirs(TEMP_DIR)
