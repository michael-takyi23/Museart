from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.contrib import messages
from products.models import Product
from django.views.decorators.http import require_POST
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
        # Safely parse the quantity or default to 1
        quantity = int(request.POST.get('quantity', 1))
        # Default redirect URL if not provided
        redirect_url = request.POST.get('redirect_url', '/cart/')
        # Optional size for the product
        size = request.POST.get('product_size', None)
        # Get or initialize the cart from the session
        cart = request.session.get('cart', {})

        # Check for valid quantity
        if quantity <= 0:
            messages.error(request, "Quantity must be at least 1.")
            return redirect(redirect_url)

        # Add item to cart, handling size variations if applicable
        if size:
            cart[item_id] = cart.get(item_id, {'items_by_size': {}})
            cart[item_id]['items_by_size'][size] = cart[item_id]['items_by_size'].get(size, 0) + quantity
        else:
            cart[item_id] = cart.get(item_id, 0) + quantity

        # Save the updated cart in the session
        request.session['cart'] = cart
        # Show success message and redirect
        messages.success(request, f"Added {product.name} to your cart.")
        return redirect(redirect_url)

    except Exception as e:
        # Log the error and inform the user
        logger.error(f"Error adding item {item_id} to cart: {e}")
        messages.error(request, "Failed to add the item to your cart. Please try again.")
        return redirect(request.META.get('HTTP_REFERER', '/'))



# Remove from Cart
def remove_from_cart(request, item_id):
    """ A view to remove an item from the shopping cart """
    try:
        # Fetch size and cart from session
        size = request.POST.get('product_size', None)
        cart = request.session.get('cart', {})

        if item_id in cart:
            # If size is specified, remove the size-specific entry
            if size and 'items_by_size' in cart[item_id]:
                if size in cart[item_id]['items_by_size']:
                    del cart[item_id]['items_by_size'][size]
                    # If no sizes remain, remove the entire item
                    if not cart[item_id]['items_by_size']:
                        cart.pop(item_id)
                    messages.success(request, f"Removed size {size.upper()} from your cart.")
                else:
                    messages.warning(request, f"Size {size.upper()} not found in your cart.")
            else:
                # Remove the entire item if no size is specified
                cart.pop(item_id)
                messages.success(request, "Item removed from your cart.")
            
            # Save updated cart back to the session
            request.session['cart'] = cart

            # Calculate and return the updated cart total
            cart_total = sum(item['quantity'] for item in cart.values() if isinstance(item, dict))
            return JsonResponse({'cart_total': cart_total}, status=200)

        # If the item was not found in the cart, return a 404 response
        messages.warning(request, "Item not found in your cart.")
        return HttpResponse(status=404)

    except Exception as e:
        # Log the error and return a generic 500 response
        logger.error(f"Error removing item {item_id} from cart: {e}")
        messages.error(request, "Failed to remove the item. Please try again.")
        return HttpResponse(status=500)


# Update Cart Item Quantity
@require_POST
def update_cart(request, item_id):
    try:
        # Parse JSON data from request body
        data = json.loads(request.body)
        quantity = data.get('quantity', 0)
        
        # Validate quantity
        if quantity < 1:
            return JsonResponse({'error': 'Quantity must be at least 1.'}, status=400)
        
        # Get the cart item and update quantity
        cart_item = get_object_or_404(CartItem, product__id=item_id, user=request.user)
        cart_item.quantity = quantity
        cart_item.save()

        # Calculate subtotal and total
        item_subtotal = cart_item.product.price * cart_item.quantity
        cart_total = sum(item.product.price * item.quantity for item in CartItem.objects.filter(user=request.user))
        
        return JsonResponse({
            'item_subtotal': item_subtotal,
            'cart_total': cart_total
        }, status=200)

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid data format.'}, status=400)
    except CartItem.DoesNotExist:
        return JsonResponse({'error': 'Item not found.'}, status=404)
    
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
