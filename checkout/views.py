import stripe
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.http import HttpResponse
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
    stripe_public_key = settings.STRIPE_PUBLIC_KEY if settings.DEBUG else settings.STRIPE_LIVE_PUBLIC_KEY
    stripe.api_key = settings.STRIPE_SECRET_KEY if settings.DEBUG else settings.STRIPE_LIVE_SECRET_KEY
    
    client_secret = ''
    success_url = request.build_absolute_uri(reverse('order_confirmation', args=['<order_number>']))

    if request.method == "POST":
        form = OrderForm(request.POST)
        if form.is_valid():
            # Save order instance
            order = form.save(commit=False)
            order.delivery_cost = 50.00  
            order.grand_total = order.delivery_cost + order.order_total 
            order.save()

            # Create OrderLineItems
            cart = request.session.get('cart', {})
            for item_id, quantity in cart.items():
                product = Product.objects.get(id=item_id)
                OrderLineItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                    lineitem_total=product.price * quantity
                )

            # Create Stripe PaymentIntent
            stripe_total = int(order.grand_total * 100)  # Convert to cents
            stripe_api_key = stripe_secret_key
            intent = stripe.PaymentIntent.create(
                amount=stripe_total,
                currency=settings.STRIPE_CURRENCY,
                metadata={'order_id': order.order_number}
            )
            
            client_secret = intent.client_secret 

            # Clear the cart
            request.session['cart'] = {}
            send_order_confirmation(order)  # Send confirmation email
            messages.success(request, "Your order was placed successfully!")
            return redirect('order_confirmation', order_number=order.order_number)
        else:
            messages.error(request, "There was an error with your form submission. Please try again.")
    else:
        form = OrderForm()
        
        
        if not stripe_public_key:
            message.warning(request, 'Stripe public key is missing. Did you forget to set it in your environment?')

    context = {
    
        'form': form,
        'stripe_public_key': stripe_public_key,
        'client_secret': client_secret,
        'success_url': success_url,
    }  
    return render(request, 'checkout/checkout.html', context)


def order_confirmation(request, order_number):
    """ View to display the order confirmation page """
    order = get_object_or_404(Order, order_number=order_number)
    return render(request, 'checkout/order_confirmation.html', {'order': order})


def send_test_email(request):
    """ Function to test email sending """
    EmailMessage(
        subject="Test Email",
        body="This is a test email for Stripe integration.",
        from_email="museart2024@outlook.com",
        to=["museart2024@outlook.com"]
    ).send()
    return HttpResponse('Test email sent successfully.')
