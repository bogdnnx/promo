# FROM python:3.11-slim
#
# WORKDIR /app
#
# # Копируем файлы зависимостей
# COPY tg_bot/requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt
#
# # Копируем код бота
# COPY tg_bot/ /app/tg_bot/
#
# # Добавляем путь к Python
# ENV PYTHONPATH=/app
#
# # Запускаем бота
# CMD ["python", "/app/tg_bot/bot.py"]


FROM python:3.11-slim

WORKDIR /app

# Копируем файлы зависимостей
COPY tg_bot/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код бота
COPY ufanet_project/ ./ufanet_project/

COPY tg_bot/ ./tg_bot/


# Добавляем путь к Python
ENV PYTHONPATH=/app

# Запускаем бота
CMD ["python", "tg_bot/bot.py"]