from aiogram import Router, types
from aiogram.filters import Command
from aiogram.exceptions import TelegramForbiddenError, TelegramBadRequest
from db import (
    get_all_users, get_last_posts, get_top_hashtags,
    ban_user, unban_user, is_banned, latest_post,
    add_admin_id, remove_admin_id, get_admin_ids, get_user_by_id,
    get_all_banned_users  # ✅ diperbaiki dari get_banned_users
)
from utils import set_post_status
import asyncio
import logging
import html

router = Router()
admin_set = set(get_admin_ids())

def is_admin(user_id: int) -> bool:
    return user_id in admin_set

def extract_user_id_arg(message: types.Message):
    parts = message.text.split()
    return int(parts[1]) if len(parts) == 2 and parts[1].isdigit() else None

@router.message(Command(commands=["broadcast", "stat", "ban", "unban", "addadmin", "deladmin"]))
async def log_admin_command(message: types.Message):
    logging.info(f"[ADMIN CMD] {message.from_user.id} -> {message.text}")

@router.message(Command("broadcast"))
async def broadcast_handler(message: types.Message):
    if not is_admin(message.from_user.id):
        return await message.reply(f"Maaf, kamu bukan admin.\nID kamu: <code>{message.from_user.id}</code>", parse_mode="HTML")

    msg = message.text[len("/broadcast"):].strip()
    if not msg:
        return await message.reply("Isi dulu dong pesannya.\nContoh: /broadcast Halo semua!")

    users = get_all_users()
    total, sent, failed = len(users), 0, 0

    await message.reply(f"📤 Broadcast dimulai ke {total} user...")

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
        f"✅ Terkirim: {sent}\n"
        f"❌ Gagal: {failed}"
    )

@router.message(Command("balas"))
async def reply_user(message: types.Message):
    if not is_admin(message.from_user.id):
        return await message.reply(f"❌ Kamu bukan admin.\nID kamu: <code>{message.from_user.id}</code>", parse_mode="HTML")

    parts = message.text.split(maxsplit=2)
    if len(parts) < 3:
        return await message.reply("❗ Format salah.\nGunakan: /balas <user_id> <pesan>")

    try:
        user_id = int(parts[1])
        reply_msg = parts[2]
        await message.bot.send_message(user_id, f"👩‍💻 <b>Balasan Admin:</b>\n\n{reply_msg}", parse_mode="HTML")
        await message.reply("✅ Pesan berhasil dikirim!")
    except TelegramForbiddenError:
        await message.reply("❌ Gagal kirim. User mungkin telah memblokir bot.")
    except TelegramBadRequest:
        await message.reply("❌ Gagal kirim. Mungkin user_id tidak valid.")
    except Exception as e:
        await message.reply(f"⚠️ Terjadi error:\n<code>{e}</code>", parse_mode="HTML")

@router.message(Command("tutup"))
async def tutup_base(message: types.Message):
    if is_admin(message.from_user.id):
        set_post_status(False)
        await message.reply("🔒 <b>Base ditutup sementara.</b>\nLagi istirahat dulu yaa~ 😴", parse_mode="HTML")

@router.message(Command("buka"))
async def buka_base(message: types.Message):
    if is_admin(message.from_user.id):
        set_post_status(True)
        await message.reply("✅ <b>Base sudah dibuka lagi!</b>\nSilakan kirim menfess sekarang ya! 🚀", parse_mode="HTML")

@router.message(Command("stat"))
async def show_stats(message: types.Message):
    if is_admin(message.from_user.id):
        total = len(get_all_users())
        await message.reply(f"📊 <b>Statistik Pengguna</b>\n👥 Total pengguna terdaftar: <b>{total}</b>", parse_mode="HTML")

@router.message(Command("ban"))
async def ban_cmd(message: types.Message):
    if is_admin(message.from_user.id):
        uid = extract_user_id_arg(message)
        if uid is None:
            return await message.reply("❗ Format salah.\nContoh: <code>/ban 123456789</code>", parse_mode="HTML")
        if uid == message.from_user.id:
            return await message.reply("⚠️ Kamu tidak bisa blokir diri sendiri 😅")
        ban_user(uid)
        await message.reply(f"🚫 User <code>{uid}</code> telah diblokir.", parse_mode="HTML")

@router.message(Command("unban"))
async def unban_cmd(message: types.Message):
    if is_admin(message.from_user.id):
        uid = extract_user_id_arg(message)
        if uid is None:
            return await message.reply("❗ Format salah.\nContoh: <code>/unban 123456789</code>", parse_mode="HTML")
        unban_user(uid)
        await message.reply(f"✅ User <code>{uid}</code> sudah tidak diblokir lagi.", parse_mode="HTML")

