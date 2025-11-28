from django.views.generic import CreateView, FormView
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import redirect


from .models import NewsLetterModel
from .forms import NewsLetterForm


class NewsLetterCreateView(SuccessMessageMixin, CreateView):
    http_method_names = [
        "post",
    ]
    form_class = NewsLetterForm
    success_message = "عضویت شما در خبرنامه با موفقیت ثبت گردید"

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f"{field}: {error}")
        return redirect(self.get_success_url())

    def get_success_url(self):
        return self.request.META.get(
            "HTTP_REFERER", reverse_lazy("website:index")
        )
