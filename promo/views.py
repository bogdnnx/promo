from django.shortcuts import render, get_object_or_404

# Create your views here.
from django.shortcuts import render
from .models import Category, Offer, City
from django.db.models import Q




def category_list(request):
    categories = Category.objects.all()
    city_id = request.GET.get('city', '')
    return render(request, 'promo/category_list.html', {'categories': categories, 'selected_city': city_id})

def offer_list(request, category_id):
    city_id = request.GET.get('city')
    offers = Offer.objects.filter(category_id=category_id)
    if city_id:
        offers = offers.filter(city_id=city_id)
    category = get_object_or_404(Category, id=category_id)
    cities = City.objects.all()
    return render(request, 'promo/offer_list.html', {
        'offers': offers, 'category': category, 'cities': cities, 'selected_city': city_id
    })

def offer_detail(request, offer_id):
    offer = get_object_or_404(Offer, id=offer_id)
    city_id = request.GET.get('city', '')
    return render(request, 'promo/offer_detail.html', {'offer': offer, 'selected_city': city_id})


def search(request):
    query = request.GET.get('q', '')
    city_id = request.GET.get('city')
    offers = Offer.objects.all()
    if query:
        offers = offers.filter(
            Q(title__icontains=query) | Q(description__icontains=query) | Q(partner__name__icontains=query)
        )
    if city_id:
        offers = offers.filter(city_id=city_id)
    return render(request, 'promo/search_results.html', {'offers': offers, 'query': query})

# def promotion_list(request, category_id):
#     promotions = Promotion.objects.filter(category_id=category_id, is_active=True)
#     return render(request, 'promo/promotions.html', {'promotions': promotions})
#
# def promotion_detail(request, promotion_id):
#     promotion = Promotion.objects.get(id=promotion_id)
#     return render(request, 'promo/detail.html', {'promotion': promotion})