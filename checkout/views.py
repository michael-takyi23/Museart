import json
import logging
import time
import stripe

from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .forms import OrderForm
from .models import Order, OrderLineItem, generate_order_number
from products.models import Product
from profiles.models import UserProfile
from profiles.forms import UserProfileForm
from cart.contexts import cart_contents

# Stripe and Logger Setup
stripe.api_key = settings.STRIPE_SECRET_KEY
logger = logging.getLogger(__name__)


# -----------------------------
# POST: Cache Checkout Metadata
# -----------------------------
@require_POST
def cache_checkout_data(request):
    try:
        pid = request.POST.get('client_secret').split('_secret')[0]
        stripe.PaymentIntent.modify(pid, metadata={
            'cart': json.dumps(request.session.get('cart', {})),
            'save_info': request.POST.get('save_info'),
            'username': request.user.username,
        })
        return HttpResponse(status=200)
    except Exception as e:
        return HttpResponse(content=str(e), status=400)


# -----------------------------
# GET/POST: Checkout Page Logic
# -----------------------------
def checkout(request):
    stripe_public_key = settings.STRIPE_PUBLIC_KEY
    cart = request.session.get('cart', {})

    if not cart:
        messages.error(request, "Your cart is empty. Please add items before checking out.")
        return redirect('view_cart')

    order_number = generate_order_number()

    if request.method == 'POST':
        form_data = {field: request.POST[field] for field in [
            'full_name', 'email', 'phone_number', 'country', 'postcode',
            'town_or_city', 'street_address1', 'street_address2', 'county']}

        order_form = OrderForm(form_data)
        if order_form.is_valid():
            order = order_form.save(commit=False)
            cart_data = cart_contents(request)

            # Build cart snapshot
            cart_snapshot = []
            for item in cart_data['cart_items']:
                cart_snapshot.append({
                    'product_id': item['product'].id,
                    'product_name': item['product'].name,
                    'quantity': item['quantity'],
                    'price': float(item['product'].price),
                    'subtotal': float(item['subtotal']),
                })

            # Save order data
            pid = request.POST.get('client_secret')
            order.payment_intent_id = pid.split('_secret')[0] if pid else ''
            order.original_cart = json.dumps(cart_snapshot)
            order.order_total = cart_data['total']
            order.delivery_cost = cart_data['delivery']
            order.grand_total = cart_data['grand_total']
            order.order_number = order_number
            order.save()

            # Save line items
            for item_id, item_data in cart.items():
                try:
                    product = Product.objects.get(id=item_id)
                    OrderLineItem.objects.create(
                        order=order,
                        product=product,
                        quantity=item_data
                    )
                except Product.DoesNotExist:
                    messages.error(request, "A product in your cart wasn't found.")
                    order.delete()
                    return redirect('view_cart')

            request.session['save_info'] = 'save-info' in request.POST
            return redirect(reverse('checkout:checkout_success', args=[order.order_number]))
        else:
            messages.error(request, "There was an error in your form. Please double-check.")

    else:
        # Create PaymentIntent
        cart_data = cart_contents(request)
        stripe_total = round(cart_data['grand_total'] * 100)
        intent = stripe.PaymentIntent.create(
            amount=stripe_total,
            currency=settings.STRIPE_CURRENCY,
            metadata={
                'order_number': order_number,
                'username': str(request.user) if request.user.is_authenticated else 'guest',
            }
        )

        # Pre-fill form
        if request.user.is_authenticated:
            try:
                profile = UserProfile.objects.get(user=request.user)
                initial = {
                    'full_name': profile.user.get_full_name(),
                    'email': profile.user.email,
                    'phone_number': profile.default_phone_number,
                    'country': profile.default_country,
                    'postcode': profile.default_postcode,
                    'town_or_city': profile.default_town_or_city,
                    'street_address1': profile.default_street_address1,
                    'street_address2': profile.default_street_address2,
                    'county': profile.default_county,
                }
                order_form = OrderForm(initial=initial)
            except UserProfile.DoesNotExist:
                order_form = OrderForm()
        else:
            order_form = OrderForm()

    return render(request, 'checkout/checkout.html', {
        'order_form': order_form,
        'stripe_public_key': stripe_public_key,
        'client_secret': intent.client_secret,
        'order_number': order_number,
    })


