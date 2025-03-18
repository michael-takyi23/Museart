from django.urls import path
from . import views  

urlpatterns = [
    # ✅ Checkout Page
    path('', views.checkout, name='checkout'),

    # ✅ Order Number Retrieval (used to fetch the order after payment)
    path('get-order-number/', views.get_order_number, name='get_order_number'),

    # ✅ Checkout Success Page
    path('checkout-success/<slug:order_number>/', views.checkout_success, name='checkout_success'),

    # ✅ Caching Checkout Data Before Payment
    path('cache-checkout-data/', views.cache_checkout_data, name='cache_checkout_data'),

    # ✅ Stripe Webhook (Handles payment processing updates)
    path('webhook/', views.stripe_webhook, name='stripe_webhook'),
]
