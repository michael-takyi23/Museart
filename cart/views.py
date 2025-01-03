from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.contrib import messages
from products.models import Product
import logging
import json  # Required for parsing JSON data in `update_cart`

logger = logging.getLogger(__name__)

# View Cart
def view_cart(request):
    """ A view to render the shopping cart page """
    cart = request.session.get('cart', {})
    context = {
        'cart': cart,
    }
    return render(request, 'cart/cart.html', context)


# Add to Cart
def add_to_cart(request, item_id):
    """ A view to add a quantity of a product to the shopping cart """
    try:
        product = get_object_or_404(Product, pk=item_id)
        quantity = int(request.POST.get('quantity', 1))
        redirect_url = request.POST.get('redirect_url', '/cart/')
        size = request.POST.get('product_size') if 'product_size' in request.POST else None
        cart = request.session.get('cart', {})

        if quantity <= 0:
            messages.error(request, "Quantity must be at least 1.")
            return redirect(redirect_url)

        # Handle size variations
        if size:
            if item_id in cart:
                cart[item_id]['items_by_size'] = cart[item_id].get('items_by_size', {})
                cart[item_id]['items_by_size'][size] = cart[item_id]['items_by_size'].get(size, 0) + quantity
            else:
                cart[item_id] = {'items_by_size': {size: quantity}}
        else:
            cart[item_id] = cart.get(item_id, 0) + quantity

        request.session['cart'] = cart  # Save session
        messages.success(request, f'Added {product.name} to your cart.')
        return redirect(redirect_url)

    except Exception as e:
        logger.error(f"Error adding item {item_id} to cart: {e}")
        messages.error(request, "Failed to add the item to your cart. Please try again.")
        return redirect(request.META.get('HTTP_REFERER', '/'))


# Remove from Cart
def remove_from_cart(request, item_id):
    """ A view to remove an item from the shopping cart """
    try:
        size = request.POST.get('product_size', None)
        cart = request.session.get('cart', {})

        if item_id in cart:
            if size:
                if 'items_by_size' in cart[item_id] and size in cart[item_id]['items_by_size']:
                    del cart[item_id]['items_by_size'][size]
                    if not cart[item_id]['items_by_size']:
                        cart.pop(item_id)
                else:
                    messages.warning(request, 'Item size not found in your cart.')
            else:
                cart.pop(item_id)

            request.session['cart'] = cart  # Save session
            messages.success(request, 'Item removed from your cart.')

            # Return updated cart total
            cart_total = sum(
                item['quantity'] for item_id, item in cart.items() if isinstance(item, dict)
            )
            return JsonResponse({'cart_total': cart_total}, status=200)

        messages.warning(request, 'Item not found in your cart.')
        return HttpResponse(status=404)

    except Exception as e:
        logger.error(f"Error removing item {item_id} from cart: {e}")
        messages.error(request, "Failed to remove the item. Please try again.")
        return HttpResponse(status=500)



# Update Cart
def update_cart(request, item_id):
    """ A view to update the quantity of an item in the shopping cart """
    try:
        cart = request.session.get('cart', {})
        product = get_object_or_404(Product, pk=item_id)
        data = json.loads(request.body.decode('utf-8'))  # Parse JSON data
        size = data.get('size', None)
        quantity = int(data.get('quantity', 1))

        if quantity <= 0:
            return JsonResponse({'error': "Quantity must be greater than zero."}, status=400)

        if size:
            if item_id in cart and 'items_by_size' in cart[item_id]:
                cart[item_id]['items_by_size'][size] = quantity
        else:
            cart[item_id] = quantity

        request.session['cart'] = cart  # Save session
        messages.success(request, f'Updated {product.name} quantity to {quantity}.')

        # Calculate updated totals
        item_subtotal = product.price * quantity
        cart_total = sum(
            item['quantity'] * product.price for item_id, item in cart.items() if isinstance(item, dict)
        )
        return JsonResponse({'item_subtotal': item_subtotal, 'cart_total': cart_total}, status=200)

    except Exception as e:
        logger.error(f"Error updating item {item_id} in cart: {e}")
        return JsonResponse({'error': "Failed to update cart. Please try again."}, status=500)



# Confirm Order
def confirm_order(request):
    """ A view to confirm the order """
    try:
        # Placeholder for order confirmation logic
        request.session['cart'] = {}  # Clear cart after order confirmation
        messages.success(request, 'Your order has been confirmed!')
        return redirect('order_confirmation_page')

    except Exception as e:
        logger.error(f"Error confirming order: {e}")
        messages.error(request, "Failed to confirm your order. Please try again.")
        return redirect('cart')
