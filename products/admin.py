from django.contrib import admin
from .models import Product, Category, Address, Order, Shipment, SpecialOffer 


# Register your models here.

class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'category',
        'price',
        'rating',
        'image',
    )
    
    ordering = ('name',)

class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'name',
    )   

class SpecialOfferAdmin(admin.ModelAdmin):
    list_display = ('product', 'discount', 'active', 'start_date', 'end_date')  # Ensure 'discount' is listed
    list_filter = ('active', 'start_date', 'end_date')


admin.site.register(SpecialOffer, SpecialOfferAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Address)
admin.site.register(Order)
admin.site.register(Shipment)
