from django.db import models
from django.contrib.auth.models import User
from djmoney.models.fields import MoneyField

# Category
# Product
# Address
# Buyer
# Seller
# Payment
# Shipment

class Category(models.Model):

    class Meta:
        verbose_name_plural = 'Categories'
        
    name = models.CharField(max_length=254)
    description = models.TextField()

    def _str_(self):
        return self.name

class Product(models.Model):
    category = models.ForeignKey('category', null=True, blank=True, on_delete=models.CASCADE)
    Sku = models.CharField(max_length=254, null=True, blank=True)
    name = models.CharField(max_length=254)
    description = models.TextField()
    price = models.DecimalField(decimal_places=2, default=0, max_digits=6)
    rating = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    image_url = models.URLField(max_length=1024, null=True, blank=True)
    image = models.ImageField(null=True, blank=True)

    def __str__(self):
        return self.name            


class Address(models.Model):
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    country = models.CharField(max_length=255)
    postal_code = models.CharField(max_length=20)

    def __str__(self):
        return f'{self.street}, {self.city}, {self.state}, {self.country}, {self.postal_code}'


class Buyer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    default_shipping_address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, related_name='buyer_shipping_address')
    default_billing_address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, related_name='buyer_billing_address')


class Seller(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)


class Order(models.Model):
    buyer = models.ForeignKey(Buyer, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    order_date = models.DateTimeField(auto_now_add=True)


class Payment(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    amount_paid = MoneyField(decimal_places=2, default=0, default_currency='EUR', max_digits=12)
    payment_date = models.DateTimeField(auto_now_add=True)


class Shipment(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    address = models.ForeignKey(Address, on_delete=models.CASCADE)
    tracking_number = models.CharField(max_length=100)
    shipment_date = models.DateTimeField(auto_now_add=True)
