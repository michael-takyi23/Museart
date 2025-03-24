from django.urls import path
from .views import checkout, checkout_success, cache_checkout_data, get_order_number, stripe_webhook

urlpatterns = [
    # ✅ Checkout Page
    path('', checkout, name='checkout'),

    # ✅ Checkout Success Page
    path("checkout-success/<str:order_number>/", checkout_success, name="checkout_success"),

    path('get-order-number/', get_order_number, name='get_order_number'),

    # ✅ Caching Checkout Data Before Payment
    path('cache-checkout-data/', cache_checkout_data, name='cache_checkout_data'),

    path('stripe webhook/', stripe_webhook, name='stripe_webhook'), 

]
