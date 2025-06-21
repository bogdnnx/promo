#!/bin/bash

# Скрипт для запуска тестов проекта

echo "🚀 Запуск тестов для Telegram бота и WAL-listener..."

# Проверяем, установлен ли pytest
if ! command -v pytest &> /dev/null; then
    echo "❌ pytest не установлен. Устанавливаем зависимости для тестов..."
    pip install -r tg_bot/tests/requirements-test.txt
fi

# Создаем временную переменную окружения для тестов
export TELEGRAM_BOT_TOKEN="test_token_for_testing"

echo "📋 Запуск unit тестов..."
pytest tg_bot/tests/ -v --tb=short -m "not integration" --cov=tg_bot --cov-report=term-missing

echo "🔗 Запуск интеграционных тестов..."
pytest tg_bot/tests/ -v --tb=short -m "integration" --cov=tg_bot --cov-report=term-missing

echo "📊 Запуск тестов WAL-listener..."
pytest wal-listener/tests/ -v --tb=short --cov=wal-listener --cov-report=term-missing

echo "📈 Генерация отчета о покрытии..."
pytest --cov=tg_bot --cov=wal-listener --cov-report=html:htmlcov --cov-report=xml:coverage.xml

echo "✅ Тесты завершены!"
echo "📁 Отчет о покрытии доступен в папке htmlcov/"
echo "📄 XML отчет доступен в файле coverage.xml" 