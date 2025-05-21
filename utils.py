from aiogram import Bot
from aiogram.types import ChatMember
from aiogram.exceptions import TelegramForbiddenError, TelegramBadRequest
from config import REQUIRED_CHANNELS

# Status apakah fitur menfess dibuka atau tidak
_POST_STATUS = {"is_open": True}

def set_post_status(status: bool):
    """Set status buka/tutup fitur menfess."""
    _POST_STATUS["is_open"] = status

def get_post_status() -> bool:
    """Ambil status buka/tutup fitur menfess."""
    return _POST_STATUS["is_open"]

async def check_subscription(user_id: int, bot: Bot) -> bool:
    """
    Cek apakah user sudah subscribe ke semua channel wajib.

    Returns:
        True jika semua channel disubscribe, False jika ada yang belum atau gagal dicek.
    """
    for channel_id in REQUIRED_CHANNELS:
        try:
            member: ChatMember = await bot.get_chat_member(chat_id=channel_id, user_id=user_id)
            if member.status not in {"member", "administrator", "creator"}:
                return False
        except (TelegramForbiddenError, TelegramBadRequest):
            return False
        except Exception:
            return False
    return True
