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

import json
from .forms import OrderForm
from .models import Order, OrderLineItem
from products.models import Product
from cart.contexts import cart_contents  
import time  # ✅ Import time for retry logic

# Initialize logger
logger = logging.getLogger(__name__)


def order_confirmation(request, order_number):
    """
    Display order confirmation page after successful checkout.
    """
    order = get_object_or_404(Order, order_number=order_number)

    context = {
        'order': order,
    }

    return render(request, 'checkout/order_confirmation.html', context)


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
        stripe_total = int(cart_total * 100)

        # ✅ Create Stripe PaymentIntent BEFORE saving the order
        intent = stripe.PaymentIntent.create(
            amount=stripe_total,
            currency=settings.STRIPE_CURRENCY,
            metadata={'order_number': 'PENDING'},
        )
        client_secret = intent.client_secret

        print(f"🟡 Stripe PaymentIntent Created: {intent.id}")

    except stripe.error.StripeError as e:
        logger.error(f"Stripe Payment Error: {e}")
        messages.error(request, f"Payment error: {str(e)}")
        return redirect('view_cart')

    if request.method == "POST":
        print("🟡 Form Submission Detected")  # ✅ Print to confirm POST request
        form = OrderForm(request.POST)

        if form.is_valid():
            print("✅ Order form is valid, proceeding to save order.")

            order = form.save(commit=False)  # ✅ Do not save yet
            order.delivery_cost = 50.00
            order.grand_total = order.order_total + order.delivery_cost
            order.original_cart = json.dumps(cart_contents(request)['cart_items'])  # ✅ Store cart data

            # ✅ Assign Stripe Payment Intent BEFORE saving
            order.stripe_payment_intent = intent.id
            order.save()

            # ✅ Debugging logs
            print(f"✅ Order {order.order_number} saved with PaymentIntent: {order.stripe_payment_intent}")

            # ✅ Update Stripe PaymentIntent metadata
            stripe.PaymentIntent.modify(
                intent.id,
                metadata={'order_number': order.order_number}
            )

            return JsonResponse({
                'success': True,
                'order_number': order.order_number,
                'redirect_url': reverse('order_confirmation', args=[order.order_number])
            })

        else:
            print("❌ Order form is NOT valid!")
            print(form.errors)  # ✅ Print form validation errors
            messages.error(request, "Invalid form submission. Please check your details.")

    else:
        form = OrderForm()

    context = {
        'form': form,
        'stripe_public_key': stripe_public_key,
        'client_secret': client_secret,
    }
    return render(request, 'checkout/checkout.html', context)


def get_order_number(request):
    """Fetch the order number using the payment intent ID."""
    payment_intent_id = request.GET.get("payment_intent")

    if not payment_intent_id:
        return JsonResponse({"error": "Missing payment intent ID"}, status=400)

    # ✅ Retry logic: Wait up to **10 seconds** for the order to be saved before failing
    for attempt in range(10):  # Increased retries
        try:
            order = Order.objects.get(stripe_payment_intent=payment_intent_id)
            print(f"✅ Order {order.order_number} found for PaymentIntent: {payment_intent_id}")
            return JsonResponse({
                "success": True,
                "redirect_url": reverse("order_confirmation", args=[order.order_number])
            })
        except Order.DoesNotExist:
            logger.warning(f"⚠️ Order not found for PaymentIntent: {payment_intent_id}. Retrying... ({attempt+1}/10)")
            time.sleep(1)  # ✅ Wait 1 second before retrying

    # ✅ If we reach here, the order was never found – return a proper JSON response
    logger.error(f"🚨 Order NOT FOUND after retries for PaymentIntent: {payment_intent_id}")
    return JsonResponse({"error": "Order not found"}, status=404)


def checkout_success(request, order_number):
    """
    Handle successful checkouts and redirect to order confirmation.
    """
    order = get_object_or_404(Order, order_number=order_number)

    # ✅ Clear cart session completely
    request.session.pop('cart', None)
    request.session.modified = True  # ✅ Force session save

    messages.success(request, f"🎉 Order processed! Order No: {order_number}")

    return redirect(reverse('order_confirmation', args=[order_number]))


@csrf_exempt
def stripe_webhook(request):
    """
    Stripe webhook to handle post-payment events.
    """
    stripe.api_key = settings.STRIPE_SECRET_KEY if settings.DEBUG else settings.STRIPE_LIVE_SECRET_KEY

    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except ValueError as e:
        logger.error(f"⚠️ Invalid Payload: {e}")
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"❌ Webhook signature verification failed: {e}")
        return HttpResponse(status=400)

    if event['type'] == 'payment_intent.succeeded':
        intent = event['data']['object']
        payment_intent_id = intent.get('id')
        metadata = intent.get('metadata', {})
        order_number = metadata.get('order_number')

        if not order_number:
            logger.error(f"🚨 No Order Number found in webhook metadata for PaymentIntent {payment_intent_id}")
            return HttpResponse(status=200)  # ✅ Return 200 OK so Stripe does not retry endlessly

        try:
            order = Order.objects.get(order_number=order_number)
            order.stripe_payment_intent = payment_intent_id  # ✅ Store Stripe Intent ID
            order.save()
            logger.info(f"✅ Order {order.order_number} successfully updated with Stripe PaymentIntent")
        except Order.DoesNotExist:
            logger.error(f"🚨 Order {order_number} not found in database for webhook processing")
            return HttpResponse(status=200)  # ✅ Avoid failing Stripe retries

        # ✅ Send order confirmation email
        send_order_confirmation(order)

    return HttpResponse(status=200)


