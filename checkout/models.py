import uuid
from decimal import Decimal
from django.db import models
from django.db.models import Sum
from django.conf import settings
from django_countries.fields import CountryField
from products.models import Product
from profiles.models import UserProfile


def generate_order_number():
    """
    Generate a random, unique order number using UUID.
    """
    return uuid.uuid4().hex.upper()


class Order(models.Model):
    order_number = models.CharField(
        max_length=32, 
        null=False, 
        editable=False, 
        unique=True, 
        default=generate_order_number
    )
    user_profile = models.ForeignKey(
        UserProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders'
    )
    full_name = models.CharField(max_length=50, null=False, blank=False)
    email = models.EmailField(max_length=254, null=False, blank=False)
    phone_number = models.CharField(max_length=20, null=False, blank=False)
    country = CountryField(blank_label='Country *', null=False, blank=False, max_length=80)
    postcode = models.CharField(max_length=20, null=True, blank=True)
    town_or_city = models.CharField(max_length=40, null=False, blank=False)
    street_address1 = models.CharField(max_length=80, null=False, blank=False)
    street_address2 = models.CharField(max_length=80, null=True, blank=True)
    county = models.CharField(max_length=80, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)

    delivery_cost = models.DecimalField(max_digits=6, decimal_places=2, null=False, default=0)
    order_total = models.DecimalField(max_digits=10, decimal_places=2, null=False, default=0)
    grand_total = models.DecimalField(max_digits=10, decimal_places=2, null=False, default=0)

    original_cart = models.TextField(null=False, blank=False, default="{}")
    payment_intent_id = models.CharField(
        max_length=255, 
        unique=True, 
        null=True,  
        blank=True, 
        db_index=True
    )

    def update_total(self):
        """
        Update grand total each time a line item is added, including delivery.
        """
        self.order_total = self.lineitems.aggregate(
            total=Sum('lineitem_total')
        )['total'] or Decimal(0)

        if self.order_total < Decimal(settings.FREE_DELIVERY_THRESHOLD):
            self.delivery_cost = self.order_total * Decimal(settings.STANDARD_DELIVERY_PERCENTAGE) / Decimal(100)
        else:
            self.delivery_cost = Decimal(0)

        self.grand_total = self.order_total + self.delivery_cost
        self.save()

    def __str__(self):
        return f"Order {self.order_number} by {self.full_name}"

class OrderLineItem(models.Model):
    order = models.ForeignKey(
        Order, null=False, blank=False, on_delete=models.CASCADE, related_name='lineitems'
    )
    product = models.ForeignKey(Product, null=False, blank=False, on_delete=models.CASCADE)
    product_size = models.CharField(max_length=10, null=True, blank=True)
    product_price = models.DecimalField(max_digits=10, decimal_places=2, null=False, blank=False)  # ✅ Stores price at order time
    quantity = models.PositiveIntegerField(null=False, blank=False, default=1)
    lineitem_total = models.DecimalField(max_digits=10, decimal_places=2, null=False, blank=False, editable=False)

    def save(self, *args, **kwargs):
        """
        Save the product price at the time of order to prevent price changes from affecting past orders.
        """
        if not self.pk:  # Only set product_price for new items
            self.product_price = self.product.price
        self.lineitem_total = self.product_price * Decimal(self.quantity)
        super().save(*args, **kwargs)
        self.order.update_total()

    def __str__(self):
        return f'{self.product.name} (x{self.quantity}) in Order {self.order.order_number}'
