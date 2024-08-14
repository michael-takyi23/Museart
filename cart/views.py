from django.shortcuts import render, redirect


# Create your views here.
def view_cart(request):
    """ A view that renders the shopping cart content page """

    return render(request, 'cart/cart.html')

def add_to_cart(request, item_id):
    """ A view to add quantity of product to the shopping cart """

    quantity = int(request.POST.get('quantity'))
    redirect_url = request.POST.get('redirect_url')
    cart = request.session.get('cart', {})
    size = None
    if 'product_size' in request.POST:
        size = request.POST['product_size']
    cart = request.session.get('cart', {})

    if item_id in list(cart.keys()):
        cart[item_id] += quantity
    if size:
        if item_id in list(cart.keys()):
            if size in cart[item_id]['items_by_size'].keys():
                cart[item_id]['items_by_size'][size] += quantity
            else:
                cart[item_id]['items_by_size'][size] = quantity
        else:
            cart[item_id] = {'items_by_size': {size: quantity}}
    else:
        cart[item_id] = quantity
        if item_id in list(cart.keys()):
            cart[item_id] += quantity
        else:
            cart[item_id] = quantity

    request.session['cart'] = cart
    return redirect(redirect_url)

    request.session['cart'] = cart 
    return redirect(redirect_url)
             
