from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib import messages
from django.db.models import Q 
from django.contrib.auth.decorators import login_required
from django.db.models.functions import Lower
from .models import Product, Category
from products.forms import ProductForm


def all_products(request):
    """A view to show all products, including sorting and search queries"""

    products = Product.objects.all()
    query = None
    categories = None
    sort = None
    direction = None

    if request.GET:
        if "sort" in request.GET:
            sortkey = request.GET["sort"]
            sort = sortkey
            if sortkey == "name":
                sortkey = "lower_name"
                products = products.annotate(lower_name=Lower("name"))
            if sortkey == "category":
                sortkey = "category__name"
            if "direction" in request.GET:
                direction = request.GET["direction"]
                if direction == "desc":
                    sortkey = f"-{sortkey}"
            products = products.order_by(sortkey)

        if "category" in request.GET:
            categories = request.GET["category"].split(",")
            products = products.filter(category__name__in=categories)
            categories = Category.objects.filter(name__in=categories)

        if "q" in request.GET:
            query = request.GET["q"].strip()  # Strip spaces
            if not query:
                messages.error(request, "You didn't enter any search criteria.")
                return redirect(reverse("products"))

            # **✅ Improved Search Query**
            queries = (
                Q(name__icontains=query)
                | Q(description__icontains=query)
                | Q(category__name__icontains=query)  # 🔹 Allows searching by category name
            )
            products = products.filter(queries)

    current_sorting = f"{sort}_{direction}"

    context = {
        "products": products,
        "search_term": query,
        "current_categories": categories,
        "current_sorting": current_sorting,
    }

    return render(request, "products/products.html", context)


def product_detail(request, product_id):
    """
    View to show product details.
    """
    product = get_object_or_404(Product, pk=product_id)

    context = {
        "product": product
    }

    return render(request, "products/product_detail.html", context)


@login_required
def add_product(request):
    """
    Allows superusers to add new products.
    """
    if not request.user.is_superuser:
        messages.error(request, "🚫 Only store owners can add products.")
        return redirect(reverse("home"))

    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            messages.success(request, f"🎉 Product '{product.name}' added successfully!")
            return redirect(reverse("product_detail", args=[product.id]))
        else:
            messages.error(request, "❌ Failed to add product. Please check your input.")

    else:
        form = ProductForm()

    context = {"form": form}
    return render(request, "products/add_product.html", context)


@login_required
def edit_product(request, product_id):
    """
    Allows superusers to edit existing products.
    """
    if not request.user.is_superuser:
        messages.error(request, "🚫 Only store owners can edit products.")
        return redirect(reverse("home"))

    product = get_object_or_404(Product, pk=product_id)

    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, f"✅ '{product.name}' updated successfully!")
            return redirect(reverse("product_detail", args=[product.id]))
        else:
            messages.error(request, "❌ Failed to update product. Please check your input.")

    else:
        form = ProductForm(instance=product)
        messages.info(request, f"📝 Editing {product.name}")

    context = {"form": form, "product": product}
    return render(request, "products/edit_product.html", context)


@login_required
def delete_product(request, product_id):
    """
    Allows superusers to delete products.
    """
    if not request.user.is_superuser:
        messages.error(request, "🚫 Only store owners can delete products.")
        return redirect(reverse("home"))

    product = get_object_or_404(Product, pk=product_id)
    product.delete()
    messages.success(request, f"🗑️ Product '{product.name}' deleted successfully!")

    return redirect(reverse("products"))
