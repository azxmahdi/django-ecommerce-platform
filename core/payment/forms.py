from django import forms

from .models import PaymentGateway


class GatewaySelectionForm(forms.Form):
    gateway = forms.ModelChoiceField(
        queryset=PaymentGateway.objects.filter(is_active=True),
        widget=forms.RadioSelect(),
        error_messages={
            "required": "لطفاً درگاه پرداخت مد نظر خود را انتخاب کنید"
        },
    )
