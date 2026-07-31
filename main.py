import asyncio
import logging
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from database.db import init_db
from handlers import common, cards, quiz
from services.scheduler import setup_scheduler

# Настройка логирования
logging.basicConfig(level=logging.INFO)

async def main():
    if not BOT_TOKEN or BOT_TOKEN == "YOUR_TELEGRAM_BOT_TOKEN_HERE":
        print("❌ Ошибка: Укажите корректный BOT_TOKEN в файле .env!")
        return

    # Инициализация базы данных
    await init_db()

    # Инициализация бота и диспетчера
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    # Регистрация роутеров
    dp.include_router(common.router)
    dp.include_router(cards.router)
    dp.include_router(quiz.router)

    # Настройка APScheduler для ежедневных напоминаний
    scheduler = setup_scheduler(bot)
    scheduler.start()

    print("🚀 Telegram-бот для изучения английского языка успешно запущен!")
    
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
