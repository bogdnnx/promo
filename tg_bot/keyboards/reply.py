from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_main_keyboard() -> ReplyKeyboardMarkup:
    """Создает основную клавиатуру"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="📝 Подписаться на уведомления"),
                KeyboardButton(text="❌ Отписаться от уведомлений")
            ],
            [
                KeyboardButton(text="ℹ️ Помощь")
            ]
        ],
        resize_keyboard=True
    )
    return keyboard