# -----------------------------
# GET: Polling - Get Order Number
# -----------------------------
def get_order_number(request):
    payment_intent_id = request.GET.get("payment_intent")
    if not payment_intent_id:
        return JsonResponse({"error": "Missing payment intent ID"}, status=400)

    for attempt in range(30):
        try:
            order = Order.objects.get(payment_intent_id=payment_intent_id)
            return JsonResponse({
                "success": True,
                "redirect_url": reverse("checkout:checkout_success", args=[order.order_number]),
            })
        except Order.DoesNotExist:
            time.sleep(1)

    return JsonResponse({"error": "Order not found"}, status=404)


# -----------------------------
# GET: Checkout Success Page
# -----------------------------
def checkout_success(request, order_number):
    save_info = request.session.get('save_info', False)
    order = get_object_or_404(Order, order_number=order_number)

    if request.user.is_authenticated:
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        order.user_profile = profile
        order.save()

        if save_info:
            profile_data = {
                'default_phone_number': order.phone_number,
                'default_country': order.country,
                'default_postcode': order.postcode,
                'default_town_or_city': order.town_or_city,
                'default_street_address1': order.street_address1,
                'default_street_address2': order.street_address2,
                'default_county': order.county,
            }
            user_profile_form = UserProfileForm(profile_data, instance=profile)
            if user_profile_form.is_valid():
                user_profile_form.save()
            else:
                messages.warning(request, "⚠️ We couldn't update your profile with the saved info.")

    request.session.pop('cart', None)
    messages.success(request, f"🎉 Order successfully processed! Your order number is {order_number}.")
    send_order_confirmation(order)

    return render(request, 'checkout/checkout_success.html', {'order': order})


# -----------------------------
# Stripe Webhook
# -----------------------------
@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")
    endpoint_secret = settings.STRIPE_WH_SECRET

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except (ValueError, stripe.error.SignatureVerificationError):
        return HttpResponse(status=400)

    if event["type"] == "payment_intent.succeeded":
        intent = event["data"]["object"]
        payment_intent_id = intent.get("id")
        metadata = intent.get("metadata", {})
        order_number = metadata.get("order_number")
        email = metadata.get("email")
        cart_json = metadata.get("cart", "{}")

        if not order_number:
            return HttpResponse(status=400)

        try:
            order = Order.objects.get(order_number=order_number)
            if not order.payment_intent_id:
                order.payment_intent_id = payment_intent_id
                order.save()
        except Order.DoesNotExist:
            try:
                order = Order.objects.create(
                    order_number=order_number,
                    email=email,
                    payment_intent_id=payment_intent_id,
                    original_cart=cart_json,
                    order_total=intent["amount"] / 100,
                    grand_total=intent["amount"] / 100,
                )
            except Exception as e:
                logger.error(f"Webhook fallback failed to create order: {e}")
                return HttpResponse(status=500)

        send_order_confirmation(order)

    return HttpResponse(status=200)


# -----------------------------
# Email Helper
# -----------------------------
def send_order_confirmation(order):
    from django.core.mail import EmailMessage
    from django.template.loader import render_to_string
    from weasyprint import HTML
    import tempfile

    subject = f"Order Confirmation - {order.order_number}"
    body = render_to_string('checkout/order_confirmation_email.html', {'order': order})
    invoice_html = render_to_string('checkout/pdf_invoice.html', {'order': order})

    with tempfile.NamedTemporaryFile(delete=True, suffix=".pdf") as temp:
        HTML(string=invoice_html).write_pdf(temp.name)
        temp.seek(0)
        pdf_data = temp.read()

        email = EmailMessage(
            subject=subject,
            body=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[order.email],
        )
        email.content_subtype = 'html'
        email.attach(f"Invoice_{order.order_number}.pdf", pdf_data, 'application/pdf')
        email.send()
        logger.info(f"Confirmation email with invoice sent for order {order.order_number}")
