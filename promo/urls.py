from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter
from .views import CityViewSet, CategoryViewSet, PartnerViewSet, OfferViewSet

router = DefaultRouter()
router.register(r'cities', CityViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'partners', PartnerViewSet)
router.register(r'offers', OfferViewSet)

urlpatterns = [
    path('', views.category_list, name='category_list'),
    path('category/<int:category_id>/', views.offer_list, name='offer_list'),
    path('offer/<int:offer_id>/', views.offer_detail, name='offer_detail'),
    path('search/', views.search, name='search'),
    path('offers/', views.all_offers, name='all_offers'),
    path('api/', include(router.urls))
]