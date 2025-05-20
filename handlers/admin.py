from aiogram import Router, types, F
from config import ADMIN_IDS
from db import get_all_users
from db import get_last_posts
from db import get_top_hashtags
from db import ban_user, unban_user, is_banned
from utils import set_post_status
from aiogram.exceptions import (
    TelegramForbiddenError, TelegramBadRequest,
    TelegramRetryAfter, TelegramNotFound
    )
import asyncio
import logging

router = Router()

def is_admin(user_id: int) -> bool:
    return int(user_id) in ADMIN_IDS  # Pastikan ADMIN_IDS adalah list of int

@router.message(F.text.startswith("/broadcast"))
async def broadcast_handler(message: types.Message):
    if not is_admin(message.from_user.id):
        return await message.reply("Kamu bukan admin, sayang 🤍")

    msg = message.text[len("/broadcast"):].strip()
    if not msg:
        return await message.reply("Isi dulu dong pesannya.\nContoh: /broadcast Halo semua!")

    users = get_all_users()
    total = len(users)
    sent = failed = 0

    await message.reply("Broadcast dimulai...")

    for uid in users:
        try:
            await message.bot.send_message(uid, f"📢 <b>Broadcast Admin:</b>\n\n{msg}")
            sent += 1
            await asyncio.sleep(0.05)
        except (TelegramForbiddenError, TelegramBadRequest, TelegramNotFound):
            failed += 1
        except TelegramRetryAfter as e:
            logging.warning(f"Flood wait: sleeping for {e.retry_after}")
            await asyncio.sleep(e.retry_after)
        except Exception as e:
            logging.error(f"Gagal kirim ke {uid}: {e}")
            failed += 1

    await message.reply(
        f"📣 Broadcast selesai!\n"
        f"👥 Total user: {total}\n"
        f"✅ Berhasil: {sent}\n"
        f"❌ Gagal: {failed}"
    )

@router.message(F.text.startswith("/balas"))
async def reply_user(message: types.Message):
    if not is_admin(message.from_user.id):
        return await message.reply("Cuma admin yang bisa balas DM.")

    parts = message.text.split(maxsplit=2)
    if len(parts) < 3:
        return await message.reply("Format: /balas <user_id> <pesan>")

    try:
        user_id = int(parts[1])
        reply_msg = parts[2]
        await message.bot.send_message(user_id, f"👩‍💻 Admin:\n{reply_msg}")
        await message.reply("Pesan terkirim, mantap!")
    except Exception as e:
        await message.reply(f"❌ Gagal kirim pesan ke user. Error:\n<code>{e}</code>", parse_mode="HTML")

@router.message(F.text.in_({"/tutup", "/buka"}))
async def toggle_post(message: types.Message):
    if not is_admin(message.from_user.id):
        return await message.reply("Kamu ga punya akses, bestie.")

    if message.text == "/tutup":
        set_post_status(False)
        await message.reply("✋ Base ditutup dulu yaa, istirahat sejenak.")
    else:
        set_post_status(True)
        await message.reply("✅ Base sudah dibuka lagi, gaskeun!")

@router.message(F.text == "/stat")
async def show_stats(message: types.Message):
    if not is_admin(message.from_user.id):
        return await message.reply("Akses ditolak.")

    users = get_all_users()
    total = len(users)
    await message.reply(f"📊 Jumlah total pengguna yang tersimpan di database: <b>{total}</b>", parse_mode="HTML")


@router.message(F.text == "/help_admin")
async def help_admin(message: types.Message):
    if not is_admin(message.from_user.id):
        return await message.reply("Khusus admin yaa.")

    help_text = (
        "✦ <b>Panel Admin SortFess</b>\n\n"
        "Berikut daftar command admin:\n"
        "• <code>/broadcast <pesan></code> — Kirim pesan ke semua user\n"
        "• <code>/balas <user_id> <pesan></code> — Balas DM user\n"
        "• <code>/tutup</code> — Menutup base\n"
        "• <code>/buka</code> — Membuka base\n"
        "• <code>/stat</code> — Lihat jumlah user\n"
        "• <code>/help_admin</code> — Tampilkan bantuan ini\n"
    )
    await message.reply(help_text, parse_mode="HTML")

@router.message(F.text.startswith("/ban"))
async def ban_cmd(message: types.Message):
    if not is_admin(message.from_user.id):
        return await message.reply("Akses ditolak.")

    parts = message.text.split()
    if len(parts) != 2 or not parts[1].isdigit():
        return await message.reply("Format: /ban <user_id>")

    uid = int(parts[1])
    ban_user(uid)
    await message.reply(f"User <code>{uid}</code> telah diblokir dari mengirim menfess.", parse_mode="HTML")

@router.message(F.text.startswith("/unban"))
async def unban_cmd(message: types.Message):
    if not is_admin(message.from_user.id):
        return await message.reply("Akses ditolak.")

    parts = message.text.split()
    if len(parts) != 2 or not parts[1].isdigit():
        return await message.reply("Format: /unban <user_id>")

    uid = int(parts[1])
    unban_user(uid)
    await message.reply(f"User <code>{uid}</code> telah diizinkan kembali mengirim menfess.", parse_mode="HTML")

@router.message(F.text == "/last10")
async def last_10_posters(message: types.Message):
    if not is_admin(message.from_user.id):
        return await message.reply("Akses ditolak.")

    posts = get_last_posts()
    if not posts:
        return await message.reply("Belum ada menfess terbaru.")

    result = "\n\n".join([f"<b>{uid}</b>:\n{text[:200]}" for uid, text in posts])
    await message.reply(f"🕵️‍♂️ Riwayat Pengirim Terakhir:\n\n{result}", parse_mode="HTML")

@router.message(F.text == "/tophashtag")
async def top_hashtag(message: types.Message):
    if not is_admin(message.from_user.id):
        return await message.reply("Akses ditolak.")

    top_tags = get_top_hashtags()
    if not top_tags:
        return await message.reply("Belum ada data hashtag.")

    msg = "\n".join([f"{i+1}. <b>{tag}</b> — {count}x" for i, (tag, count) in enumerate(top_tags)])
    await message.reply(f"🏷 <b>Hashtag Terpopuler:</b>\n\n{msg}", parse_mode="HTML")