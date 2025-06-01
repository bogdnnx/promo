from rest_framework import serializers
from .models import City, Category, Partner, Offer
from django.utils import timezone

class CitySerializer(serializers.ModelSerializer):
    offers_count = serializers.SerializerMethodField()

    class Meta:
        model = City
        fields = ['id', 'name', 'offers_count']

    def get_offers_count(self, obj):
        return obj.offer_set.count()

class CategorySerializer(serializers.ModelSerializer):
    offers_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'icon', 'offers_count']

    def get_offers_count(self, obj):
        return obj.offer_set.count()

class PartnerSerializer(serializers.ModelSerializer):
    active_offers = serializers.SerializerMethodField()

    class Meta:
        model = Partner
        fields = ['id', 'name', 'description', 'active_offers']

    def get_active_offers(self, obj):
        return obj.offer_set.filter(
            valid_from__lte=timezone.now(),
            valid_to__gte=timezone.now()
        ).count()


class OfferSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    partner = PartnerSerializer(read_only=True)
    city = CitySerializer(read_only=True)
    is_active = serializers.SerializerMethodField()
    days_left = serializers.SerializerMethodField()
    category_id = serializers.IntegerField(write_only=True)
    partner_id = serializers.IntegerField(write_only=True)
    city_id = serializers.IntegerField(write_only=True)


    class Meta:
        model = Offer
        fields = [
            'id', 'title', 'description', 'discount', 'promo_code',
            'category', 'partner', 'city', 'valid_from', 'valid_to',
            'image', 'is_active', 'days_left', 'category_id', 'partner_id', 'city_id'
        ]


    def get_is_active(self, obj):
        now = timezone.now().date()  # Преобразуем datetime в date
        return obj.valid_from <= now <= obj.valid_to


    def get_days_left(self, obj):
        if obj.valid_to:
            return (obj.valid_to - timezone.now().date()).days
        return None


    def validate(self, data):
        if data.get('valid_from') and data.get('valid_to'):
            if data['valid_from'] > data['valid_to']:
                raise serializers.ValidationError(
                    "Дата начала не может быть позже даты окончания"
                )
        return data