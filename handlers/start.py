from aiogram import Router, types, Bot
from aiogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton,
    CallbackQuery
)
from aiogram.filters import Command, Filter
from aiogram import F  # ⬅️ tambahkan ini
from db import add_user
from config import REQUIRED_CHANNELS, VALID_HASHTAGS

router = Router()
BASE_CHANNEL_ID = 2538940104  # ID channel @sortfess

def sub_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="命 ｡ Base Menfess", url="https://t.me/sortfess")],
        [InlineKeyboardButton(text="命 ｡ Heart Heart", url="https://t.me/fiIIyourheart")],
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
        photo="https://raw.githubusercontent.com/zarcoza/sortfess/main/banner.png",
        caption=caption_text,
        reply_markup=sub_keyboard(),
        parse_mode="HTML"
    )

@router.callback_query(types.CallbackQuery.filter(lambda c: c.data == "check_sub"))
async def check_subscription(callback: CallbackQuery, bot: Bot):
    user_id = callback.from_user.id
    all_joined = True

    for channel in REQUIRED_CHANNELS:
        try:
            member = await bot.get_chat_member(chat_id=channel, user_id=user_id)
            if member.status in ["left", "kicked"]:
                all_joined = False
                break
        except:
            all_joined = False
            break

    if all_joined:
        await callback.message.edit_reply_markup()
        await callback.message.answer("☆ Oke kamu sudah subscribe, bisa mulai ngirim menfess yaa!")
    else:
        await callback.message.answer("𖦹 Waduh kamu belum subscribe nih, subscribe dulu yaa!", reply_markup=sub_keyboard())

@router.message()
async def handle_menfess(message: types.Message, bot: Bot):
    if not message.text:
        return

    for tag in VALID_HASHTAGS:
        if tag in message.text.lower():
            try:
                await bot.send_message(
                    chat_id=BASE_CHANNEL_ID,
                    text=message.text,
                    parse_mode="HTML"
                )
                await message.reply("☆ Menfess kamu sudah terkirim ke channel!")
            except Exception:
                await message.reply("𖦹 Gagal mengirim menfess. Coba lagi nanti.")
            break  # hanya kirim 1x
