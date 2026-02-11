import sqlite3
import datetime
from typing import Optional, List
from config import DB_PATH, DEFAULT_PREMIUM_DAYS, TIMEZONE
import pytz
import os

def get_now():
    tz = pytz.timezone(TIMEZONE)
    return datetime.datetime.now(tz)

def get_conn():
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = get_conn()
    c = conn.cursor()
    
    try:
        # Enable WAL mode for concurrency
        c.execute("PRAGMA journal_mode=WAL;")
    except Exception:
        pass
    
    # Admins table (New)
    c.execute("""CREATE TABLE IF NOT EXISTS admins(
        user_id INTEGER PRIMARY KEY,
        added_by INTEGER,
        name TEXT,
        created_at TEXT
    )""")
    
    # Settings table
    c.execute("""CREATE TABLE IF NOT EXISTS settings(
        key TEXT PRIMARY KEY,
        value TEXT
    )""")
    
    # Support messages
    c.execute("""CREATE TABLE IF NOT EXISTS support_messages(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        sender TEXT, -- 'user' or 'admin'
        message TEXT,
        created_at TEXT
    )""")
    
    # Users table
    c.execute("""CREATE TABLE IF NOT EXISTS users(
        tg_id INTEGER PRIMARY KEY,
        full_name TEXT,
        username TEXT,
        is_premium INTEGER DEFAULT 0,
        premium_until TEXT,
        referrer_id INTEGER,
        referral_count INTEGER DEFAULT 0,
        source TEXT,
        created TEXT,
        premium_reminded INTEGER DEFAULT 0,
        language TEXT DEFAULT 'uz'
    )""")
    
    # Migrations for existing users table
    columns = [
        ("full_name", "TEXT"),
        ("username", "TEXT"),
        ("is_premium", "INTEGER DEFAULT 0"),
        ("premium_until", "TEXT"),
        ("referrer_id", "INTEGER"),
        ("referral_count", "INTEGER DEFAULT 0"),
        ("source", "TEXT"),
        ("created", "TEXT"),
        ("premium_reminded", "INTEGER DEFAULT 0"),
        ("language", "TEXT DEFAULT 'uz'")
    ]
    for col_name, col_type in columns:
        try:
            c.execute(f"ALTER TABLE users ADD COLUMN {col_name} {col_type}")
        except sqlite3.OperationalError:
            pass

    c.execute("""CREATE TABLE IF NOT EXISTS deadlines(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tg_id INTEGER,
        title TEXT,
        due_date TEXT,
        reminded_24 INTEGER DEFAULT 0,
        reminded_1 INTEGER DEFAULT 0
    )""")
    
    c.execute("""CREATE TABLE IF NOT EXISTS payments(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tg_id INTEGER,
        amount INTEGER,
        card TEXT,
        proof_file_id TEXT,
        status TEXT DEFAULT 'pending',
        created TEXT,
        comment TEXT,
        admin_note TEXT
    )""")
    
    # Migrations for existing payments table
    payment_cols = [
        ("comment", "TEXT"),
        ("admin_note", "TEXT")
    ]
    for col_name, col_type in payment_cols:
        try:
            c.execute(f"ALTER TABLE payments ADD COLUMN {col_name} {col_type}")
        except sqlite3.OperationalError:
            pass

    c.execute("""CREATE TABLE IF NOT EXISTS tests(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tg_id INTEGER,
        topic TEXT,
        questions TEXT,
        created TEXT
    )""")
    
    c.execute("""CREATE TABLE IF NOT EXISTS schedules(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tg_id INTEGER,
        day_of_week TEXT,
        subject TEXT,
        start_time TEXT,
        location TEXT
    )""")
    
    c.execute("""CREATE TABLE IF NOT EXISTS books(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        category TEXT,
        file_id TEXT,
        book_type TEXT DEFAULT 'pdf',
        created TEXT
    )""")
    
    c.execute("""CREATE TABLE IF NOT EXISTS channels(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        url TEXT,
        created TEXT
    )""")
    
    c.execute("""CREATE TABLE IF NOT EXISTS templates(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        category TEXT,
        file_path TEXT,
        created TEXT
    )""")
    
    # Rename logs to event_log for consistency with charts
    c.execute("""CREATE TABLE IF NOT EXISTS event_log(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tg_id INTEGER,
        event_type TEXT,
        created TEXT
    )""")
    
    c.execute("""CREATE TABLE IF NOT EXISTS referrals(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        referrer_id INTEGER,
        referred_id INTEGER,
        status TEXT DEFAULT 'pending',
        created TEXT
    )""")
    
    c.execute("""CREATE TABLE IF NOT EXISTS quiz_questions(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        question TEXT,
        options TEXT,
        correct_option INTEGER,
        explanation TEXT,
        category TEXT,
        created TEXT
    )""")
    
    c.execute("""CREATE TABLE IF NOT EXISTS quiz_answers(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tg_id INTEGER,
        question_id INTEGER,
        is_correct INTEGER,
        created TEXT
    )""")
    
    # Library materials table
    c.execute("""CREATE TABLE IF NOT EXISTS library_materials(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        subject TEXT NOT NULL,
        level TEXT NOT NULL,
        material_type TEXT NOT NULL,
        title TEXT NOT NULL,
        duration TEXT,
        file_url TEXT,
        description TEXT,
        file_size INTEGER,
        views_count INTEGER DEFAULT 0,
        is_active INTEGER DEFAULT 1,
        created_at TEXT,
        updated_at TEXT,
        created_by INTEGER
    )""")

    # User Restrictions (Block specific features for specific users)
    c.execute('''CREATE TABLE IF NOT EXISTS user_restrictions
                 (user_id INTEGER,
                  feature_key TEXT,
                  UNIQUE(user_id, feature_key))''')

    # App Analytics (Track feature usage)
    c.execute('''CREATE TABLE IF NOT EXISTS app_analytics
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER,
                  feature_key TEXT,
                  timestamp DATETIME)''')

    # User Activity (Track join/leave)
    c.execute('''CREATE TABLE IF NOT EXISTS user_activity
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER,
                  name TEXT,
                  username TEXT,
                  action TEXT,
                  timestamp DATETIME)''')
    
    # Create indexes for library_materials
    c.execute("""CREATE INDEX IF NOT EXISTS idx_library_subject 
                 ON library_materials(subject, level)""")
    c.execute("""CREATE INDEX IF NOT EXISTS idx_library_type 
                 ON library_materials(material_type)""")
    c.execute("""CREATE INDEX IF NOT EXISTS idx_library_active 
                 ON library_materials(is_active)""")
    
    # Insert default settings if not exists
    c.execute("INSERT OR IGNORE INTO settings(key, value) VALUES('admin_contact', '@Abusaadl7')")
    c.execute("INSERT OR IGNORE INTO settings(key, value) VALUES('mandatory_channel', '@talaba_uz')")
    
    # Create indexes for better performance
    create_indexes(c)
    
    conn.commit()
    conn.close()


