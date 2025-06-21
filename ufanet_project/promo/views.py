from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView, DetailView
from rest_framework import viewsets, filters, status
from django_filters import rest_framework as django_filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import City, Category, Partner, Offer
from .serializers import (
    CitySerializer, CategorySerializer,
    PartnerSerializer, OfferSerializer
)
from django.db.models import Q


class CategoryListView(ListView):
    """
    Отображает список всех категорий акций.
    Использует пагинацию для оптимизации загрузки данных.
    """
    model = Category
    template_name = "promo/category_list.html"
    context_object_name = "categories"
    paginate_by = 8


class AllOffersListView(ListView):
    """
    Представление для отображения всех акций с возможностью фильтрации по городу.
    Реализует пагинацию и фильтрацию на стороне сервера.
    """
    model = Offer
    template_name = "promo/offer_list.html"
    context_object_name = "offers"
    paginate_by = 6

    def get_queryset(self):
        """Возвращает отсортированный по названию queryset всех акций."""
        return Offer.objects.all().order_by("title")

    def get_context_data(self, **kwargs):
        """
        Расширяет контекст данными о городах и выбранном городе для фильтрации.
        """
        context = super().get_context_data(**kwargs)
        context["cities"] = City.objects.all()
        city_id = self.request.GET.get("city")
        if city_id:
            context["selected_city"] = city_id
        return context


class OfferListListView(ListView):
    """
    Отображает список акций для конкретной категории.
    Поддерживает фильтрацию по городу и пагинацию.
    """
    model = Offer
    template_name = "promo/offer_list.html"
    context_object_name = "offers"

    def get_queryset(self):
        """
        Фильтрует акции по категории и городу.
        Проверяет валидность city_id перед фильтрацией.
        """
        category_id = self.kwargs["category_id"]
        queryset = Offer.objects.filter(category__id=category_id)
        city_id = self.request.GET.get("city")
        if city_id and city_id.isdigit():
            queryset = queryset.filter(city_id=city_id)
        return queryset

    def get_context_data(self, **kwargs):
        """
        Добавляет в контекст данные о категории, городах и выбранном городе.
        """
        context = super().get_context_data(**kwargs)
        category_id = self.kwargs["category_id"]
        context["category"] = get_object_or_404(Category, id=category_id)
        context["cities"] = City.objects.all()
        city_id = self.request.GET.get("city")
        if city_id:
            context["selected_city"] = city_id
        return context


class OfferDetailView(DetailView):
    """
    Детальное представление отдельной акции.
    Использует offer_id вместо pk для идентификации акции.
    """
    model = Offer
    template_name = "promo/offer_detail.html"
    context_object_name = "offer"
    pk_url_kwarg = "offer_id"


class SearchOffersListView(ListView):
    """
    Реализует поиск акций по названию, описанию и имени партнера.
    Поддерживает фильтрацию по городу и пагинацию результатов.
    """
    model = Offer
    context_object_name = "offers"
    template_name = "promo/search_results.html"

    def get_queryset(self):
        """
        Выполняет поиск по нескольким полям с учетом фильтра по городу.
        Использует Q-объекты для построения сложных запросов.
        """
        queryset = Offer.objects.all()
        query = self.request.GET.get("q")
        city = self.request.GET.get("city")

        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(partner__name__icontains=query)
            )

        if city and city.isdigit():
            queryset = queryset.filter(city_id=city)

        return queryset

    def get_context_data(self, **kwargs):
        """
        Добавляет в контекст поисковый запрос и данные для фильтрации по городу.
        """
        context = super().get_context_data(**kwargs)
        context["query"] = self.request.GET.get("q", "")
        context["cities"] = City.objects.all()
        city_id = self.request.GET.get("city")
        if city_id:
            context["selected_city"] = city_id
        return context


