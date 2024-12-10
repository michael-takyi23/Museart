import stripe
from django.conf import settings
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib import messages
from django.db import transaction
from django.core.mail import send_mail, EmailMessage
from django.template.loader import render_to_string
from django.http import HttpResponse
from .forms import OrderForm
from .models import Order, OrderLineItem
from cart.contexts import cart_contents

stripe_public_key = settings.STRIPE_TEST_PUBLIC_KEY if settings.DEBUG else settings.STRIPE_LIVE_PUBLIC_KEY
context = {
    'stripe_public_key': stripe_public_key,
}


# Send email function
def send_order_confirmation(order):
    # Email subject and message
    subject = f"Order Confirmation - {order.order_number}"
    message = render_to_string('checkout/order_confirmation_email.html', {'order': order})
    
    # Sending the HTML email to the customer
    email = EmailMessage(
        subject=subject,
        body=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[order.email],
    )
    email.content_subtype = 'html'  # Sending HTML email
    email.send()


def checkout(request):
    cart = request.session.get('cart', {})
    if not cart:
        messages.error(request, "There is nothing in your cart at the moment")
        return redirect(reverse('products'))

    # Ensure that cart_items is initialized before any operation
    cart_items = cart_contents(request)['cart_items']
    for item in cart_items:
        item['subtotal'] = item['product'].price * item['quantity']

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    order = form.save(commit=False)
                    order.save()

                    for item in cart_items:
                        OrderLineItem.objects.create(
                            order=order,
                            product=item['product'],
                            quantity=item['quantity'],
                            lineitem_total=item['subtotal']
                        )

                    # Calculate total amount for Stripe Payment (convert to cents)
                    total_amount = int(order.grand_total * 100)  # Convert to cents

                    # Handle Stripe payment using Payment Intent
                    payment_method_id = request.POST.get('stripePaymentMethodId')  # The stripe payment method ID from frontend
                    if not payment_method_id:
                        messages.error(request, "No payment method found.")
                        return redirect('checkout')

                    # Create the PaymentIntent with the received payment method
                    intent = stripe.PaymentIntent.create(
                        amount=total_amount,
                        currency='usd',
                        payment_method=payment_method_id,
                        confirmation_method='automatic',  # Auto confirm payment
                        confirm=True,
                    )

                    # Handle case when additional actions are required (e.g., 3D Secure)
                    if intent.status == 'requires_action' or intent.status == 'requires_source_action':
                        return redirect(intent.next_action.redirect_to_url)

                    # Check for confirmation status
                    if intent.status == 'succeeded':
                        messages.success(request, "Order successfully placed!")
                        send_order_confirmation(order)  # Send the confirmation email
                        return redirect(reverse('order_confirmation', args=[order.order_number]))
                    else:
                        messages.error(request, "Payment could not be processed. Please try again.")
                        return redirect(reverse('checkout'))

            except stripe.error.CardError as e:
                messages.error(request, "Your card was declined. Please try again.")
            except stripe.error.StripeError as e:
                messages.error(request, f"Stripe error occurred: {e.error.message}")
            except Exception as e:
                messages.error(request, f"An error occurred during checkout: {e}")
        else:
            messages.error(request, "Please check your form for errors.")

    else:
        form = OrderForm()

    context = {
        'form': form,
        'cart_items': cart_items,
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
    }
    return render(request, 'checkout/checkout.html', context)


def order_confirmation(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)
    return render(request, 'checkout/order_confirmation.html', {'order': order})


def send_test_email(request):
    send_mail(
        'Test Email',
        'This is a test email from SendGrid.',
        'museart2024@outlook.com',  # sender email
        ['museart2024@outlook.com'],  # recipient email
    )
    return HttpResponse('Test email sent!')
