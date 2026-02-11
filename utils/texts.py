from database import get_user_language

TEXTS = {
    'uz': {
        'welcome': "Assalomu alaykum, {name}!\n\nStatus: {status}\n{trial}Talaba Service Botga xush kelibsiz. Marhamat, kerakli bo'limni tanlang:",
        'main_menu': "Asosiy menyu:",
        'premium_info': "💎 **Talaba Premium — Imkoniyatlaringizni kengaytiring!**\n\nQuyidagi tariflardan birini tanlang:\n\n💥 1 Oy – 25 000 so‘m\n⚡ 3 Oy – 60 000 so‘m 🔻 (20% Tejang!)\n🌟 6 Oy – 99 000 so‘m 🔻 (34% Tejang!)\n\nTanlash uchun tugmalardan foydalaning:",
        'referat_topic': "Referat mavzusini yozing:",
        'test_topic': "Test mavzusini va savollar sonini yuboring (Masalan: Informatika 10):",
        'ppt_topic': "Slaydlar uchun mavzuni kiriting:",
        'tutor_welcome': "🤖 **Repetitor faollashtirildi!**\n\nMen sizning shaxsiy o'qituvchingizman. Istalgan savolni bering!",
        'cancel': "❌ Bekor qilish",
        'back': "🔙 Orqaga",
        'settings': "⚙️ Sozlamalar",
        'lang_select': "Tilni tanlang / Выберите язык / Select language:",
        # Buttons
        'btn_test': "📚 Test generator",
        'btn_referat': "🧾 Referat",
        'btn_library': "📚 Onlayn kutubxona",
        'btn_ppt': "📊 Prezentatsiya",
        'btn_deadline': "⏰ Deadline qo'shish",
        'btn_tutor': "🤖 Repetitor",
        'btn_my_deadlines': "📋 Mening deadline'larim",
        'btn_solver': "📝 Vazifa Yechuvchi",
        'btn_quiz': "🏆 Reyting",
        'btn_checker': "✍️ Insho Tekshiruvchi",
        'btn_lang': "🌐 Tilni o'zgartirish",
        'btn_flashcards': "🎴 Flashcards",
        'btn_invite': "🗣 Do'stlarni taklif qilish",
        'btn_file_konspekt': "📂 Fayl → Konspekt",
        'btn_free_resources': "📚 Bepul manbalar",
        'btn_photo_konspekt': "📸 Foto → Konspekt",
        'btn_channels': "📢 Foydali kanallar",
        'btn_audio_konspekt': "🎧 Audio → Konspekt",
        'btn_news': "🏢 Universitet yangiliklari",
        'btn_grants': "🏆 Grantlar",
        'btn_about': "📖 Malumotnoma",
        'btn_premium': "🌟 Premium sotib olish",
        'btn_admin': "🔑 Boshqaruv Paneli",
        'btn_dashboard': "🌐 Web Dashboard",
        'btn_clear_chat': "🗑 Suhbatni tozalash",
        'btn_admin_contact': "👨‍💻 Admin bilan bog'lanish",
        'btn_cancel': "❌ Bekor qilish",
        'btn_back': "🔙 Orqaga",
        'btn_1month': "💥 1 Oy (25k)",
        'btn_3months': "⚡ 3 Oy (60k)",
        'btn_6months': "🌟 6 Oy (99k)",
        'payment_info': "💳 **To'lov Ma'lumotlari**\n\nKarta raqami: `{card}`\nMiqdor: **{amount} so'm**\n\n📝 To'lovni amalga oshirgandan so'ng, chek rasmini yuboring.",
        'payment_pending': "⏳ **To'lov Kutilmoqda**\n\nSizning to'lovingiz ko'rib chiqilmoqda. Admin tasdiqlashini kuting.",
        'payment_approved': "✅ **To'lov Tasdiqlandi!**\n\nTabriklaymiz! Sizning Premium obunangiz faollashtirildi.\nMuddati: {days} kun",
        'payment_rejected': "❌ **To'lov Rad Etildi**\n\nAfsuski, to'lovingiz tasdiqlanmadi.\nSabab: {reason}\n\nIltimos, qaytadan urinib ko'ring.",
        'about_text': (
            "🤖 **Talaba Servis Bot — Sizning shaxsiy yordamchingiz!**\n\n"
            "Ushbu bot talabalar uchun o'qish jarayonini osonlashtirish va samaradorlikni oshirish uchun yaratilgan.\n\n"
            "🛠 **ASOSIY IMKONIYATLAR:**\n\n"
            "🧠 **Sun'iy Intellekt (AI):**\n"
            "• 🧾 **Referat Yozish** — Istalgan mavzuda tayyor Word (.docx) referat.\n"
            "• 📊 **Prezentatsiya** — Mavzu bo'yicha tayyor PowerPoint (.pptx) slaydlar.\n"
            "• 📚 **Test Generator** — Bilimingizni sinash uchun testlar tuzish.\n\n"
            "• 📝 **Vazifa Yechuvchi** — Murakkab masalalar yechimi.\n\n\n"
            "💎 **Premium Obuna:**\n"
            "Cheklovsiz AI so'rovlari va maxsus imkoniyatlar uchun Premium oling!\n\n"
            "Botdan foydalanishda omad tilaymiz! 🚀"
        ),
        'enter_test_subject': "📚 Test mavzusini va savollar sonini kiriting:\n\nMasalan: Informatika 10",
        'enter_referat_topic': "📝 Referat mavzusini kiriting:\n\nMasalan: Sun'iy intellekt tarixi",
        'enter_ppt_topic': "📊 Prezentatsiya mavzusini kiriting:\n\nMasalan: Python dasturlash tili",
        'premium_required': "⚠️ **Premium Kerak**\n\nBu funksiya faqat Premium foydalanuvchilar uchun mavjud.\n\n💎 Premium obuna sotib oling va barcha imkoniyatlardan foydalaning!",
    },
    'ru': {
        'welcome': "Здравствуйте, {name}!\n\nСтатус: {status}\n{trial}Добро пожаловать в Talaba Service Bot. Пожалуйста, выберите нужный раздел:",
        'main_menu': "Главное меню:",
        'premium_info': "💎 **Premium Подписка**\n\nЦена: **{price} сум / месяц**\n\n💳 **Карта для оплаты:**\n`{card}`\n\n❗️ После оплаты отправьте чек.",
        'referat_topic': "Введите тему реферата:",
        'test_topic': "Введите тему теста и количество вопросов (Например: Информатика 10):",
        'ppt_topic': "Введите тему для слайдов:",
        'tutor_welcome': "🤖 **AI Tutor активирован!**\n\nЯ ваш личный преподаватель. Задавайте любые вопросы!",
        'cancel': "❌ Отмена",
        'back': "🔙 Назад",
        'settings': "⚙️ Настройки",
        'lang_select': "Tilni tanlang / Выберите язык / Select language:",
        # Buttons
        'btn_test': "📚 Тест генератор",
        'btn_referat': "🧾 Реферат (AI)",
        'btn_library': "📚 Онлайн библиотека",
        'btn_ppt': "📊 Презентация (AI)",
        'btn_deadline': "⏰ Добавить дедлайн",
        'btn_tutor': "🤖 AI Tutor",
        'btn_my_deadlines': "📋 Мои дедлайны",
        'btn_solver': "📝 Решатель задач",
        'btn_quiz': "🏆 Рейтинг",
        'btn_checker': "✍️ Проверка эссе",
        'btn_lang': "🌐 Изменить язык",
        'btn_flashcards': "🎴 Флешкарточки",
        'btn_invite': "🗣 Пригласить друзей",
        'btn_file_konspekt': "📂 Файл → Конспект",
        'btn_free_resources': "📚 Бесплатные ресурсы",
        'btn_photo_konspekt': "📸 Фото → Конспект",
        'btn_channels': "📢 Полезные каналы",
        'btn_audio_konspekt': "🎧 Аудио → Конспект",
        'btn_news': "🏢 Новости университета",
        'btn_grants': "🏆 Гранты",
        'btn_about': "📖 Справка",
        'btn_premium': "🌟 Купить Premium",
        'btn_admin': "🔑 Админ панель",
        'btn_dashboard': "🌐 Web Dashboard",
        'btn_clear_chat': "🗑 Очистить историю",
        'btn_admin_contact': "👨‍💻 Связаться с админом",
        'btn_cancel': "❌ Отмена",
        'btn_back': "🔙 Назад",
        'btn_1month': "💥 1 Месяц (25k)",
        'btn_3months': "⚡ 3 Месяца (60k)",
        'btn_6months': "🌟 6 Месяцев (99k)",
        'payment_info': "💳 **Информация об Оплате**\n\nНомер карты: `{card}`\nСумма: **{amount} сум**\n\n📝 После оплаты отправьте фото чека.",
        'payment_pending': "⏳ **Ожидание Оплаты**\n\nВаш платеж рассматривается. Ожидайте подтверждения администратора.",
        'payment_approved': "✅ **Платеж Подтвержден!**\n\nПоздравляем! Ваша Premium подписка активирована.\nСрок: {days} дней",
        'payment_rejected': "❌ **Платеж Отклонен**\n\nК сожалению, ваш платеж не был подтвержден.\nПричина: {reason}\n\nПожалуйста, попробуйте снова.",
        'about_text': (
            "🤖 **Talaba Service Bot — Ваш личный помощник!**\n\n"
            "Этот бот создан для упрощения учебного процесса и повышения эффективности студентов.\n\n"
            "🛠 **ОСНОВНЫЕ ВОЗМОЖНОСТИ:**\n\n"
            "🧠 **Искусственный Интеллект (AI):**\n"
            "• 🧾 **Рефераты** — Готовые рефераты в Word (.docx) на любую тему.\n"
            "• 📊 **Презентации** — Готовые слайды PowerPoint (.pptx) по вашей теме.\n"
            "• 📚 **Генератор Тестов** — Создание тестов для проверки знаний.\n\n"
            "• 📝 **Решение Задач** — Пошаговое решение сложных задач.\n\n\n"
            "💎 **Premium Подписка:**\n"
            "Оформите Premium для безлимитных AI запросов и специальных функций!\n\n"
            "Удачи в учебе! 🚀"
        ),
        'enter_test_subject': "📚 Введите тему теста и количество вопросов:\n\nНапример: Информатика 10",
        'enter_referat_topic': "📝 Введите тему реферата:\n\nНапример: История искусственного интеллекта",
        'enter_ppt_topic': "📊 Введите тему презентации:\n\nНапример: Язык программирования Python",
        'premium_required': "⚠️ **Требуется Premium**\n\nЭта функция доступна только для Premium пользователей.\n\n💎 Купите Premium подписку и используйте все возможности!",
    },
    'en': {
        'welcome': "Hello, {name}!\n\nStatus: {status}\n{trial}Welcome to Talaba Service Bot. Please choose a section:",
        'main_menu': "Main menu:",
        'premium_info': "💎 **Premium Subscription**\n\nPrice: **{price} UZS / month**\n\n💳 **Payment card:**\n`{card}`\n\n❗️ After payment, please send the receipt.",
        'referat_topic': "Enter the topic for the referat:",
        'test_topic': "Enter the test topic and number of questions (Example: Computer Science 10):",
        'ppt_topic': "Enter the topic for slides:",
        'tutor_welcome': "🤖 **AI Tutor activated!**\n\nI am your personal tutor. Ask me anything!",
        'cancel': "❌ Cancel",
        'back': "🔙 Back",
        'settings': "⚙️ Settings",
        'lang_select': "Tilni tanlang / Выберите язык / Select language:",
        # Buttons
        'btn_test': "📚 Test Generator",
        'btn_referat': "🧾 Referat (AI)",
        'btn_library': "📚 Online Library",
        'btn_ppt': "📊 Presentation (AI)",
        'btn_deadline': "⏰ Add Deadline",
        'btn_tutor': "🤖 AI Tutor",
        'btn_my_deadlines': "📋 My Deadlines",
        'btn_solver': "📝 Task Solver",
        'btn_quiz': "🏆 Ranking",
        'btn_checker': "✍️ Essay Checker",
        'btn_lang': "🌐 Change Language",
        'btn_flashcards': "🎴 Flashcards",
        'btn_invite': "🗣 Invite Friends",
        'btn_file_konspekt': "📂 File → Summary",
        'btn_free_resources': "📚 Free Resources",
        'btn_photo_konspekt': "📸 Photo → Summary",
        'btn_channels': "📢 Useful Channels",
        'btn_audio_konspekt': "🎧 Audio → Summary",
        'btn_news': "🏢 University News",
        'btn_grants': "🏆 Grants",
        'btn_about': "📖 Information",
        'btn_premium': "🌟 Buy Premium",
        'btn_admin': "🔑 Admin Panel",
        'btn_dashboard': "🌐 Web Dashboard",
        'btn_clear_chat': "🗑 Clear Chat",
        'btn_admin_contact': "👨‍💻 Contact Admin",
        'btn_cancel': "❌ Cancel",
        'btn_back': "🔙 Back",
        'btn_1month': "💥 1 Month (25k)",
        'btn_3months': "⚡ 3 Months (60k)",
        'btn_6months': "🌟 6 Months (99k)",
        'payment_info': "💳 **Payment Information**\n\nCard number: `{card}`\nAmount: **{amount} UZS**\n\n📝 After payment, send the receipt photo.",
        'payment_pending': "⏳ **Payment Pending**\n\nYour payment is being reviewed. Please wait for admin confirmation.",
        'payment_approved': "✅ **Payment Approved!**\n\nCongratulations! Your Premium subscription has been activated.\nDuration: {days} days",
        'payment_rejected': "❌ **Payment Rejected**\n\nUnfortunately, your payment was not confirmed.\nReason: {reason}\n\nPlease try again.",
        'about_text': (
            "🤖 **Talaba Servis Bot — Your Personal Assistant!**\n\n"
            "This bot is designed to simplify the learning process and increase student efficiency.\n\n"
            "🛠 **MAIN FEATURES:**\n\n"
            "🧠 **Artificial Intelligence (AI):**\n"
            "• 🧾 **Referat Writing** — Ready-made Word (.docx) papers on any topic.\n"
            "• 📊 **Presentations** — Ready-made PowerPoint (.pptx) slides on your topic.\n"
            "• 📚 **Test Generator** — Create tests to check your knowledge.\n\n"
            "• 📝 **Task Solver** — Step-by-step solutions for complex problems.\n\n\n"
            "💎 **Premium Subscription:**\n"
            "Get Premium for unlimited AI requests and special features!\n\n"
            "Good luck with your studies! 🚀"
        ),
        'enter_test_subject': "📚 Enter test topic and number of questions:\n\nExample: Computer Science 10",
        'enter_referat_topic': "📝 Enter referat topic:\n\nExample: History of Artificial Intelligence",
        'enter_ppt_topic': "📊 Enter presentation topic:\n\nExample: Python Programming Language",
        'premium_required': "⚠️ **Premium Required**\n\nThis feature is only available for Premium users.\n\n💎 Buy Premium subscription and use all features!",
    }
}

def get_text(key: str, user_id: int, **kwargs) -> str:
    lang = get_user_language(user_id)
    text = TEXTS.get(lang, TEXTS['uz']).get(key, TEXTS['uz'].get(key, key))
    return text.format(**kwargs) if kwargs else text

def get_all_translations(key: str) -> list:
    return [TEXTS[lang].get(key) for lang in TEXTS if key in TEXTS[lang]]
