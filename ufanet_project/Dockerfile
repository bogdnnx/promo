# Используем официальную сборку Python
FROM python:3.11-slim

# Установка необходимых пакетов
RUN apt-get update && apt-get install -y postgresql-client

# Рабочая директория внутри контейнера
WORKDIR /app

# Копируем файлы зависимостей и устанавливаем
COPY ufanet_project/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь код проекта
COPY ufanet_project/ .

# Создаем необходимые директории
RUN mkdir -p /app/media/category_icons /app/media/offer_images /app/media/partner_logos

# Запускаем миграции и сервер
CMD python manage.py migrate && python manage.py runserver 0.0.0.0:8000