import os
import tempfile
from unittest.mock import call, mock_open, patch

import pytest

from tg_bot.db_utils import SUBSCRIBERS_FILE, get_all_subscribed_users, load_subscribers, save_subscribers


class TestDbUtils:
    """Тесты для функций работы с подписчиками"""

    def test_get_all_subscribed_users_file_exists(self):
        """Тест получения подписчиков из существующего файла"""
        with patch("builtins.open", mock_open(read_data="123456789\n987654321\n")):
            result = get_all_subscribed_users()
            assert result == [123456789, 987654321]

    def test_get_all_subscribed_users_file_not_exists(self):
        """Тест получения подписчиков из несуществующего файла"""
        with patch("builtins.open", side_effect=FileNotFoundError()):
            result = get_all_subscribed_users()
            assert result == []

    def test_get_all_subscribed_users_empty_file(self):
        """Тест получения подписчиков из пустого файла"""
        with patch("builtins.open", mock_open(read_data="")):
            result = get_all_subscribed_users()
            assert result == []

    def test_get_all_subscribed_users_with_invalid_data(self):
        """Тест получения подписчиков с некорректными данными"""
        with patch("builtins.open", mock_open(read_data="123\nabc\n456\n\n789")):
            result = get_all_subscribed_users()
            assert result == [123, 456, 789]

    def test_load_subscribers_file_exists(self):
        """Тест загрузки подписчиков из существующего файла"""
        with patch("builtins.open", mock_open(read_data="123456789\n987654321\n")):
            result = load_subscribers()
            assert result == {123456789, 987654321}

    def test_load_subscribers_file_not_exists(self):
        """Тест загрузки подписчиков из несуществующего файла"""
        with patch("builtins.open", side_effect=FileNotFoundError()):
            result = load_subscribers()
            assert result == set()

    def test_load_subscribers_empty_file(self):
        """Тест загрузки подписчиков из пустого файла"""
        with patch("builtins.open", mock_open(read_data="")):
            result = load_subscribers()
            assert result == set()

    def test_load_subscribers_with_invalid_data(self):
        """Тест загрузки подписчиков с некорректными данными"""
        with patch("builtins.open", mock_open(read_data="123\nabc\n456\n\n789")):
            result = load_subscribers()
            assert result == {123, 456, 789}

    def test_save_subscribers(self):
        """Тест сохранения подписчиков в файл"""
        subscribers = {123456789, 987654321, 555666777}

        with patch("builtins.open", mock_open()) as mock_file:
            save_subscribers(subscribers)

            mock_file.assert_called_once()
            handle = mock_file()
            expected_calls = [call(f"{user_id}\n") for user_id in subscribers]
            actual_calls = handle.write.call_args_list
            assert sorted(str(c) for c in actual_calls) == sorted(str(c) for c in expected_calls)

    def test_save_subscribers_empty_set(self):
        """Тест сохранения пустого множества подписчиков"""
        subscribers = set()

        with patch("builtins.open", mock_open()) as mock_file:
            save_subscribers(subscribers)

            mock_file.assert_called_once()
            handle = mock_file()
            assert handle.write.call_count == 0

    def test_save_subscribers_with_duplicates(self):
        """Тест сохранения подписчиков с дубликатами"""
        subscribers = {123456789, 123456789, 987654321}

        with patch("builtins.open", mock_open()) as mock_file:
            save_subscribers(subscribers)

            mock_file.assert_called_once()
            handle = mock_file()
            expected_calls = [call(f"{user_id}\n") for user_id in {123456789, 987654321}]
            actual_calls = handle.write.call_args_list
            assert sorted(str(c) for c in actual_calls) == sorted(str(c) for c in expected_calls)

    def test_file_operations_integration(self):
        """Интеграционный тест операций с файлом"""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
            temp_file = f.name

        try:
            with patch("tg_bot.db_utils.SUBSCRIBERS_FILE", temp_file):
                test_subscribers = {111, 222, 333}
                save_subscribers(test_subscribers)

                loaded_subscribers = load_subscribers()
                assert loaded_subscribers == test_subscribers

                user_list = get_all_subscribed_users()
                assert set(user_list) == test_subscribers

        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)
