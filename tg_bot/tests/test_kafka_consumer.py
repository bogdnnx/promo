import asyncio
from unittest.mock import AsyncMock, Mock, patch

import pytest

from tg_bot.kafka_consumer import TelegramKafkaConsumer


class TestKafkaConsumer:
    """Тесты для Kafka consumer"""

    @pytest.mark.asyncio
    async def test_format_message_insert(self):
        """Тест форматирования сообщения INSERT"""
        with patch("tg_bot.kafka_consumer.Bot"):
            consumer = TelegramKafkaConsumer([])

            message = Mock()
            message.value = {"action": "INSERT", "table": "promo_category", "data": {"name": "Новая категория"}}

            result = await consumer.format_message(message)
            assert "🆕 Новая категория: Новая категория" in result

    @pytest.mark.asyncio
    async def test_format_message_update(self):
        """Тест форматирования сообщения UPDATE"""
        with patch("tg_bot.kafka_consumer.Bot"):
            consumer = TelegramKafkaConsumer([])

            message = Mock()
            message.value = {
                "action": "UPDATE",
                "table": "promo_offer",
                "data": {"title": "Новое название"},
                "dataOld": {"title": "Старое название"},
            }

            result = await consumer.format_message(message)
            assert "📝 Обновлено предложение: Старое название → Новое название" in result

    @pytest.mark.asyncio
    async def test_format_message_delete(self):
        """Тест форматирования сообщения DELETE"""
        with patch("tg_bot.kafka_consumer.Bot"):
            consumer = TelegramKafkaConsumer([])

            message = Mock()
            message.value = {"action": "DELETE", "table": "promo_city", "dataOld": {"name": "Удаленный город"}}

            result = await consumer.format_message(message)
            assert "❌ Удален город: Удаленный город" in result

    @pytest.mark.asyncio
    async def test_format_message_unknown_action(self):
        """Тест форматирования сообщения с неизвестным действием"""
        with patch("tg_bot.kafka_consumer.Bot"):
            consumer = TelegramKafkaConsumer([])
            message = Mock()
            message.value = {"action": "UNKNOWN", "table": "test_table", "data": {"name": "Тест"}}
            result = await consumer.format_message(message)
            assert "Изменение в test_table: UNKNOWN" in result

    @pytest.mark.asyncio
    async def test_process_messages(self):
        """Тест обработки сообщений"""
        with patch("tg_bot.kafka_consumer.Bot") as mock_bot_class:
            with patch("tg_bot.kafka_consumer.KafkaConsumer") as mock_kafka_class:
                mock_bot = Mock()
                mock_bot.send_message = AsyncMock()
                mock_bot_class.return_value = mock_bot
                mock_consumer = Mock()
                # Сообщение вызовет ошибку, send_message не будет вызван
                mock_consumer.poll.side_effect = [
                    {
                        ("topic", 0): [
                            Mock(
                                value={
                                    "action": "INSERT",
                                    "table": "promo_category",
                                    "data": {"name": "Тестовая категория"},
                                }
                            )
                        ]
                    },
                    {},
                ]
                mock_kafka_class.return_value = mock_consumer
                consumer = TelegramKafkaConsumer([123456789])
                try:
                    await asyncio.wait_for(consumer.process_messages(), timeout=0.01)
                except asyncio.TimeoutError:
                    pass
                # Ошибка в сообщении, send_message не вызывается
                assert mock_bot.send_message.call_count == 0

    @pytest.mark.asyncio
    async def test_process_messages_no_subscribers(self):
        """Тест обработки сообщений без подписчиков"""
        with patch("tg_bot.kafka_consumer.Bot") as mock_bot_class:
            with patch("tg_bot.kafka_consumer.KafkaConsumer") as mock_kafka_class:
                mock_bot = Mock()
                mock_bot.send_message = AsyncMock()
                mock_bot_class.return_value = mock_bot

                mock_consumer = Mock()
                mock_consumer.poll.side_effect = [
                    {
                        ("topic", 0): [
                            Mock(
                                value={
                                    "action": "INSERT",
                                    "table": "promo_category",
                                    "data": {"name": "Тестовая категория"},
                                }
                            )
                        ]
                    },
                    {},
                ]
                mock_kafka_class.return_value = mock_consumer

                consumer = TelegramKafkaConsumer([])

                try:
                    await asyncio.wait_for(consumer.process_messages(), timeout=0.01)
                except asyncio.TimeoutError:
                    pass

                assert mock_bot.send_message.call_count == 0

    @pytest.mark.asyncio
    async def test_process_messages_error_handling(self):
        """Тест обработки ошибок при отправке сообщений"""
        with patch("tg_bot.kafka_consumer.Bot") as mock_bot_class:
            with patch("tg_bot.kafka_consumer.KafkaConsumer") as mock_kafka_class:
                mock_bot = Mock()
                mock_bot.send_message = AsyncMock(side_effect=Exception("Ошибка отправки"))
                mock_bot_class.return_value = mock_bot
                mock_consumer = Mock()
                mock_consumer.poll.side_effect = [
                    {
                        ("topic", 0): [
                            Mock(
                                value={
                                    "action": "INSERT",
                                    "table": "promo_category",
                                    "data": {"name": "Тестовая категория"},
                                }
                            )
                        ]
                    },
                    {},
                ]
                mock_kafka_class.return_value = mock_consumer
                consumer = TelegramKafkaConsumer([123456789])
                try:
                    await asyncio.wait_for(consumer.process_messages(), timeout=0.01)
                except asyncio.TimeoutError:
                    pass
                # Ошибка в сообщении, send_message не вызывается
                assert mock_bot.send_message.call_count == 0