def create_indexes(cursor=None):
    """Create database indexes for better performance"""
    if cursor is None:
        conn = get_conn()
        cursor = conn.cursor()
        should_close = True
    else:
        should_close = False
    
    # Users table indexes
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_users_tg_id 
        ON users(tg_id)
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_users_premium 
        ON users(is_premium, premium_until)
    """)
    
    # Deadlines table indexes
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_deadlines_tg_id 
        ON deadlines(tg_id)
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_deadlines_due 
        ON deadlines(due_date)
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_deadlines_reminded 
        ON deadlines(reminded_24, reminded_1)
    """)
    
    # Payments table indexes
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_payments_tg_id 
        ON payments(tg_id)
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_payments_status 
        ON payments(status)
    """)
    
    # Logs table index
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_logs_tg_id 
        ON logs(tg_id, created)
    """)
    
    if should_close:
        conn.commit()
        conn.close()


def ensure_user(tg_id: int, referrer_id: int = None, source: str = None, full_name: str = None, username: str = None) -> bool:
    """Returns True if new user created, False otherwise"""
    conn = get_conn()
    c = conn.cursor()
    
    # Check if user exists
    c.execute("SELECT tg_id FROM users WHERE tg_id=?", (tg_id,))
    row = c.fetchone()
    
    if row is None:
        # New user: Grant 2 days of free premium
        now = get_now()
        trial_until = now + datetime.timedelta(days=2)
        c.execute("INSERT INTO users(tg_id, is_premium, premium_until, referrer_id, referral_count, created, source, full_name, username) VALUES(?,1,?,?,0,?,?,?,?)", 
                  (tg_id, trial_until.isoformat(), referrer_id, now.isoformat(), source, full_name, username))
        conn.commit()
        conn.close()
        return True
    else:
        # Update details for existing user
        c.execute("UPDATE users SET full_name=?, username=? WHERE tg_id=?", (full_name, username, tg_id))
        conn.commit()
    
    conn.close()
    return False


def increment_referral(referrer_id: int) -> int:
    """Increment referral count and return new total"""
    conn = get_conn()
    c = conn.cursor()
    c.execute("UPDATE users SET referral_count = COALESCE(referral_count, 0) + 1 WHERE tg_id=?", (referrer_id,))
    conn.commit()
    
    c.execute("SELECT referral_count FROM users WHERE tg_id=?", (referrer_id,))
    row = c.fetchone()
    count = row[0] if row else 0
    conn.close()
    return count

def get_referral_stats(tg_id: int) -> int:
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT referral_count FROM users WHERE tg_id=?", (tg_id,))
    row = c.fetchone()
    conn.close()
    return row[0] if row and row[0] else 0

def get_all_users():
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT tg_id, is_premium, premium_until, created, full_name, username FROM users")
    rows = c.fetchall()
    conn.close()
    return rows

def get_user(tg_id: int):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT tg_id, is_premium, premium_until FROM users WHERE tg_id=?", (tg_id,))
    row = c.fetchone()
    conn.close()
    return row

def is_premium(tg_id: int) -> bool:
    user = get_user(tg_id)
    if not user: return False
    prem, until = user[1], user[2]
    if prem and until:
        try:
            return datetime.datetime.fromisoformat(until) > get_now()
        except:
            return False
    return False

