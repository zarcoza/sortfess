from aiogram import Router, types, F
from filters import contains_bad_word
from config import VALID_HASHTAGS, CHANNEL_ID
from utils import check_subscription, get_post_status
from handlers.start import sub_keyboard
from db import add_user
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

router = Router()

def report_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup().add(
        InlineKeyboardButton("★ Laporkan ke Admin", url="https://t.me/anxtariksa")
    )

@router.message(F.text)
async def handle_menfess(message: types.Message):
    # simpan user
    add_user(message.from_user.id, message.from_user.username or "")
    
    # cek subscribe
    if not await check_subscription(message.from_user.id):
        return await message.reply(
            "Eits, belum join base nih!\nYuk follow dulu channel kita biar bisa kirim menfess.",
            reply_markup=sub_keyboard()
        )

    text = message.text.strip()

    # cek kata kotor
    if contains_bad_word(text):
        return await message.reply("Ups, no toxic zone ya ma bro. Jaga omongan dong~")

    # cek hashtag
    text_lower = text.lower()
    if not any(tag in text_lower for tag in VALID_HASHTAGS):
        return await message.reply(
            "Tambahin hashtag dulu dong guys. Contoh: #sorta yh ok ckp tw"
        )

    # cek typo hashtag
    wrong = [w for w in text_lower.split() if w.startswith('#') and w not in VALID_HASHTAGS]
    if wrong:
        return await message.reply("Hashtagmu salah nih, cek kembali ya!")

    # cek status open/close
    if not get_post_status():
        return await message.reply("Base lagi rehat beb. Nanti balik lagi ya~")

    # ======== LOGIKA TAMBAHAN UNTUK #gonna ========
    show_username = False
    if '#gonna' in text_lower:
        show_username = True

    # format pesan untuk dikirim ke channel
    if show_username:
        forward = f"{message.text}\n\nDipost oleh: @{message.from_user.username or 'noname'}"
    else:
        forward = f"{message.text}\n\nAnonim by: 🕶 {message.from_user.mention_html()}"

    # kirim ke channel
    await message.bot.send_message(chat_id=CHANNEL_ID, text=forward, reply_markup=report_keyboard())
    await message.reply("Done kak! Fess kamu udah terbang ke base!")