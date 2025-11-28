from django import forms

from .models import NewsLetterModel


class NewsLetterForm(forms.ModelForm):
    class Meta:
        model = NewsLetterModel
        fields = [
            "email",
        ]
        error_messages = {
            "email": {
                "invalid": "ایمیل وارد شده نامعتبر است",
            }
        }