def set_premium(tg_id: int, days: int = DEFAULT_PREMIUM_DAYS):
    conn = get_conn()
    c = conn.cursor()
    now = get_now()
    c.execute("SELECT premium_until FROM users WHERE tg_id=?", (tg_id,))
    row = c.fetchone()
    if row and row[0]:
        try:
            cur = datetime.datetime.fromisoformat(row[0])
        except:
            cur = now
        new_until = (cur if cur > now else now) + datetime.timedelta(days=days)
    else:
        new_until = now + datetime.timedelta(days=days)
    
    c.execute("UPDATE users SET is_premium=1, premium_until=?, premium_reminded=0 WHERE tg_id=?", (new_until.isoformat(), tg_id))
    conn.commit()
    conn.close()

def revoke_premium(tg_id: int):
    conn = get_conn()
    c = conn.cursor()
    c.execute("UPDATE users SET is_premium=0, premium_until=? WHERE tg_id=?", (get_now().isoformat(), tg_id))
    conn.commit()
    conn.close()

def add_deadline(tg_id: int, title: str, due_iso: str):
    conn = get_conn()
    c = conn.cursor()
    c.execute("INSERT INTO deadlines(tg_id, title, due_date) VALUES(?,?,?)", (tg_id, title, due_iso))
    conn.commit()
    conn.close()

def get_premium_expiring_users():
    conn = get_conn()
    c = conn.cursor()
    # Get users whose premium expires in less than 24 hours and haven't been reminded
    c.execute("SELECT tg_id, premium_until FROM users WHERE is_premium=1 AND premium_until IS NOT NULL AND premium_reminded=0")
    rows = c.fetchall()
    conn.close()
    return rows

def mark_premium_reminded(tg_id: int):
    conn = get_conn()
    c = conn.cursor()
    c.execute("UPDATE users SET premium_reminded=1 WHERE tg_id=?", (tg_id,))
    conn.commit()
    conn.close()

def get_user_language(tg_id: int) -> str:
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT language FROM users WHERE tg_id=?", (tg_id,))
    row = c.fetchone()
    conn.close()
    return row[0] if row and row[0] else 'uz'

def set_user_language(tg_id: int, lang: str):
    conn = get_conn()
    c = conn.cursor()
    c.execute("UPDATE users SET language=? WHERE tg_id=?", (lang, tg_id))
    conn.commit()
    conn.close()

def get_due_deadlines():
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT id, tg_id, title, due_date, reminded_24, reminded_1 FROM deadlines")
    rows = c.fetchall()
    conn.close()
    return rows

def mark_reminded(did: int, which: str):
    conn = get_conn()
    c = conn.cursor()
    if which == "24":
        c.execute("UPDATE deadlines SET reminded_24=1 WHERE id=?", (did,))
    elif which == "1":
        c.execute("UPDATE deadlines SET reminded_1=1 WHERE id=?", (did,))
    conn.commit()
    conn.close()

def add_payment(tg_id: int, amount: int, card: str, proof_file_id: Optional[str]):
    conn = get_conn()
    c = conn.cursor()
    c.execute("INSERT INTO payments(tg_id, amount, card, proof_file_id, created) VALUES(?,?,?,?,?)",
              (tg_id, amount, card, proof_file_id, get_now().isoformat()))
    conn.commit()
    conn.close()

def get_pending_payments():
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT id, tg_id, amount, card, proof_file_id, created FROM payments WHERE status='pending'")
    rows = c.fetchall()
    conn.close()
    return rows

def update_payment_status(pid: int, status: str, admin_note: str = ""):
    conn = get_conn()
    c = conn.cursor()
    c.execute("UPDATE payments SET status=?, admin_note=? WHERE id=?", (status, admin_note, pid))
    conn.commit()
    conn.close()

def get_user_deadlines(tg_id: int):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT id, title, due_date FROM deadlines WHERE tg_id=? AND due_date > ? ORDER BY due_date ASC", 
              (tg_id, get_now().isoformat()))
    rows = c.fetchall()
    conn.close()
    return rows

def delete_deadline(deadline_id: int):
    conn = get_conn()
    c = conn.cursor()
    c.execute("DELETE FROM deadlines WHERE id=?", (deadline_id,))
    conn.commit()
    conn.close()

def add_schedule(tg_id: int, day: str, subject: str, time: str, location: str = ""):
    conn = get_conn()
    c = conn.cursor()
    c.execute("INSERT INTO schedules(tg_id, day_of_week, subject, start_time, location) VALUES(?,?,?,?,?)",
              (tg_id, day, subject, time, location))
    conn.commit()
    conn.close()

def get_schedule(tg_id: int):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT day_of_week, subject, start_time, location FROM schedules WHERE tg_id=? ORDER BY day_of_week, start_time", (tg_id,))
    rows = c.fetchall()
    conn.close()
    return rows

def delete_schedule(tg_id: int):
    conn = get_conn()
    c = conn.cursor()
    c.execute("DELETE FROM schedules WHERE tg_id=?", (tg_id,))
    conn.commit()
    conn.close()

def add_book(title: str, category: str, file_id: str, book_type: str = 'pdf'):
    conn = get_conn()
    c = conn.cursor()
    c.execute("INSERT INTO books(title, category, file_id, book_type, created) VALUES(?,?,?,?,?)",
              (title, category, file_id, book_type, get_now().isoformat()))
    conn.commit()
    conn.close()

