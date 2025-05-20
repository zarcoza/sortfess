from aiogram import Router, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from filters import contains_bad_word
from config import VALID_HASHTAGS, CHANNEL_ID
from utils import check_subscription, get_post_status
from handlers.start import sub_keyboard
from db import add_user

router = Router()

def report_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton("★ Laporkan ke Admin", url="https://t.me/anxtariksa")]
    ])

@router.message(F.text)
async def handle_text_menfess(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username or ""
    full_name = message.from_user.full_name
    text: str = message.text.strip()

    add_user(user_id, username)

    if not get_post_status():
        return await message.reply("♬ ˖ ࣪  Base lagi rehat beb. Nanti balik lagi ya~")

    if not await check_subscription(user_id):
        return await message.reply(
            "Eits, belum join base nih!\nYuk follow dulu channel kita biar bisa kirim menfess 🤍",
            reply_markup=sub_keyboard()
        )

    if len(text) < 10:
        return await message.reply("Pesanmu terlalu pendek kak, coba tambahkan lebih banyak ya~")

    if contains_bad_word(text):
        return await message.reply("Ups, no toxic zone ya ma bro. Jaga omongan dong~")

    text_lower = text.lower()
    if not any(tag in text_lower for tag in VALID_HASHTAGS):
        return await message.reply("Tambahin hashtag dulu dong \nContoh: #sorta pengen martabak")

    wrong_tags = [w for w in text_lower.split() if w.startswith('#') and w not in VALID_HASHTAGS]
    if wrong_tags:
        return await message.reply("Kayaknya ada typo di hashtag kamu deh \nCek lagi yaa!")

    if '#gonna' in text_lower:
        mention = f"@{username}" if username else "(tidak ada username)"
        forward_text = (
            f"{message.text}\n\n"
            f"👤 Nama  : {full_name}\n"
            f"🆔 ID    : <code>{user_id}</code>\n"
            f"🔗 User : {mention}"
        )
    else:
        forward_text = f"{message.text}\n\n🕶 Anonim by: {message.from_user.mention_html()}"

    await message.bot.send_message(
        chat_id=CHANNEL_ID,
        text=forward_text,
        reply_markup=report_keyboard(),
        parse_mode="HTML"
    )

    await message.reply("Done kak! Fess kamu udah terbang ke base ✈️")

@router.message(F.photo)
async def handle_photo_menfess(message: types.Message):
    user_id = message.from_user.id
    if not await check_subscription(user_id):
        return await message.reply("Eits, belum subscribe! Klik tombol di bawah dulu yaa~", reply_markup=sub_keyboard())

    caption = message.caption or ""
    if len(caption) < 10:
        return await message.reply("Caption kamu terlalu pendek kak~")

    photo = message.photo[-1].file_id
    await message.bot.send_photo(
        chat_id=CHANNEL_ID,
        photo=photo,
        caption=f"{caption}\n\n🕶 Anonim by: {message.from_user.mention_html()}",
        reply_markup=report_keyboard(),
        parse_mode="HTML"
    )

    await message.reply("Pesan kamu sudah dikirim ke base!")