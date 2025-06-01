from rest_framework import serializers
from .models import City, Category, Partner, Offer

class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ['id', 'name']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'icon']

class PartnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Partner
        fields = ['id', 'name', 'description']

class OfferSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    partner = PartnerSerializer(read_only=True)
    city = CitySerializer(read_only=True)

    class Meta:
        model = Offer
        fields = [
            'id', 'title', 'description', 'discount', 'promo_code',
            'category', 'partner', 'city', 'valid_from', 'valid_to', 'image'
        ] 