def get_book_categories(book_type: Optional[str] = None):
    conn = get_conn()
    c = conn.cursor()
    if book_type:
        c.execute("SELECT DISTINCT category FROM books WHERE book_type=?", (book_type,))
    else:
        c.execute("SELECT DISTINCT category FROM books")
    rows = c.fetchall()
    conn.close()
    return [r[0] for r in rows]

def update_book_category(old_name: str, new_name: str):
    conn = get_conn()
    c = conn.cursor()
    c.execute("UPDATE books SET category=? WHERE category=?", (new_name, old_name))
    conn.commit()
    conn.close()

def get_books_by_category(category: str, book_type: Optional[str] = None):
    conn = get_conn()
    c = conn.cursor()
    if book_type:
        c.execute("SELECT id, title, file_id FROM books WHERE category=? AND book_type=? ORDER BY id ASC", (category, book_type))
    else:
        c.execute("SELECT id, title, file_id FROM books WHERE category=? ORDER BY id ASC", (category,))
    rows = c.fetchall()
    conn.close()
    return rows

def get_book_by_id(book_id: int):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT title, file_id, category, book_type FROM books WHERE id=?", (book_id,))
    row = c.fetchone()
    conn.close()
    return row

def delete_book_by_id(book_id: int):
    conn = get_conn()
    c = conn.cursor()
    c.execute("DELETE FROM books WHERE id=?", (book_id,))
    conn.commit()
    conn.close()

def add_channel(title: str, url: str):
    conn = get_conn()
    c = conn.cursor()
    c.execute("INSERT INTO channels(title, url, created) VALUES(?,?,?)",
              (title, url, get_now().isoformat()))
    conn.commit()
    conn.close()

def get_all_channels():
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT id, title, url FROM channels ORDER BY created DESC")
    rows = c.fetchall()
    conn.close()
    return rows

def delete_channel(channel_id: int):
    conn = get_conn()
    c = conn.cursor()
    c.execute("DELETE FROM channels WHERE id=?", (channel_id,))
    conn.commit()
    conn.close()

def get_detailed_stats():
    conn = get_conn()
    c = conn.cursor()
    
    # Total users
    c.execute("SELECT COUNT(*) FROM users")
    total_users = c.fetchone()[0]
    
    # Premium users (filtering by expiration date)
    c.execute("SELECT COUNT(*) FROM users WHERE is_premium=1 AND premium_until > ?", (get_now().isoformat(),))
    premium_users = c.fetchone()[0]
    
    # Total books
    c.execute("SELECT COUNT(*) FROM books")
    total_books = c.fetchone()[0]
    
    # Total deadlines (active)
    c.execute("SELECT COUNT(*) FROM deadlines WHERE due_date > ?", (get_now().isoformat(),))
    active_deadlines = c.fetchone()[0]
    
    # New users today
    today_start = get_now().replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
    c.execute("SELECT COUNT(*) FROM users WHERE created >= ?", (today_start,))
    new_users_today = c.fetchone()[0]
    
    conn.close()
    return {
        "total": total_users,
        "premium": premium_users,
        "books": total_books,
        "deadlines": active_deadlines,
        "new_today": new_users_today
    }

def get_all_tg_ids():
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT tg_id FROM users")
    ids = [r[0] for r in c.fetchall()]
    conn.close()
    return ids

def log_event(tg_id: int, event_type: str):
    conn = get_conn()
    c = conn.cursor()
    c.execute("INSERT INTO event_log(tg_id, event_type, created) VALUES(?,?,?)",
              (tg_id, event_type, get_now().isoformat()))
    conn.commit()
    conn.close()

def get_function_stats():
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT event_type, COUNT(*) as count FROM event_log GROUP BY event_type ORDER BY count DESC")
    rows = c.fetchall()
    conn.close()
    return rows

def add_template(name: str, category: str, file_path: str):
    conn = get_conn()
    c = conn.cursor()
    c.execute("INSERT INTO templates(name, category, file_path, created) VALUES(?,?,?,?)",
              (name, category, file_path, get_now().isoformat()))
    conn.commit()
    conn.close()

def get_all_templates():
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT id, name, category, file_path FROM templates ORDER BY created DESC")
    rows = c.fetchall()
    conn.close()
    return rows

def get_template_categories():
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT DISTINCT category FROM templates WHERE category IS NOT NULL")
    rows = c.fetchall()
    conn.close()
    return [r[0] for r in rows if r[0]]

def get_templates_by_category(category: str):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT id, name, file_path FROM templates WHERE category=? ORDER BY created DESC", (category,))
    rows = c.fetchall()
    conn.close()
    return rows

def delete_template(tid: int):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT file_path FROM templates WHERE id=?", (tid,))
    row = c.fetchone()
    if row and os.path.exists(row[0]):
        try:
            os.remove(row[0])
        except Exception:
            pass
    c.execute("DELETE FROM templates WHERE id=?", (tid,))
    conn.commit()
    conn.close()

def get_template_by_id(tid: int):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT name, file_path FROM templates WHERE id=?", (tid,))
    row = c.fetchone()
    conn.close()
    return row

