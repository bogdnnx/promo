from unittest.mock import AsyncMock, Mock, patch

import pytest
from aiogram.types import Message, ReplyKeyboardMarkup, User

from tg_bot.handlers.common import cmd_start
from tg_bot.handlers.subscription import subscribe_to_notifications, unsubscribe_from_notifications


class TestBotHandlers:
    """Тесты для обработчиков бота"""

    @pytest.mark.asyncio
    async def test_cmd_start(self):
        """Тест команды /start"""
        message = Mock(spec=Message)
        message.answer = AsyncMock()

        await cmd_start(message)

        message.answer.assert_called_once()
        call_args = message.answer.call_args
        assert "Привет! Я бот для уведомлений" in call_args[0][0]
        assert call_args[1]["reply_markup"] is not None

    @pytest.mark.asyncio
    async def test_subscribe_to_notifications(self):
        """Тест подписки на уведомления"""
        message = Mock(spec=Message)
        message.from_user = Mock(spec=User)
        message.from_user.id = 123456789
        message.text = "📝 Подписаться на уведомления"
        message.answer = AsyncMock()

        with patch("tg_bot.handlers.subscription.load_subscribers", return_value=set()) as mock_load:
            with patch("tg_bot.handlers.subscription.save_subscribers") as mock_save:
                await subscribe_to_notifications(message)

                mock_save.assert_called_once()
                message.answer.assert_called_once_with("Вы подписались на уведомления о новых акциях и предложениях!")

    @pytest.mark.asyncio
    async def test_subscribe_to_notifications_existing_user(self):
        """Тест подписки уже подписанного пользователя"""
        message = Mock(spec=Message)
        message.from_user = Mock(spec=User)
        message.from_user.id = 123456789
        message.text = "📝 Подписаться на уведомления"
        message.answer = AsyncMock()

        with patch("tg_bot.handlers.subscription.load_subscribers", return_value={123456789}) as mock_load:
            with patch("tg_bot.handlers.subscription.save_subscribers") as mock_save:
                await subscribe_to_notifications(message)

                mock_save.assert_not_called()
                message.answer.assert_called_once_with("Вы уже подписаны на уведомления!")

    @pytest.mark.asyncio
    async def test_unsubscribe_from_notifications(self):
        """Тест отписки от уведомлений"""
        message = Mock(spec=Message)
        message.from_user = Mock(spec=User)
        message.from_user.id = 123456789
        message.text = "Отписаться от уведомлений"
        message.answer = AsyncMock()

        with patch("tg_bot.handlers.subscription.load_subscribers", return_value={123456789}) as mock_load:
            with patch("tg_bot.handlers.subscription.save_subscribers") as mock_save:
                await unsubscribe_from_notifications(message)

                mock_save.assert_called_once()
                message.answer.assert_called_once_with("Вы отписались от уведомлений о новых акциях и предложениях.")

    @pytest.mark.asyncio
    async def test_unsubscribe_from_notifications_non_existing_user(self):
        """Тест отписки несуществующего пользователя"""
        message = Mock(spec=Message)
        message.from_user = Mock(spec=User)
        message.from_user.id = 123456789
        message.text = "Отписаться от уведомлений"
        message.answer = AsyncMock()

        with patch("tg_bot.handlers.subscription.load_subscribers", return_value=set()) as mock_load:
            with patch("tg_bot.handlers.subscription.save_subscribers") as mock_save:
                await unsubscribe_from_notifications(message)

                mock_save.assert_not_called()
                message.answer.assert_called_once_with("Вы не были подписаны на уведомления!")
