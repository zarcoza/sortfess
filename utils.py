from aiogram import Bot
from aiogram.types import ChatMember
from aiogram.exceptions import TelegramForbiddenError, TelegramBadRequest
from config import REQUIRED_CHANNELS

# Status apakah fitur menfess dibuka atau tidak
_POST_STATUS = {"is_open": True}

def set_post_status(status: bool):
    """
    Mengatur status apakah fitur menfess dibuka atau ditutup.

    Args:
        status (bool): True untuk membuka, False untuk menutup.
    """
    _POST_STATUS["is_open"] = status

def get_post_status() -> bool:
    """
    Mengambil status apakah fitur menfess sedang dibuka.

    Returns:
        bool: True jika dibuka, False jika ditutup.
    """
    return _POST_STATUS["is_open"]

async def check_subscription(user_id: int) -> bool:
    """
    Memeriksa apakah user sudah subscribe ke semua channel wajib.

    Args:
        user_id (int): ID pengguna Telegram.

    Returns:
        bool: True jika user sudah subscribe ke semua channel, False jika belum atau gagal cek.
    """
    bot = Bot.get_current()

    for channel_id in REQUIRED_CHANNELS:
        try:
            member: ChatMember = await bot.get_chat_member(chat_id=channel_id, user_id=user_id)
            if member.status not in {"member", "administrator", "creator"}:
                return False
        except (TelegramForbiddenError, TelegramBadRequest):
            # Bot tidak punya akses atau channel tidak valid
            return False
        except Exception:
            # Error tak terduga, asumsikan belum subscribe
            return False

    return True
