# Talaba Bot - Technical Manual

## 📚 Table of Contents
1. [Architecture Overview](#architecture-overview)
2. [Database Schema](#database-schema)
3. [Handler System](#handler-system)
4. [Premium Features](#premium-features)
5. [AI Services](#ai-services)
6. [Localization](#localization)
7. [Admin Panel](#admin-panel)
8. [Deployment](#deployment)

---

## 🏗 Architecture Overview

### Project Structure
```
talaba_bot/
├── handlers/           # Message and callback handlers
│   ├── common.py      # Main menu and basic commands
│   ├── student_tools.py # Test, Referat, Presentation
│   ├── konspekt.py    # File/Photo/Audio to text
│   ├── admin.py       # Admin panel
│   ├── languages.py   # Language selection
│   └── premium/       # Premium features
│       ├── ai_tutor.py
│       ├── homework_solver.py
│       ├── flashcards.py
│       └── essay_checker.py
├── services/          # External API integrations
│   ├── ai_service.py  # OpenAI integration
│   ├── gemini_service.py # Google Gemini
│   ├── multi_ai_service.py # Multi-provider AI
│   └── file_parser.py # Document parsing
├── utils/             # Utility functions
│   ├── texts.py       # Localization texts
│   ├── docx_gen.py    # Word document generation
│   ├── pptx_gen.py    # PowerPoint generation
│   ├── charts.py      # Statistics charts
│   └── check_sub.py   # Channel subscription check
├── database.py        # Database operations
├── config.py          # Configuration
└── main.py           # Entry point
```

### Core Components

#### 1. **Dispatcher (main.py)**
- Initializes bot and dispatcher
- Registers all routers
- Runs polling loop
- Manages reminders (deadlines, premium expiry)

#### 2. **Database (database.py)**
- SQLite database with 17 tables
- 49 database functions
- Handles users, payments, deadlines, books, etc.

#### 3. **Handlers**
- Message handlers for user commands
- Callback query handlers for inline buttons
- FSM (Finite State Machine) for multi-step flows

#### 4. **Services**
- AI text generation (OpenAI, Gemini)
- File parsing (PDF, DOCX, images)
- Document generation (DOCX, PPTX)

---

## 🗄 Database Schema

### Main Tables

#### `users`
```sql
CREATE TABLE users (
    tg_id INTEGER PRIMARY KEY,
    full_name TEXT,
    username TEXT,
    language TEXT DEFAULT 'uz',
    is_premium INTEGER DEFAULT 0,
    premium_until TEXT,
    referrer_id INTEGER,
    referral_count INTEGER DEFAULT 0,
    source TEXT,
    created TEXT
)
```

#### `deadlines`
```sql
CREATE TABLE deadlines (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tg_id INTEGER,
    title TEXT,
    due_date TEXT,
    reminded_1d INTEGER DEFAULT 0,
    reminded_1h INTEGER DEFAULT 0,
    created TEXT
)
```

#### `payments`
```sql
CREATE TABLE payments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tg_id INTEGER,
    amount INTEGER,
    card_number TEXT,
    proof_file_id TEXT,
    status TEXT DEFAULT 'pending',
    created TEXT
)
```

#### `books`
```sql
CREATE TABLE books (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    category TEXT,
    file_id TEXT,
    type TEXT DEFAULT 'pdf',
    created TEXT
)
```

### Statistics Tables

- `event_log` - User activity tracking
- `quiz_history` - Quiz attempts
- `settings` - Bot configuration

---

## 🎮 Handler System

### Message Flow

1. **User sends message** → Dispatcher
2. **Router matches** → Handler function
3. **Handler processes** → Database/AI service
4. **Response sent** → User

### FSM States

```python
class StudentToolStates(StatesGroup):
    waiting_for_test_subject = State()
    waiting_for_test_topic = State()
    waiting_for_referat_topic = State()
    waiting_for_ppt_topic = State()
```

### Example Handler

```python
@router.message(F.text.in_(get_all_translations('btn_test')))
async def start_test_generator(message: types.Message, state: FSMContext):
    if not is_premium(message.from_user.id):
        return await message.answer(get_text('premium_required', message.from_user.id))
    
    await state.set_state(StudentToolStates.waiting_for_test_subject)
    await message.answer(
        get_text('enter_test_subject', message.from_user.id),
        reply_markup=get_cancel_kb(message.from_user.id)
    )
```

---

## 💎 Premium Features

### Feature List

1. **AI Test Generator** - Generates multiple-choice tests
2. **AI Referat** - Creates academic essays
3. **AI Presentation** - Generates PowerPoint slides
4. **File → Konspekt** - Summarizes documents
5. **Photo → Konspekt** - OCR + summarization
6. **Audio → Konspekt** - Transcription + summary
7. **AI Tutor** - Interactive learning assistant
8. **Homework Solver** - Step-by-step solutions
9. **Flashcards** - Study card generation
10. **Essay Checker** - Grammar and style feedback

### Premium Check

```python
def is_premium(tg_id: int) -> bool:
    user = get_user(tg_id)
    if not user or not user[4]:  # is_premium
        return False
    
    premium_until = user[5]
    if not premium_until:
        return False
    
    return datetime.fromisoformat(premium_until) > get_now()
```

---

## 🤖 AI Services

### Multi-Provider System

```python
# services/multi_ai_service.py
async def generate_with_fallback(prompt: str, **kwargs):
    providers = ['gemini', 'openai']
    
    for provider in providers:
        try:
            if provider == 'gemini':
                return await gemini_generate(prompt, **kwargs)
            elif provider == 'openai':
                return await openai_generate(prompt, **kwargs)
        except Exception as e:
            logging.error(f"{provider} failed: {e}")
            continue
    
    raise Exception("All AI providers failed")
```

### Gemini Integration

```python
# services/gemini_service.py
async def gemini_chat(messages: list, **kwargs):
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    chat = model.start_chat(history=messages[:-1])
    response = await chat.send_message_async(messages[-1])
    
    return response.text
```

---

## 🌐 Localization

### Text System

```python
# utils/texts.py
TEXTS = {
    'uz': {
        'welcome': "Xush kelibsiz!",
        'btn_test': "📝 Test Generator",
        # ... 100+ keys
    },
    'ru': {
        'welcome': "Добро пожаловать!",
        'btn_test': "📝 Генератор Тестов",
    },
    'en': {
        'welcome': "Welcome!",
        'btn_test': "📝 Test Generator",
    }
}

def get_text(key: str, user_id: int, **kwargs) -> str:
    lang = get_user_language(user_id)
    text = TEXTS.get(lang, TEXTS['uz']).get(key, key)
    return text.format(**kwargs) if kwargs else text
```

### Multi-Language Handlers

```python
@router.message(F.text.in_(get_all_translations('btn_test')))
async def handle_test(message: types.Message):
    # Matches "📝 Test Generator" in all languages
    pass
```

---

## 🔑 Admin Panel

### Features

- 📊 Statistics dashboard
- 👥 User management
- 💰 Payment processing
- 📚 Book library management
- 📢 Channel management
- 📣 Broadcast messages
- ⚙️ Settings configuration

### Admin Check

```python
@router.message(F.chat.id == ADMIN_ID)
async def admin_only_handler(message: types.Message):
    # Only admin can access
    pass
```

---

## 🚀 Deployment

### Requirements

```txt
aiogram==3.4.1
python-dotenv==1.0.0
google-generativeai==0.3.2
python-docx==1.1.0
python-pptx==0.6.23
Pillow==10.2.0
matplotlib==3.8.2
pytz==2024.1
```

### Environment Variables

```env
BOT_TOKEN=your_bot_token
ADMIN_ID=your_telegram_id
GEMINI_API_KEY=your_gemini_key
OPENAI_API_KEY=your_openai_key (optional)
DB_PATH=talaba_bot.db
```

### Running the Bot

```bash
# Install dependencies
pip install -r requirements.txt

# Initialize database
python -c "from database import init_db; init_db()"

# Test connection
python test_ping.py

# Start bot
python main.py
```

### Systemd Service (Linux)

```ini
[Unit]
Description=Talaba Bot
After=network.target

[Service]
Type=simple
User=botuser
WorkingDirectory=/path/to/talaba_bot
ExecStart=/path/to/venv/bin/python main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

---

## 📈 Performance

### Optimization Tips

1. **Database Indexing**
   ```sql
   CREATE INDEX idx_users_premium ON users(is_premium, premium_until);
   CREATE INDEX idx_deadlines_due ON deadlines(due_date, reminded_1d);
   ```

2. **AI Rate Limiting**
   ```python
   RATE_LIMITS = {
       'ai_tutor': 50,  # messages per day
       'test_gen': 10,  # tests per day
   }
   ```

3. **Caching**
   - Cache frequently accessed settings
   - Store AI responses for common queries

---

## 🔧 Troubleshooting

### Common Issues

1. **Bot not responding**
   - Check BOT_TOKEN in .env
   - Verify internet connection
   - Check bot is not blocked by user

2. **AI generation fails**
   - Verify API keys
   - Check rate limits
   - Review error logs

3. **Database locked**
   - Close other connections
   - Use WAL mode: `PRAGMA journal_mode=WAL`

---

## 📞 Support

For technical support or questions:
- Telegram: @YourSupportChannel
- Email: support@example.com
- GitHub: github.com/yourusername/talaba_bot

---

**Last Updated:** 2026-02-06
**Version:** 2.0.0
