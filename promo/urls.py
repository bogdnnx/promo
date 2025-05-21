from django.urls import path
from . import views

urlpatterns = [
    path('', views.category_list, name='category_list'),
    path('category/<int:category_id>/', views.offer_list, name='offer_list'),
    path('offer/<int:offer_id>/', views.offer_detail, name='offer_detail'),
    path('search/', views.search, name='search'),
    path('offers/', views.all_offers, name='all_offers'),
]