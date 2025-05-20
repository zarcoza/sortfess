import sqlite3
import os
from typing import List, Optional, Tuple

DB_DIR = os.path.join(os.path.dirname(__file__), 'data')
DB_PATH = os.path.join(DB_DIR, 'users.db')

# Pastikan direktori data tersedia
os.makedirs(DB_DIR, exist_ok=True)

def get_connection() -> sqlite3.Connection:
    """Mengembalikan koneksi SQLite ke database user."""
    return sqlite3.connect(DB_PATH, check_same_thread=False)

# Inisialisasi semua tabel
with get_connection() as conn:
    conn.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT)')
    conn.execute('CREATE TABLE IF NOT EXISTS banned_users (id INTEGER PRIMARY KEY)')
    conn.execute('CREATE TABLE IF NOT EXISTS posts (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, text TEXT)')
    conn.execute('CREATE TABLE IF NOT EXISTS hashtag_stats (hashtag TEXT PRIMARY KEY, count INTEGER)')
    conn.commit()

def add_user(user_id: int, username: Optional[str]):
    """Menambahkan user baru ke database jika belum ada."""
    with get_connection() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO users (id, username) VALUES (?, ?)",
            (user_id, username)
        )
        conn.commit()

def get_all_users() -> List[int]:
    """Mengambil semua ID user dari database."""
    with get_connection() as conn:
        cursor = conn.execute("SELECT id FROM users")
        return [row[0] for row in cursor.fetchall()]

# BAN / UNBAN (persistent)
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

# LOG POST & HISTORY
def log_post(user_id: int, text: str):
    with get_connection() as conn:
        conn.execute("INSERT INTO posts (user_id, text) VALUES (?, ?)", (user_id, text))
        conn.commit()

def get_last_posts(limit=10) -> List[Tuple[int, str]]:
    with get_connection() as conn:
        cur = conn.execute(
            "SELECT user_id, text FROM posts ORDER BY id DESC LIMIT ?",
            (limit,)
        )
        return cur.fetchall()[::-1]  # agar urut dari lama ke terbaru

# HASHTAG STATS
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
        cur = conn.execute(
            "SELECT hashtag, count FROM hashtag_stats ORDER BY count DESC LIMIT ?",
            (n,)
        )
        return cur.fetchall()

# Opsional: clear semua data banned (gunakan hati-hati)
def clear_banlist():
    with get_connection() as conn:
        conn.execute("DELETE FROM banned_users")
        conn.commit()