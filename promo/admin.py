from django.contrib import admin
from .models import City, Category, Partner, Offer

# Регистрируем модели для управления ими через админку
admin.site.register(City)
admin.site.register(Category)
admin.site.register(Partner)
# admin.site.register(Offer)


@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    """Кастомизация отображения модели Offer в админке: фильтрация по категории и партнёру."""
    list_filter = ("category_id", "partner__name")
