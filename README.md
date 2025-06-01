# Ufanet Promo API

API для управления акциями и скидками партнеров Уфанет.

## Требования

- Python 3.9+
- Django 5.2+
- Django REST Framework
- PostgreSQL

## Установка и запуск

1. Клонируйте репозиторий:
```bash
git clone https://github.com/your-username/ufanet_django.git
cd ufanet_django
```

2. Создайте и активируйте виртуальное окружение:
```bash
python -m venv venv
source venv/bin/activate  # для Linux/Mac
# или
venv\Scripts\activate  # для Windows
```

3. Установите зависимости:
```bash
pip install -r requirements.txt
```

4. Настройте базу данных в `settings.py`:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'your_db_name',
        'USER': 'your_db_user',
        'PASSWORD': 'your_db_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

5. Примените миграции:
```bash
python manage.py migrate
```

6. Создайте суперпользователя:
```bash
python manage.py createsuperuser
```

7. Запустите сервер разработки:
```bash
python manage.py runserver
```

## API Endpoints

### Города (Cities)

- `GET /api/cities/` - список всех городов
- `GET /api/cities/{id}/` - детали города
- `GET /api/cities/{id}/offers/` - акции в городе

### Категории (Categories)

- `GET /api/categories/` - список всех категорий
- `GET /api/categories/{id}/` - детали категории
- `GET /api/categories/{id}/offers/` - акции в категории

### Партнеры (Partners)

- `GET /api/partners/` - список всех партнеров
- `GET /api/partners/{id}/` - детали партнера
- `GET /api/partners/{id}/active_offers/` - активные акции партнера

### Акции (Offers)

- `GET /api/offers/` - список всех акций
- `GET /api/offers/{id}/` - детали акции
- `POST /api/offers/` - создание новой акции
- `PUT /api/offers/{id}/` - обновление акции
- `PATCH /api/offers/{id}/` - частичное обновление акции
- `DELETE /api/offers/{id}/` - удаление акции

#### Специальные эндпоинты для акций

- `GET /api/offers/active/` - список активных акций
- `GET /api/offers/expiring_soon/` - список акций, срок действия которых истекает в течение недели

#### Фильтрация акций

Доступны следующие параметры фильтрации:
- `?city={id}` - фильтр по городу
- `?category={id}` - фильтр по категории
- `?partner={id}` - фильтр по партнеру
- `?min_discount={value}` - минимальная скидка
- `?max_discount={value}` - максимальная скидка
- `?active={true/false}` - фильтр по активности

#### Поиск

- `?search={query}` - поиск по названию, описанию и промокоду

#### Сортировка

- `?ordering={field}` - сортировка по полю
  - Доступные поля: valid_from, valid_to, discount
  - Для обратной сортировки используйте префикс "-"

## Веб-интерфейс

- `/` - главная страница со списком категорий
- `/categories/` - список всех категорий
- `/category/{id}/` - список акций в категории
- `/offer/{id}/` - детальная страница акции
- `/search/` - поиск акций
- `/offers/` - список всех акций

## Разработка

### Запуск тестов

```bash
python manage.py test
```

### Проверка кода

```bash
pylint ufanet_project/
autopep8 --in-place --aggressive --aggressive ufanet_project/
```

