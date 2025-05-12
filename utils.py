from aiogram import Bot
from config import REQUIRED_CHANNELS

# Status POST OPEN/CLOSED
_POST_STATUS = {"is_open": True}

def set_post_status(status: bool):
    _POST_STATUS["is_open"] = status

def get_post_status() -> bool:
    return _POST_STATUS["is_open"]

async def check_subscription(user_id: int) -> bool:
    bot = Bot.get_current()
    for ch in REQUIRED_CHANNELS:
        member = await bot.get_chat_member(chat_id=ch, user_id=user_id)
        if member.status not in ['member', 'administrator', 'creator']:
            return False
    return True