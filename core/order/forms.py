from django import forms
from django.core.exceptions import ValidationError

from .models import AddressModel, ShippingMethodModel


class CheckoutShippingForm(forms.Form):
    address = forms.ModelChoiceField(
        queryset=AddressModel.objects.none(),
        widget=forms.RadioSelect,
        error_messages={"required": "لطفاً آدرس خود را انتخاب کنید"},
    )
    shipping_method = forms.ModelChoiceField(
        queryset=ShippingMethodModel.objects.all(),
        widget=forms.RadioSelect,
        error_messages={"required": "لطفاً نحوه ارسال را انتخاب کنید"},
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user")
        super().__init__(*args, **kwargs)
        self.fields["address"].queryset = AddressModel.objects.filter(
            user=user
        )


class AddressForm(forms.ModelForm):
    class Meta:
        model = AddressModel
        fields = [
            "first_name",
            "last_name",
            "phone",
            "postal_code",
            "address",
            "province",
            "city",
            "plaque",
            "unit",
        ]

    def clean_phone(self):
        phone = self.cleaned_data.get("phone")
        if phone:
            phone = "".join(filter(str.isdigit, phone))
            if not phone.isdigit():
                raise ValidationError("شماره تلفن باید فقط شامل اعداد باشد.")
            if len(phone) != 11:
                raise ValidationError("شماره تلفن باید 11 رقمی باشد.")
            if not phone.startswith("09"):
                raise ValidationError("شماره تلفن باید با 09 شروع شود.")
        return phone

    def clean_postal_code(self):
        postal_code = self.cleaned_data.get("postal_code")
        if postal_code:
            postal_code = "".join(filter(str.isdigit, postal_code))
            if not postal_code.isdigit():
                raise ValidationError("کد پستی باید فقط شامل اعداد باشد.")
            if len(postal_code) != 10:
                raise ValidationError("کد پستی باید دقیقاً 10 رقم باشد.")
        return postal_code

    def clean_plaque(self):
        plaque = self.cleaned_data.get("plaque")
        if plaque:
            if not plaque.isdigit():
                raise ValidationError("پلاک باید یک عدد باشد.")
        return plaque

    def clean_unit(self):
        unit = self.cleaned_data.get("unit")
        if unit and not isinstance(unit, int):
            raise ValidationError("واحد باید یک عدد باشد.")
        return unit

    def save(self, commit=True):
        instance = super().save(commit=False)
        if not instance.user_id:
            instance.user = self.initial.get("user")
        if commit:
            instance.save()
        return instance
