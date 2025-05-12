import asyncio
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from config import BOT_TOKEN
from handlers import start, menfess, admin

# Inisialisasi bot & dispatcher
bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

# Register semua routers dari handler
dp.include_router(start.router)
dp.include_router(menfess.router)
dp.include_router(admin.router)

async def main():
    print("Bot Sort Menfess berjalan ...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())