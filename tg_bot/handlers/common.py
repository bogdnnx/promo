from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command

from keyboards.reply import get_main_keyboard

router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message):
    """Обработчик команды /start"""
    await message.answer(
        "Привет! Я бот для уведомлений о новых акциях и предложениях.",
        reply_markup=get_main_keyboard()
    )


@router.message(Command("help"))
async def cmd_help(message: Message):
    """Обработчик команды /help"""
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