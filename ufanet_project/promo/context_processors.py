from .models import City


def cities_processor(request):
    """
    Контекстный процессор для передачи списка городов и выбранного города во все шаблоны.
    """
    cities = City.objects.all()
    selected_city = request.GET.get('city', '')
    return {'cities': cities, 'selected_city': selected_city}
