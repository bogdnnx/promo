import pytest
from unittest.mock import Mock
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from tg_bot.keyboards import get_main_keyboard


class TestKeyboards:
    """Тесты для клавиатур"""

    def test_get_main_keyboard(self):
        """Тест создания основной клавиатуры"""
        keyboard = get_main_keyboard()
        
        assert isinstance(keyboard, ReplyKeyboardMarkup)
        assert len(keyboard.keyboard) == 2
        
        # Проверяем первую строку (2 кнопки)
        first_row = keyboard.keyboard[0]
        assert len(first_row) == 2
        assert isinstance(first_row[0], KeyboardButton)
        assert isinstance(first_row[1], KeyboardButton)
        assert first_row[0].text == "📝 Подписаться на уведомления"
        assert first_row[1].text == "Отписаться от уведомлений"
        
        # Проверяем вторую строку (1 кнопка)
        second_row = keyboard.keyboard[1]
        assert len(second_row) == 1
        assert isinstance(second_row[0], KeyboardButton)
        assert second_row[0].text == "ℹ️ Помощь"

    def test_keyboard_button_texts(self):
        """Тест текстов кнопок клавиатуры"""
        keyboard = get_main_keyboard()
        
        # Проверяем все тексты кнопок
        all_buttons = []
        for row in keyboard.keyboard:
            for button in row:
                all_buttons.append(button.text)
        
        expected_texts = [
            "📝 Подписаться на уведомления",
            "Отписаться от уведомлений",
            "ℹ️ Помощь"
        ]
        
        assert all_buttons == expected_texts

    def test_keyboard_structure(self):
        """Тест структуры клавиатуры"""
        keyboard = get_main_keyboard()
        
        # Проверяем, что клавиатура имеет правильную структуру
        assert keyboard.resize_keyboard is True
        assert keyboard.one_time_keyboard is None
        assert keyboard.selective is None
        
        # Проверяем количество строк и кнопок
        assert len(keyboard.keyboard) == 2
        assert len(keyboard.keyboard[0]) == 2  # Первая строка: 2 кнопки
        assert len(keyboard.keyboard[1]) == 1  # Вторая строка: 1 кнопка

    def test_keyboard_button_types(self):
        """Тест типов кнопок клавиатуры"""
        keyboard = get_main_keyboard()
        
        # Проверяем, что все кнопки имеют правильный тип
        for row in keyboard.keyboard:
            for button in row:
                assert isinstance(button, KeyboardButton)
                assert hasattr(button, 'text')
                assert button.text is not None
                assert len(button.text) > 0 