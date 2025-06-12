import json
import asyncio
import time
from kafka import KafkaConsumer
from kafka.errors import NoBrokersAvailable
from aiogram import Bot
from tg_bot.config import TELEGRAM_BOT_TOKEN


class TelegramKafkaConsumer:
    def __init__(self, subscribed_users):
        print("Инициализация бота...")
        self.bot = Bot(token=TELEGRAM_BOT_TOKEN)
        self.subscribed_users = subscribed_users
        print(f"Подписанные пользователи: {self.subscribed_users}")

        print("Подключение к Kafka...")
        self.consumer = self._connect_to_kafka()
        print("Бот инициализирован")

    def _connect_to_kafka(self, max_retries=30, retry_delay=1):
        """Подключение к Kafka с повторными попытками"""
        for attempt in range(max_retries):
            try:
                print(f"Попытка подключения к Kafka (попытка {attempt + 1}/{max_retries})...")
                consumer = KafkaConsumer(
                    'wal_listener.promo_categories',
                    'wal_listener.promo_offers',
                    bootstrap_servers='kafka:9092',
                    auto_offset_reset='latest',
                    enable_auto_commit=True,
                    group_id='telegram_bot_group',
                    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
                )
                print("Успешное подключение к Kafka!")
                return consumer
            except NoBrokersAvailable:
                if attempt < max_retries - 1:
                    print(f"Не удалось подключиться к Kafka. Повторная попытка через {retry_delay} секунд...")
                    time.sleep(retry_delay)
                else:
                    print("Превышено максимальное количество попыток подключения к Kafka")
                    raise

    async def format_message(self, message):
        """Форматирование сообщения для Telegram"""
        print(f"Форматирование сообщения: {message.value}")
        data = message.value
        action = data['action']
        table = data['table']

        print(f"Действие: {action}, Таблица: {table}")

        if table == 'promo_category':
            if action == 'INSERT':
                return f"🆕 Новая категория: {data['data']['name']}"
            elif action == 'UPDATE':
                return f"📝 Обновлена категория: {data['data']['name']}"
            elif action == 'DELETE':
                return f"❌ Удалена категория: {data['data']['name']}"

        elif table == 'promo_offer':
            if action == 'INSERT':
                return f"🆕 Новое предложение: {data['data']['title']}"
            elif action == 'UPDATE':
                return f"📝 Обновлено предложение: {data['data']['title']}"
            elif action == 'DELETE':
                return f"❌ Удалено предложение: {data['data']['title']}"

        # elif table == 'promo_city':
        #     if action == 'INSERT':
        #         return f"🏙️ Новый город: {data['data']['name']}"
        #     elif action == 'UPDATE':
        #         return f"📝 Обновлен город: {data['data']['name']}"
        #     elif action == 'DELETE':
        #         return f"❌ Удален город: {data['data']['name']}"
        #
        # elif table == 'promo_partner':
        #     if action == 'INSERT':
        #         return f"🤝 Новый партнер: {data['data']['name']}"
        #     elif action == 'UPDATE':
        #         return f"📝 Обновлен партнер: {data['data']['name']}"
        #     elif action == 'DELETE':
        #         return f"❌ Удален партнер: {data['data']['name']}"


        return f"Изменение в {table}: {action}"

    async def process_messages(self):
        """Обработка сообщений из Kafka"""
        print("Начинаем обработку сообщений из Kafka...")
        print(f"Подписанные пользователи: {self.subscribed_users}")

        try:
            print("Ожидаем сообщения из Kafka...")
            while True:
                # Получаем сообщения из Kafka
                messages = self.consumer.poll(timeout_ms=1000)

                for tp, msgs in messages.items():
                    print(f"Получены сообщения из топика {tp.topic}")
                    for message in msgs:
                        print(f"Получено сообщение: {message.value}")
                        formatted_message = await self.format_message(message)
                        print(f"Отформатированное сообщение: {formatted_message}")

                        # Отправляем сообщение всем подписанным пользователям
                        for user_id in self.subscribed_users:
                            try:
                                await self.bot.send_message(user_id, formatted_message)
                                print(f"Сообщение отправлено пользователю {user_id}")
                            except Exception as e:
                                print(f"Ошибка отправки сообщения пользователю {user_id}: {e}")

                # Даем возможность другим задачам выполниться
                await asyncio.sleep(0.1)

        except asyncio.CancelledError:
            print("Получен сигнал отмены, завершаем работу...")
            raise
        except Exception as e:
            print(f"Ошибка при обработке сообщений: {e}")
            print(f"Тип ошибки: {type(e)}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")