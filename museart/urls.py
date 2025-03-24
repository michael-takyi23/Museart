"""museart URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

"""Museart URL Configuration"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse, HttpRequest

# Custom Error Handlers
handler404 = "home.views.custom_404_view"
handler500 = "home.views.custom_500_view"

# robots.txt response for SEO
def robots_txt(request: HttpRequest):
    return HttpResponse(
        "User-agent: *\n"
        "Disallow: /admin/\n"
        "Allow: /\n"
        "Sitemap: https://museart-b6682941c690.herokuapp.com/sitemap.xml\n",
        content_type="text/plain"
    )

urlpatterns = [
    # 🔐 Admin Panel
    path("admin/", admin.site.urls),

    # 🔐 User Authentication (django-allauth)
    path("accounts/", include("allauth.urls")),

    # 🌐 Core App Routes
    path("", include("home.urls")),             # Homepage & error views
    path("products/", include("products.urls")),  # Product listing, detail
    path("cart/", include("cart.urls")),          # Cart add/remove/view
    path("profile/", include("profiles.urls")),   # User account settings

    # 💳 Checkout & Payments
    path("checkout/", include(("checkout.urls", "checkout"), namespace="checkout")),

    # 🗺️ SEO & Meta
    path("robots.txt", robots_txt, name="robots_txt"),
]

# 📁 Static & Media files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)