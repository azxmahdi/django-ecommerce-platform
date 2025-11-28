from django.urls import path

from .views import (
    AddOrRemoveWishlistProductView,
    RemoveWishlistProductView,
    RemoveAllWishlistProductsView,
)

app_name = "wishlist"

urlpatterns = [
    path(
        "add-or-remove/wishlist/product/",
        AddOrRemoveWishlistProductView.as_view(),
        name="add-or-remove-wishlist-product",
    ),
    path(
        "remove/wishlist/product/",
        RemoveWishlistProductView.as_view(),
        name="remove-wishlist-product",
    ),
    path(
        "remove-all/wishlist/products/",
        RemoveAllWishlistProductsView.as_view(),
        name="remove-all-wishlist-products",
    ),
]
