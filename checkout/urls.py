from django.urls import path
from .views import checkout, checkout_success, get_order_number, cache_checkout_data, stripe_webhook

urlpatterns = [
    # ✅ Checkout Page
    path('', checkout, name='checkout'),

    # ✅ Order Number Retrieval (used to fetch the order after payment)
    path('get-order-number/', get_order_number, name='get_order_number'),

    # ✅ Checkout Success Page
    path("checkout-success/<str:order_number>/", checkout_success, name="checkout_success"),

    # ✅ Caching Checkout Data Before Payment
    path('cache-checkout-data/', cache_checkout_data, name='cache_checkout_data'),

    # ✅ Stripe Webhook (Handles payment processing updates)
    path('webhook/', stripe_webhook, name='stripe_webhook'),
]
