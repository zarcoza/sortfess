import sqlite3
import os
from typing import List, Optional, Tuple, Dict

DB_DIR = os.path.join(os.path.dirname(__file__), 'data')
DB_PATH = os.path.join(DB_DIR, 'users.db')

os.makedirs(DB_DIR, exist_ok=True)

def get_connection() -> sqlite3.Connection:
    return sqlite3.connect(DB_PATH, check_same_thread=False)

# Inisialisasi tabel
with get_connection() as conn:
    conn.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT)')
    conn.execute('CREATE TABLE IF NOT EXISTS banned_users (id INTEGER PRIMARY KEY)')
    conn.execute('CREATE TABLE IF NOT EXISTS posts (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, text TEXT)')
    conn.execute('CREATE TABLE IF NOT EXISTS hashtag_stats (hashtag TEXT PRIMARY KEY, count INTEGER)')
    conn.execute('CREATE TABLE IF NOT EXISTS admins (id INTEGER PRIMARY KEY)')
    conn.commit()

def add_user(user_id: int, username: Optional[str]):
    with get_connection() as conn:
        conn.execute("INSERT OR IGNORE INTO users (id, username) VALUES (?, ?)", (user_id, username))
        conn.commit()

def get_all_users() -> List[int]:
    with get_connection() as conn:
        cursor = conn.execute("SELECT id FROM users")
        return [row[0] for row in cursor.fetchall()]

def get_user_by_id(user_id: int) -> Optional[Dict[str, Optional[str]]]:
    with get_connection() as conn:
        cur = conn.execute("SELECT id, username FROM users WHERE id = ?", (user_id,))
        row = cur.fetchone()
        if row:
            return {"id": row[0], "username": row[1]}
        return None

def ban_user(user_id: int):
    with get_connection() as conn:
        conn.execute("INSERT OR IGNORE INTO banned_users (id) VALUES (?)", (user_id,))
        conn.commit()

def unban_user(user_id: int):
    with get_connection() as conn:
        conn.execute("DELETE FROM banned_users WHERE id = ?", (user_id,))
        conn.commit()

def is_banned(user_id: int) -> bool:
    with get_connection() as conn:
        cur = conn.execute("SELECT 1 FROM banned_users WHERE id = ?", (user_id,))
        return cur.fetchone() is not None

def get_all_banned_users() -> List[int]:
    with get_connection() as conn:
        cur = conn.execute("SELECT id FROM banned_users")
        return [row[0] for row in cur.fetchall()]

def log_post(user_id: int, text: str):
    with get_connection() as conn:
        conn.execute("INSERT INTO posts (user_id, text) VALUES (?, ?)", (user_id, text))
        conn.commit()

def get_last_posts(limit=10) -> List[Tuple[int, str]]:
    with get_connection() as conn:
        cur = conn.execute("SELECT user_id, text FROM posts ORDER BY id DESC LIMIT ?", (limit,))
        return cur.fetchall()[::-1]

def latest_post(user_id: int) -> Optional[str]:
    with get_connection() as conn:
        cur = conn.execute("SELECT text FROM posts WHERE user_id = ? ORDER BY id DESC LIMIT 1", (user_id,))
        row = cur.fetchone()
        return row[0] if row else None

def count_hashtags(text: str):
    with get_connection() as conn:
        words = text.lower().split()
        for word in words:
            if word.startswith("#"):
                hashtag = word.strip()
                cur = conn.execute("SELECT count FROM hashtag_stats WHERE hashtag = ?", (hashtag,))
                row = cur.fetchone()
                if row:
                    conn.execute("UPDATE hashtag_stats SET count = count + 1 WHERE hashtag = ?", (hashtag,))
                else:
                    conn.execute("INSERT INTO hashtag_stats (hashtag, count) VALUES (?, 1)", (hashtag,))
        conn.commit()

def get_top_hashtags(n=5) -> List[Tuple[str, int]]:
    with get_connection() as conn:
        cur = conn.execute("SELECT hashtag, count FROM hashtag_stats ORDER BY count DESC LIMIT ?", (n,))
        return cur.fetchall()

def clear_banlist():
    with get_connection() as conn:
        conn.execute("DELETE FROM banned_users")
        conn.commit()

# === Admin Functions ===
def get_admin_ids() -> List[int]:
    with get_connection() as conn:
        cur = conn.execute("SELECT id FROM admins")
        return [row[0] for row in cur.fetchall()]

def get_all_admins() -> List[Dict[str, Optional[str]]]:
    with get_connection() as conn:
        cur = conn.execute("SELECT a.id, u.username FROM admins a LEFT JOIN users u ON a.id = u.id")
        return [{"id": row[0], "username": row[1]} for row in cur.fetchall()]

def add_admin_id(user_id: int):
    with get_connection() as conn:
        conn.execute("INSERT OR IGNORE INTO admins (id) VALUES (?)", (user_id,))
        conn.commit()

def remove_admin_id(user_id: int):
    with get_connection() as conn:
        conn.execute("DELETE FROM admins WHERE id = ?", (user_id,))
        conn.commit()

def get_username_by_id(user_id: int) -> Optional[str]:
    with get_connection() as conn:
        cur = conn.execute("SELECT username FROM users WHERE id = ?", (user_id,))
        row = cur.fetchone()
        return row[0] if row else None
