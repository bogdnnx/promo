from aiogram import Router, F
from aiogram.types import Message
import asyncio
from utils.scheduler import send_periodic_message

router = Router()

# Словарь для хранения активных задач
active_tasks = {}


@router.message(F.text == "📝 Подписаться на уведомления")
async def subscribe(message: Message):
    """Обработчик подписки на уведомления"""
    user_id = message.from_user.id

    # Проверяем, не подписан ли уже пользователь
    if user_id in active_tasks:
        await message.answer("Вы уже подписаны на уведомления!")
        return

    # Создаем новую задачу для пользователя
    task = asyncio.create_task(
        send_periodic_message(message.bot, user_id)
    )
    active_tasks[user_id] = task

    await message.answer(
        "Вы подписались на уведомления о новых акциях и предложениях!"
    )


@router.message(F.text == "❌ Отписаться от уведомлений")
async def unsubscribe(message: Message):
    """Обработчик отписки от уведомлений"""
    user_id = message.from_user.id

    # Проверяем, подписан ли пользователь
    if user_id not in active_tasks:
        await message.answer("Вы не были подписаны на уведомления!")
        return

    # Отменяем задачу
    task = active_tasks.pop(user_id)
    task.cancel()

    try:
        await task
    except asyncio.CancelledError:
        pass

    await message.answer(
        "Вы отписались от уведомлений о новых акциях и предложениях."
    )


@router.message(F.text == "ℹ️ Помощь")
async def help_button(message: Message):
    """Обработчик кнопки помощи"""
    help_text = """
    Доступные команды:
    /start - Начать работу с ботом
    /help - Показать это сообщение

    Кнопки:
    📝 Подписаться на уведомления - Подписаться на уведомления
    ❌ Отписаться от уведомлений - Отписаться от уведомлений
    ℹ️ Помощь - Показать это сообщение
    """
    await message.answer(help_text)