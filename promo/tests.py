from rest_framework.test import APITestCase, APIClient
from django.urls import reverse
from django.utils import timezone
from datetime import date, timedelta
from .models import City, Category, Partner, Offer


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
