import stripe
import logging
import json
import time
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.http import JsonResponse, HttpResponse
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .forms import OrderForm
from .models import Order, OrderLineItem, generate_order_number
from products.models import Product
from profiles.models import UserProfile
from cart.contexts import cart_contents

# Initialize logger
logger = logging.getLogger(__name__)

# ✅ Stripe API key configuration
stripe.api_key = settings.STRIPE_SECRET_KEY


def checkout(request):
    """
    Checkout view to process Stripe payments and create orders.
    """
    stripe_public_key = settings.STRIPE_PUBLIC_KEY

    cart = request.session.get("cart", {})

    if not cart:
        messages.error(request, "Your cart is empty. Please add items before checking out.")
        return redirect("view_cart")

    # ✅ Generate a REAL order number instead of "PENDING"
    order_number = generate_order_number()

    # ✅ Calculate total & create PaymentIntent
    cart_data = cart_contents(request)
    total = cart_data["grand_total"]
    stripe_total = round(total * 100)

    try:
        order_number = generate_order_number()
        intent = stripe.PaymentIntent.create(
            amount=stripe_total,
            currency=settings.STRIPE_CURRENCY,
            metadata={
                "order_number": order_number,
                "email": request.POST.get("email", request.user.email if request.user.is_authenticated else ""),
            },
        )
        client_secret = intent.client_secret
        logger.info(f"🟢 Stripe PaymentIntent Created: {intent.id} with order number {order_number}")

    except stripe.error.StripeError as e:
        logger.error(f"🔴 Stripe Payment Error: {e}")
        messages.error(request, f"Payment error: {e.user_message}")
        return redirect("view_cart")

    if request.method == "POST":
        print("TEST ____ request.method == POST - pre-save Order")
        order_form = OrderForm(request.POST)

        if order_form.is_valid():
            order = order_form.save(commit=False)
            order.email = order_form.cleaned_data.get("email")
            order.payment_intent_id = request.POST.get("client_secret").split("_secret")[0]  # ✅ Store PaymentIntent
            order.original_cart = json.dumps(cart_data["cart_items"])
            order.delivery_cost = 50.00
            order.grand_total = order.order_total + order.delivery_cost
            order.save()

            stripe.PaymentIntent.modify(
                order.payment_intent_id,
                metadata={
                    "order_number": order.order_number,
                    "cart": json.dumps(cart_data["cart_items"]),
                },
            )

            return JsonResponse({
                "success": True,
                "order_number": order.order_number,
                "redirect_url": reverse("checkout_success", args=[order.order_number]),
            })
        else:
            messages.error(request, "Error in checkout form")

    else:
        if request.user.is_authenticated:
            try:
                profile = UserProfile.objects.get(user=request.user)
                order_form = OrderForm(initial={
                    'full_name': profile.user.get_full_name(),
                    'email': profile.user.email,
                    'phone_number': profile.default_phone_number,
                    'country': profile.default_country,
                    'postcode': profile.default_postcode,
                    'town_or_city': profile.default_town_or_city,
                    'street_address1': profile.default_street_address1,
                    'street_address2': profile.default_street_address2,
                    'county': profile.default_county,
                })
            except UserProfile.DoesNotExist:
                order_form = OrderForm()
        else:
            order_form = OrderForm()

    return render(
        request,
        "checkout/checkout.html",
        {
            "order_form": order_form,
            "stripe_public_key": stripe_public_key,
            "client_secret": client_secret,
            "order_number": order_number,
        },
    )


@require_POST
def cache_checkout_data(request):
    """
    Store checkout data in the PaymentIntent metadata.
    """
    try:
        pid = request.POST.get("client_secret").split("_secret")[0]
        stripe.PaymentIntent.modify(
            pid,
            metadata={
                "cart": json.dumps(request.session.get("cart", {})),
                "save_info": request.POST.get("save_info"),
                "username": str(request.user),
            },
        )
        return HttpResponse(status=200)
    except Exception as e:
        logger.error(f"Cache Checkout Data Error: {e}")
        return HttpResponse(content=str(e), status=400)


