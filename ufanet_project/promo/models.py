# models.py
from django.db import models


class City(models.Model):
    """Модель города, в котором действуют акции."""

    name = models.CharField(max_length=100)

    def __str__(self):
        """Возвращает строковое представление города (его название)."""
        return self.name

    class Meta:
        ordering = ["id"]  # Сортировка по id


class Category(models.Model):
    """Модель категории акций (например, еда, спорт, развлечения)."""

    name = models.CharField(max_length=100)
    icon = models.ImageField(upload_to="category_icons/", null=True, blank=True)

    class Meta:
        ordering = ["id"]  # Сортировка по id

    def __str__(self):
        """Возвращает строковое представление категории (её название)."""
        return self.name


class Partner(models.Model):
    """Модель партнёра, предоставляющего акции."""

    name = models.CharField(max_length=100)
    description = models.TextField()
    # logo = models.ImageField(upload_to='partner_logos/', null=True, blank=True)

    class Meta:
        ordering = ["id"]  # Сортировка по id

    def __str__(self):
        """Возвращает строковое представление партнёра (его название)."""
        return self.name


class Offer(models.Model):
    """Модель акции или скидки, предоставляемой партнёром."""

    title = models.CharField(max_length=200)
    description = models.TextField()
    discount = models.CharField(max_length=50)
    promo_code = models.CharField(max_length=50, blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    partner = models.ForeignKey(Partner, on_delete=models.CASCADE)
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    valid_from = models.DateField()
    valid_to = models.DateField()
    image = models.ImageField(upload_to="offer_images/", null=True, blank=True)

    def __str__(self):
        """Возвращает строковое представление акции (её название)."""
        return self.title

    class Meta:
        ordering = ["id"]  # Сортировка по id


class TelegramSubscription(models.Model):
    """Модель для хранения подписок пользователей Telegram."""

    user_id = models.BigIntegerField(unique=True, verbose_name="ID пользователя Telegram")
    username = models.CharField(max_length=100, blank=True, null=True, verbose_name="Username")
    is_active = models.BooleanField(default=True, verbose_name="Активна")
    subscribed_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата подписки")

    class Meta:
        verbose_name = "Подписка Telegram"
        verbose_name_plural = "Подписки Telegram"

    def __str__(self):
        return f"Подписка {self.user_id} ({self.username or 'Неизвестный'})"

    @classmethod
    def add_subscription(cls, user_id, username=None):
        """Добавить или обновить подписку пользователя."""
        subscription, created = cls.objects.update_or_create(
            user_id=user_id, defaults={"username": username, "is_active": True}
        )
        return subscription

    @classmethod
    def remove_subscription(cls, user_id):
        """Отключить подписку пользователя."""
        try:
            subscription = cls.objects.get(user_id=user_id)
            subscription.is_active = False
            subscription.save()
            return True
        except cls.DoesNotExist:
            return False

    @classmethod
    def is_subscribed(cls, user_id):
        """Проверить, подписан ли пользователь."""
        return cls.objects.filter(user_id=user_id, is_active=True).exists()

    @classmethod
    def get_all_subscribed_users(cls):
        """Получить список всех активных подписчиков."""
        return list(cls.objects.filter(is_active=True).values_list("user_id", flat=True))
