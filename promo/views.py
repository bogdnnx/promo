from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView, DetailView
from rest_framework import viewsets, filters
from django_filters import rest_framework as django_filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import City, Category, Partner, Offer
from rest_framework import viewsets
from .serializers import CitySerializer, CategorySerializer, PartnerSerializer, OfferSerializer

from rest_framework import viewsets, filters
from django_filters import rest_framework as django_filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import City, Category, Partner, Offer
from .serializers import (
    CitySerializer, CategorySerializer,
    PartnerSerializer, OfferSerializer
)

# Представления для работы с акциями, категориями и поиском
from django.shortcuts import render
from .models import Category, Offer, City, Partner
from django.db.models import Q


# def category_list(request):
#     """
#     Отображает список всех категорий с пагинацией.
#     """
#     categories = Category.objects.all()
#     city_id = request.GET.get('city', '')
#
#     # Пагинация для категорий
#     paginator = Paginator(categories, 8)  # 8 категорий на страницу
#     page = request.GET.get('page')
#     try:
#         page_obj = paginator.page(page)
#     except PageNotAnInteger:
#         page_obj = paginator.page(1)
#     except EmptyPage:
#         page_obj = paginator.page(paginator.num_pages)
#
#     return render(request, 'promo/category_list.html', {
#         'categories': page_obj
#     })

class CategoryListView(ListView):
    model = Category
    template_name = 'promo/category_list.html'
    context_object_name = 'categories'
    paginate_by = 8



# def all_offers(request):
#     """
#     Отображает все акции без фильтрации по городу или категории, с пагинацией.
#     """
#     offers = Offer.objects.all().order_by('-id')
#     paginator = Paginator(offers, 6)
#     page = request.GET.get('page')
#     try:
#         page_obj = paginator.page(page)
#     except PageNotAnInteger:
#         page_obj = paginator.page(1)
#     except EmptyPage:
#         page_obj = paginator.page(paginator.num_pages)
#     return render(request, 'promo/offer_list.html', {
#         'offers': page_obj,
#         'category': None,  # чтобы шаблон не ждал category
#         'cities': City.objects.all()
#     })

# class AllOffersListView(ListView):
#     model = Offer
#     template_name = 'promo/offer_list.html'
#     context_object_name = 'offers'
#     paginate_by = 6
#
#     def get_queryset(self):
#         # Переопределяем, чтобы добавить сортировку
#         queryset = Offer.objects.all().order_by('title')
#         print(
#             f"DEBUG: AllOffersListView get_queryset returned {queryset.count()} objects")  # <-- Добавьте эту строку для отладки
#         return queryset
#
#     def get_context_data(self, **kwargs):
#         # Переопределяем, чтобы добавить города в контекст (для фильтра в шаблоне)
#         context = super().get_context_data(**kwargs)
#         context['cities'] = City.objects.all()
#         # Возможно, нужно добавить selected_city, если форма фильтра в шаблоне общая
#         city_id = self.request.GET.get('city')
#         if city_id:
#             context['selected_city'] = city_id  # Здесь нужно подумать, как обрабатывать фильтр города
#         return context

class AllOffersListView(ListView):
    model = Offer
    template_name = 'promo/offer_list.html'
    context_object_name = 'offers'  # Это будет page_obj в контексте
    paginate_by = 6  # Убедитесь, что эта строка не закомментирована

    def get_queryset(self):
        queryset = Offer.objects.all().order_by('title')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        page_obj = context.get('page_obj')  # Получаем объект Page из контекста

        context['cities'] = City.objects.all()
        city_id = self.request.GET.get('city')
        if city_id:
            context['selected_city'] = city_id

        return context








# def offer_list(request, category_id):
#     """
#     Отображает список акций по выбранной категории и (опционально) городу, с пагинацией.
#     """
#     city_id = request.GET.get('city')
#     offers = Offer.objects.filter(category_id=category_id)
#     if city_id and city_id != 'None':
#         try:
#             city_id = int(city_id)
#             offers = offers.filter(city_id=city_id)
#         except (ValueError, TypeError):
#             pass
#     category = get_object_or_404(Category, id=category_id)
#     cities = City.objects.all()
#
#     # Пагинация для акций
#     paginator = Paginator(offers, 10)  # 6 акций на страницу
#     page = request.GET.get('page')
#     try:
#         page_obj = paginator.page(page)
#     except PageNotAnInteger:
#         page_obj = paginator.page(1)
#     except EmptyPage:
#         page_obj = paginator.page(paginator.num_pages)
#
#     return render(request, 'promo/offer_list.html', {
#         'offers': page_obj,
#         'category': category,
#         'cities': cities
#     })


class OfferListListView(ListView):
    model = Offer
    template_name = 'promo/offer_list.html'
    context_object_name = 'offers'

    def get_queryset(self):
        category_id = self.kwargs['category_id']
        queryset = Offer.objects.filter(category__id=category_id)
        city_id = self.request.GET.get('city')
        if city_id and city_id.isdigit():  # Проверяем, что city_id - число
            queryset = queryset.filter(city_id=city_id)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Получаем объект категории для контекста
        category_id = self.kwargs['category_id']
        context['category'] = get_object_or_404(Category, id=category_id)
        # Добавляем список всех городов для формы фильтра
        context['cities'] = City.objects.all()
        # Добавляем выбранный город, если есть
        city_id = self.request.GET.get('city')
        if city_id:
            context['selected_city'] = city_id  # Здесь нужно подумать, как правильно передать в шаблон

        return context




