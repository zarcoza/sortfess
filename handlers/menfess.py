from aiogram import Router, types, F, Bot
from filters import contains_bad_word
from config import VALID_HASHTAGS, CHANNEL_ID
from utils import check_subscription, get_post_status
from handlers.start import sub_keyboard
from db import (
    add_user,
    is_banned,
    count_hashtags,
    log_post
)

router = Router()

@router.message(F.text)
async def handle_text_menfess(message: types.Message, bot: Bot):
    user_id = message.from_user.id
    username = message.from_user.username or ""
    full_name = message.from_user.full_name
    text: str = message.text.strip()

    add_user(user_id, username)

    if is_banned(user_id):
        return await message.reply("Maaf kamu telah diblokir dari mengirim menfess.")

    if not get_post_status():
        return await message.reply("♬ ˖ ࣪  Base lagi rehat beb. Nanti balik lagi ya~")

    if not await check_subscription(user_id, bot):
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

    count_hashtags(text)
    log_post(user_id, text)

    if '#gonna' in text_lower:
        mention = f"@{username}" if username else "(tidak ada username)"
        forward_text = (
            f"{message.text}\n\n"
            f"👤 Nama  : {full_name}\n"
            f"🆔 ID    : <code>{user_id}</code>\n"
            f"🔗 User : {mention}"
        )
    else:
        forward_text = f"{message.text}"

    await bot.send_message(
        chat_id=CHANNEL_ID,
        text=forward_text,
        parse_mode="HTML"
    )

    await message.reply("Done kak! Fess kamu udah terbang ke base ✈️")

@router.message(F.photo)
async def handle_photo_menfess(message: types.Message, bot: Bot):
    user_id = message.from_user.id
    caption = message.caption or ""

    add_user(user_id, message.from_user.username or "")

    if is_banned(user_id):
        return await message.reply("Maaf kamu telah diblokir dari mengirim menfess.")

    if not get_post_status():
        return await message.reply("♬ ˖ ࣪  Base lagi rehat beb. Nanti balik lagi ya~")

    if not await check_subscription(user_id, bot):
        return await message.reply(
            "Eits, belum subscribe! Klik tombol di bawah dulu yaa~",
            reply_markup=sub_keyboard()
        )

    if len(caption) < 10:
        return await message.reply("Caption kamu terlalu pendek kak~")

    count_hashtags(caption)
    log_post(user_id, caption)

    photo = message.photo[-1].file_id
    await bot.send_photo(
        chat_id=CHANNEL_ID,
        photo=photo,
        caption=f"{caption}",
        parse_mode="HTML"
    )
    await message.reply("Pesan kamu sudah dikirim ke base!")

@router.message(F.document)
async def handle_document_menfess(message: types.Message, bot: Bot):
    user_id = message.from_user.id
    caption = message.caption or ""

    add_user(user_id, message.from_user.username or "")

    if is_banned(user_id):
        return await message.reply("Maaf kamu telah diblokir dari mengirim menfess.")

    if not get_post_status():
        return await message.reply("♬ ˖ ࣪  Base lagi rehat beb. Nanti balik lagi ya~")

    if not await check_subscription(user_id, bot):
        return await message.reply("Eits, belum subscribe dulu yaa~", reply_markup=sub_keyboard())

    if len(caption) < 10:
        return await message.reply("Caption kamu terlalu pendek kak~")

    count_hashtags(caption)
    log_post(user_id, caption)

    await bot.send_document(
        chat_id=CHANNEL_ID,
        document=message.document.file_id,
        caption=f"{caption}",
        parse_mode="HTML"
    )
    await message.reply("Dokumen kamu sudah dikirim ke base!")

@router.message(F.voice)
async def handle_voice_menfess(message: types.Message, bot: Bot):
    user_id = message.from_user.id

    add_user(user_id, message.from_user.username or "")

    if is_banned(user_id):
        return await message.reply("Maaf kamu telah diblokir dari mengirim menfess.")

    if not get_post_status():
        return await message.reply("♬ ˖ ࣪  Base lagi rehat beb. Nanti balik lagi ya~")

    if not await check_subscription(user_id, bot):
        return await message.reply("Eits, belum subscribe dulu yaa~", reply_markup=sub_keyboard())

    caption = message.caption or ""
    count_hashtags(caption)
    log_post(user_id, caption)

    await bot.send_voice(
        chat_id=CHANNEL_ID,
        voice=message.voice.file_id,
        caption=f"{caption}",
        parse_mode="HTML"
    )
    await message.reply("Voice note kamu udah dikirim ke base!")

@router.message(F.sticker)
async def handle_sticker_menfess(message: types.Message, bot: Bot):
    user_id = message.from_user.id

    add_user(user_id, message.from_user.username or "")

    if is_banned(user_id):
        return await message.reply("Maaf kamu telah diblokir dari mengirim menfess.")

    if not get_post_status():
        return await message.reply("♬ ˖ ࣪  Base lagi rehat beb. Nanti balik lagi ya~")

    if not await check_subscription(user_id, bot):
        return await message.reply("Eits, belum subscribe dulu yaa~", reply_markup=sub_keyboard())

    log_post(user_id, "[STIKER]")

    await bot.send_sticker(
        chat_id=CHANNEL_ID,
        sticker=message.sticker.file_id
    )

    # Jika ingin mengirim pesan teks untuk stiker, tambahkan bot.send_message di bawah.
    # await bot.send_message(
    #     chat_id=CHANNEL_ID,
    #     text="🧩 Stiker dari pengguna anonim"
    # )

    await message.reply("Stiker kamu udah dikirim ke base!")