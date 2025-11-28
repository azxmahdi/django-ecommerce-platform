from django.urls import path

from .views import (
    CounterView,
    OrderListView,
    WishlistProductView,
    RecentlyViewedProductsView,
    OrderDetailView,
    RepaymentView,
    GeneratePaymentUrlView,
    GetAddressDetailsView,
    AddressView,
    MessageListView,
    ProfileDetailView,
    FirstnameAndLastnameEditView,
    PasswordEditView,
    PhoneEditView,
    VerifyNewPhoneView,
)

app_name = "dashboard"

urlpatterns = [
    path("counter/", CounterView.as_view(), name="counter"),
    path("order/list/", OrderListView.as_view(), name="order-list"),
    path(
        "wishlist/product/",
        WishlistProductView.as_view(),
        name="wishlist-product",
    ),
    path(
        "recently-viewed/products/",
        RecentlyViewedProductsView.as_view(),
        name="recently-viewed-products",
    ),
    path(
        "order/detail/<int:pk>", OrderDetailView.as_view(), name="order-detail"
    ),
    path("repayment/", RepaymentView.as_view(), name="repayment"),
    path(
        "generate/payment/url/",
        GeneratePaymentUrlView.as_view(),
        name="generate-payment-url",
    ),
    path(
        "get/address/details/",
        GetAddressDetailsView.as_view(),
        name="get-address-details",
    ),
    path("address/", AddressView.as_view(), name="address"),
    path("message/list/", MessageListView.as_view(), name="message-list"),
    path(
        "profile/detail/<int:pk>",
        ProfileDetailView.as_view(),
        name="profile-detail",
    ),
    path(
        "firstname-and-lastname/edit/",
        FirstnameAndLastnameEditView.as_view(),
        name="firstname-and-lastname-edit",
    ),
    path("password/edit/", PasswordEditView.as_view(), name="password-edit"),
    path("phone/edit/", PhoneEditView.as_view(), name="phone-edit"),
    path(
        "verify/new-phone/",
        VerifyNewPhoneView.as_view(),
        name="verify-new-phone",
    ),
]
