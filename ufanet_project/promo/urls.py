from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views
from .views import CategoryViewSet, CityViewSet, OfferViewSet, PartnerViewSet

# Роутер для API endpoints
router = DefaultRouter()
router.register(r"cities", CityViewSet)
router.register(r"categories", CategoryViewSet)
router.register(r"partners", PartnerViewSet)
router.register(r"offers", OfferViewSet)

# URL patterns для веб-интерфейса и API
urlpatterns = [
    # Веб-интерфейс
    path("", views.CategoryListView.as_view(), name="category_list"),  # Главная страница со списком категорий
    path(
        "category/<int:category_id>/", views.OfferListListView.as_view(), name="offer_list"
    ),  # Список акций по категории
    path("offer/<int:offer_id>/", views.OfferDetailView.as_view(), name="offer_detail"),  # Детальная страница акции
    path("search/", views.SearchOffersListView.as_view(), name="search"),  # Поиск акций
    path("offers/", views.AllOffersListView.as_view(), name="all_offers"),  # Список всех акций
    # API endpoints
    path("api/", include(router.urls)),  # Все API endpoints через роутер
]
