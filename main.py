import asyncio
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from config import BOT_TOKEN

# Import routers
from handlers.start import router as start_router
from handlers.menfess import router as menfess_router
from handlers.admin import router as admin_router

# Inisialisasi bot dan dispatcher
bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

# Daftarkan router
dp.include_router(start_router)
dp.include_router(menfess_router)
dp.include_router(admin_router)

# Fungsi utama
async def main():
    print("🤖 Bot Sort Menfess sedang berjalan...")
    try:
        await dp.start_polling(bot)
    except Exception as e:
        print(f"❌ Terjadi error saat polling: {e}")
    finally:
        await bot.session.close()

# Entry point
if __name__ == "__main__":
    asyncio.run(main())
