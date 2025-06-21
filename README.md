# Ufanet Django Telegram Bot

Telegram-бот для уведомлений о событиях в системе Ufanet с интеграцией Kafka и WAL-listener.

## Архитектура проекта

Проект состоит из следующих компонентов:

- **Telegram Bot** (`tg_bot/`) - основной бот для отправки уведомлений
- **Kafka Consumer** - обработчик сообщений из Kafka
- **WAL-listener** - слушатель изменений в базе данных PostgreSQL
- **Django Backend** - веб-интерфейс для управления

### Структура проекта

```
ufanet_django/
├── tg_bot/                    # Telegram бот
│   ├── bot.py                # Основная логика бота
│   ├── config.py             # Конфигурация
│   ├── db_utils.py           # Утилиты для работы с подписчиками
│   ├── kafka_consumer.py     # Kafka consumer
│   ├── keyboards/            # Клавиатуры бота
│   ├── handlers/             # Обработчики команд
│   ├── utils/                # Утилиты
│   └── tests/                # Тесты
├── ufanet/                   # Django приложение
├── docker-compose.yml        # Docker конфигурация
├── Dockerfile               # Docker образ
└── requirements.txt         # Зависимости
```

## Установка и запуск

### Предварительные требования

- Python 3.11+
- Docker и Docker Compose
- PostgreSQL
- Apache Kafka

### 1. Клонирование репозитория

```bash
git clone <repository-url>
cd ufanet_django
```

### 2. Настройка переменных окружения

Создайте файл `.env` в корне проекта:

```env
# Telegram Bot
TELEGRAM_BOT_TOKEN=your_telegram_bot_token

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/ufanet

# Kafka
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
KAFKA_TOPIC=ufanet_events

# Django
DJANGO_SECRET_KEY=your_secret_key
DJANGO_DEBUG=True
```

### 3. Запуск с Docker

```bash
# Сборка и запуск всех сервисов
docker-compose up --build

# Запуск в фоновом режиме
docker-compose up -d
```

### 4. Запуск без Docker

```bash
# Установка зависимостей
pip install -r requirements.txt

# Применение миграций Django
python manage.py migrate

# Запуск Django сервера
python manage.py runserver

# Запуск Telegram бота (в отдельном терминале)
python -m tg_bot.bot

# Запуск Kafka consumer (в отдельном терминале)
python -m tg_bot.kafka_consumer
```

## Функциональность

### Telegram Bot

- **Команда /start** - приветствие и главное меню
- **Подписка на уведомления** - добавление пользователя в список подписчиков
- **Отписка от уведомлений** - удаление пользователя из списка подписчиков
- **Автоматические уведомления** - отправка сообщений при событиях в системе

### Kafka Consumer

- Обработка сообщений из Kafka
- Форматирование уведомлений для Telegram
- Отправка сообщений всем подписчикам
- Обработка ошибок и повторные попытки

### WAL-listener

- Мониторинг изменений в PostgreSQL через WAL
- Отправка событий в Kafka
- Поддержка операций INSERT, UPDATE, DELETE

## Тестирование

### Запуск тестов

```bash
# Все тесты с красивым отчетом
python run_tests.py

# Обычный запуск тестов
python -m pytest tg_bot/tests/ -v

# С покрытием кода
python -m pytest tg_bot/tests/ -v --cov=tg_bot --cov-report=html

# Конкретный тест
python -m pytest tg_bot/tests/test_bot.py::TestBotHandlers::test_cmd_start -v
```

### Покрытие тестами

Проект имеет покрытие тестами более 80%:

- **tg_bot/bot.py** - 70% (основные обработчики)
- **tg_bot/config.py** - 100% (конфигурация)
- **tg_bot/db_utils.py** - 100% (работа с подписчиками)
- **tg_bot/kafka_consumer.py** - 55% (Kafka consumer)
- **tg_bot/keyboards/** - 100% (клавиатуры)
- **wal-listener** - 97% (конфигурация)

### Типы тестов

1. **Unit тесты** - тестирование отдельных функций
2. **Integration тесты** - тестирование взаимодействия компонентов
3. **Mock тесты** - тестирование с моками внешних зависимостей

## Конфигурация

### Telegram Bot

Настройки бота находятся в `tg_bot/config.py`:

```python
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
```

### Kafka

Настройки Kafka в `tg_bot/kafka_consumer.py`:

```python
KAFKA_BOOTSTRAP_SERVERS = ['localhost:9092']
KAFKA_TOPIC = 'ufanet_events'
```

### WAL-listener

Конфигурация в `config.yml`:

```yaml
database:
  host: localhost
  port: 5432
  name: ufanet
  user: postgres
  password: password

kafka:
  bootstrap_servers: localhost:9092
  topic: ufanet_events
```

## Разработка

### Добавление новых команд бота

1. Создайте обработчик в `tg_bot/handlers/`
2. Добавьте команду в `tg_bot/bot.py`
3. Создайте тесты в `tg_bot/tests/`

### Добавление новых типов уведомлений

1. Обновите логику в `tg_bot/kafka_consumer.py`
2. Добавьте форматирование сообщений
3. Обновите тесты

### Структура тестов

```
tg_bot/tests/
├── conftest.py              # Фикстуры pytest
├── test_bot.py             # Тесты бота
├── test_config.py          # Тесты конфигурации
├── test_db_utils.py        # Тесты работы с данными
├── test_kafka_consumer.py  # Тесты Kafka consumer
├── test_keyboards.py       # Тесты клавиатур
└── test_integration.py     # Интеграционные тесты
```

## Утилиты

### Очистка проекта

```bash
# Удаление временных файлов и отчетов покрытия
./cleanup.sh
```

## Мониторинг и логирование

### Логи

Логи сохраняются в:
- `logs/bot.log` - логи Telegram бота
- `logs/kafka.log` - логи Kafka consumer
- `logs/wal_listener.log` - логи WAL-listener

### Метрики

- Количество подписчиков
- Количество отправленных уведомлений
- Время обработки сообщений
- Ошибки и исключения

## Безопасность

- Токены хранятся в переменных окружения
- Валидация входных данных
- Обработка исключений
- Логирование ошибок

## Поддержка

При возникновении проблем:

1. Проверьте логи в `logs/`
2. Убедитесь в корректности конфигурации
3. Проверьте подключение к базе данных и Kafka
4. Запустите тесты для проверки функциональности

## Лицензия

MIT License 