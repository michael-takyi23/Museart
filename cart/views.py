from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.contrib import messages
from products.models import Product
from django.views.decorators.http import require_POST
from django.http import JsonResponse
import logging
import json  # Ensure JSON parsing

logger = logging.getLogger(__name__)

# View Cart
def view_cart(request):
    """ A view to render the shopping cart page """
    cart = request.session.get('cart', {})

    cart_items = []
    for item_id, item_data in cart.items():
        product = get_object_or_404(Product, id=int(item_id))

        if isinstance(item_data, dict) and 'items_by_size' in item_data:
            for size, quantity in item_data['items_by_size'].items():
                cart_items.append({
                    'product': product,
                    'quantity': quantity,
                    'size': size,
                    'subtotal': product.price * quantity
                })
        else:
            cart_items.append({
                'product': product,
                'quantity': item_data,
                'size': None,
                'subtotal': product.price * item_data
            })

    cart_total = sum(item['subtotal'] for item in cart_items)

    context = {
        'cart_items': cart_items,
        'cart_total': cart_total
    }
    return render(request, 'cart/cart.html', context)

# Add to Cart
def add_to_cart(request, item_id):
    """ A view to add a quantity of a product to the shopping cart """
    try:
        product = get_object_or_404(Product, pk=item_id)
        quantity = int(request.POST.get('quantity', 1))
        redirect_url = request.POST.get('redirect_url', '/cart/')
        size = request.POST.get('product_size', None)
        cart = request.session.get('cart', {})

        if quantity <= 0:
            messages.error(request, "Quantity must be at least 1.")
            return redirect(redirect_url)

        if size:
            if str(item_id) not in cart:
                cart[str(item_id)] = {'items_by_size': {}}
            cart[str(item_id)]['items_by_size'][size] = cart[str(item_id)]['items_by_size'].get(size, 0) + quantity
        else:
            cart[str(item_id)] = cart.get(str(item_id), 0) + quantity

        request.session['cart'] = cart
        messages.success(request, f"Added {product.name} to your cart.")
        return redirect(redirect_url)

    except Exception as e:
        logger.error(f"Error adding item {item_id} to cart: {e}")
        messages.error(request, "Failed to add the item to your cart. Please try again.")
        return redirect(request.META.get('HTTP_REFERER', '/'))

# Remove from Cart
@require_POST
def remove_from_cart(request, item_id):
    """ Remove an item from the cart stored in the session """
    try:
        cart = request.session.get('cart', {})

        if str(item_id) in cart:
            del cart[str(item_id)]
            request.session['cart'] = cart  # Save updated cart

            # Calculate new total
            cart_total = sum(get_object_or_404(Product, id=int(pid)).price * qty for pid, qty in cart.items() if isinstance(qty, int))

            return JsonResponse({'success': True, 'cart_total': float(cart_total)}, status=200)

        return JsonResponse({'error': 'Item not found in cart.'}, status=404)

    except Exception as e:
        logger.error(f"Error removing item {item_id} from cart: {e}")
        return JsonResponse({'error': 'Failed to remove item.'}, status=500)

# Update Cart Item Quantity
@require_POST
def update_cart(request, item_id):
    """ Update item quantity in the cart stored in the session """
    try:
        data = json.loads(request.body)
        quantity = int(data.get('quantity', 1))

        if quantity < 1:
            return JsonResponse({'error': 'Quantity must be at least 1.'}, status=400)

        cart = request.session.get('cart', {})

        if str(item_id) in cart:
            cart[str(item_id)] = quantity
            request.session['cart'] = cart  # Save cart session

            product = get_object_or_404(Product, id=item_id)
            item_subtotal = product.price * quantity
            cart_total = sum(get_object_or_404(Product, id=int(pid)).price * qty for pid, qty in cart.items() if isinstance(qty, int))

            return JsonResponse({
                'item_subtotal': float(item_subtotal),
                'cart_total': float(cart_total),
            }, status=200)

        return JsonResponse({'error': 'Item not found in cart.'}, status=404)

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid data format.'}, status=400)
    except Exception as e:
        logger.error(f"Error updating cart: {e}")
        return JsonResponse({'error': 'Failed to update cart.'}, status=500)

# Confirm Order
def confirm_order(request):
    """ A view to confirm the order """
    try:
        request.session['cart'] = {}  # Clear cart after order confirmation
        messages.success(request, 'Your order has been confirmed!')
        return redirect('order_confirmation_page')

    except Exception as e:
        logger.error(f"Error confirming order: {e}")
        messages.error(request, "Failed to confirm your order. Please try again.")
        return redirect('cart')
