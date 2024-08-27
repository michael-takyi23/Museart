from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order, OrderLineItem
from cart.contexts import cart_contents

@receiver(post_save, sender=Order)
def create_order_line_items(sender, instance, created, **kwargs):
    if created:
        cart_items = cart_contents(instance.request)['cart_items']
        for item in cart_items:
            OrderLineItem.objects.create(
                order=instance,
                product=item['product'],
                quantity=item['quantity'],
                lineitem_total=item['total'],
            )
