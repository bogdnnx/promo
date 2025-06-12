import asyncio
from datetime import datetime
from aiogram import Bot

async def send_periodic_message(bot: Bot, user_id: int):
    """Отправка периодических сообщений"""
    while True:
        try:
            current_time = datetime.now().strftime("%H:%M:%S")
            await bot.send_message(
                user_id,
                f"Тестовое сообщение! Текущее время: {current_time}"
            )
            await asyncio.sleep(10)  # Пауза 10 секунд
        except Exception as e:
            print(f"Ошибка при отправке сообщения: {e}")
            await asyncio.sleep(10)