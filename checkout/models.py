import uuid
from django.db import models
from django.db.models import Sum
from django.conf import settings
from django_countries.fields import CountryField

from products.models import Product
from profiles.models import UserProfile
from cart.contexts import cart_contents


# ✅ Function to generate unique order numbers (move it outside the model)
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
    
    original_cart = models.TextField(null=False, blank=False, default="{}")  # ✅ Ensures cart data is stored  
    stripe_payment_intent = models.CharField(
        max_length=255, 
        unique=True, 
        null=True,  
        blank=True
    )

    def update_total(self):
        """
        Update grand total each time a line item is added,
        accounting for delivery costs.
        """
        self.order_total = self.lineitems.aggregate(
            Sum('lineitem_total')
        )['lineitem_total__sum'] or 0

        if self.order_total < settings.FREE_DELIVERY_THRESHOLD:
            self.delivery_cost = self.order_total * settings.STANDARD_DELIVERY_PERCENTAGE / 100
        else:
            self.delivery_cost = 0

        self.grand_total = self.order_total + self.delivery_cost
        self.save()

    def save(self, *args, **kwargs):
        """
        Override the original save method to set the order number
        if it hasn't been set already.
        """
        if not self.order_number:
            self.order_number = generate_order_number()  # ✅ Correct reference
        super().save(*args, **kwargs)

    def __str__(self):
        return self.order_number


class OrderLineItem(models.Model):
    order = models.ForeignKey(
        Order, null=False, blank=False, on_delete=models.CASCADE, related_name='lineitems'
    )
    product = models.ForeignKey(Product, null=False, blank=False, on_delete=models.CASCADE)
    product_size = models.CharField(max_length=10, null=True, blank=True)
    quantity = models.IntegerField(null=False, blank=False, default=0)
    lineitem_total = models.DecimalField(max_digits=6, decimal_places=2, null=False, blank=False, editable=False)

    def save(self, *args, **kwargs):
        """
        Override the save method to set the lineitem total and update the order total.
        """
        self.lineitem_total = self.product.price * self.quantity
        super().save(*args, **kwargs)
        self.order.update_total()  # ✅ Ensure order total is updated when a line item is added

    def __str__(self):
        return f'Product {self.product.name} on order {self.order.order_number}'
