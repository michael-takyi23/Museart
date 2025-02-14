import stripe
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.http import JsonResponse, HttpResponse
from django.urls import reverse
from .forms import OrderForm
from .models import Order, OrderLineItem
from products.models import Product
from cart.contexts import cart_contents


# Send email function
def send_order_confirmation(order):
    subject = f"Order Confirmation - {order.order_number}"
    message = render_to_string('checkout/order_confirmation_email.html', {'order': order})
    email = EmailMessage(
        subject=subject,
        body=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[order.email],
    )
    email.content_subtype = 'html'
    email.send()


def checkout(request):
    """
    Checkout view to process payments and create orders.
    """
    stripe_public_key = settings.STRIPE_PUBLIC_KEY if settings.DEBUG else settings.STRIPE_LIVE_PUBLIC_KEY
    stripe.api_key = settings.STRIPE_SECRET_KEY if settings.DEBUG else settings.STRIPE_LIVE_SECRET_KEY
    
    cart = request.session.get('cart', {})

    if not cart:
        messages.error(request, "Your cart is empty. Please add items before checking out.")
        return redirect('view_cart')

    # Create Stripe PaymentIntent
    try:
        stripe_total = int(cart_contents(request)['grand_total'] * 100)  # Convert to cents
        intent = stripe.PaymentIntent.create(
            amount=stripe_total,
            currency=settings.STRIPE_CURRENCY,
            metadata={'integration_check': 'accept_a_payment'},
        )
        client_secret = intent.client_secret
    except stripe.error.StripeError as e:
        messages.error(request, f"Stripe Error: {str(e)}")
        return redirect('view_cart')
    except Exception as e:
        messages.error(request, f"An unexpected error occurred: {str(e)}")
        return redirect('view_cart')

    # Handle form submission
    if request.method == "POST":
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.delivery_cost = 50.00
            order.grand_total = order.delivery_cost + order.order_total
            order.save()

            # Create OrderLineItems
            for item_id, quantity in cart.items():
                product = Product.objects.get(id=item_id)
                OrderLineItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                    lineitem_total=product.price * quantity
                )

            # Send order confirmation email
            send_order_confirmation(order)

            # DO NOT CLEAR CART UNTIL PAYMENT IS CONFIRMED
            return JsonResponse({'success': True, 'order_number': order.order_number})
        else:
            messages.error(request, "There was an error with your form submission. Please try again.")

    else:
        form = OrderForm()

    context = {
        'form': form,
        'stripe_public_key': stripe_public_key,
        'client_secret': client_secret,
        'success_url': request.build_absolute_uri(reverse('order_confirmation', args=['order_number_placeholder'])),
    }
    return render(request, 'checkout/checkout.html', context)


def order_confirmation(request, order_number):
    """
    View to display the order confirmation page.
    """
    order = get_object_or_404(Order, order_number=order_number)
    
    # Clear the cart only after successful confirmation
    if 'cart' in request.session:
        del request.session['cart']

    return render(request, 'checkout/order_confirmation.html', {'order': order})


def send_test_email(request):
    """
    Function to test email sending.
    """
    EmailMessage(
        subject="Test Email",
        body="This is a test email for Stripe integration.",
        from_email="museart2024@outlook.com",
        to=["museart2024@outlook.com"]
    ).send()
    return HttpResponse('Test email sent successfully.')
