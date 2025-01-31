from decimal import Decimal
from django.conf import settings
from django.shortcuts import get_object_or_404
from products.models import Product
from .utils import calculate_cart_total

def calculate_cart_total(cart):
    """
    Utility function to calculate the cart total.
    This function sums the price of all items in the cart, considering size variations.
    """
    total = 0
    for item_id, item_data in cart.items():
        product = get_object_or_404(Product, pk=item_id)
        # If the item has size-specific quantities
        if isinstance(item_data, dict) and 'items_by_size' in item_data:
            for size, quantity in item_data['items_by_size'].items():
                total += quantity * product.price
        else:
            total += item_data * product.price
    return total


def cart_total_processor(request):
    """
    A context processor to add the cart total to the context globally.
    """
    cart = request.session.get('cart', {})
    total = calculate_cart_total(cart)
    return {'cart_total': total}


def cart_contents(request):
    """
    A context processor to provide detailed information about the cart contents,
    including items, quantities, totals, delivery costs, and thresholds.
    """
    cart = request.session.get('cart', {})

    cart_items = []
    total = 0
    product_count = 0

    for item_id, item_data in cart.items():
        try:
            product = get_object_or_404(Product, pk=item_id)

            if isinstance(item_data, dict) and 'items_by_size' in item_data:
                # If items are stored by size
                for size, quantity in item_data['items_by_size'].items():
                    total += quantity * product.price
                    product_count += quantity
                    cart_items.append({
                        'item_id': item_id,
                        'size': size,
                        'quantity': quantity,
                        'product': product,
                        'subtotal': quantity * product.price,
                    })
            else:
                # If items are stored without size
                total += item_data * product.price
                product_count += item_data
                cart_items.append({
                    'item_id': item_id,
                    'quantity': item_data,
                    'product': product,
                    'subtotal': item_data * product.price,
                })

        except Product.DoesNotExist:
            continue  # Skip invalid product IDs

    # Calculate delivery cost and grand total
    if total < settings.FREE_DELIVERY_THRESHOLD:
        delivery = total * Decimal(settings.STANDARD_DELIVERY_PERCENTAGE / 100)
        free_delivery_delta = settings.FREE_DELIVERY_THRESHOLD - total
    else:
        delivery = 0
        free_delivery_delta = 0

    grand_total = total + delivery

    # Construct the context
    context = {
        'cart_items': cart_items,
        'total': total,
        'product_count': product_count,
        'delivery': delivery,
        'free_delivery_delta': free_delivery_delta,
        'free_delivery_threshold': settings.FREE_DELIVERY_THRESHOLD,
        'grand_total': grand_total,
    }

    return context
