from django.urls import path

from .views import (
    CheckoutPaymentView,
    PaymentProcessView,
    PaymentVerifyView,
    PaymentSuccessView,
    PaymentFailedView,
)

app_name = "payment"

urlpatterns = [
    path(
        "checkout/payment/<int:order_id>/",
        CheckoutPaymentView.as_view(),
        name="checkout-payment",
    ),
    path("process/", PaymentProcessView.as_view(), name="process"),
    path("verify/", PaymentVerifyView.as_view(), name="verify"),
    path("success/<int:pk>/", PaymentSuccessView.as_view(), name="success"),
    path("failed/<int:pk>/", PaymentFailedView.as_view(), name="failed"),
]
