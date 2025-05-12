from aiogram import Router, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from db import add_user
from config import REQUIRED_CHANNELS, VALID_HASHTAGS

router = Router()

def sub_keyboard() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton("命 ｡ Subscribe Channel Base Menfess", url=f"https://t.me/{REQUIRED_CHANNELS[0][1:]}")],
        [InlineKeyboardButton("命 ｡ Subscribe Channel Heart Heart", url=f"https://t.me/{REQUIRED_CHANNELS[1][1:]}")],
        [InlineKeyboardButton("✦ Done Subscribe", callback_data="check_sub")]
    ])
    return kb

def hashtag_info() -> str:
    info = "\n".join([f"• <b>{tag}</b> → {desc}" for tag, desc in VALID_HASHTAGS.items()])
    return info

@router.message(commands=["start"])
async def start_cmd(message: types.Message):
    add_user(message.from_user.id, message.from_user.username or "")
    await message.answer_photo(
        photo='https://yourbannerurl.com/banner.jpg',
        caption=(
            "⾕ — <b>Welcome to Sort Menfess!</b> \n\n"
            "Mau kirim confess buat orang? Pengakuan? Sambat? Atau bahkan cerita hal diluar nurul? Gampang kok, cukup pake hashtag sesuai jenisnya:\n\n"
            f"{hashtag_info()}\n\n"
            "Tapi subscribe dulu ya sebelum ngirim menfess, klik tombol di bawah ini. ⬇"
        ),
        reply_markup=sub_keyboard()
    )