class CityViewSet(viewsets.ModelViewSet):
    """
    ViewSet для работы с городами через API.
    Поддерживает поиск по названию и получение акций для конкретного города.
    """
    queryset = City.objects.all()
    serializer_class = CitySerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["name"]

    # def destroy(self, request, *args, **kwargs):
    #     instance = self.get_object()
    #     data = {
    #         'id': instance.id,
    #         'name': instance.name,
    #     }
    #     self.perform_destroy(instance)
    #     return Response(data, status=status.HTTP_200_OK)
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        # Сохраняем данные перед удалением
        data = {
            'id': instance.id,
            'name': instance.name,
        }
        # Удаляем объект
        self.perform_destroy(instance)
        # Возвращаем данные об удаленном объекте
        return Response({
            'data': data,  # Добавляем данные в поле 'data'
            'action': 'DELETE',
            'table': 'promo_city'
        }, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get"])
    def offers(self, request, pk=None):
        """Возвращает список всех акций для выбранного города."""
        city = self.get_object()
        offers = Offer.objects.filter(city=city)
        serializer = OfferSerializer(offers, many=True)
        return Response(serializer.data)


class CategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet для работы с категориями через API.
    Поддерживает поиск по названию и получение акций по категории.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["name"]

    @action(detail=True, methods=["get"])
    def offers(self, request, pk=None):
        """Возвращает список всех акций в выбранной категории."""
        category = self.get_object()
        offers = Offer.objects.filter(category=category)
        serializer = OfferSerializer(offers, many=True)
        return Response(serializer.data)


class PartnerViewSet(viewsets.ModelViewSet):
    """
    ViewSet для работы с партнерами через API.
    Поддерживает поиск по названию и описанию, получение активных акций.
    """
    queryset = Partner.objects.all()
    serializer_class = PartnerSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["name", "description"]

    @action(detail=True, methods=["get"])
    def active_offers(self, request, pk=None):
        """Возвращает список активных акций для выбранного партнера."""
        partner = self.get_object()
        offers = Offer.objects.filter(
            partner=partner,
            valid_from__lte=timezone.now(),
            valid_to__gte=timezone.now()
        )
        serializer = OfferSerializer(offers, many=True)
        return Response(serializer.data)


class OfferFilter(django_filters.FilterSet):
    """
    Набор фильтров для акций.
    Поддерживает фильтрацию по городу, категории, партнеру,
    диапазону скидок и статусу активности.
    """
    min_discount = django_filters.NumberFilter(
        field_name="discount", lookup_expr="gte")
    max_discount = django_filters.NumberFilter(
        field_name="discount", lookup_expr="lte")
    active = django_filters.BooleanFilter(method="filter_active")

    class Meta:
        model = Offer
        fields = [
            "city",
            "category",
            "partner",
            "min_discount",
            "max_discount",
            "active"
        ]

    def filter_active(self, queryset, name, value):
        """
        Фильтрует акции по статусу активности.
        Активная акция должна иметь текущую дату в пределах срока действия.
        """
        if value:
            return queryset.filter(
                valid_from__lte=timezone.now(),
                valid_to__gte=timezone.now()
            )
        return queryset


class OfferViewSet(viewsets.ModelViewSet):
    """
    ViewSet для работы с акциями через API.
    Поддерживает фильтрацию, поиск, сортировку и специальные действия.
    """
    queryset = Offer.objects.all()
    serializer_class = OfferSerializer
    filter_backends = [
        django_filters.DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter
    ]
    filterset_class = OfferFilter
    search_fields = ["title", "description", "promo_code"]
    ordering_fields = ["valid_from", "valid_to", "discount"]
    ordering = ["-valid_from"]

    @action(detail=False, methods=["get"])
    def active(self, request):
        """Возвращает список всех активных акций."""
        offers = Offer.objects.filter(
            valid_from__lte=timezone.now(),
            valid_to__gte=timezone.now()
        )
        serializer = self.get_serializer(offers, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def expiring_soon(self, request):
        """Возвращает список акций, срок действия которых истекает в течение недели."""
        offers = Offer.objects.filter(
            valid_to__gte=timezone.now(),
            valid_to__lte=timezone.now() + timezone.timedelta(days=7)
        )
        serializer = self.get_serializer(offers, many=True)
        return Response(serializer.data)
