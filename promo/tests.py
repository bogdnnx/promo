from rest_framework.test import APITestCase, APIClient
from django.urls import reverse
from django.utils import timezone
from datetime import date, timedelta
from .models import City, Category, Partner, Offer


from django.test import TestCase, Client
from datetime import date, timedelta


class OfferAPITestCase(APITestCase):
    """
    Тесты для API акций.
    """

    def setUp(self):
        """
        Подготовка данных для тестов.
        Создаем тестовые объекты City, Category, Partner, Offer.
        """
        self.client = APIClient()

        # Создаем тестовые данные
        self.city1 = City.objects.create(name="Город 1")
        self.city2 = City.objects.create(name="Город 2")
        self.category1 = Category.objects.create(name="Категория 1")
        self.category2 = Category.objects.create(name="Категория 2")
        self.partner1 = Partner.objects.create(name="Партнер 1", description="Описание 1")
        self.partner2 = Partner.objects.create(name="Партнер 2", description="Описание 2")

        # Создаем тестовые акции
        self.offer1 = Offer.objects.create(
            title="Акция 1",
            description="Описание акции 1",
            discount="10%",
            promo_code="PROMO1",
            valid_from=date.today(),
            valid_to=date.today() + timedelta(days=30),
            city=self.city1,
            category=self.category1,
            partner=self.partner1
        )
        self.offer2 = Offer.objects.create(
            title="Акция 2",
            description="Описание акции 2",
            discount="20%",
            promo_code="PROMO2",
            valid_from=date.today() - timedelta(days=10),
            valid_to=date.today() + timedelta(days=20),
            city=self.city1,
            category=self.category2,
            partner=self.partner2
        )
        self.offer3 = Offer.objects.create(
            title="Акция 3",
            description="Описание акции 3",
            discount="30%",
            promo_code="PROMO3",
            valid_from=date.today() + timedelta(days=5),  # Будет неактивна на старте теста
            valid_to=date.today() + timedelta(days=15),
            city=self.city2,
            category=self.category1,
            partner=self.partner1
        )

        # Определяем URL для ViewSet
        self.list_url = reverse('offer-list')  # Имя маршрута из router
        self.detail_url = lambda pk: reverse('offer-detail', args=[pk])  # Имя маршрута для деталей

    def test_list_offers(self):
        """
        Тест получения списка акций.
        """
        response = self.client.get(self.list_url)

        # Проверяем статус код
        self.assertEqual(response.status_code, 200)

        # Проверяем, что количество акций в ответе совпадает с созданным
        # Учитываем, что пагинация по умолчанию 10
        self.assertEqual(response.data['count'], 3)
        self.assertEqual(len(response.data['results']), 3)

        # Проверяем, что акции в ответе присутствуют
        offer_titles = [item['title'] for item in response.data['results']]
        self.assertIn('Акция 1', offer_titles)
        self.assertIn('Акция 2', offer_titles)
        self.assertIn('Акция 3', offer_titles)

    def test_retrieve_offer(self):
        """
        Тест получения деталей конкретной акции.
        """
        response = self.client.get(self.detail_url(self.offer1.id))

        # Проверяем статус код
        self.assertEqual(response.status_code, 200)

        # Проверяем данные в ответе
        self.assertEqual(response.data['title'], 'Акция 1')
        self.assertEqual(response.data['discount'], '10%')
        # Проверяем вложенные поля
        self.assertEqual(response.data['city']['name'], 'Город 1')
        self.assertEqual(response.data['category']['name'], 'Категория 1')
        self.assertEqual(response.data['partner']['name'], 'Партнер 1')

        # Проверяем вычисляемые поля
        self.assertTrue(response.data['is_active'])  # offer1 должен быть активен
        self.assertIsNotNone(response.data['days_left'])

    def test_create_offer(self):
        """
        Тест создания новой акции.
        """
        new_offer_data = {
            'title': 'Новая Акция',
            'description': 'Описание новой акции',
            'discount': '50%',
            'promo_code': 'NEW50',
            'valid_from': date.today().isoformat(),  # Даты должны быть в формате YYYY-MM-DD
            'valid_to': (date.today() + timedelta(days=60)).isoformat(),
            'city_id': self.city2.id,
            'category_id': self.category2.id,
            'partner_id': self.partner2.id
            # Поле image можно не отправлять, если оно blank=True
        }

        response = self.client.post(self.list_url, new_offer_data, format='json')

        # Проверяем статус код (201 Created)
        self.assertEqual(response.status_code, 201)

        # Проверяем, что акция создана в базе данных
        self.assertEqual(Offer.objects.count(), 4)  # Было 3, стала 4
        created_offer = Offer.objects.get(id=response.data['id'])
        self.assertEqual(created_offer.title, 'Новая Акция')
        self.assertEqual(created_offer.city, self.city2)

    def test_update_offer(self):
        """
        Тест полного обновления акции (PUT).
        """
        updated_data = {
            'title': 'Обновленная Акция 1',
            'description': 'Новое описание акции 1',
            'discount': '15%',
            'promo_code': 'UPDATED1',
            'valid_from': (date.today() - timedelta(days=5)).isoformat(),
            'valid_to': (date.today() + timedelta(days=35)).isoformat(),
            'city_id': self.city2.id,  # Меняем город
            'category_id': self.category1.id,
            'partner_id': self.partner1.id,
        }

        response = self.client.put(self.detail_url(self.offer1.id), updated_data, format='json')

        # Проверяем статус код
        self.assertEqual(response.status_code, 200)

        # Обновляем объект из базы данных и проверяем изменения
        self.offer1.refresh_from_db()
        self.assertEqual(self.offer1.title, 'Обновленная Акция 1')
        self.assertEqual(self.offer1.city, self.city2)

    def test_partial_update_offer(self):
        """
        Тест частичного обновления акции (PATCH).
        """
        partial_data = {
            'discount': '25%',  # Обновляем только скидку
        }

        response = self.client.patch(self.detail_url(self.offer2.id), partial_data, format='json')

        # Проверяем статус код
        self.assertEqual(response.status_code, 200)

        # Обновляем объект из базы данных и проверяем изменения
        self.offer2.refresh_from_db()
        self.assertEqual(self.offer2.discount, '25%')
        # Проверяем, что другие поля не изменились
        self.assertEqual(self.offer2.title, 'Акция 2')

    def test_delete_offer(self):
        """
        Тест удаления акции.
        """
        response = self.client.delete(self.detail_url(self.offer3.id))

        # Проверяем статус код (204 No Content)
        self.assertEqual(response.status_code, 204)

        # Проверяем, что акция удалена из базы данных
        self.assertEqual(Offer.objects.count(), 2)  # Было 3, стала 2
        from django.core.exceptions import ObjectDoesNotExist
        with self.assertRaises(ObjectDoesNotExist):
            Offer.objects.get(id=self.offer3.id)

    def test_filter_offers_by_city(self):
        """
        Тест фильтрации акций по городу.
        """
        response = self.client.get(self.list_url, {'city': self.city1.id})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 2)  # Акция 1 и Акция 2 в городе 1
        offer_titles = [item['title'] for item in response.data['results']]
        self.assertIn('Акция 1', offer_titles)
        self.assertIn('Акция 2', offer_titles)
        self.assertNotIn('Акция 3', offer_titles)

    def test_filter_offers_by_active(self):
        """
        Тест фильтрации акций по активности.
        """
        response = self.client.get(self.list_url, {'active': 'true'})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 2)  # Акция 1 и Акция 2 активны
        offer_titles = [item['title'] for item in response.data['results']]
        self.assertIn('Акция 1', offer_titles)
        self.assertIn('Акция 2', offer_titles)
        self.assertNotIn('Акция 3', offer_titles)

    def test_search_offers(self):
        """
        Тест поиска акций по названию.
        """
        response = self.client.get(self.list_url, {'search': 'Акция 1'})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['title'], 'Акция 1')

    def test_order_offers(self):
        """
        Тест сортировки акций по скидке (по возрастанию).
        """
        response = self.client.get(self.list_url, {'ordering': 'discount'})

        self.assertEqual(response.status_code, 200)
        # Проверяем порядок акций по скидке: 10%, 20%, 30%
        discounts = [int(item['discount'].strip('%')) for item in response.data['results']]
        self.assertEqual(discounts, [10, 20, 30])

    def test_list_active_offers_action(self):
        """
        Тест эндпоинта /active/
        """
        active_url = reverse('offer-active')  # Имя маршрута для action

        response = self.client.get(active_url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)  # Ожидаем 2 активные акции
        offer_titles = [item['title'] for item in response.data]
        self.assertIn('Акция 1', offer_titles)
        self.assertIn('Акция 2', offer_titles)
        self.assertNotIn('Акция 3', offer_titles)











