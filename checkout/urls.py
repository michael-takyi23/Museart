from django.urls import path
from . import views

urlpatterns = [
    path('', views.checkout, name='checkout'),
    path('order-confirmation/<order_number>/', views.order_confirmation, name='order_confirmation'),

]
