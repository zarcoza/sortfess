import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'data', 'users.db')
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

conn = sqlite3.connect(DB_PATH, check_same_thread=False)
c = conn.cursor()

c.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    username TEXT
)
''')
conn.commit()

def add_user(user_id: int, username: str):
    c.execute("INSERT OR IGNORE INTO users (id, username) VALUES (?, ?)", (user_id, username))
    conn.commit()

def get_all_users() -> list[int]:
    c.execute("SELECT id FROM users")
    return [row[0] for row in c.fetchall()]