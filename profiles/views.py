from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import UserProfile
from .forms import UserProfileForm
from checkout.models import Order


@login_required
def profile(request):
    """
    Display and update the user's profile.
    """
    profile = get_object_or_404(UserProfile, user=request.user)
    orders = profile.orders.all()

    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Profile updated successfully!")
        else:
            messages.error(request, "❌ Update failed. Please check the form and try again.")
    else:
        form = UserProfileForm(instance=profile)

    context = {
        'form': form,
        'orders': orders,
        'on_profile_page': True  # Helps with template-specific logic
    }
    
    return render(request, 'profiles/profile.html', context)


@login_required
def order_history(request, order_number):
    """
    Display past order details for the user.
    """
    order = get_object_or_404(Order, order_number=order_number)

    messages.info(request, (
        f"📦 This is a past confirmation for Order #{order_number}. "
        "A confirmation email was sent on the order date."
    ))

    context = {
        'order': order,
        'from_profile': True,  # Helps distinguish order history from normal checkout success
    }

    return render(request, 'checkout/checkout_success.html', context)

