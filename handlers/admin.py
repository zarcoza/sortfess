from aiogram import Router, types, F
from config import ADMIN_ID
from db import get_all_users
from utils import set_post_status

router = Router()

@router.message(F.text.startswith("/broadcast"))
async def broadcast_handler(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return await message.reply("Kamu bukan admin, sayang.")
    msg = message.text.removeprefix("/broadcast").strip()
    if not msg:
        return await message.reply("Isi dulu dong pesannya.\nContoh: /broadcast Halo semua!")
    users = get_all_users()
    sent = failed = 0
    for uid in users:
        try:
            await message.bot.send_message(uid, f"📢 <b>Broadcast:</b>\n\n{msg}")
            sent += 1
        except:
            failed += 1
    await message.reply(f"Broadcast selesai!\n✅ Terkirim: {sent}\n❌ Gagal: {failed}")

@router.message(F.text.startswith("/balas"))
async def reply_user(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return await message.reply("Cuma admin yang bisa balas DM.")
    parts = message.text.split(maxsplit=2)
    if len(parts) < 3:
        return await message.reply("Format: /balas <user_id> <pesan>")
    user_id = int(parts[1])
    reply_msg = parts[2]
    await message.bot.send_message(user_id, f"👩‍💻 Admin:\n{reply_msg}")
    await message.reply("Pesan terkirim, mantap!")

@router.message(F.text.in_(["/tutup", "/buka"]))
async def toggle_post(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return await message.reply("Kamu ga punya akses, bestie.")
    if message.text == "/tutup":
        set_post_status(False)
        await message.reply("Base ditutup dulu yaa, istirahat dulu.")
    else:
        set_post_status(True)
        await message.reply("Base udah dibuka lagi, yuk lanjut!")