@router.message(Command("listban"))
async def list_banned_users(message: types.Message):
    if is_admin(message.from_user.id):
        banned = get_all_banned_users()  # ✅ ganti dari get_banned_users()
        if not banned:
            return await message.reply("✅ Tidak ada user yang sedang diblokir.")
        text = "🚫 <b>Daftar User Terblokir:</b>\n" + "\n".join([f"• <code>{uid}</code>" for uid in banned])
        await message.reply(text, parse_mode="HTML")

@router.message(Command("last10"))
async def last_10_posters(message: types.Message):
    if is_admin(message.from_user.id):
        posts = get_last_posts()
        if not posts:
            return await message.reply("ℹ️ Belum ada menfess terbaru.")
        result_lines = [
            f"👤 <b>{uid}</b>:\n{html.escape(text[:200]) + '...' if len(text) > 200 else html.escape(text)}"
            for uid, text in posts
        ]
        await message.reply("🕵️‍♂️ <b>Riwayat Pengirim Terakhir:</b>\n\n" + "\n\n".join(result_lines), parse_mode="HTML")

@router.message(Command("addadmin"))
async def add_admin_cmd(message: types.Message):
    if is_admin(message.from_user.id):
        uid = extract_user_id_arg(message)
        if uid is None:
            return await message.reply("Format: /addadmin <user_id>")
        if is_admin(uid):
            return await message.reply(f"⚠️ User <code>{uid}</code> sudah menjadi admin.", parse_mode="HTML")
        add_admin_id(uid)
        admin_set.add(uid)
        await message.reply(f"✅ User <code>{uid}</code> telah ditambahkan sebagai admin.", parse_mode="HTML")

@router.message(Command("deladmin"))
async def del_admin_cmd(message: types.Message):
    if is_admin(message.from_user.id):
        uid = extract_user_id_arg(message)
        if uid is None:
            return await message.reply("Format: /deladmin <user_id>")
        if not is_admin(uid):
            return await message.reply(f"⚠️ User <code>{uid}</code> bukan admin.", parse_mode="HTML")
        remove_admin_id(uid)
        admin_set.discard(uid)
        await message.reply(f"🗑️ User <code>{uid}</code> telah dihapus dari admin.", parse_mode="HTML")

@router.message(Command("listadmin"))
async def list_admin_cmd(message: types.Message):
    if is_admin(message.from_user.id):
        if not admin_set:
            return await message.reply("Belum ada admin terdaftar.")
        result = []
        for uid in sorted(admin_set):
            user = get_user_by_id(uid)
            line = f"• <code>{uid}</code>"
            if user:
                name = user.get("name", "Tidak diketahui")
                username = user.get("username")
                line = f"• <b>{name}</b> <code>{uid}</code>"
                if username:
                    line += f" [<i>@{username}</i>]"
            result.append(line)
        await message.reply("👑 <b>Daftar Admin Aktif:</b>\n\n" + "\n".join(result), parse_mode="HTML")

@router.message(Command("help_admin"))
async def help_admin(message: types.Message):
    if not is_admin(message.from_user.id):
        return await message.reply("🚫 Khusus admin yaa.")
    help_text = (
        "📖 <b>Panel Bantuan Admin — SortFess</b>\n\n"
        "🔊 <b>Broadcast & Balas</b>\n"
        "• <code>/broadcast &lt;pesan&gt;</code>\n"
        "• <code>/balas &lt;user_id&gt; &lt;pesan&gt;</code>\n\n"
        "🚪 <b>Kontrol Base</b>\n"
        "• <code>/tutup</code> / <code>/buka</code>\n\n"
        "📊 <b>Statistik</b>\n"
        "• <code>/stat</code>\n"
        "• <code>/last10</code>\n\n"
        "🔒 <b>Manajemen Pengguna</b>\n"
        "• <code>/ban &lt;user_id&gt;</code> / <code>/unban &lt;user_id&gt;</code>\n"
        "• <code>/listban</code>\n\n"
        "🛡 <b>Manajemen Admin</b>\n"
        "• <code>/addadmin &lt;user_id&gt;</code>\n"
        "• <code>/deladmin &lt;user_id&gt;</code>\n"
        "• <code>/listadmin</code>\n"
    )
    await message.reply(help_text, parse_mode="HTML")
