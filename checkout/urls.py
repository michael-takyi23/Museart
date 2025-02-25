from django.urls import path
from . import views

urlpatterns = [
    # ✅ Checkout page
    path('', views.checkout, name='checkout'),

    # ✅ Order Confirmation Page
    path('order-confirmation/<str:order_number>/', views.order_confirmation, name='order_confirmation'),

    # ✅ Test Email Sending (Fixing duplicate URL issue)
    path('send-test-email/', views.send_test_email, name='send_test_email'),
]
