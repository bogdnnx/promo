import asyncio
import json
import time

from aiogram import Bot
from kafka import KafkaConsumer
from kafka.errors import NoBrokersAvailable

from tg_bot.config import TELEGRAM_BOT_TOKEN
from tg_bot.db_utils import get_all_subscribed_users


class TelegramKafkaConsumer:
    def __init__(self, _):
        print("Инициализация бота...")
        self.bot = Bot(token=TELEGRAM_BOT_TOKEN)
        print("Подключение к Kafka...")
        self.consumer = self._connect_to_kafka()
        print("Бот инициализирован")
        self.get_subscribers = get_all_subscribed_users

    def _connect_to_kafka(self, max_retries=30, retry_delay=1):
        """Подключение к Kafka с повторными попытками"""
        for attempt in range(max_retries):
            try:
                print(f"Попытка подключения к Kafka (попытка {attempt + 1}/{max_retries})...")
                consumer = KafkaConsumer(
                    'wal_listener.promo_categories',
                    'wal_listener.promo_offers',
                    'wal_listener.cities',
                    'wal_listener.partners',
                    bootstrap_servers='kafka:9092',
                    auto_offset_reset='earliest',
                    enable_auto_commit=True,
                    group_id='telegram_bot_group',
                    value_deserializer=lambda x: json.loads(x.decode('utf-8')),
                    session_timeout_ms=30000,
                    heartbeat_interval_ms=10000,
                    max_poll_interval_ms=300000,
                    request_timeout_ms=305000,
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
        action = data["action"]
        table = data["table"]

        print(f"Действие: {action}, Таблица: {table}")

        try:
            if table == "promo_category":
                if action == "INSERT":
                    return f"🆕 Новая категория: {data['data']['name']}"
                elif action == "UPDATE":
                    old_name = data.get("dataOld", {}).get("name", "")
                    new_name = data["data"]["name"]
                    return f"📝 Обновлена категория: {old_name} → {new_name}"
                elif action == "DELETE":
                    return f"❌ Удалена категория: {data.get('dataOld', {}).get('name', 'Неизвестная категория')}"

            elif table == "promo_offer":
                if action == "INSERT":
                    return f"🆕 Новое предложение: {data['data']['title']}"
                elif action == "UPDATE":
                    old_title = data.get("dataOld", {}).get("title", "")
                    new_title = data["data"]["title"]
                    return f"📝 Обновлено предложение: {old_title} → {new_title}"
                elif action == "DELETE":
                    return f"❌ Удалено предложение: {data.get('dataOld', {}).get('title', 'Неизвестное предложение')}"

            elif table == "promo_city":
                if action == "INSERT":
                    return f"🏙️ Новый город: {data['data']['name']}"
                elif action == "UPDATE":
                    old_name = data.get("dataOld", {}).get("name", "")
                    new_name = data["data"]["name"]
                    return f"📝 Обновлен город: {old_name} → {new_name}"
                elif action == "DELETE":
                    return f"❌ Удален город: {data.get('dataOld', {}).get('name', 'Неизвестный город')}"

            elif table == "promo_partner":
                if action == "INSERT":
                    return f"🤝 Новый партнер: {data['data']['name']}"
                elif action == "UPDATE":
                    old_name = data.get("dataOld", {}).get("name", "")
                    new_name = data["data"]["name"]
                    return f"📝 Обновлен партнер: {old_name} → {new_name}"
                elif action == "DELETE":
                    return f"❌ Удален партнер: {data.get('dataOld', {}).get('name', 'Неизвестный партнер')}"

            return f"Изменение в {table}: {action}"
        except Exception as e:
            print(f"Ошибка при форматировании сообщения: {e}")
            print(f"Данные сообщения: {data}")
            return f"Произошло изменение в {table}: {action}"

    async def process_messages(self):
        """Обработка сообщений из Kafka"""
        print("Начинаем обработку сообщений из Kafka...")
        print(f"Подключенные топики: {self.consumer.subscription()}")

        try:
            print("Ожидаем сообщения из Kafka...")
            while True:
                try:
                    # Получаем актуальный список подписчиков
                    subscribed_users = self.get_subscribers()  # get_all_subscribed_users()
                    print(f"Актуальные подписчики: {subscribed_users}")

                    # Получаем сообщения из Kafka
                    messages = self.consumer.poll(timeout_ms=1000)
                    print(f"Получено сообщений из Kafka: {len(messages)}")

                    for tp, msgs in messages.items():
                        print(f"Получены сообщения из топика {tp.topic}: {len(msgs)} сообщений")
                        for message in msgs:
                            try:
                                print(f"Получено сообщение: {message.value}")
                                formatted_message = await self.format_message(message)
                                print(f"Отформатированное сообщение: {formatted_message}")

                                # Отправляем сообщение всем подписанным пользователям
                                for user_id in subscribed_users:
                                    try:
                                        await self.bot.send_message(user_id, formatted_message)
                                        print(f"Сообщение отправлено пользователю {user_id}")
                                    except Exception as e:
                                        print(f"Ошибка отправки сообщения пользователю {user_id}: {e}")

                            except Exception as e:
                                print(f"Ошибка обработки сообщения: {e}")
                                print(f"Содержимое сообщения: {message.value}")

                    # Даем возможность другим задачам выполниться
                    await asyncio.sleep(0.1)

                except Exception as e:
                    print(f"Ошибка при получении сообщений: {e}")
                    # Пробуем переподключиться
                    try:
                        self.consumer = self._connect_to_kafka()
                    except Exception as reconnect_error:
                        print(f"Ошибка при переподключении: {reconnect_error}")
                        await asyncio.sleep(5)

        except asyncio.CancelledError:
            print("Получен сигнал отмены, завершаем работу...")
            raise
        except Exception as e:
            print(f"Ошибка при обработке сообщений: {e}")
            print(f"Тип ошибки: {type(e)}")
            import traceback

            print(f"Traceback: {traceback.format_exc()}")
