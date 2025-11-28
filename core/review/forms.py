from django import forms
from django.utils.translation import gettext_lazy as _

from shop.models import ProductModel, ProductStatusType

from .models import ProductCommentModel


class ProductCommentForm(forms.ModelForm):
    class Meta:
        model = ProductCommentModel
        fields = ["product", "parent", "title", "text", "is_recommended"]
        error_messages = {
            "text": {
                "required": _("فیلد توضیحات اجباری است"),
            },
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        product = cleaned_data.get("product")

        try:
            ProductModel.objects.get(
                id=product.id, status=ProductStatusType.PUBLISH.value
            )
        except ProductModel.DoesNotExist:
            raise forms.ValidationError(_("این محصول وجود ندارد"))

        user = getattr(self.request, "user", None)
        parent = cleaned_data.get("parent")

        if (
            parent
            and ProductCommentModel.objects.filter(
                user=user, parent=parent
            ).exists()
        ):
            raise forms.ValidationError(_("شما قبلاً به این نظر پاسخ داده‌اید."))

        return cleaned_data
