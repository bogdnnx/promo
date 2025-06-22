from django.contrib import admin

from .models import Category, City, Offer, Partner, TelegramSubscription

# Регистрируем модели для управления ими через админку
admin.site.register(City)
admin.site.register(Category)
admin.site.register(Partner)
# admin.site.register(Offer)


@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    """Кастомизация отображения модели Offer в админке: фильтрация по категории и партнёру."""

    list_filter = ("category_id", "partner__name")


@admin.register(TelegramSubscription)
class TelegramSubscriptionAdmin(admin.ModelAdmin):
    list_display = ["user_id", "username", "is_active", "subscribed_at"]
    list_filter = ["is_active", "subscribed_at"]
    search_fields = ["user_id", "username"]
    readonly_fields = ["subscribed_at"]
