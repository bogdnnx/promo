from aiogram import Router, F
from aiogram.types import Message
import asyncio
from tg_bot.utils.scheduler import send_periodic_message

router = Router()

# Временное хранилище подписок (потом заменим на базу данных)
subscribed_users = set()


@router.message(F.text == "📝 Подписаться на уведомления")
async def subscribe(message: Message):
    """Обработчик подписки на уведомления"""
    user_id = message.from_user.id

    if user_id in subscribed_users:
        await message.answer("Вы уже подписаны на уведомления!")
        return

    subscribed_users.add(user_id)
    await message.answer(
        "Вы подписались на уведомления о новых акциях и предложениях!"
    )


@router.message(F.text == "Отписаться от уведомлений")
async def unsubscribe(message: Message):
    """Обработчик отписки от уведомлений"""
    user_id = message.from_user.id

    if user_id not in subscribed_users:
        await message.answer("Вы не были подписаны на уведомления!")
        return

    subscribed_users.remove(user_id)
    await message.answer(
        "Вы отписались от уведомлений о новых акциях и предложениях."
    )