from rest_framework.test import APITestCase, APIClient
from django.urls import reverse
from django.utils import timezone
from datetime import date, timedelta
from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase, Client # Импорт для обычных тестов


# Можно добавить базовые данные для всех видов тестов, если они общие
# Например, базовые города, категории, партнеры
class BaseTestData(TestCase):
    def setUp(self):
        self.client = Client()
        self.city1 = City.objects.create(name="Город А")
        self.city2 = City.objects.create(name="Город Б")
        self.category1 = Category.objects.create(name="Категория X")
        self.category2 = Category.objects.create(name="Категория Y")
        self.partner1 = Partner.objects.create(name="Партнер 1", description="...")
        self.partner2 = Partner.objects.create(name="Партнер 2", description="...")

        # Пример акций
        # Используем короткие описания, соответствующие тому, что рендерится в шаблонах
        self.offer1 = Offer.objects.create(
            title="Акция 1", description="Desc 1", discount="10%", promo_code="",
            valid_from=date.today(), valid_to=date.today() + timedelta(days=10),
            city=self.city1, category=self.category1, partner=self.partner1
        )
        self.offer2 = Offer.objects.create(
            title="Акция 2", description="Desc 2", discount="20%", promo_code="",
            valid_from=date.today(), valid_to=date.today() + timedelta(days=10),
            city=self.city1, category=self.category2, partner=self.partner2
        )
        self.offer3 = Offer.objects.create(
            title="Акция 3", description="Desc 3", discount="30%", promo_code="",
            valid_from=date.today(), valid_to=date.today() + timedelta(days=10),
            city=self.city2, category=self.category1, partner=self.partner1
        )


