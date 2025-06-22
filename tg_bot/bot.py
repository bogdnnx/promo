import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from dotenv import load_dotenv

from tg_bot.config import TELEGRAM_BOT_TOKEN
from tg_bot.db_utils import get_all_subscribed_users, load_subscribers, save_subscribers
from tg_bot.handlers.common import router as common_router
from tg_bot.handlers.subscription import router as subscription_router
from tg_bot.kafka_consumer import TelegramKafkaConsumer
from tg_bot.keyboards.reply import get_main_keyboard

SUBSCRIBERS_FILE = "subscribers.txt"

subscribed_users = load_subscribers()

load_dotenv()  # чтобы переменные из .env подхватились

logging.basicConfig(level=logging.INFO)

# Получаем токен из переменных окружения
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN не найден в переменных окружения")


async def main():
    """Основная функция запуска бота"""
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    dp = Dispatcher()

    # Подключаем роутеры
    dp.include_router(common_router)
    dp.include_router(subscription_router)

    print("Бот запущен...")
    
    # Инициализируем Kafka consumer
    kafka_consumer = TelegramKafkaConsumer(subscribed_users)
    
    # Запускаем обе задачи параллельно
    polling_task = asyncio.create_task(dp.start_polling(bot))
    kafka_task = asyncio.create_task(kafka_consumer.process_messages())
    
    try:
        await asyncio.gather(polling_task, kafka_task)
    except asyncio.CancelledError:
        polling_task.cancel()
        kafka_task.cancel()
        await asyncio.gather(polling_task, kafka_task, return_exceptions=True)
    finally:
        await bot.session.close()
        kafka_consumer.consumer.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот остановлен")
