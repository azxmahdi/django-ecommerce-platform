from django.urls import path, re_path
from .views import ProductListView, ProductDetailView, ProductVariantView


app_name = "shop"

urlpatterns = [
    path("product/list/", ProductListView.as_view(), name="product-list"),
    re_path(
        r"product/(?P<slug>[-\w]+)/detail/",
        ProductDetailView.as_view(),
        name="product-detail",
    ),
    path(
        "product/<int:pk>/variant/",
        ProductVariantView.as_view(),
        name="product-variant",
    ),
]