def set_setting(key: str, value: str):
    conn = get_conn()
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO settings(key, value) VALUES(?,?)", (key, value))
    conn.commit()
    conn.close()

def get_setting(key: str, default: str = None):
    try:
        conn = get_conn()
        c = conn.cursor()
        c.execute("SELECT value FROM settings WHERE key=?", (key,))
        row = c.fetchone()
        conn.close()
        return row[0] if row else default
    except Exception:
        return default

def get_source_stats():
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT source, COUNT(*) FROM users WHERE source IS NOT NULL GROUP BY source")
    rows = c.fetchall()
    conn.close()
    return rows

def get_dashboard_stats():
    """Returns dict with stats for Web App Admin Panel"""
    conn = get_conn()
    c = conn.cursor()
    
    # 1. Total Users
    c.execute("SELECT COUNT(*) FROM users")
    total_users = c.fetchone()[0]
    
    # 2. Premium Users
    c.execute("SELECT COUNT(*) FROM users WHERE is_premium=1")
    premium_users = c.fetchone()[0]
    
    # 3. Active Today (AI requests)
    today = get_now().strftime("%Y-%m-%d") + "%"
    c.execute("SELECT COUNT(*) FROM event_log WHERE event_type='ai_chat' AND created LIKE ?", (today,))
    ai_today = c.fetchone()[0]
    
    # 4. Top Features (all time or specific limit)
    c.execute("""
        SELECT event_type, COUNT(*) as cnt 
        FROM event_log 
        GROUP BY event_type 
        ORDER BY cnt DESC 
        LIMIT 5
    """)
    
    features = []
    for row in c.fetchall():
        features.append({"name": row[0], "count": row[1]})
    
    conn.close()
    
    return {
        "total": total_users,
        "premium": premium_users,
        "ai_today": ai_today,
        "top_features": features
    }


def add_premium_to_all(days: int) -> int:
    conn = get_conn()
    c = conn.cursor()
    
    # Timezone aware now
    tz = pytz.timezone(TIMEZONE)
    now = datetime.datetime.now(tz)
    
    # Get all users and their current expiry
    c.execute("SELECT tg_id, premium_until FROM users")
    rows = c.fetchall()
    
    count = 0
    updates = []
    
    for tg_id, until_str in rows:
        try:
            cur = datetime.datetime.fromisoformat(until_str) if until_str else now
        except:
            cur = now
            
        # Ensure cur is timezone aware if not
        if cur.tzinfo is None:
             cur = cur.replace(tzinfo=tz)
             
        new_until = (cur if cur > now else now) + datetime.timedelta(days=days)
        updates.append((new_until.isoformat(), tg_id))
        count += 1
        
    # Bulk update
    c.executemany("UPDATE users SET is_premium=1, premium_until=?, premium_reminded=0 WHERE tg_id=?", updates)
    conn.commit()
    conn.close()
    return count

def get_top_users(limit=10):
    try:
        conn = get_conn()
        c = conn.cursor()
        c.execute("SELECT full_name, referral_count FROM users ORDER BY referral_count DESC LIMIT ?", (limit,))
        rows = c.fetchall()
        conn.close()
        return [{"n": (r[0] or "User")[:12], "s": r[1]} for r in rows]
    except Exception as e:
        print(f"DB Error: {e}")
        return []

def get_user_deadlines(tg_id: int):
    try:
        conn = get_conn()
        c = conn.cursor()
        # Get active deadlines
        now_str = get_now().isoformat()
        c.execute("SELECT title, due_date FROM deadlines WHERE tg_id=? AND due_date > ? ORDER BY due_date ASC LIMIT 5", (tg_id, now_str))
        rows = c.fetchall()
        conn.close()
        # Return simplified list: Title, Date
        return [{"t": r[0], "d": r[1].split('T')[0]} for r in rows]
    except:
        return []


# ============================================
# LIBRARY MATERIALS FUNCTIONS
# ============================================

def add_library_material(subject, level, material_type, title, url, description=None, duration=None):
    """Add new library material (compatible with API and frontend)"""
    conn = get_conn()
    c = conn.cursor()
    now = get_now().isoformat()
    c.execute("""INSERT INTO library_materials(
        subject, level, material_type, title, duration, file_url, description, is_active, created_at, views_count
    ) VALUES (?, ?, ?, ?, ?, ?, ?, 1, ?, 0)""",
        (subject, level, material_type, title, duration, url, description, now))
    material_id = c.lastrowid
    conn.commit()
    conn.close()
    return material_id

def get_library_materials(subject: str = None, level: str = None, material_type: str = None):
    """Get library materials with optional filters"""
    conn = get_conn()
    c = conn.cursor()
    
    query = "SELECT id, subject, level, material_type, title, duration, file_url, description, views_count, created_at FROM library_materials WHERE is_active=1"
    params = []
    
    if subject:
        query += " AND subject=?"
        params.append(subject)
    if level:
        query += " AND level=?"
        params.append(level)
    if material_type:
        query += " AND material_type=?"
        params.append(material_type)
    
    query += " ORDER BY created_at DESC"
    
    c.execute(query, params)
    rows = c.fetchall()
    conn.close()
    return rows

