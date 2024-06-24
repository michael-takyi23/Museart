from django.shortcuts import render
from .models import Product


# Create your views here.
def All_products(request):
    """ A view to show all products, including sorting and search queries """

    products = products.objects.all()

    context = {
        'products': products,
    }

    return render(request, 'products/products.html', context)