# Тесты для обычных представлений
class PromoViewsTest(BaseTestData): # Наследуемся от BaseTestData для общих данных
    """
    Тесты для обычных представлений Django в приложении promo.
    """

    def test_all_offers_view(self):
        """
        Тест представления all_offers (список всех акций).
        """
        url = reverse('all_offers')  # Используем имя маршрута из urls.py
        response = self.client.get(url)

        # 1. Проверяем статус код
        self.assertEqual(response.status_code, 200)

        # 2. Проверяем используемый шаблон
        self.assertTemplateUsed(response, 'promo/offer_list.html')

        # 3. Проверяем контекст шаблона
        self.assertIn('offers', response.context)  # Проверяем, что список акций в контексте
        self.assertIn('cities', response.context)  # Проверяем, что список городов в контексте
        self.assertIn('page_obj', response.context)  # Проверяем наличие объекта пагинации

        # Проверяем, что объекты пагинатора корректны
        self.assertTrue(hasattr(response.context['page_obj'], 'paginator'))
        # Проверяем общее количество объектов до пагинации
        self.assertEqual(response.context['page_obj'].paginator.count, 3)
        # Проверяем количество объектов на текущей странице (первой)
        self.assertEqual(len(response.context['page_obj']), 3)


        # Проверяем, что акции присутствуют на странице (по содержимому HTML)
        # Используем фактические описания из setUp
        self.assertContains(response, "Акция 1")
        self.assertContains(response, "Акция 2")
        self.assertContains(response, "Акция 3")


    def test_offer_list_view_by_category(self):
        """
        Тест представления offer_list (акции по категории).
        """
        # Предполагаем, что в urls.py есть маршрут типа path('category/<int:category_id>/', views.offer_list, name='offer_list')
        url = reverse('offer_list', args=[self.category1.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'promo/offer_list.html')

        self.assertIn('offers', response.context)
        self.assertIn('category', response.context)
        self.assertEqual(response.context['category'], self.category1) # Проверяем, что категория правильная

        # В категории 1 должны быть Акция 1 и Акция 3
        # Проверяем количество объектов на текущей странице
        self.assertEqual(len(response.context['offers']), 2) # <-- Исправлено
        offer_titles_in_context = [offer.title for offer in response.context['offers']]
        self.assertIn('Акция 1', offer_titles_in_context)
        self.assertIn('Акция 3', offer_titles_in_context)
        self.assertNotIn('Акция 2', offer_titles_in_context)

        # Проверяем содержимое HTML
        self.assertContains(response, "Акция 1")
        self.assertContains(response, "Акция 3")
        self.assertNotContains(response, "Акция 2")


    def test_offer_list_view_by_category_and_city(self):
        """
        Тест представления offer_list (акции по категории и городу).
        """
        # Предполагаем, что в urls.py есть маршрут типа path('category/<int:category_id>/', views.offer_list, name='offer_list')
        url = reverse('offer_list', args=[self.category1.id])
        # Передаем GET параметр 'city'
        response = self.client.get(url, {'city': self.city1.id})

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'promo/offer_list.html')

        self.assertIn('offers', response.context)
        self.assertEqual(response.context['category'], self.category1)

        # В категории 1 и городе 1 должна быть только Акция 1
        # Проверяем количество объектов на текущей странице
        self.assertEqual(len(response.context['offers']), 1) # <-- Исправлено
        self.assertEqual(response.context['offers'][0].title, 'Акция 1')

        # Проверяем содержимое HTML
        self.assertContains(response, "Акция 1")
        self.assertNotContains(response, "Акция 3") # Акция 3 в другом городе


    def test_offer_detail_view(self):
        """
        Тест представления offer_detail (детали акции).
        """
        # Предполагаем, что в urls.py есть маршрут типа path('offer/<int:offer_id>/', views.offer_detail, name='offer_detail')
        url = reverse('offer_detail', args=[self.offer1.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'promo/offer_detail.html')

        self.assertIn('offer', response.context)
        self.assertEqual(response.context['offer'], self.offer1)
        self.assertEqual(response.context['offer'].title, "Акция 1")

        # Проверяем наличие заголовка и описания в HTML
        self.assertContains(response, "Акция 1")
        self.assertContains(response, "Desc 1") # <-- Исправлено на фактическое описание


    def test_search_view(self):
        """
        Тест представления search (поиск акций).
        """
        # Предполагаем, что в urls.py есть маршрут типа path('search/', views.search, name='search')
        url = reverse('search')
        # Передаем GET параметр 'q' для поиска
        response = self.client.get(url, {'q': 'Акция 2'})

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'promo/search_results.html')

        self.assertIn('offers', response.context)
        self.assertIn('query', response.context)
        self.assertEqual(response.context['query'], 'Акция 2')

        # Ожидаем найти только Акцию 2
        # Проверяем количество объектов на текущей странице
        self.assertEqual(len(response.context['offers']), 1) # <-- Исправлено
        self.assertEqual(response.context['offers'][0].title, 'Акция 2')

        # Проверяем содержимое HTML
        self.assertContains(response, "Акция 2")
        self.assertNotContains(response, "Акция 1")




    # Можно добавить тесты для edge-кейсов:
    def test_offer_detail_not_found(self):
        """
        Тест получения деталей несуществующей акции.
        """
        # Предполагаем, что в urls.py есть маршрут типа path('offer/<int:offer_id>/', views.offer_detail, name='offer_detail')
        url = reverse('offer_detail', args=[999]) # Несуществующий ID
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404) # Ожидаем 404 Not Found


