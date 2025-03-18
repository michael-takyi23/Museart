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

try:
    from django.contrib import admin
except ImportError as e:
    print("🚨 Admin module not found! Check your Django installation:", e)

from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse, HttpRequest

# Error Handlers
handler404 = "home.views.custom_404_view"
handler500 = "home.views.custom_500_view"

# Robots.txt View
def robots_txt(request: HttpRequest):
    """
    Serve a simple robots.txt file to guide search engine crawlers.
    """
    content = (
        "User-agent: *\n"
        "Disallow: /admin/\n"
        "Allow: /\n"
        "Sitemap: https://museart-b6682941c690.herokuapp.com/sitemap.xml\n"
    )
    return HttpResponse(content, content_type="text/plain")

# URL Patterns
urlpatterns = [

    path("admin/", admin.site.urls),  # ✅ Admin Panel
    path("accounts/", include("allauth.urls")),  # ✅ Authentication (Login/Signup)
    
    # Core App URLs
    path("", include("home.urls")),  # ✅ Home Page
    path("products/", include("products.urls")),  # ✅ Products App
    path("cart/", include("cart.urls")),  # ✅ Shopping Cart
    path("checkout/", include("checkout.urls")),  # ✅ Checkout Process
    path("profile/", include("profiles.urls")),  # ✅ User Profile

    # Miscellaneous
    path("robots.txt", robots_txt, name="robots_txt"),  # ✅ Robots.txt for SEO
]

# Serve static & media files in development mode
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

