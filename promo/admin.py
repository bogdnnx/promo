from django.contrib import admin
from .models import City, Category, Partner, Offer

# Register your models here.
admin.site.register(City)
admin.site.register(Category)
admin.site.register(Partner)
#admin.site.register(Offer)

@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_filter = ("category_id", "partner__name")

