from django.urls import path
from .views import view_cart, add_to_cart, update_cart, remove_from_cart, confirm_order  

urlpatterns = [
    path("", view_cart, name="view_cart"),
    path("add/<int:item_id>/", add_to_cart, name="add_to_cart"), 
    path("update/<int:item_id>/", update_cart, name="update_cart"),  
    path("remove/<int:item_id>/", remove_from_cart, name="remove_cart"),  
    path("order/confirm/", confirm_order, name="confirm_order"),
]
