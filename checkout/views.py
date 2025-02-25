import stripe
import logging
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.http import JsonResponse, HttpResponse
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from .forms import OrderForm
from .models import Order, OrderLineItem
from products.models import Product
from cart.contexts import cart_contents

# Initialize logger
logger = logging.getLogger(__name__)

# ✅ Send email function
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
    Checkout view to process Stripe payments and create orders.
    """
    stripe_public_key = settings.STRIPE_PUBLIC_KEY if settings.DEBUG else settings.STRIPE_LIVE_PUBLIC_KEY
    stripe.api_key = settings.STRIPE_SECRET_KEY if settings.DEBUG else settings.STRIPE_LIVE_SECRET_KEY

    cart = request.session.get('cart', {})

    if not cart:
        messages.error(request, "Your cart is empty. Please add items before checking out.")
        return redirect('view_cart')

    try:
        cart_total = cart_contents(request)['grand_total']
        stripe_total = int(cart_total * 100)  # Convert to cents

        # ✅ Create Stripe PaymentIntent
        intent = stripe.PaymentIntent.create(
            amount=stripe_total,
            currency=settings.STRIPE_CURRENCY,
            metadata={'integration_check': 'accept_a_payment'},
        )
        client_secret = intent.client_secret

    except stripe.error.StripeError as e:
        logger.error(f"Stripe Payment Error: {e}")
        messages.error(request, f"Payment error: {str(e)}")
        return redirect('view_cart')

    if request.method == "POST":
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.delivery_cost = 50.00
            order.grand_total = order.order_total + order.delivery_cost
            order.save()

            # ✅ Create OrderLineItems
            for item_id, quantity in cart.items():
                product = get_object_or_404(Product, id=item_id)
                OrderLineItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                    lineitem_total=product.price * quantity
                )

            # ✅ Send order confirmation email
            send_order_confirmation(order)

            return JsonResponse({
                'success': True,
                'order_number': order.order_number,
                'redirect_url': reverse('order_confirmation', args=[order.order_number])
            })

        else:
            messages.error(request, "Invalid form submission. Please check your details.")

    else:
        form = OrderForm()

    context = {
        'form': form,
        'stripe_public_key': stripe_public_key,
        'client_secret': client_secret,
    }
    return render(request, 'checkout/checkout.html', context)


def order_confirmation(request, order_number):
    """
    View to display the order confirmation page after successful payment.
    """
    order = get_object_or_404(Order, order_number=order_number)

    # ✅ Clear cart only after successful order confirmation
    request.session.pop('cart', None)

    return render(request, 'checkout/order_confirmation.html', {'order': order})


@csrf_exempt
def stripe_webhook(request):
    """
    Stripe webhook to handle post-payment events.
    """
    stripe.api_key = settings.STRIPE_SECRET_KEY if settings.DEBUG else settings.STRIPE_LIVE_SECRET_KEY

    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except ValueError as e:
        logger.error(f"⚠️ Invalid Payload: {e}")
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"❌ Webhook signature verification failed: {e}")
        return HttpResponse(status=400)

    # ✅ Handle successful payment event
    if event['type'] == 'payment_intent.succeeded':
        intent = event['data']['object']
        logger.info(f"✅ Payment Successful: {intent['id']}")

    return HttpResponse(status=200)


def send_test_email(request):
    """
    Function to test email sending.
    """
    EmailMessage(
        subject="Test Email",
        body="This is a test email for Stripe integration.",
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=["museart2024@outlook.com"]
    ).send()
    return HttpResponse('Test email sent successfully.')
