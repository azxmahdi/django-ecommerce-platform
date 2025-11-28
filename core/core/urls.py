"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from website.views import custom_page_not_found


handler404 = custom_page_not_found


urlpatterns = [
    path("admin/", admin.site.urls),
    path("summernote/", include("django_summernote.urls")),
    path("account/", include("account.urls"), name="account"),
    path("blog/", include("blog.urls"), name="blog"),
    path("", include("website.urls"), name="website"),
    path("shop/", include("shop.urls"), name="shop"),
    path("review/", include("review.urls"), name="review"),
    path("cart/", include("cart.urls"), name="cart"),
    path("order/", include("order.urls"), name="order"),
    path("payment/", include("payment.urls"), name="payment"),
    path("coupon/", include("coupon.urls"), name="coupon"),
    path("dashboard/", include("dashboard.urls"), name="dashboard"),
    path("wishlist/", include("wishlist.urls"), name="wishlist"),
    path(
        "recently-viewed/",
        include("recently_viewed.urls"),
        name="recently-viewed",
    ),
    path(
        "notifications/", include("notifications.urls"), name="notifications"
    ),
    path("contact/", include("contact.urls"), name="contact"),
    path("faq/", include("faq.urls"), name="faq"),
    path("pages/", include("pages.urls"), name="pages"),
    path("newsletter/", include("newsletter.urls"), name="newsletter"),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.STATIC_URL, document_root=settings.STATIC_ROOT
    )
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
    import debug_toolbar

    urlpatterns = [
        path("__debug__/", include(debug_toolbar.urls)),
    ] + urlpatterns
