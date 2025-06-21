import pytest
import asyncio
import tempfile
import os
from unittest.mock import Mock, patch, AsyncMock
from aiogram import Bot, Dispatcher
from aiogram.types import Message, User, Chat

# Устанавливаем валидный тестовый токен для всех тестов
os.environ['TELEGRAM_BOT_TOKEN'] = '123456789:TEST_FAKE_TOKEN_FOR_UNITTESTS'

# Правильный мок kafka для избежания проблем с Python 3.11
import sys
kafka_mock = Mock()
kafka_errors_mock = Mock()
kafka_errors_mock.NoBrokersAvailable = Exception
kafka_mock.errors = kafka_errors_mock
kafka_mock.KafkaConsumer = Mock()
sys.modules['kafka'] = kafka_mock
sys.modules['kafka.errors'] = kafka_errors_mock
sys.modules['kafka.consumer'] = Mock()

@pytest.fixture
def event_loop():
    """Создает event loop для асинхронных тестов"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def temp_subscribers_file():
    """Фикстура для создания временного файла с подписчиками"""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        f.write("123456789\n987654321\n")
        temp_file = f.name
    
    yield temp_file
    
    if os.path.exists(temp_file):
        os.unlink(temp_file)


@pytest.fixture
def mock_message():
    """Создает мок сообщения Telegram"""
    message = Mock(spec=Message)
    message.from_user = Mock(spec=User)
    message.from_user.id = 123456789
    message.text = "📝 Подписаться на уведомления"
    message.answer = AsyncMock()
    return message


@pytest.fixture
def mock_bot():
    """Создает мок бота"""
    bot_mock = Mock(spec=Bot)
    bot_mock.send_message = AsyncMock()
    return bot_mock


@pytest.fixture
def mock_kafka_consumer():
    """Создает мок Kafka consumer"""
    consumer_mock = Mock()
    consumer_mock.poll = Mock(return_value={})
    consumer_mock.close = Mock()
    return consumer_mock


@pytest.fixture
def sample_kafka_message():
    """Создает пример сообщения из Kafka"""
    return {
        'action': 'INSERT',
        'table': 'promo_category',
        'data': {
            'name': 'Тестовая категория',
            'id': 1
        }
    }


@pytest.fixture
def sample_kafka_message_update():
    """Создает пример сообщения обновления из Kafka"""
    return {
        'action': 'UPDATE',
        'table': 'promo_offer',
        'data': {
            'title': 'Новое название',
            'id': 1
        },
        'dataOld': {
            'title': 'Старое название',
            'id': 1
        }
    }


@pytest.fixture
def sample_kafka_message_delete():
    """Создает пример сообщения удаления из Kafka"""
    return {
        'action': 'DELETE',
        'table': 'promo_city',
        'data': {
            'name': 'Удаленный город',
            'id': 1
        }
    } 