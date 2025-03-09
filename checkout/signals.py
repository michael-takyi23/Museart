import json
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order, OrderLineItem

@receiver(post_save, sender=Order)
def create_order_line_items(sender, instance, created, **kwargs):
    """
    Create order line items after an order is saved.
    """
    if created:
        cart_items = json.loads(instance.original_cart)  # Get cart_items passed from the view
        for item in cart_items:
            OrderLineItem.objects.create(
                order=instance,
                product=item['product'],
                quantity=item['quantity'],
                lineitem_total=item['total'],
            )
