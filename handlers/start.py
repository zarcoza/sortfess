from aiogram import Router, types, Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters import Command
from aiogram import F
from db import add_user
from config import REQUIRED_CHANNELS, VALID_HASHTAGS

router = Router()

# Tombol subscribe
def sub_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton("命 ｡ Base Menfess", url="https://t.me/sortfess")],
        [InlineKeyboardButton("命 ｡ Heart Heart", url="https://t.me/fiIIyourheart")],
        [InlineKeyboardButton("✦ Done Subscribe", callback_data="check_sub")]
    ])

# Tombol info setelah subscribe
def info_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton("✸ Rules", url="https://t.me/sortfess/5")],
        [InlineKeyboardButton("𖥔 Admin", url="https://t.me/sortfess/6")]
    ])

# Format list hashtag
def hashtag_info() -> str:
    return "\n".join([f"• <b>{tag}</b> → {desc}" for tag, desc in VALID_HASHTAGS.items()])

# Handle /start
@router.message(Command("start"))
async def start_cmd(message: types.Message):
    add_user(message.from_user.id, message.from_user.username or "")

    caption = (
        "<b>⾕ — Welcome to Sort Menfess!</b>\n\n"
        "Mau kirim confess buat orang? Pengakuan? Sambat? Atau bahkan cerita hal diluar nurul?\n"
        "Gampang kok! Cukup pake hashtag sesuai jenisnya:\n\n"
        f"{hashtag_info()}\n\n"
        "Tapi subscribe dulu ya sebelum ngirim menfess, klik tombol di bawah ini. ⬇"
    )

    await message.answer_photo(
        photo="https://raw.githubusercontent.com/zarcoza/sortfess/main/banner.png",
        caption=caption,
        reply_markup=sub_keyboard(),
        parse_mode="HTML"
    )

# Handle tombol "✦ Done Subscribe"
@router.callback_query(F.data == "check_sub")
async def check_subscription(callback: CallbackQuery, bot: Bot):
    user_id = callback.from_user.id
    all_joined = True

    for channel in REQUIRED_CHANNELS:
        try:
            member = await bot.get_chat_member(chat_id=channel, user_id=user_id)
            if member.status in ["left", "kicked"]:
                all_joined = False
                break
        except Exception as e:
            print(f"Error checking subscription: {e}")
            all_joined = False
            break

    await callback.answer()

    try:
        await callback.message.delete()
    except:
        pass

    if all_joined:
        try:
            await bot.send_message(
                chat_id=user_id,
                text="☆ Oke kamu sudah subscribe, bisa mulai ngirim menfess yaa!",
                reply_markup=info_keyboard(),
                parse_mode="HTML"
            )
        except Exception as e:
            print(f"Gagal kirim pesan ke user: {e}")
    else:
        try:
            await bot.send_message(
                chat_id=user_id,
                text="𖦹 Waduh kamu belum subscribe nih, subscribe dulu yaa!",
                reply_markup=sub_keyboard(),
                parse_mode="HTML"
            )
        except Exception as e:
            print(f"Gagal kirim pesan ke user: {e}")
