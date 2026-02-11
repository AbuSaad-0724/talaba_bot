# 🚀 Talaba Bot Web App Rivojlantirish Rejasi

Talaba Bot Web App hozirda oddiy "Launcher" vazifasini bajarmoqda. Uni to'laqonli **Talaba Super App**iga aylantirish uchun quyidagi rivojlanish bosqichlarini taklif qilaman.

---

## 🎯 1-BOSQICH: Interfeys va Navigatsiya (Frontend)

Hozirgi bitta sahifali dizayndan **Multi-Tab** (ko'p oynali) tizimga o'tish kerak.

### 📱 Yangi Navigatsiya Tuzilmasi (Bottom Navigation Bar):
1.  **🏠 Asosiy (Home):** Botning asosiy AI funksiyalari (Referat, Test, va h.k.) va yangiliklar.
2.  **📅 Jadval (Schedule):** Dars jadvali va kunlik reja.
3.  **✅ Vazifalar (Tasks):** Deadline'lar va shaxsiy vazifalar ro'yxati (Todo list).
4.  **🧰 Asboblar (Tools):** Konspekt muharriri, Kutubxona.
5.  **👤 Profil (Profile):** Foydalanuvchi darajasi, statistikalar, sozlamalar.

---

## 🛠 2-BOSQICH: Yangi Funksiyalar (Features)

Web Appda amalga oshirish qulay bo'lgan, ammo Telegram chatda noqulay bo'lgan funksiyalarni qo'shamiz.

### 1. 📅 Interaktiv Dars Jadvali
*   **Muammo:** Chatda jadvalni ko'rish noqulay.
*   **Yechim:** Haftalik ko'rinishdagi rangli jadval.
*   **Imkoniyatlar:**
    *   Drag & Drop orqali darslarni o'zgartirish.
    *   Dars vaqtida avtomatik "Hozirgi dars" belgisini ko'rsatish.
    *   Xona va o'qituvchi ismini saqlash.


### 3. 📝 Smart Notes (Konspektlar)
*   **Muammo:** Telegramda uzun matn yozish noqulay.
*   **Yechim:** Rich Text Editor (Notion style).
*   **Imkoniyatlar:**
    *   Sarlavhalar, ro'yxatlar, qalin matnlar.
    *   Yozib bo'lgach, "Save" tugmasi orqali botga PDF sifatida jo'natish.

### 4. 📚 Vizual Kutubxona
*   **Muammo:** Fayl nomlari orqali kitob qidirish zerikarli.
*   **Yechim:** Kitob muqovalari (Covers) bilan galereya.
*   **Imkoniyatlar:**
    *   Kategoriyalar bo'yicha filtr (Dasturlash, Tibbiyot, Badiiy).
    *   Qidiruv tizimi.
    *   "O'qish" tugmasi orqali botdan yuklab olish.

### 5. 🏆 Gamification (O'yinlashtirish)
*   **Maqsad:** Foydalanuvchini faol ushlab turish.
*   **Imkoniyatlar:**
    *   **Streak:** "Ketma-ket 7 kun kirdingiz!"
    *   **Badges:** "Kitobsevar", "A'lochi", "AI Master" nishonlari.
    *   **Progress Bar:** Semestr tugashiga qancha qolgani.

---

## ⚙️ 3-BOSQICH: Backend Integratsiyasi (API)

Web App shunchaki "chiroyli oyna" bo'lib qolmasligi uchun u bot bazasi bilan gaplashishi kerak.

### Kerakli API Endpointlar (FastAPI/Aiohttp yordamida):
1.  `GET /api/user/{id}` - Foydalanuvchi ma'lumotlari (Premium, ballar).
2.  `GET /api/tasks/{id}` - Foydalanuvchi deadline'lari.
3.  `POST /api/tasks` - Yangi deadline qo'shish.
4.  `GET /api/schedule/{id}` - Dars jadvalini olish.
5.  `POST /api/schedule` - Dars jadvalini yangilash.

*Hozircha `Telegram.WebApp.sendData` orqali ishlash mumkin, lekin to'liq sinhronizatsiya uchun API kerak.*

---

## 🎨 Dizayn Konsepsiyasi (UI/UX)

*   **Tema:** "Glassmorphism" (oyna effekti) va "Neumorphism" elementlari.
*   **Ranglar:**
    *   Asosiy: To'q ko'k (#0d1117)
    *   Accent: Neon binafsha (#5865f2) va Moviy (#00d2ff)
*   **Animatsiyalar:** Sahifalar almashganda silliq o'tishlar (Page Transitions).

---

## 📍 Tavsiya Etiladigan Birinchi Qadamlar

Sizga hozirning o'zida **Bottom Navigation Bar** va **3 ta asosiy sahifa** (Home, Schedule, Profile) ni qo'shishni tavsiya qilaman. Bu foydalanuvchi tajribasini keskin oshiradi.

1.  **index.html** tuzilmasini o'zgartirish (SPA - Single Page Application).
2.  **Navigation bar** qo'shish.
3.  **Schedule** (Jadval) bo'limini oddiy HTML/JS da yaratish.
