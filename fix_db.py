import sqlite3
import os

db_path = "bot_database.db" # Check proper path if different
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("DELETE FROM settings WHERE key='webapp_url'")
    conn.commit()
    print("Bazadagi eski webapp_url o'chirildi.")
    conn.close()
else:
    print("Baza topilmadi.")
