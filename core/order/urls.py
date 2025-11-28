from django.urls import path

from .views import (
    CheckoutShippingView,
    CreateAddressView,
    DeleteAddressView,
    EditAddressView,
    ApplyShippingMethodView,
)


app_name = "order"

urlpatterns = [
    path(
        "checkout/shipping/",
        CheckoutShippingView.as_view(),
        name="checkout-shipping",
    ),
    path(
        "create/address/", CreateAddressView.as_view(), name="create-address"
    ),
    path(
        "delete/address/<int:pk>/",
        DeleteAddressView.as_view(),
        name="delete-address",
    ),
    path(
        "edit/address/<int:pk>/",
        EditAddressView.as_view(),
        name="edit-address",
    ),
    path(
        "apply/shipping-method/",
        ApplyShippingMethodView.as_view(),
        name="apply-shipping-method",
    ),
]
