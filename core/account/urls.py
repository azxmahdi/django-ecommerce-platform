from django.urls import path

from .views import (
    PhoneAuthenticationView,
    LoginPasswordView,
    SignupOTPView,
    SendOTPView,
    SetPasswordView,
    LoginOTPView,
    ForgotOTPView,
    ForgotResetView,
    LogoutView,
)

app_name = "account"


urlpatterns = [
    path("phone-auth/", PhoneAuthenticationView.as_view(), name="phone-auth"),
    path("resend-otp/", SendOTPView.as_view(), name="send-otp"),
    path("signup-otp/", SignupOTPView.as_view(), name="signup-otp"),
    path("set-password/", SetPasswordView.as_view(), name="set-password"),
    path(
        "login-password/", LoginPasswordView.as_view(), name="login-password"
    ),
    path("login-otp/", LoginOTPView.as_view(), name="login-otp"),
    path("forgot-otp/", ForgotOTPView.as_view(), name="forgot-otp"),
    path("forgot-reset/", ForgotResetView.as_view(), name="forgot-reset"),
    path("logout/", LogoutView.as_view(), name="logout"),
]
