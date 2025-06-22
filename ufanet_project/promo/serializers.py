from django.utils import timezone
from rest_framework import serializers

from .models import Category, City, Offer, Partner


class CitySerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели City.
    Используется в API для представления данных о городах.
    """

    class Meta:
        model = City
        fields = ["id", "name"]


class CategorySerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Category.
    Используется в API для представления данных о категориях акций.
    """

    class Meta:
        model = Category
        fields = ["id", "name"]


class PartnerSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Partner.
    Используется в API для представления данных о партнерах.
    """

    class Meta:
        model = Partner
        fields = ["id", "name", "description"]


class OfferSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Offer.
    Включает вложенные сериализаторы для связанных моделей и
    дополнительные поля для статуса активности и оставшегося времени.
    """

    city = CitySerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    partner = PartnerSerializer(read_only=True)
    city_id = serializers.PrimaryKeyRelatedField(queryset=City.objects.all(), source="city", write_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), source="category", write_only=True
    )
    partner_id = serializers.PrimaryKeyRelatedField(queryset=Partner.objects.all(), source="partner", write_only=True)
    is_active = serializers.SerializerMethodField()
    days_left = serializers.SerializerMethodField()

    class Meta:
        model = Offer
        fields = [
            "id",
            "title",
            "description",
            "discount",
            "promo_code",
            "valid_from",
            "valid_to",
            "city",
            "city_id",
            "category",
            "category_id",
            "partner",
            "partner_id",
            "is_active",
            "days_left",
            "image",
        ]
        read_only_fields = ["is_active", "days_left"]

    def get_is_active(self, obj):
        """
        Возвращает статус активности акции.
        Акция считается активной, если текущая дата находится
        в пределах срока её действия.
        """
        now = timezone.now().date()
        return obj.valid_from <= now <= obj.valid_to

    def get_days_left(self, obj):
        """
        Возвращает количество оставшихся дней действия акции.
        Если срок действия истек, возвращает None.
        """
        if obj.valid_to:
            return (obj.valid_to - timezone.now().date()).days
        return None

    def validate(self, data):
        """
        Проверяет корректность дат начала и окончания акции.
        Дата начала не может быть позже даты окончания.
        """
        if data.get("valid_from") and data.get("valid_to"):
            if data["valid_from"] > data["valid_to"]:
                raise serializers.ValidationError("Дата начала не может быть позже даты окончания")
        return data
