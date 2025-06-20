# import os
# import sys
#
# import django
# from typing import List, Optional
#
# sys.path.append('/app')
#
# # Настройка Django для работы с ORM
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ufanet_project.ufanet_project.settings')
#
#
# settings_path = '/app/ufanet_project/settings.py'
# if not os.path.exists(settings_path):
#     print(f"Ошибка: файл settings.py не найден по пути {settings_path}")
#     print(f"Текущая директория: {os.getcwd()}")
#     print(f"Содержимое /app: {os.listdir('/app')}")
#     sys.exit(1)
#
# django.setup()
#
# from promo.models import TelegramSubscription
#
#
# def add_subscription(user_id: int, username: str = None) -> bool:
#     """Добавить подписку пользователя"""
#     try:
#         TelegramSubscription.add_subscription(user_id=user_id, username=username)
#         return True
#     except Exception as e:
#         print(f"Ошибка при добавлении подписки: {e}")
#         return False
#
#
# def remove_subscription(user_id: int) -> bool:
#     """Удалить подписку пользователя"""
#     return TelegramSubscription.remove_subscription(user_id)
#
#
# def is_subscribed(user_id: int) -> bool:
#     """Проверить, подписан ли пользователь"""
#     return TelegramSubscription.is_subscribed(user_id)
#
#
# def get_all_subscribed_users() -> List[int]:
#     """Получить список всех активных подписчиков"""
#     return TelegramSubscription.get_all_subscribed_users()
#
#
# def get_total_subscribers() -> int:
#     """Получить общее количество активных подписчиков"""
#     return TelegramSubscription.objects.filter(is_active=True).count()


# import os
# import sys
# import django
# from typing import List, Optional
#
# # Добавляем пути к Django проекту в sys.path
# sys.path.append('/app')
# sys.path.append('/app/ufanet_project')

# # Выводим структуру для диагностики
# print("=== ДИАГНОСТИКА ===")
# print(f"Текущая директория: {os.getcwd()}")
# print(f"Содержимое /app: {os.listdir('/app')}")
# print(f"Содержимое /app/ufanet_project: {os.listdir('/app/ufanet_project')}")
#
# # Проверяем, есть ли файл settings.py
# settings_paths = [
#     '/app/ufanet_project/settings.py',
#     '/app/ufanet_project/ufanet_project/settings.py',
#     '/app/settings.py'
# ]
#
# for path in settings_paths:
#     if os.path.exists(path):
#         print(f"✅ Найден settings.py: {path}")
#     else:
#         print(f"❌ Не найден: {path}")
#
# # Пробуем найти правильный путь
# if os.path.exists('/app/ufanet_project/ufanet_project'):
#     print(f"Содержимое /app/ufanet_project/ufanet_project: {os.listdir('/app/ufanet_project/ufanet_project')}")
#
# print("=== КОНЕЦ ДИАГНОСТИКИ ===")
#
# # Пока отключаем Django setup для диагностики
# # os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ufanet_project.ufanet_project.settings')
# # django.setup()
# # from promo.models import TelegramSubscription
#
# # Временные заглушки функций
# def add_subscription(user_id: int, username: str = None) -> bool:
#     print(f"Добавление подписки: {user_id}, {username}")
#     return True
#
# def remove_subscription(user_id: int) -> bool:
#     print(f"Удаление подписки: {user_id}")
#     return True
#
# def is_subscribed(user_id: int) -> bool:
#     print(f"Проверка подписки: {user_id}")
#     return False
#
# def get_all_subscribed_users() -> List[int]:
#     print("Получение всех подписчиков")
#     return []
#
# def get_total_subscribers() -> int:
#     print("Подсчет подписчиков")
#     return 0


import os

SUBSCRIBERS_FILE = os.path.join(os.path.dirname(__file__), "subscribers.txt")

def get_all_subscribed_users():
    if not os.path.exists(SUBSCRIBERS_FILE):
        return []
    with open(SUBSCRIBERS_FILE, "r") as f:
        return [int(line.strip()) for line in f if line.strip().isdigit()]

def load_subscribers():
    if not os.path.exists(SUBSCRIBERS_FILE):
        return set()
    with open(SUBSCRIBERS_FILE, "r") as f:
        return set(int(line.strip()) for line in f if line.strip().isdigit())

def save_subscribers(subscribers):
    with open(SUBSCRIBERS_FILE, "w") as f:
        for user_id in subscribers:
            f.write(f"{user_id}\n")