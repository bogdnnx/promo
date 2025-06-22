import importlib
import os
from unittest.mock import patch

import pytest


class TestConfig:
    """Тесты для конфигурации"""

    def test_telegram_bot_token_loaded_from_env(self):
        """Тест загрузки токена из переменной окружения"""
        with patch.dict(os.environ, {"TELEGRAM_BOT_TOKEN": "test_token_123"}):
            import tg_bot.config

            importlib.reload(tg_bot.config)
            assert tg_bot.config.TELEGRAM_BOT_TOKEN == "test_token_123"

    def test_telegram_bot_token_empty(self):
        """Тест пустого токена"""
        with patch.dict(os.environ, {"TELEGRAM_BOT_TOKEN": ""}):
            import importlib

            import tg_bot.config

            try:
                importlib.reload(tg_bot.config)
                _ = tg_bot.config.TELEGRAM_BOT_TOKEN
                assert False, "ValueError должен быть вызван"
            except ValueError:
                pass

    def test_telegram_bot_token_whitespace(self):
        """Тест токена с пробелами"""
        with patch.dict(os.environ, {"TELEGRAM_BOT_TOKEN": "  test_token  "}):
            import tg_bot.config

            importlib.reload(tg_bot.config)
            assert tg_bot.config.TELEGRAM_BOT_TOKEN == "  test_token  "

    def test_telegram_bot_token_valid_format(self):
        """Тест валидного формата токена"""
        with patch.dict(os.environ, {"TELEGRAM_BOT_TOKEN": "1234567890:ABCDEFGHIJKLMNOPQRSTUVWXYZ"}):
            import tg_bot.config

            importlib.reload(tg_bot.config)
            assert tg_bot.config.TELEGRAM_BOT_TOKEN == "1234567890:ABCDEFGHIJKLMNOPQRSTUVWXYZ"

    def test_telegram_bot_token_special_characters(self):
        """Тест токена со специальными символами"""
        with patch.dict(os.environ, {"TELEGRAM_BOT_TOKEN": "test_token_with_special_chars_!@#$%^&*()"}):
            import tg_bot.config

            importlib.reload(tg_bot.config)
            assert tg_bot.config.TELEGRAM_BOT_TOKEN == "test_token_with_special_chars_!@#$%^&*()"

    def test_telegram_bot_token_numeric(self):
        """Тест числового токена"""
        with patch.dict(os.environ, {"TELEGRAM_BOT_TOKEN": "123456789"}):
            import tg_bot.config

            importlib.reload(tg_bot.config)
            assert tg_bot.config.TELEGRAM_BOT_TOKEN == "123456789"

    def test_telegram_bot_token_case_sensitive(self):
        """Тест чувствительности к регистру"""
        with patch.dict(os.environ, {"TELEGRAM_BOT_TOKEN": "TestToken"}):
            import tg_bot.config

            importlib.reload(tg_bot.config)
            assert tg_bot.config.TELEGRAM_BOT_TOKEN == "TestToken"

    def test_telegram_bot_token_very_long(self):
        """Тест очень длинного токена"""
        long_token = "a" * 1000
        with patch.dict(os.environ, {"TELEGRAM_BOT_TOKEN": long_token}):
            import tg_bot.config

            importlib.reload(tg_bot.config)
            assert tg_bot.config.TELEGRAM_BOT_TOKEN == long_token

    def test_telegram_bot_token_unicode(self):
        """Тест токена с Unicode символами"""
        with patch.dict(os.environ, {"TELEGRAM_BOT_TOKEN": "токен_с_русскими_символами"}):
            import tg_bot.config

            importlib.reload(tg_bot.config)
            assert tg_bot.config.TELEGRAM_BOT_TOKEN == "токен_с_русскими_символами"

    def test_telegram_bot_token_multiple_environment_variables(self):
        """Тест с несколькими переменными окружения"""
        with patch.dict(os.environ, {"TELEGRAM_BOT_TOKEN": "correct_token", "OTHER_VAR": "other_value"}):
            import tg_bot.config

            importlib.reload(tg_bot.config)
            assert tg_bot.config.TELEGRAM_BOT_TOKEN == "correct_token"

    def test_telegram_bot_token_reload_behavior(self):
        """Тест поведения при перезагрузке переменной окружения"""
        with patch.dict(os.environ, {"TELEGRAM_BOT_TOKEN": "first_token"}):
            import tg_bot.config

            importlib.reload(tg_bot.config)
            assert tg_bot.config.TELEGRAM_BOT_TOKEN == "first_token"

        with patch.dict(os.environ, {"TELEGRAM_BOT_TOKEN": "second_token"}):
            import tg_bot.config

            importlib.reload(tg_bot.config)
            assert tg_bot.config.TELEGRAM_BOT_TOKEN == "second_token"
