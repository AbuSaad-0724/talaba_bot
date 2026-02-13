# Talaba Bot - Professional Versiya

Bu loyiha talabalar uchun sun'iy intellekt (Google Gemini) yordamida referat, prezentatsiya, insho va testlar yaratuvchi Telegram bot hisoblanadi.

## Xususiyatlar

- 🤖 **Google Gemini AI**: Haqiqiy sun'iy intellekt yordamida kontent yaratish.
- ⚡ **Asinxron**: Tezkor ishlash uchun `asyncio` va `aiosqlite`.
- 🌐 **Web App**: Telegram ichida qulay interfeys (FastAPI + HTML/JS).
- 💾 **Ma'lumotlar bazasi**: Foydalanuvchilar va to'lovlar tarixi (`talaba_bot.db`).
- 💳 **To'lov tizimi**: Admin orqali tasdiqlanadigan oddiy to'lov tizimi.

## O'rnatish va Ishga Tushirish

1. **Kutubxonalarni o'rnatish:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Sozlamalar:**
   `config.env` fayliga o'zingizning ma'lumotlaringizni kiriting:
   - `BOT_TOKEN`: BotFather dan olingan token.
   - `GEMINI_API_KEY`: Google AI Studio dan olingan API kalit.
   - `ADMIN_ID`: Sizning Telegram ID raqamingiz.
   - `WEBAPP_URL`: Web App manzili (masalan, ngrok URL).

3. **Ishga tushirish:**
   ```bash
   python main.py
   ```

## Web App haqida

Web App ishlashi uchun bot `https` manzilni talab qiladi. Sinov uchun `ngrok` ishlatishingiz mumkin:
```bash
ngrok http 8081
```
Ngrok bergan URL manzilini `config.env` dagi `WEBAPP_URL` ga yozing.

## Muammolar yuzaga kelsa

- Agar API xatolik bersa, `log` larni tekshiring.
- Bazani yangilash kerak bo'lsa, `talaba_bot.db` faylini o'chirib qayta ishga tushiring (eski ma'lumotlar o'chib ketadi).
