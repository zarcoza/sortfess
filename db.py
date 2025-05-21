import sqlite3
import os
import logging
from typing import List, Optional, Tuple, Dict

# Lokasi database
DB_DIR = os.path.join(os.path.dirname(__file__), 'data')
DB_PATH = os.path.join(DB_DIR, 'users.db')
os.makedirs(DB_DIR, exist_ok=True)

def get_connection() -> sqlite3.Connection:
    """Buka koneksi SQLite ke database pengguna."""
    return sqlite3.connect(DB_PATH, check_same_thread=False)

# Inisialisasi skema database
with get_connection() as conn:
    conn.executescript('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT
        );
        CREATE TABLE IF NOT EXISTS banned_users (
            id INTEGER PRIMARY KEY
        );
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            text TEXT
        );
        CREATE TABLE IF NOT EXISTS hashtag_stats (
            hashtag TEXT PRIMARY KEY,
            count INTEGER
        );
        CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY
        );
    ''')
    conn.commit()

# === USERS ===

def add_user(user_id: int, username: Optional[str]) -> None:
    with get_connection() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO users (id, username) VALUES (?, ?)",
            (user_id, username)
        )
        conn.commit()

def get_user_by_id(user_id: int) -> Optional[Dict[str, Optional[str]]]:
    with get_connection() as conn:
        row = conn.execute("SELECT id, username FROM users WHERE id = ?", (user_id,)).fetchone()
        return {"id": row[0], "username": row[1]} if row else None

def get_username_by_id(user_id: int) -> Optional[str]:
    with get_connection() as conn:
        row = conn.execute("SELECT username FROM users WHERE id = ?", (user_id,)).fetchone()
        return row[0] if row else None

def get_all_users() -> List[int]:
    with get_connection() as conn:
        return [row[0] for row in conn.execute("SELECT id FROM users").fetchall()]

# === BANNED USERS ===

def ban_user(user_id: int) -> None:
    with get_connection() as conn:
        conn.execute("INSERT OR IGNORE INTO banned_users (id) VALUES (?)", (user_id,))
        conn.commit()

def unban_user(user_id: int) -> None:
    with get_connection() as conn:
        conn.execute("DELETE FROM banned_users WHERE id = ?", (user_id,))
        conn.commit()

def is_banned(user_id: int) -> bool:
    with get_connection() as conn:
        return conn.execute("SELECT 1 FROM banned_users WHERE id = ?", (user_id,)).fetchone() is not None

def get_all_banned_users() -> List[int]:
    with get_connection() as conn:
        return [row[0] for row in conn.execute("SELECT id FROM banned_users").fetchall()]

def clear_banlist() -> None:
    with get_connection() as conn:
        conn.execute("DELETE FROM banned_users")
        conn.commit()

# === POSTS ===

def log_post(user_id: int, text: str) -> None:
    with get_connection() as conn:
        conn.execute("INSERT INTO posts (user_id, text) VALUES (?, ?)", (user_id, text))
        conn.commit()

def latest_post(user_id: int) -> Optional[str]:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT text FROM posts WHERE user_id = ? ORDER BY id DESC LIMIT 1",
            (user_id,)
        ).fetchone()
        return row[0] if row else None

def get_last_posts(limit: int = 10) -> List[Tuple[int, str]]:
    with get_connection() as conn:
        return conn.execute(
            "SELECT user_id, text FROM posts ORDER BY id DESC LIMIT ?",
            (limit,)
        ).fetchall()[::-1]

# === HASHTAGS ===

def count_hashtags(text: str) -> None:
    """Perbarui statistik hashtag berdasarkan teks."""
    words = text.lower().split()
    with get_connection() as conn:
        for word in words:
            if word.startswith("#"):
                hashtag = word.strip()
                row = conn.execute("SELECT count FROM hashtag_stats WHERE hashtag = ?", (hashtag,)).fetchone()
                if row:
                    conn.execute("UPDATE hashtag_stats SET count = count + 1 WHERE hashtag = ?", (hashtag,))
                else:
                    conn.execute("INSERT INTO hashtag_stats (hashtag, count) VALUES (?, 1)", (hashtag,))
        conn.commit()

def get_top_hashtags(n: int = 5) -> List[Tuple[str, int]]:
    with get_connection() as conn:
        return conn.execute(
            "SELECT hashtag, count FROM hashtag_stats ORDER BY count DESC LIMIT ?",
            (n,)
        ).fetchall()

# === ADMINS ===

def add_admin_id(user_id: int) -> None:
    with get_connection() as conn:
        conn.execute("INSERT OR IGNORE INTO admins (id) VALUES (?)", (user_id,))
        conn.commit()

def remove_admin_id(user_id: int) -> None:
    with get_connection() as conn:
        conn.execute("DELETE FROM admins WHERE id = ?", (user_id,))
        conn.commit()

def get_admin_ids() -> List[int]:
    with get_connection() as conn:
        return [row[0] for row in conn.execute("SELECT id FROM admins").fetchall()]

def get_all_admins() -> List[Dict[str, Optional[str]]]:
    with get_connection() as conn:
        return [
            {"id": row[0], "username": row[1]}
            for row in conn.execute(
                "SELECT a.id, u.username FROM admins a LEFT JOIN users u ON a.id = u.id"
            ).fetchall()
        ]
