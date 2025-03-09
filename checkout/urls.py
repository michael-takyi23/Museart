from django.urls import path
from . import views  

urlpatterns = [
    # ✅ Main checkout page
    path('', views.checkout, name='checkout'),

    # ✅ Handle order number retrieval after payment
    path("get-order-number/", views.get_order_number, name="get_order_number"),

    # ✅ Handle successful checkout and redirect
    path('checkout-success/<str:order_number>/', views.checkout_success, name='checkout_success'),

    # ✅ Order confirmation page
    path('order-confirmation/<str:order_number>/', views.order_confirmation, name='order_confirmation'),

    # ✅ Stripe Webhook Handler
    path("webhook/", views.stripe_webhook, name="stripe_webhook"),
]