# Тесты для API представлений
class OfferAPITestCase(APITestCase):
    """
    Тесты для API акций.
    """
    def setUp(self):
        """
        Подготовка данных для тестов.
        Создаем тестовые объекты City, Category, Partner, Offer.
        """
        self.client = APIClient()

        # Создаем тестовые данные
        self.city1 = City.objects.create(name="Город 1 API")
        self.city2 = City.objects.create(name="Город 2 API")
        self.category1 = Category.objects.create(name="Категория 1 API")
        self.category2 = Category.objects.create(name="Категория 2 API")
        self.partner1 = Partner.objects.create(name="Партнер 1 API", description="Описание 1 API")
        self.partner2 = Partner.objects.create(name="Партнер 2 API", description="Описание 2 API")

        # Создаем тестовые акции
        self.offer1 = Offer.objects.create(
            title="Акция 1 API",
            description="Описание акции 1 API",
            discount="10", # Используем число, если фильтр ожидает число
            promo_code="PROMO1_API",
            valid_from=date.today(),
            valid_to=date.today() + timedelta(days=30),
            city=self.city1,
            category=self.category1,
            partner=self.partner1
        )
        self.offer2 = Offer.objects.create(
            title="Акция 2 API",
            description="Описание акции 2 API",
            discount="20",
            promo_code="PROMO2_API",
            valid_from=date.today() - timedelta(days=10),
            valid_to=date.today() + timedelta(days=20),
            city=self.city1,
            category=self.category2,
            partner=self.partner2
        )
        # Акция неактивна на дату теста
        self.offer3 = Offer.objects.create(
            title="Акция 3 API",
            description="Описание акции 3 API",
            discount="30",
            promo_code="PROMO3_API",
            valid_from=date.today() + timedelta(days=5),
            valid_to=date.today() + timedelta(days=15),
            city=self.city2,
            category=self.category1,
            partner=self.partner1
        )

        # Определяем URL для ViewSet
        self.list_url = reverse('offer-list') # Имя маршрута из router
        self.detail_url = lambda pk: reverse('offer-detail', args=[pk]) # Имя маршрута для деталей
        self.active_offers_url = reverse('offer-active') # Имя маршрута для action 'active'
        # self.expiring_soon_url = reverse('offer-expiring-soon') # Имя маршрута для action 'expiring_soon'

    # Тесты для API (CRUD)
    def test_list_offers(self):
        """
        Тест получения списка акций через API.
        """
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 3)
        self.assertEqual(len(response.data['results']), 3)
        offer_titles = [item['title'] for item in response.data['results']]
        self.assertIn('Акция 1 API', offer_titles)
        self.assertIn('Акция 2 API', offer_titles)
        self.assertIn('Акция 3 API', offer_titles)


    def test_retrieve_offer(self):
        """
        Тест получения деталей конкретной акции через API.
        """
        response = self.client.get(self.detail_url(self.offer1.id))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['title'], 'Акция 1 API')
        self.assertEqual(response.data['discount'], '10') # Сверяем с числом в setUp
        self.assertEqual(response.data['city']['name'], 'Город 1 API')
        self.assertTrue(response.data['is_active'])
        self.assertIsNotNone(response.data['days_left'])


    def test_create_offer(self):
        """
        Тест создания новой акции через API.
        """
        new_offer_data = {
            'title': 'Новая Акция API',
            'description': 'Описание новой акции API',
            'discount': '50',
            'promo_code': 'NEW50_API',
            'valid_from': date.today().isoformat(),
            'valid_to': (date.today() + timedelta(days=60)).isoformat(),
            'city_id': self.city2.id,
            'category_id': self.category2.id,
            'partner_id': self.partner2.id
        }
        response = self.client.post(self.list_url, new_offer_data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Offer.objects.count(), 4)
        created_offer = Offer.objects.get(id=response.data['id'])
        self.assertEqual(created_offer.title, 'Новая Акция API')
        self.assertEqual(created_offer.city, self.city2)


    def test_update_offer(self):
        """
        Тест полного обновления акции (PUT) через API.
        """
        updated_data = {
            'title': 'Обновленная Акция 1 API',
            'description': 'Новое описание акции 1 API',
            'discount': '15',
            'promo_code': 'UPDATED1_API',
            'valid_from': (date.today() - timedelta(days=5)).isoformat(),
            'valid_to': (date.today() + timedelta(days=35)).isoformat(),
            'city_id': self.city2.id,
            'category_id': self.category1.id,
            'partner_id': self.partner1.id,
        }
        response = self.client.put(self.detail_url(self.offer1.id), updated_data, format='json')
        self.assertEqual(response.status_code, 200)
        self.offer1.refresh_from_db()
        self.assertEqual(self.offer1.title, 'Обновленная Акция 1 API')
        self.assertEqual(self.offer1.city, self.city2)

    def test_partial_update_offer(self):
        """
        Тест частичного обновления акции (PATCH) через API.
        """
        partial_data = {
            'discount': '25', # Обновляем только скидку
        }
        response = self.client.patch(self.detail_url(self.offer2.id), partial_data, format='json')
        self.assertEqual(response.status_code, 200)
        self.offer2.refresh_from_db()
        self.assertEqual(self.offer2.discount, '25')
        self.assertEqual(self.offer2.title, 'Акция 2 API')


    def test_delete_offer(self):
        """
        Тест удаления акции через API.
        """
        response = self.client.delete(self.detail_url(self.offer3.id))
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Offer.objects.count(), 2)
        with self.assertRaises(ObjectDoesNotExist):
            Offer.objects.get(id=self.offer3.id)

    # Тесты для API (фильтрация, поиск, сортировка)
    def test_filter_offers_by_city(self):
        """
        Тест фильтрации акций по городу через API.
        """
        response = self.client.get(self.list_url, {'city': self.city1.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 2)
        offer_titles = [item['title'] for item in response.data['results']]
        self.assertIn('Акция 1 API', offer_titles)
        self.assertIn('Акция 2 API', offer_titles)
        self.assertNotIn('Акция 3 API', offer_titles)

    def test_filter_offers_by_active(self):
        """
        Тест фильтрации акций по активности через API.
        """
        response = self.client.get(self.list_url, {'active': 'true'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 2)
        offer_titles = [item['title'] for item in response.data['results']]
        self.assertIn('Акция 1 API', offer_titles)
        self.assertIn('Акция 2 API', offer_titles)
        self.assertNotIn('Акция 3 API', offer_titles)

    def test_search_offers(self):
        """
        Тест поиска акций по названию через API.
        """
        response = self.client.get(self.list_url, {'search': 'Акция 1 API'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['title'], 'Акция 1 API')

    def test_order_offers(self):
        """
        Тест сортировки акций по скидке (по возрастанию) через API.
        """
        response = self.client.get(self.list_url, {'ordering': 'discount'})
        self.assertEqual(response.status_code, 200)
        # Проверяем порядок акций по скидке: 10, 20, 30
        discounts = [int(item['discount'].strip('%')) if isinstance(item['discount'], str) and item['discount'].endswith('%') else int(item['discount']) for item in response.data['results']]
        self.assertEqual(discounts, [10, 20, 30])


    # Тесты для дополнительных действий (actions)
    def test_list_active_offers_action(self):
        """
        Тест эндпоинта /api/offers/active/
        """
        response = self.client.get(self.active_offers_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)
        offer_titles = [item['title'] for item in response.data]
        self.assertIn('Акция 1 API', offer_titles)
        self.assertIn('Акция 2 API', offer_titles)
        self.assertNotIn('Акция 3 API', offer_titles)








