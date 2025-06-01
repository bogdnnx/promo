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
    path('', views.CategoryListView.as_view(), name='category_list'),
    path('category/<int:category_id>/', views.OfferListListView.as_view(), name='offer_list'),
    path('offer/<int:offer_id>/', views.OfferDetailView.as_view(), name='offer_detail'),
    path('search/', views.SearchOffersListView.as_view(), name='search'),
    path('offers/', views.AllOffersListView.as_view(), name='all_offers'),
    path('api/', include(router.urls))
]