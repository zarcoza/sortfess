from aiogram import Router, types
from aiogram.filters import Command
from aiogram.exceptions import TelegramForbiddenError, TelegramBadRequest
from config import ADMIN_IDS
from db import (
    get_all_users, get_last_posts, get_top_hashtags,
    ban_user, unban_user, is_banned, latest_post,
    add_admin_id, remove_admin_id, get_admin_ids, get_username_by_id
)
from utils import set_post_status
import asyncio
import logging

router = Router()
admin_set = set(ADMIN_IDS)

def is_admin(user_id: int) -> bool:
    return user_id in admin_set


@router.message(Command("broadcast"))
async def broadcast_handler(message: types.Message):
    if not is_admin(message.from_user.id):
        return await message.reply("Kamu bukan admin, sayang 🤍")

    msg = message.text[len("/broadcast"):].strip()
    if not msg:
        return await message.reply("Isi dulu dong pesannya.\nContoh: /broadcast Halo semua!")

    users = get_all_users()
    total, sent, failed = len(users), 0, 0

    await message.reply("📤 Broadcast dimulai...")

    for uid in users:
        try:
            await message.bot.send_message(uid, f"📢 <b>Broadcast Admin:</b>\n\n{msg}", parse_mode="HTML")
            sent += 1
            await asyncio.sleep(0.05)
        except (TelegramForbiddenError, TelegramBadRequest):
            failed += 1
        except Exception as e:
            logging.error(f"Gagal kirim ke {uid}: {e}")
            failed += 1

    await message.reply(
        f"📣 Broadcast selesai!\n"
        f"👥 Total user: {total}\n"
        f"✅ Berhasil: {sent}\n"
        f"❌ Gagal: {failed}"
    )


@router.message(Command("balas"))
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
        await message.reply(f"❌ Gagal kirim pesan ke user.\n<code>{e}</code>", parse_mode="HTML")


@router.message(Command("tutup"))
async def tutup_base(message: types.Message):
    if not is_admin(message.from_user.id):
        return await message.reply("Kamu ga punya akses, bestie.")

    set_post_status(False)
    await message.reply("✋ Base ditutup dulu yaa, istirahat sejenak.")


@router.message(Command("buka"))
async def buka_base(message: types.Message):
    if not is_admin(message.from_user.id):
        return await message.reply("Kamu ga punya akses, bestie.")

    set_post_status(True)
    await message.reply("✅ Base sudah dibuka lagi, gaskeun!")


@router.message(Command("stat"))
async def show_stats(message: types.Message):
    if not is_admin(message.from_user.id):
        return await message.reply("Akses ditolak.")

    total = len(get_all_users())
    await message.reply(f"📊 Jumlah total pengguna: <b>{total}</b>", parse_mode="HTML")


@router.message(Command("help_admin"))
async def help_admin(message: types.Message):
    if not is_admin(message.from_user.id):
        return await message.reply("Khusus admin yaa.")

    help_text = (
        "✦ <b>Panel Admin SortFess</b>\n\n"
        "📌 Daftar perintah admin:\n"
        "• <code>/broadcast <pesan></code> — Kirim pesan ke semua user\n"
        "• <code>/balas <user_id> <pesan></code> — Balas DM user\n"
        "• <code>/tutup</code> — Menutup base\n"
        "• <code>/buka</code> — Membuka base\n"
        "• <code>/stat</code> — Lihat jumlah user\n"
        "• <code>/last10</code> — Riwayat pengirim terakhir\n"
        "• <code>/tophashtag</code> — Tag paling sering digunakan\n"
        "• <code>/ban <user_id></code> — Blokir user\n"
        "• <code>/unban <user_id></code> — Buka blokir user\n"
        "• <code>/user <user_id></code> — Cek status user\n"
        "• <code>/setstatus buka|tutup</code> — Atur status base\n"
        "• <code>/listban</code> — Lihat daftar user terblokir\n"
        "• <code>/cekaktif</code> — Aktivitas user terakhir\n"
        "• <code>/addadmin <user_id></code> — Tambah admin\n"
        "• <code>/deladmin <user_id></code> — Hapus admin"
    )
    await message.reply(help_text, parse_mode="HTML")


@router.message(Command("ban"))
async def ban_cmd(message: types.Message):
    if not is_admin(message.from_user.id):
        return await message.reply("Akses ditolak.")

    parts = message.text.split()
    if len(parts) != 2 or not parts[1].isdigit():
        return await message.reply("Format: /ban <user_id>")

    uid = int(parts[1])
    ban_user(uid)
    await message.reply(f"🚫 User <code>{uid}</code> telah diblokir.", parse_mode="HTML")


@router.message(Command("unban"))
async def unban_cmd(message: types.Message):
    if not is_admin(message.from_user.id):
        return await message.reply("Akses ditolak.")

    parts = message.text.split()
    if len(parts) != 2 or not parts[1].isdigit():
        return await message.reply("Format: /unban <user_id>")

    uid = int(parts[1])
    unban_user(uid)
    await message.reply(f"✅ User <code>{uid}</code> telah diizinkan kembali.", parse_mode="HTML")


@router.message(Command("last10"))
async def last_10_posters(message: types.Message):
    if not is_admin(message.from_user.id):
        return await message.reply("Akses ditolak.")

    posts = get_last_posts()
    if not posts:
        return await message.reply("Belum ada menfess terbaru.")

    result = "\n\n".join([f"<b>{uid}</b>:\n{text[:200]}" for uid, text in posts])
    await message.reply(f"🕵️‍♂️ Riwayat Pengirim Terakhir:\n\n{result}", parse_mode="HTML")


@router.message(Command("tophashtag"))
async def top_hashtag(message: types.Message):
    if not is_admin(message.from_user.id):
        return await message.reply("Akses ditolak.")

    top_tags = get_top_hashtags()
    if not top_tags:
        return await message.reply("Belum ada data hashtag.")

    msg = "\n".join([f"{i+1}. <b>{tag}</b> — {count}x" for i, (tag, count) in enumerate(top_tags)])
    await message.reply(f"🏷 <b>Hashtag Terpopuler:</b>\n\n{msg}", parse_mode="HTML")

@router.message(Command("addadmin"))
async def add_admin_cmd(message: types.Message):
    if not is_admin(message.from_user.id):
        return await message.reply("Akses ditolak.")

    parts = message.text.split()
    if len(parts) != 2 or not parts[1].isdigit():
        return await message.reply("Format: /addadmin <user_id>")

    uid = int(parts[1])
    add_admin_id(uid)
    admin_set.add(uid)
    await message.reply(f"✅ User <code>{uid}</code> sekarang adalah admin.", parse_mode="HTML")

@router.message(Command("deladmin"))
async def del_admin_cmd(message: types.Message):
    if not is_admin(message.from_user.id):
        return await message.reply("Akses ditolak.")

    parts = message.text.split()
    if len(parts) != 2 or not parts[1].isdigit():
        return await message.reply("Format: /deladmin <user_id>")

    uid = int(parts[1])
    remove_admin_id(uid)
    admin_set.discard(uid)
    await message.reply(f"🗑️ User <code>{uid}</code> telah dihapus dari admin.", parse_mode="HTML")
