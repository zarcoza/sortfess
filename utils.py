from aiogram import Bot
from config import REQUIRED_CHANNELS
from aiogram.exceptions import TelegramForbiddenError, TelegramBadRequest

# ✅ Status apakah pengguna boleh kirim menfess
_POST_STATUS = {"is_open": True}

def set_post_status(status: bool):
    """Set status POST (True = buka menfess, False = tutup)."""
    _POST_STATUS["is_open"] = status

def get_post_status() -> bool:
    """Ambil status apakah menfess sedang dibuka atau tidak."""
    return _POST_STATUS["is_open"]

async def check_subscription(user_id: int) -> bool:
    """
    Cek apakah user sudah subscribe ke semua channel yang diwajibkan.
    Jika salah satu belum, return False.
    """
    bot = Bot.get_current()
    for ch in REQUIRED_CHANNELS:
        try:
            member = await bot.get_chat_member(chat_id=ch, user_id=user_id)
            if member.status not in ['member', 'administrator', 'creator']:
                return False
        except (TelegramForbiddenError, TelegramBadRequest):
            # Jika channel tidak valid, atau bot tidak punya akses
            return False
    return True