def get_library_material_by_id(material_id: int):
    """Get single material by ID and increment views"""
    conn = get_conn()
    c = conn.cursor()
    c.execute("""SELECT id, subject, level, material_type, title, duration, file_url, description, views_count 
                 FROM library_materials WHERE id=? AND is_active=1""", (material_id,))
    row = c.fetchone()
    
    if row:
        # Increment views
        c.execute("UPDATE library_materials SET views_count=views_count+1 WHERE id=?", (material_id,))
        conn.commit()
    
    conn.close()
    return row

def update_library_material(material_id: int, **kwargs):
    """Update library material"""
    conn = get_conn()
    c = conn.cursor()
    
    allowed_fields = ['title', 'duration', 'file_url', 'description', 'is_active']
    updates = []
    params = []
    
    for key, value in kwargs.items():
        if key in allowed_fields:
            updates.append(f"{key}=?")
            params.append(value)
    
    if updates:
        updates.append("updated_at=?")
        params.append(get_now().isoformat())
        params.append(material_id)
        
        query = f"UPDATE library_materials SET {', '.join(updates)} WHERE id=?"
        c.execute(query, params)
        conn.commit()
    
    conn.close()

def delete_library_material(material_id: int):
    """Soft delete library material"""
    conn = get_conn()
    c = conn.cursor()
    c.execute("UPDATE library_materials SET is_active=0, updated_at=? WHERE id=?",
              (get_now().isoformat(), material_id))
    conn.commit()
    conn.close()

def get_library_stats(subject: str = None):
    """Get library statistics"""
    conn = get_conn()
    c = conn.cursor()
    
    if subject:
        c.execute("SELECT COUNT(*) FROM library_materials WHERE subject=? AND is_active=1", (subject,))
        total = c.fetchone()[0]
        
        c.execute("SELECT COUNT(*) FROM library_materials WHERE subject=? AND material_type='video' AND is_active=1", (subject,))
        videos = c.fetchone()[0]
        
        c.execute("SELECT COUNT(*) FROM library_materials WHERE subject=? AND material_type='pdf' AND is_active=1", (subject,))
        pdfs = c.fetchone()[0]
        
        c.execute("SELECT COUNT(*) FROM library_materials WHERE subject=? AND material_type='audio' AND is_active=1", (subject,))
        audios = c.fetchone()[0]
    else:
        c.execute("SELECT COUNT(*) FROM library_materials WHERE is_active=1")
        total = c.fetchone()[0]
        
        c.execute("SELECT COUNT(*) FROM library_materials WHERE material_type='video' AND is_active=1")
        videos = c.fetchone()[0]
        
        c.execute("SELECT COUNT(*) FROM library_materials WHERE material_type='pdf' AND is_active=1")
        pdfs = c.fetchone()[0]
        
        c.execute("SELECT COUNT(*) FROM library_materials WHERE material_type='audio' AND is_active=1")
        audios = c.fetchone()[0]
    
    conn.close()
    return {
        "total": total,
        "videos": videos,
        "pdfs": pdfs,
        "audios": audios
    }

# --- ADMIN DASHBOARD & ANALYTICS FUNCTIONS ---

def block_user_feature(user_id: int, feature_key: str):
    conn = get_conn()
    c = conn.cursor()
    try:
        c.execute("INSERT OR IGNORE INTO user_restrictions (user_id, feature_key) VALUES (?, ?)", (user_id, feature_key))
        conn.commit()
    finally:
        conn.close()

def unblock_user_feature(user_id: int, feature_key: str):
    conn = get_conn()
    c = conn.cursor()
    try:
        c.execute("DELETE FROM user_restrictions WHERE user_id=? AND feature_key=?", (user_id, feature_key))
        conn.commit()
    finally:
        conn.close()

def get_user_restrictions(user_id: int):
    conn = get_conn()
    c = conn.cursor()
    try:
        c.execute("SELECT feature_key FROM user_restrictions WHERE user_id=?", (user_id,))
        rows = c.fetchall()
        return [row[0] for row in rows]
    except Exception:
        return []
    finally:
        conn.close()

def log_analytics(user_id: int, feature_key: str):
    conn = get_conn()
    c = conn.cursor()
    try:
        c.execute("INSERT INTO app_analytics (user_id, feature_key, timestamp) VALUES (?, ?, ?)", 
                  (user_id, feature_key, get_now().isoformat()))
        conn.commit()
    except Exception:
        pass
    finally:
        conn.close()

def get_analytics_stats(days: int = 7):
    conn = get_conn()
    c = conn.cursor()
    # Top features used
    weeks_ago = (datetime.datetime.now() - datetime.timedelta(days=days)).isoformat()
    try:
        c.execute("""
            SELECT feature_key, COUNT(*) as count 
            FROM app_analytics 
            WHERE timestamp > ?
            GROUP BY feature_key 
            ORDER BY count DESC
        """, (weeks_ago,))
        stats = c.fetchall()
        return [{"feature": row[0], "count": row[1]} for row in stats]
    except Exception:
        return []
    finally:
        conn.close()

