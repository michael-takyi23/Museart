from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import User
from djmoney.models.fields import MoneyField
from django.core.exceptions import ValidationError


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
    stock = models.IntegerField(default=0) 

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


def get_default_end_date():
    return timezone.now().date() + timedelta(days=14)


class SpecialOffer(models.Model):
    product = models.ForeignKey("Product", on_delete=models.CASCADE)
    discount_percentage = models.FloatField()
    active = models.BooleanField(default=True)

    def discount(self):
        """Returns the discount percentage as a formatted string."""
        return f"{self.discount_percentage}%"

    discount.short_description = "Discount"  # Admin column name

    start_date = models.DateField(default=timezone.now)  # ✅ Works fine
    end_date = models.DateField(default=get_default_end_date)  # ✅ Uses a function Django can serialize

    def is_live(self):
        """Returns True if the current date falls within the special offer period."""
        right_now = timezone.now().date()
        return self.start_date <= right_now <= self.end_date

    def clean(self):
        """Validates that the start date is before the end date."""
        if self.start_date > self.end_date:
            raise ValidationError("Start date can't be after end date!")

    def __str__(self):
        return f'Offer: {self.product} - {self.discount_percentage}% off until {self.end_date}'