# def offer_detail(request, offer_id):
#     """
#     Отображает детальную страницу акции по её id.
#     """
#     offer = get_object_or_404(Offer, id=offer_id)
#     city_id = request.GET.get('city', '')
#     return render(request, 'promo/offer_detail.html', {'offer': offer})



class OfferDetailView(DetailView):
    model = Offer
    template_name = 'promo/offer_detail.html'
    context_object_name = 'offer'
    pk_url_kwarg = 'offer_id'



# def search(request):
#     """
#     Осуществляет поиск акций по названию, описанию и названию партнёра, с учётом выбранного города и пагинацией.
#     """
#     query = request.GET.get('q', '')
#     city_id = request.GET.get('city')
#     offers = Offer.objects.all()
#     if query:
#         offers = offers.filter(
#             Q(title__icontains=query) | Q(description__icontains=query) | Q(partner__name__icontains=query) | Q()
#         )
#     if city_id and city_id != 'None':
#         try:
#             city_id = int(city_id)
#             offers = offers.filter(city_id=city_id)
#         except (ValueError, TypeError):
#             pass
#
#     # Пагинация для результатов поиска
#     paginator = Paginator(offers, 10)  # 6 результатов на страницу
#     page = request.GET.get('page')
#     try:
#         page_obj = paginator.page(page)
#     except PageNotAnInteger:
#         page_obj = paginator.page(1)
#     except EmptyPage:
#         page_obj = paginator.page(paginator.num_pages)
#
#     return render(request, 'promo/search_results.html', {
#         'offers': page_obj,
#         'query': query
#     })



class SearchOffersListView(ListView):
    model = Offer
    context_object_name = 'offers'
    template_name = 'promo/search_results.html'

    def get_queryset(self):
        queryset = Offer.objects.all()
        query = self.request.GET.get('q')

        city = self.request.GET.get('city', None)

        # if city:
        #     city_id = self.request.GET['city']

        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(partner__name__icontains=query)
            )

        if city and city.isdigit():
            city_id = self.request.GET['city']
            queryset = queryset.filter(city_id=city_id)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')  # Добавляем поисковый запрос в контекст
        context['cities'] = City.objects.all()
        city_id = self.request.GET.get('city')
        if city_id:
            context['selected_city'] = city_id

        return context

















class CityViewSet(viewsets.ModelViewSet):
    queryset = City.objects.all()
    serializer_class = CitySerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']

    @action(detail=True, methods=['get'])
    def offers(self, request, pk=None):
        city = self.get_object()
        offers = Offer.objects.filter(city=city)
        serializer = OfferSerializer(offers, many=True)
        return Response(serializer.data)

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']

    @action(detail=True, methods=['get'])
    def offers(self, request, pk=None):
        category = self.get_object()
        offers = Offer.objects.filter(category=category)
        serializer = OfferSerializer(offers, many=True)
        return Response(serializer.data)

class PartnerViewSet(viewsets.ModelViewSet):
    queryset = Partner.objects.all()
    serializer_class = PartnerSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description']

    @action(detail=True, methods=['get'])
    def active_offers(self, request, pk=None):
        partner = self.get_object()
        offers = Offer.objects.filter(
            partner=partner,
            valid_from__lte=timezone.now(),
            valid_to__gte=timezone.now()
        )
        serializer = OfferSerializer(offers, many=True)
        return Response(serializer.data)

class OfferFilter(django_filters.FilterSet):
    min_discount = django_filters.NumberFilter(field_name="discount", lookup_expr='gte')
    max_discount = django_filters.NumberFilter(field_name="discount", lookup_expr='lte')
    active = django_filters.BooleanFilter(method='filter_active')

    class Meta:
        model = Offer
        fields = ['city', 'category', 'partner', 'min_discount', 'max_discount', 'active']

    def filter_active(self, queryset, name, value):
        if value:
            return queryset.filter(
                valid_from__lte=timezone.now(),
                valid_to__gte=timezone.now()
            )
        return queryset

class OfferViewSet(viewsets.ModelViewSet):
    queryset = Offer.objects.all()
    serializer_class = OfferSerializer
    filter_backends = [
        django_filters.DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter
    ]
    filterset_class = OfferFilter
    search_fields = ['title', 'description', 'promo_code']
    ordering_fields = ['valid_from', 'valid_to', 'discount']
    ordering = ['-valid_from']

    @action(detail=False, methods=['get'])
    def active(self, request):
        offers = Offer.objects.filter(
            valid_from__lte=timezone.now(),
            valid_to__gte=timezone.now()
        )
        serializer = self.get_serializer(offers, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def expiring_soon(self, request):
        offers = Offer.objects.filter(
            valid_to__gte=timezone.now(),
            valid_to__lte=timezone.now() + timezone.timedelta(days=7)
        )
        serializer = self.get_serializer(offers, many=True)
        return Response(serializer.data)