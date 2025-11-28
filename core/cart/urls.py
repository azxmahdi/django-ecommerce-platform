from django.urls import path

from .views import (
    AddProductView,
    CheckoutView,
    UpdateQuantityProductView,
    RemoveProductView,
    ClearView,
)

app_name = "cart"

urlpatterns = [
    path("add/product/", AddProductView.as_view(), name="add-product"),
    path(
        "remove/product/", RemoveProductView.as_view(), name="remove-product"
    ),
    path("checkout/", CheckoutView.as_view(), name="checkout"),
    path(
        "update-quantity/product/",
        UpdateQuantityProductView.as_view(),
        name="update-quantity-product",
    ),
    path("clear/", ClearView.as_view(), name="clear"),
]
