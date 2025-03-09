from django.urls import path
from . import views

urlpatterns = [
    path('', views.profile, name='profile'),  # ✅ Profile Page
    path('order_history/<str:order_number>/', views.order_history, name='order_history'),  # ✅ Order History Page
]
