from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from rest_framework import viewsets
from .serializers import CitySerializer, CategorySerializer, PartnerSerializer, OfferSerializer

# Представления для работы с акциями, категориями и поиском
from django.shortcuts import render
from .models import Category, Offer, City, Partner
from django.db.models import Q


def category_list(request):
    """
    Отображает список всех категорий с пагинацией.
    """
    categories = Category.objects.all()
    city_id = request.GET.get('city', '')
    
    # Пагинация для категорий
    paginator = Paginator(categories, 8)  # 8 категорий на страницу
    page = request.GET.get('page')
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    
    return render(request, 'promo/category_list.html', {
        'categories': page_obj
    })


def all_offers(request):
    """
    Отображает все акции без фильтрации по городу или категории, с пагинацией.
    """
    offers = Offer.objects.all().order_by('-id')
    paginator = Paginator(offers, 6)
    page = request.GET.get('page')
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    return render(request, 'promo/offer_list.html', {
        'offers': page_obj,
        'category': None,  # чтобы шаблон не ждал category
        'cities': City.objects.all()
    })


def offer_list(request, category_id):
    """
    Отображает список акций по выбранной категории и (опционально) городу, с пагинацией.
    """
    city_id = request.GET.get('city')
    offers = Offer.objects.filter(category_id=category_id)
    if city_id and city_id != 'None':
        try:
            city_id = int(city_id)
            offers = offers.filter(city_id=city_id)
        except (ValueError, TypeError):
            pass
    category = get_object_or_404(Category, id=category_id)
    cities = City.objects.all()
    
    # Пагинация для акций
    paginator = Paginator(offers, 10)  # 6 акций на страницу
    page = request.GET.get('page')
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    
    return render(request, 'promo/offer_list.html', {
        'offers': page_obj,
        'category': category,
        'cities': cities
    })

def offer_detail(request, offer_id):
    """
    Отображает детальную страницу акции по её id.
    """
    offer = get_object_or_404(Offer, id=offer_id)
    city_id = request.GET.get('city', '')
    return render(request, 'promo/offer_detail.html', {'offer': offer})


def search(request):
    """
    Осуществляет поиск акций по названию, описанию и названию партнёра, с учётом выбранного города и пагинацией.
    """
    query = request.GET.get('q', '')
    city_id = request.GET.get('city')
    offers = Offer.objects.all()
    if query:
        offers = offers.filter(
            Q(title__icontains=query) | Q(description__icontains=query) | Q(partner__name__icontains=query) | Q()
        )
    if city_id and city_id != 'None':
        try:
            city_id = int(city_id)
            offers = offers.filter(city_id=city_id)
        except (ValueError, TypeError):
            pass
    
    # Пагинация для результатов поиска
    paginator = Paginator(offers, 10)  # 6 результатов на страницу
    page = request.GET.get('page')
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    
    return render(request, 'promo/search_results.html', {
        'offers': page_obj,
        'query': query
    })



class CityViewSet(viewsets.ModelViewSet):
    queryset = City.objects.all()
    serializer_class = CitySerializer

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class PartnerViewSet(viewsets.ModelViewSet):
    queryset = Partner.objects.all()
    serializer_class = PartnerSerializer

class OfferViewSet(viewsets.ModelViewSet):
    queryset = Offer.objects.all()
    serializer_class = OfferSerializer