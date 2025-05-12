import asyncio
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from config import BOT_TOKEN
from handlers.start import router as start_router  # import router start
from handlers.menfess import router as menfess_router  # import router menfess
from handlers.admin import router as admin_router  # import router admin

# Inisialisasi bot & dispatcher
bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

# Register semua routers dari handler
dp.include_router(start_router)  # register start router
dp.include_router(menfess_router)  # register menfess router
dp.include_router(admin_router)  # register admin router

# Fungsi utama untuk menjalankan bot
async def main():
    print("Bot Sort Menfess berjalan ...")
    await dp.start_polling(bot)

# Menjalankan bot
if __name__ == "__main__":
    asyncio.run(main())
