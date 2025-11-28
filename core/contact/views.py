import logging
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic import CreateView
from django.urls import reverse_lazy

from .forms import ContactForm


apps_logger = logging.getLogger("apps")


class ContactCreateView(SuccessMessageMixin, CreateView):
    template_name = "contact/create.html"
    form_class = ContactForm
    success_url = reverse_lazy("contact:create")
    success_message = "پشتیبانی به زودی با شما ارتباط برقرار خواهد کرد"

    def form_valid(self, form):
        try:
            response = super().form_valid(form)

            apps_logger.info(
                "New contact form submitted",
                extra={
                    "extra": {
                        "contact_id": self.object.id,
                        "contact_name": self.object.name,
                        "contact_phone": self.object.phone,
                        "contact_email": self.object.email,
                        "ip": self.request.META.get("REMOTE_ADDR"),
                        "user_agent": self.request.META.get(
                            "HTTP_USER_AGENT", ""
                        )[:100],
                    }
                },
            )
            return response

        except Exception as e:
            apps_logger.error(
                "Failed to save contact form",
                extra={
                    "extra": {"form_data": form.cleaned_data, "error": str(e)}
                },
            )
            raise

    def form_invalid(self, form):
        apps_logger.warning(
            "Contact form validation failed",
            extra={
                "form_errors": form.errors,
                "ip": self.request.META.get("REMOTE_ADDR"),
            },
        )
        return super().form_invalid(form)