def checkout_success(request, order_number):
    """
    Handle successful checkouts and redirect to order confirmation.
    """
    print(f"🔍 Searching for Order Number: {order_number}")

    # Try to fetch the order
    order = get_object_or_404(Order, order_number=order_number)
    
    if not order:
        print(f"🚨 ERROR: Order {order_number} NOT FOUND in `checkout_success`!")
        return HttpResponse(f"Order {order_number} not found!", status=404)

    print(f"✅ Order found: {order}")

    # ✅ Clear cart session
    request.session.pop("cart", None)
    request.session.modified = True

    messages.success(request, f"🎉 Order processed! Order No: {order_number}")

    return redirect(reverse("order_confirmation", args=[order_number]))

    """
    Handle successful checkouts and redirect to order confirmation.
    """
    order = get_object_or_404(
        Order.objects.prefetch_related("lineitems", "user_profile"),
        order_number=order_number,
    )

    # ✅ Clear cart session
    request.session.pop("cart", None)
    request.session.modified = True

    messages.success(request, f"🎉 Order processed! Order No: {order_number}")

    return redirect(reverse("order_confirmation", args=[order_number]))


def send_order_confirmation(order):
    """
    Sends an order confirmation email.
    """
    subject = f"Order Confirmation - {order.order_number}"
    message = render_to_string(
        "checkout/order_confirmation_email.html", {"order": order}
    )
    email = EmailMessage(
        subject=subject,
        body=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[order.email],
    )
    email.content_subtype = "html"
    email.send()


def get_order_number(request):
    """
    Fetch the order number using the payment intent ID.
    """
    payment_intent_id = request.GET.get("payment_intent")

    if not payment_intent_id:
        return JsonResponse({"error": "Missing payment intent ID"}, status=400)

    logger.info(f"🔍 Searching for order with PaymentIntent ID: {payment_intent_id}")

    # ✅ Wait up to **30 seconds** for the order to be created
    for attempt in range(30):
        try:
            # order = get_object_or_404(Order, payment_intent_id=payment_intent_id)
            order = Order.objects.select_related("user_profile").get(
                payment_intent_id=payment_intent_id
            )
            logger.info(
                f"✅ Order {order.order_number} found for PaymentIntent: {payment_intent_id}"
            )

            return JsonResponse({
                "success": True,
                "redirect_url": reverse("checkout_success", args=[order.order_number]),
            })
        except Order.DoesNotExist:
            logger.warning(f"⚠️ Order not found yet. Retrying... ({attempt+1}/30)")
            time.sleep(1)

    logger.error(f"🚨 Order NOT FOUND after retries for PaymentIntent: {payment_intent_id}")
    return JsonResponse({"error": "Order not found"}, status=404)


@csrf_exempt
def stripe_webhook(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    endpoint_secret = settings.STRIPE_WH_SECRET

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except (ValueError, stripe.error.SignatureVerificationError) as e:
        logger.error(f"⚠️ Webhook Error: {e}")
        return HttpResponse(status=400)

    logger.info(f"Webhook Event Received: {json.dumps(event, indent=2)}")

    if event['type'] == 'payment_intent.succeeded':
        print("----------------- payment_intent.succeeded !!!!!!!!!!!!!!!!")
        intent = event.get('data', {}).get('object', {})
        payment_intent_id = intent.get('id')
        order_number = intent.get('metadata', {}).get('order_number')
        email = intent.get('metadata', {}).get('email', None)  # ✅ Ensure email is captured

        if order_number == "PENDING":  # Prevent saving 'PENDING' as the order number
            order_number = generate_order_number()  # Generate a new order number

        logger.info(f"💰 Payment Succeeded for PaymentIntent: {payment_intent_id}")
        logger.info(f"🔎 Looking for Order Number: {order_number}")

        if not order_number:
            logger.error(f"🚨 No Order Number found in metadata for PaymentIntent {payment_intent_id}")
            return HttpResponse(status=200)

        # ✅ Try to find the order first
        try:
            order = Order.objects.get(order_number=order_number)
            order.payment_intent_id = payment_intent_id
            order.save()
            logger.info(f"✅ Order {order.order_number} updated with Stripe PaymentIntent")
        except Order.DoesNotExist:
            logger.warning(f"⚠️ Order {order_number} NOT FOUND! Creating a new one...")

            # ✅ Check if email exists before creating order
            if not email:
                logger.error(f"🚨 Cannot create order: Missing email for PaymentIntent {payment_intent_id}")
                return HttpResponse(status=400)  # Bad request - missing required fields

            # ✅ Create Order with Correct Data
            order = Order.objects.create(
                order_number=order_number,
                payment_intent_id=payment_intent_id,
                order_total=intent.get("amount") / 100,  # Convert cents to dollars
                grand_total=intent.get("amount") / 100,
                email=email,
                original_cart=json.dumps(intent.get("metadata", {}).get("cart", {})),
            )
            logger.info(f"✅ Order {order.order_number} has been CREATED.")

        send_order_confirmation(order)

    return HttpResponse(status=200)

