from .models import City

def cities_processor(request):
    cities = City.objects.all()
    selected_city = request.GET.get('city', '')
    return {'cities': cities, 'selected_city': selected_city} 