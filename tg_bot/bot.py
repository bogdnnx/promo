import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

#from tg_bot.config import TELEGRAM_BOT_TOKEN
#from tg_bot.handlers import common, subscription
from config import TELEGRAM_BOT_TOKEN
from handlers import common, subscription
# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def main():
    """Запуск бота"""
    # Инициализация бота и диспетчера
    bot = Bot(
        token=TELEGRAM_BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()

    # Регистрация роутеров
    dp.include_router(common.router)
    dp.include_router(subscription.router)

    # Запуск бота
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())