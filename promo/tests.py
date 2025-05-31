from django.test import TestCase, Client
from django.urls import reverse
from .models import City, Category, Partner, Offer
from datetime import date, timedelta

# Create your tests here.

class ModelsTest(TestCase):
    def setUp(self):
        self.city = City.objects.create(name="Уфа")
        self.category = Category.objects.create(name="Рестораны")
        self.partner = Partner.objects.create(
            name="Test Partner",
            description="Test Description"
        )
        self.offer = Offer.objects.create(
            title="Test Offer",
            description="Test Description",
            discount="20%",
            promo_code="TEST20",
            valid_from=date.today(),
            valid_to=date.today() + timedelta(days=30),
            city=self.city,
            category=self.category,
            partner=self.partner
        )

    def test_city_creation(self):
        self.assertEqual(self.city.name, "Уфа")

    def test_category_creation(self):
        self.assertEqual(self.category.name, "Рестораны")

    def test_partner_creation(self):
        self.assertEqual(self.partner.name, "Test Partner")

    def test_offer_creation(self):
        self.assertEqual(self.offer.title, "Test Offer")
        self.assertEqual(self.offer.discount, "20%")

class ViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.city = City.objects.create(name="Уфа")
        self.category = Category.objects.create(name="Рестораны")
        self.partner = Partner.objects.create(
            name="Test Partner",
            description="Test Description"
        )
        self.offer = Offer.objects.create(
            title="Test Offer",
            description="Test Description",
            discount="20%",
            promo_code="TEST20",
            valid_from=date.today(),
            valid_to=date.today() + timedelta(days=30),
            city=self.city,
            category=self.category,
            partner=self.partner
        )

    def test_index_view(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'promo/index.html')
        self.assertContains(response, "Test Offer")

    def test_index_view_with_filters(self):
        response = self.client.get(f'{reverse("index")}?city={self.city.id}&category={self.category.id}')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Offer")
