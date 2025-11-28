from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse_lazy


class CustomLoginRequiredMixin(LoginRequiredMixin):
    login_url = reverse_lazy("account:phone-auth")

    def handle_no_permission(self):
        messages.error(
            self.request,
            "لطفا ابتدا وارد حساب کاربری خود شوید",
            extra_tags="danger",
        )
        return super().handle_no_permission()
