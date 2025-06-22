import asyncio
from aiogram import F, Router
from aiogram.types import Message
from tg_bot.db_utils import load_subscribers, save_subscribers

router = Router()


@router.message(F.text == "📝 Подписаться на уведомления")
async def subscribe_to_notifications(message: Message):
    """Обработчик подписки на уведомления"""
    user_id = message.from_user.id
    subscribed_users = load_subscribers()

    if user_id in subscribed_users:
        await message.answer("Вы уже подписаны на уведомления!")
        return

    subscribed_users.add(user_id)
    save_subscribers(subscribed_users)
    await message.answer("Вы подписались на уведомления о новых акциях и предложениях!")


@router.message(F.text == "Отписаться от уведомлений")
async def unsubscribe_from_notifications(message: Message):
    """Обработчик отписки от уведомлений"""
    user_id = message.from_user.id
    subscribed_users = load_subscribers()

    if user_id not in subscribed_users:
        await message.answer("Вы не были подписаны на уведомления!")
        return

    subscribed_users.remove(user_id)
    save_subscribers(subscribed_users)
    await message.answer("Вы отписались от уведомлений о новых акциях и предложениях.")
