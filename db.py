import sqlite3
import os
from typing import List, Optional

DB_DIR = os.path.join(os.path.dirname(__file__), 'data')
DB_PATH = os.path.join(DB_DIR, 'users.db')

os.makedirs(DB_DIR, exist_ok=True)

def get_connection() -> sqlite3.Connection:
    return sqlite3.connect(DB_PATH, check_same_thread=False)

# Inisialisasi tabel saat modul di-load
with get_connection() as conn:
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT
        )
    ''')
    conn.commit()

def add_user(user_id: int, username: Optional[str]):
    with get_connection() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO users (id, username) VALUES (?, ?)",
            (user_id, username)
        )
        conn.commit()

def get_all_users() -> List[int]:
    with get_connection() as conn:
        cursor = conn.execute("SELECT id FROM users")
        return [row[0] for row in cursor.fetchall()]
