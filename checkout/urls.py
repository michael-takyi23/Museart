from django.urls import path
from . import views  # ✅ Import views correctly

urlpatterns = [
    path('', views.checkout, name='checkout'),
    path('order-confirmation/<str:order_number>/', views.order_confirmation, name='order_confirmation'),
    path("webhook/", views.stripe_webhook, name="stripe_webhook"),  # ✅ Corrected Import
    path('send-test-email/', views.send_test_email, name='send_test_email'),
]
