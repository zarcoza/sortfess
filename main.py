import asyncio
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from config import BOT_TOKEN

# Import router dari handler
from handlers.start import router as start_router
from handlers.menfess import router as menfess_router
from handlers.admin import router as admin_router

# Inisialisasi bot dan dispatcher
bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

# Register semua routers
dp.include_router(start_router)
dp.include_router(menfess_router)
dp.include_router(admin_router)

# Fungsi utama menjalankan bot
async def main():
    print("🤖 Bot Sort Menfess sedang berjalan...")
    try:
        await dp.start_polling(bot, polling_timeout=30)  # polling timeout untuk hindari spam getUpdates
    except Exception as e:
        print(f"❌ Error saat polling: {e}")
        await bot.session.close()  # pastikan sesi bot ditutup dengan baik

# Menjalankan bot
if __name__ == "__main__":
    asyncio.run(main())