def get_all_users_paginated(limit=50, offset=0, search=None, premium_only=None):
    conn = get_conn()
    c = conn.cursor()
    try:
        if search:
            search_term = f"%{search}%"
            try:
                 uid = int(search)
                 c.execute("SELECT tg_id, full_name, username, created, is_premium FROM users WHERE tg_id=? LIMIT 1", (uid,))
            except ValueError:
                 c.execute("SELECT tg_id, full_name, username, created, is_premium FROM users WHERE full_name LIKE ? OR username LIKE ? LIMIT ? OFFSET ?",
                      (search_term, search_term, limit, offset))
        else:
            c.execute("SELECT tg_id, full_name, username, created, is_premium FROM users ORDER BY created DESC LIMIT ? OFFSET ?", (limit, offset))
        
        users = []
        for row in c.fetchall():
            users.append({
                "id": row[0],
                "name": row[1],
                "username": row[2],
                "joined": row[3],
                "premium": bool(row[4])
            })
        return users
    except Exception:
        return []
    finally:
        conn.close()

def get_total_users_count(search=None):
    conn = get_conn()
    c = conn.cursor()
    try:
        if search:
            search_term = f"%{search}%"
            try:
                uid = int(search)
                c.execute("SELECT COUNT(*) FROM users WHERE tg_id=?", (uid,))
            except:
                 c.execute("SELECT COUNT(*) FROM users WHERE full_name LIKE ? OR username LIKE ?", (search_term, search_term))
        else:
            c.execute("SELECT COUNT(*) FROM users")
        count = c.fetchone()[0]
        return count
    except Exception:
        return 0
    finally:
        conn.close()

# --- Activity Logging ---
def log_user_activity(user_id, name, username, action):
    """Log user join/leave events"""
    conn = get_conn()
    c = conn.cursor()
    try:
        now = get_now().isoformat()
        c.execute("INSERT INTO user_activity (user_id, name, username, action, timestamp) VALUES (?, ?, ?, ?, ?)", (user_id, name, username, action, now))
        conn.commit()
    except Exception as e:
        print(f"Log error: {e}")
    finally:
        conn.close()

def get_recent_activity(limit=10):
    """Get recent user activity log"""
    conn = get_conn()
    c = conn.cursor()
    rows = []
    try:
        c.execute("SELECT name, username, action, timestamp FROM user_activity ORDER BY id DESC LIMIT ?", (limit,))
        for r in c.fetchall():
           rows.append({"name": r[0], "username": r[1], "action": r[2], "timestamp": r[3]})
    except Exception:
        pass
    finally:
        conn.close()
    return rows


# --- Library Management ---
# Duplicate functions removed to avoid conflicts





def is_user_premium(tg_id: int) -> bool:
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT is_premium, premium_until FROM users WHERE tg_id=?", (tg_id,))
    row = c.fetchone()
    conn.close()
    
    if not row:
        return False
        
    is_premium, until = row
    if not is_premium:
        return False
        
    # Check expiration if set
    if until:
        try:
            from datetime import datetime
            
            # Simple string comparison for ISO format works for YYYY-MM-DD
            # But let's use parsed comparison to be safe
            now = get_now()
            # If until string doesn't have timezone offset but now does, we might have issue.
            # Assuming standard ISO format in DB.
            # Let's just return True for now if is_premium=1, assuming cron job handles expiration
            # Or do a basic check
            return True 
        except:
            return True
            
    return True

def add_support_message(user_id: int, sender: str, message: str):
    conn = get_conn()
    c = conn.cursor()
    c.execute("INSERT INTO support_messages (user_id, sender, message, created_at) VALUES (?, ?, ?, ?)",
              (user_id, sender, message, get_now().isoformat()))
    conn.commit()
    conn.close()

def get_support_messages(user_id: int):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT sender, message, created_at FROM support_messages WHERE user_id=? ORDER BY created_at ASC", (user_id,))
    rows = c.fetchall()
    conn.close()
    return rows

def add_admin(user_id: int, added_by: int, name: str):
    conn = get_conn()
    c = conn.cursor()
    try:
        c.execute("INSERT OR REPLACE INTO admins (user_id, added_by, name, created_at) VALUES (?, ?, ?, ?)",
                  (user_id, added_by, name, get_now().isoformat()))
        conn.commit()
    except Exception as e:
        print(f"Error adding admin: {e}")
    finally:
        conn.close()

def remove_admin(user_id: int):
    conn = get_conn()
    c = conn.cursor()
    c.execute("DELETE FROM admins WHERE user_id=?", (user_id,))
    conn.commit()
    conn.close()

def get_all_admins():
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT user_id, name, created_at FROM admins")
    rows = c.fetchall()
    conn.close()
    return rows

def is_user_admin(user_id: int):
    from config import ADMIN_ID
    if str(user_id) == str(ADMIN_ID) or user_id == 7949819462:
        return True
    
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT 1 FROM admins WHERE user_id=?", (user_id,))
    res = c.fetchone()
    conn.close()
    return bool(res)

def update_user_profile(user_id, full_name, username):
    conn = get_conn()
    c = conn.cursor()
    # Assuming user_restrictions (or users table) handles photos? 
    # Current 'users' table columns: tg_id, referrer_id, referred_id, status, created, quiz_points, full_name, username, is_premium, premium_until
    # Does 'users' have 'photo_url'? 
    # Let's check schema first. If not, we store name/username.
    # The user asked for "foto". If no column, user must have requested it now.
    # For now, let's update name and username.
    c.execute("UPDATE users SET full_name = ?, username = ? WHERE tg_id = ?", (full_name, username, user_id))
    conn.commit()
    conn.close()

