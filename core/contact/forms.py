from django import forms

from .models import ContactModel


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactModel
        fields = ["name", "phone", "email", "message"]
        error_messages = {
            "email": {
                "invalid": "ایمیل وارد شده نامعتبر است",
            }
        }
