# import asyncio
# import logging
# from aiogram import Bot, Dispatcher, types
# from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
# from aiogram.filters import Command
# from tg_bot.config import TELEGRAM_BOT_TOKEN
# from tg_bot.db_utils import get_all_subscribed_users
# from tg_bot.kafka_consumer import TelegramKafkaConsumer
# from tg_bot.keyboards.reply import get_main_keyboard
# import os
#
# # Настройка логирования
# logging.basicConfig(level=logging.INFO)
#
# # Инициализация бота и диспетчера
# bot = Bot(token=TELEGRAM_BOT_TOKEN)
# dp = Dispatcher()
#
# # Глобальный список подписанных пользователей
# subscribed_users = set()
#
#
# # Обработчик команды /start
# @dp.message(Command("start"))
# async def cmd_start(message: types.Message):
#     keyboard = get_main_keyboard()
#     await message.answer(
#         "Привет! Я бот для уведомлений об изменениях в категориях и предложениях.\n"
#         "Нажмите кнопку ниже, чтобы подписаться на уведомления.",
#         reply_markup=keyboard
#     )
#
#
# # Обработчик нажатия на кнопку подписки
# @dp.message(lambda message: message.text == "📝 Подписаться на уведомления")
# async def subscribe_to_notifications(message: types.Message):
#     user_id = message.from_user.id
#     if user_id in subscribed_users:
#         await message.answer("Вы уже подписаны на уведомления!")
#     else:
#         subscribed_users.add(user_id)
#         await message.answer("Вы успешно подписались на уведомления!")
#
#
# # async def main():
# #     # Инициализация Kafka consumer
# #     kafka_consumer = TelegramKafkaConsumer(subscribed_users)
# #
# #     # Создаем задачи
# #     polling_task = asyncio.create_task(dp.start_polling(bot))
# #     kafka_task = asyncio.create_task(kafka_consumer.process_messages())
# #
# #     try:
# #         # Запускаем оба процесса параллельно
# #         await asyncio.gather(polling_task, kafka_task)
# #     except asyncio.CancelledError:
# #         # Обработка отмены задач
# #         polling_task.cancel()
# #         kafka_task.cancel()
# #         await asyncio.gather(polling_task, kafka_task, return_exceptions=True)
# #     finally:
# #         # Закрываем соединения
# #         await bot.session.close()
# #         kafka_consumer.consumer.close()
# #
# #
# # if __name__ == '__main__':
# #     try:
# #         asyncio.run(main())
# #     except KeyboardInterrupt:
# #         print("Бот остановлен")
#
#
# async def main():
#     # Получаем список всех подписчиков из базы данных
#     subscribed_users = get_all_subscribed_users()
#     print(f"Загружено подписчиков из БД: {len(subscribed_users)}")
#
#     # Инициализация Kafka consumer
#     kafka_consumer = TelegramKafkaConsumer(subscribed_users)
#
#     # Создаем задачи
#     polling_task = asyncio.create_task(dp.start_polling(bot))
#     kafka_task = asyncio.create_task(kafka_consumer.process_messages())
#
#     try:
#         # Запускаем оба процесса параллельно
#         await asyncio.gather(polling_task, kafka_task)
#     except asyncio.CancelledError:
#         # Обработка отмены задач
#         polling_task.cancel()
#         kafka_task.cancel()
#         await asyncio.gather(polling_task, kafka_task, return_exceptions=True)
#     finally:
#         # Закрываем соединения
#         await bot.session.close()
#         kafka_consumer.consumer.close()
#
#
# if __name__ == '__main__':
#     try:
#         asyncio.run(main())
#     except KeyboardInterrupt:
#         print("Бот остановлен")

import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from tg_bot.config import TELEGRAM_BOT_TOKEN
from tg_bot.db_utils import get_all_subscribed_users
from tg_bot.kafka_consumer import TelegramKafkaConsumer
from tg_bot.keyboards.reply import get_main_keyboard
from dotenv import load_dotenv
import os
from tg_bot.db_utils import load_subscribers, save_subscribers, get_all_subscribed_users


SUBSCRIBERS_FILE = "subscribers.txt"


subscribed_users = load_subscribers()

load_dotenv()  # чтобы переменные из .env подхватились

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    keyboard = get_main_keyboard()
    await message.answer(
        "Привет! Я бот для уведомлений об изменениях в категориях и предложениях.",
        reply_markup=keyboard
    )

# Можно убрать обработчики подписки/отписки или оставить заглушки
@dp.message(lambda message: message.text == "📝 Подписаться на уведомления")
async def subscribe_to_notifications(message: types.Message):
    user_id = message.from_user.id
    if user_id in subscribed_users:
        await message.answer("Вы уже подписаны на уведомления!")
    else:
        subscribed_users.add(user_id)
        save_subscribers(subscribed_users)
        await message.answer("Вы успешно подписались на уведомления!")

@dp.message(lambda message: message.text == "❌ Отписаться от уведомлений")
async def unsubscribe_from_notifications(message: types.Message):
    user_id = message.from_user.id
    if user_id not in subscribed_users:
        await message.answer("Вы не были подписаны на уведомления.")
    else:
        subscribed_users.remove(user_id)
        save_subscribers(subscribed_users)
        await message.answer("Вы успешно отписались от уведомлений.")


async def main():
    subscribed_users = get_all_subscribed_users()
    print(f"Загружено подписчиков из .env: {subscribed_users}")

    kafka_consumer = TelegramKafkaConsumer(subscribed_users)

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

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот остановлен")