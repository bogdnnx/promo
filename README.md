# Ufanet Django Telegram Bot

Telegram-бот для уведомлений о событиях в системе Ufanet с интеграцией Kafka и WAL-listener.

## Быстрый запуск

### Предварительные требования

- Docker и Docker Compose
- Git

### 1. Клонирование и запуск

```bash
git clone <repository-url>
cd ufanet_django

# Запуск всех сервисов
docker-compose up --build

# Или в фоновом режиме
docker-compose up -d
```

### 2. Доступ к сервисам

После запуска будут доступны:

- **Django Web** - http://localhost:8000
- **Nginx** - http://localhost:8080  
- **PostgreSQL** - localhost:5434
- **Kafka** - localhost:9092

### 3. Остановка

```bash
docker-compose down
```

## Архитектура

Проект состоит из:

- **Django Web** - веб-интерфейс
- **Telegram Bot** - бот для уведомлений
- **Kafka** - обработка сообщений
- **WAL-listener** - мониторинг изменений БД
- **PostgreSQL** - база данных
- **Nginx** - веб-сервер

## Тестирование

```bash
# Запуск тестов
sh run_tests.sh


```

## Структура проекта

```
ufanet_django/
├── ufanet_project/     # Django приложение
├── tg_bot/            # Telegram бот
├── wal-listener/      # WAL-listener конфигурация
├── nginx/             # Nginx конфигурация
├── docker-compose.yml # Docker конфигурация
└── README.md
```

## Установка и запуск

### Предварительные требования

- Python 3.11+
- Docker и Docker Compose
- PostgreSQL
- Apache Kafka
- Wal-listener от ihippik

### 1. Клонирование репозитория

```bash
git clone <repository-url>
cd ufanet_django
```



### 2. Запуск с Docker

```bash
# Сборка и запуск всех сервисов
docker-compose up --build

# Запуск в фоновом режиме
docker-compose up -d
```


## Функциональность

### Telegram Bot

- **Команда /start** - приветствие и главное меню
- **Подписка на уведомления** - добавление пользователя в список подписчиков
- **Отписка от уведомлений** - удаление пользователя из списка подписчиков

### Kafka Consumer

- Обработка сообщений из Kafka
- Форматирование уведомлений для Telegram
- Отправка сообщений всем подписчикам
- Обработка ошибок и повторные попытки

### WAL-listener

- Мониторинг изменений в PostgreSQL через WAL
- Отправка событий в Kafka
- Поддержка операций INSERT, UPDATE, DELETE



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


## Безопасность

- Токены хранятся в переменных окружения
- Валидация входных данных
- Обработка исключений
- Логирование ошибок

## Поддержка

При возникновении проблем:

1. Проверьте логи 
2. Убедитесь в корректности конфигурации
3. Проверьте подключение к базе данных и Kafka
