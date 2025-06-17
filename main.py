import asyncio
import logging
import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from bot.handlers.basic import router as basic_router
from bot.handlers.newroute import router as newroute_router
from bot.handlers.routes import router as routes_router
from bot.handlers import routeweather
from bot.handlers.deleteroute import router as deleteroute_router
from db.db_session import init_db

# Загрузка переменных из .env
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

async def main():
    await init_db()
    logging.basicConfig(level=logging.INFO)

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    dp.include_router(routes_router)
    dp.include_router(basic_router)
    dp.include_router(newroute_router)
    dp.include_router(routeweather.router)
    dp.include_router(deleteroute_router)

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
