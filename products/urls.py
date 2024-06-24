from django.urls import path
from . import views

urlpatterns = [
    path('', views.All_products, name='products')
]
