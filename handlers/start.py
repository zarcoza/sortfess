from aiogram import Router, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from db import add_user
from config import REQUIRED_CHANNELS, VALID_HASHTAGS

router = Router()

def sub_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="命 ｡ Subscribe Channel Base Menfess", url="https://t.me/sortfess")],
        [InlineKeyboardButton(text="命 ｡ Subscribe Channel Heart Heart", url="https://t.me/fiIIyourheart")],
        [InlineKeyboardButton(text="✦ Done Subscribe", callback_data="check_sub")]
    ])

def hashtag_info() -> str:
    return "\n".join([f"• <b>{tag}</b> → {desc}" for tag, desc in VALID_HASHTAGS.items()])

@router.message(Command("start"))
async def start_cmd(message: types.Message) -> None:
    add_user(message.from_user.id, message.from_user.username or "")
    
    caption_text = (
        "<b>⾕ — Welcome to Sort Menfess!</b>\n\n"
        "Mau kirim confess buat orang? Pengakuan? Sambat? Atau bahkan cerita hal diluar nurul?\n"
        "Gampang kok! Cukup pake hashtag sesuai jenisnya:\n\n"
        f"{hashtag_info()}\n\n"
        "Tapi subscribe dulu ya sebelum ngirim menfess, klik tombol di bawah ini. ⬇"
    )
    
    await message.answer_photo(
        photo="https://github.com/zarcoza/sortfess/blob/main/banner.png",
        caption=caption_text,
        reply_markup=sub_keyboard(),
        parse_mode="HTML"
    )