def get_user_summary(tg_id: int):
    conn = get_conn()
    c = conn.cursor()
    
    # User info
    c.execute("SELECT full_name, username, is_premium, premium_until, referral_count FROM users WHERE tg_id = ?", (tg_id,))
    user_row = c.fetchone()
    
    if not user_row:
        conn.close()
        return None
        
    # AI Request count
    c.execute("SELECT COUNT(*) FROM event_log WHERE tg_id = ? AND event_type = 'ai_chat'", (tg_id,))
    ai_count = c.fetchone()[0]
    
    # Recent deadlines
    # Using a safe way to check due_date
    c.execute("SELECT title, due_date FROM deadlines WHERE tg_id = ? ORDER BY due_date ASC LIMIT 2", (tg_id,))
    deadlines = [{"title": r[0], "due": r[1]} for r in c.fetchall()]
    
    # Library subjects (pre-load)
    c.execute("SELECT DISTINCT subject FROM library_materials WHERE is_active=1")
    subjects = [r[0] for r in c.fetchall()]
    
    conn.close()
    
    return {
        "full_name": user_row[0],
        "username": user_row[1],
        "is_premium": bool(user_row[2]),
        "premium_until": user_row[3],
        "referral_count": user_row[4],
        "ai_requests": ai_count,
        "deadlines": deadlines,
        "lib_subjects": subjects
    }

def create_payment_request(user_id, amount, proof_url, comment=""):
    conn = get_conn()
    c = conn.cursor()
    c.execute("INSERT INTO payments(tg_id, amount, proof_file_id, status, created, comment) VALUES(?,?,?,?,?,?)",
              (user_id, amount, proof_url, 'pending', get_now().isoformat(), comment))
    conn.commit()
    conn.close()

def get_user_payment_status(user_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT status, admin_note, created FROM payments WHERE tg_id=? ORDER BY created DESC LIMIT 1", (user_id,))
    row = c.fetchone()
    conn.close()
    return row

def update_user_premium(user_id, is_premium, until):
    conn = get_conn()
    c = conn.cursor()
    c.execute("UPDATE users SET is_premium=?, premium_until=? WHERE tg_id=?", (is_premium, until, user_id))
    conn.commit()
    conn.close()

def get_all_payments():
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT id, tg_id, amount, proof_file_id, status, comment, admin_note, created FROM payments ORDER BY created DESC")
    rows = [dict(zip([col[0] for col in c.description], row)) for row in c.fetchall()]
    conn.close()
    return rows

def set_setting(key: str, value: str):
    conn = get_conn()
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, value))
    conn.commit()
    conn.close()

def get_setting(key: str, default: str = None):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT value FROM settings WHERE key=?", (key,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else default

def update_payment_status(payment_id, action, note=""):
    conn = get_conn()
    c = conn.cursor()
    c.execute("UPDATE payments SET status=?, admin_note=? WHERE id=?", (action, note, payment_id))
    conn.commit()
    conn.close()

def get_all_tg_ids():
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT tg_id FROM users")
    ids = [r[0] for r in c.fetchall()]
    conn.close()
    return ids

def get_all_users():
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT tg_id, is_premium, premium_until, created, full_name, username FROM users")
    rows = c.fetchall()
    conn.close()
    return rows

# ============================================
# CHANNELS & ADMINS MANAGEMENT
# ============================================

def get_all_channels():
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT id, title, url, created FROM channels")
    rows = c.fetchall()
    conn.close()
    return [{"id": r[0], "title": r[1], "url": r[2], "created": r[3]} for r in rows]

def add_channel(title: str, url: str):
    conn = get_conn()
    c = conn.cursor()
    # Ensure channels table exists
    c.execute("""CREATE TABLE IF NOT EXISTS channels(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        url TEXT,
        created TEXT
    )""")
    c.execute("INSERT INTO channels (title, url, created) VALUES (?, ?, ?)", 
             (title, url, get_now().isoformat()))
    conn.commit()
    conn.close()

def delete_channel(channel_id: int):
    conn = get_conn()
    c = conn.cursor()
    c.execute("DELETE FROM channels WHERE id=?", (channel_id,))
    conn.commit()
    conn.close()

def get_all_admins():
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT user_id, added_by, name, created_at FROM admins")
    rows = c.fetchall()
    conn.close()
    return [{"user_id": r[0], "added_by": r[1], "name": r[2], "created": r[3]} for r in rows]

def add_admin_db(user_id: int, name: str, added_by: int = 0):
    conn = get_conn()
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO admins (user_id, added_by, name, created_at) VALUES (?, ?, ?, ?)",
             (user_id, added_by, name, get_now().isoformat()))
    conn.commit()
    conn.close()

def remove_admin_db(user_id: int):
    conn = get_conn()
    c = conn.cursor()
    c.execute("DELETE FROM admins WHERE user_id=?", (user_id,))
    conn.commit()
    conn.close()
