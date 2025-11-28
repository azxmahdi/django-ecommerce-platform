from django.conf import settings
from .utils import get_redirect_url, set_next_url


class OTPContextMixin:
    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data["otp_expiry"] = settings.OTP_EXPIRY_SECONDS
        context_data["otp_length"] = settings.OTP_CODE_LENGTH
        return context_data


class RedirectNextMixin:

    default_redirect_url = None

    def get_success_url(self):
        return get_redirect_url(self.request, self.default_redirect_url)

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        if request.method == "GET" and not request.user.is_authenticated:
            set_next_url(request)


class LoginRedirectMixin(RedirectNextMixin):

    def get_success_url(self):
        url = get_redirect_url(self.request)
        if url == settings.LOGIN_REDIRECT_URL and hasattr(
            self, "redirect_url"
        ):
            url = self.redirect_url
        return url
