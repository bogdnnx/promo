from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'cities', views.CityViewSet)
router.register(r'categories', views.CategoryViewSet)
router.register(r'partners', views.PartnerViewSet)
router.register(r'offers', views.OfferViewSet)

urlpatterns = [
    path('', views.category_list, name='category_list'),
    path('category/<int:category_id>/', views.offer_list, name='offer_list'),
    path('offer/<int:offer_id>/', views.offer_detail, name='offer_detail'),
    path('search/', views.search, name='search'),
    path('offers/', views.all_offers, name='all_offers'),
    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls')),
]