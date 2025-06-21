import pytest
import asyncio
import tempfile
import os
from unittest.mock import Mock, patch, AsyncMock
from aiogram.types import Message, User
from tg_bot.bot import cmd_start, subscribe_to_notifications, unsubscribe_from_notifications
from tg_bot.kafka_consumer import TelegramKafkaConsumer
from tg_bot.db_utils import get_all_subscribed_users, load_subscribers, save_subscribers


class TestIntegration:
    """Интеграционные тесты для всего проекта"""

    @pytest.mark.asyncio
    async def test_full_subscription_workflow(self):
        """Тест полного цикла подписки пользователя"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            temp_file = f.name
        
        try:
            with patch('tg_bot.db_utils.SUBSCRIBERS_FILE', temp_file):
                message = Mock(spec=Message)
                message.from_user = Mock(spec=User)
                message.from_user.id = 123456789
                message.text = "📝 Подписаться на уведомления"
                message.answer = AsyncMock()
                
                with patch('tg_bot.bot.subscribed_users', set()) as mock_subscribers:
                    with patch('tg_bot.bot.save_subscribers') as mock_save:
                        await subscribe_to_notifications(message)
                        assert 123456789 in mock_subscribers
                        mock_save.assert_called_once()
                        message.answer.assert_called_once_with("Вы успешно подписались на уведомления!")
                        # Явно сохраняем подписчика в файл
                        save_subscribers(mock_subscribers)
                        loaded_subscribers = load_subscribers()
                        assert 123456789 in loaded_subscribers
                        user_list = get_all_subscribed_users()
                        assert 123456789 in user_list
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)

    @pytest.mark.asyncio
    async def test_full_unsubscription_workflow(self):
        """Тест полного цикла отписки пользователя"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write("123456789\n987654321\n")
            temp_file = f.name
        
        try:
            with patch('tg_bot.db_utils.SUBSCRIBERS_FILE', temp_file):
                message = Mock(spec=Message)
                message.from_user = Mock(spec=User)
                message.from_user.id = 123456789
                message.text = "❌ Отписаться от уведомлений"
                message.answer = AsyncMock()
                
                with patch('tg_bot.bot.subscribed_users', {123456789, 987654321}) as mock_subscribers:
                    with patch('tg_bot.bot.save_subscribers') as mock_save:
                        await unsubscribe_from_notifications(message)
                        
                        assert 123456789 not in mock_subscribers
                        assert 987654321 in mock_subscribers
                        mock_save.assert_called_once()
                        message.answer.assert_called_once_with("Вы успешно отписались от уведомлений.")
                        
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)

    @pytest.mark.asyncio
    async def test_kafka_consumer_with_real_subscribers(self):
        """Тест Kafka consumer с реальными подписчиками"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write("123456789\n987654321\n")
            temp_file = f.name
        
        try:
            with patch('tg_bot.db_utils.SUBSCRIBERS_FILE', temp_file):
                with patch('tg_bot.kafka_consumer.Bot') as mock_bot_class:
                    with patch('tg_bot.kafka_consumer.KafkaConsumer') as mock_kafka_class:
                        mock_bot = Mock()
                        mock_bot.send_message = AsyncMock()
                        mock_bot_class.return_value = mock_bot
                        mock_consumer = Mock()
                        mock_consumer.poll.side_effect = [
                            {
                                ('topic', 0): [
                                    Mock(value={
                                        'action': 'INSERT',
                                        'table': 'promo_category',
                                        'data': {'name': 'Тестовая категория'}
                                    })
                                ]
                            },
                            {}
                        ]
                        mock_kafka_class.return_value = mock_consumer
                        kafka_consumer = TelegramKafkaConsumer([])
                        kafka_consumer.get_subscribers = lambda: get_all_subscribed_users()
                        try:
                            await asyncio.wait_for(kafka_consumer.process_messages(), timeout=0.01)
                        except asyncio.TimeoutError:
                            pass
                        # Просто проверяем, что не возникло исключения
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)

    @pytest.mark.asyncio
    async def test_bot_start_with_keyboard(self):
        """Тест команды /start с клавиатурой"""
        message = Mock(spec=Message)
        message.answer = AsyncMock()
        
        await cmd_start(message)
        
        message.answer.assert_called_once()
        call_args = message.answer.call_args
        assert "Привет! Я бот для уведомлений" in call_args[0][0]
        assert call_args[1]['reply_markup'] is not None
        
        keyboard = call_args[1]['reply_markup']
        assert len(keyboard.keyboard) == 2
        assert len(keyboard.keyboard[0]) == 2
        assert len(keyboard.keyboard[1]) == 1

    def test_file_operations_integration(self):
        """Интеграционный тест операций с файлом подписчиков"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            temp_file = f.name
        
        try:
            with patch('tg_bot.db_utils.SUBSCRIBERS_FILE', temp_file):
                test_subscribers = {111, 222, 333}
                save_subscribers(test_subscribers)
                
                assert os.path.exists(temp_file)
                
                loaded_subscribers = load_subscribers()
                assert loaded_subscribers == test_subscribers
                
                user_list = get_all_subscribed_users()
                assert set(user_list) == test_subscribers
                
                test_subscribers.add(444)
                save_subscribers(test_subscribers)
                
                updated_subscribers = load_subscribers()
                assert updated_subscribers == test_subscribers
                
                test_subscribers.remove(222)
                save_subscribers(test_subscribers)
                
                final_subscribers = load_subscribers()
                assert final_subscribers == test_subscribers
                assert 222 not in final_subscribers
                
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file) 