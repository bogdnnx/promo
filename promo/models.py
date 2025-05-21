# models.py
from django.db import models

class City(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["id"]

class Category(models.Model):
    name = models.CharField(max_length=100)
    icon = models.ImageField(upload_to='category_icons/', null=True, blank=True)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return self.name

class Partner(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    #logo = models.ImageField(upload_to='partner_logos/', null=True, blank=True)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return self.name

class Offer(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    discount = models.CharField(max_length=50)
    promo_code = models.CharField(max_length=50, blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    partner = models.ForeignKey(Partner, on_delete=models.CASCADE)
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    valid_from = models.DateField()
    valid_to = models.DateField()
    image = models.ImageField(upload_to='offer_images/', null=True, blank=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ["id"]
