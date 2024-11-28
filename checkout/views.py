import stripe
from django.conf import settings
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib import messages
from django.db import transaction
from .forms import OrderForm
from .models import Order, OrderLineItem
from cart.contexts import cart_contents

stripe.api_key = settings.STRIPE_SECRET_KEY

stripe.api_key = settings.STRIPE_SECRET_KEY

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
                        confirmation_method='manual',
                        confirm=True,
                    )

                    # Check for confirmation status
                    if intent.status == 'succeeded':
                        messages.success(request, "Order successfully placed!")
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
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY,  # Make sure to pass the public key
    }

    template = 'checkout/checkout.html'
    return render(request, template, context)

def order_confirmation(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)
    return render(request, 'checkout/order_confirmation.html', {'order': order})
