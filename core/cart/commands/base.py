from django.http import JsonResponse
from cart.validators.quantity_validator import QuantityValidator
from cart.validators.variant_validator import VariantValidator


class BaseCartCommand:

    def __init__(
        self, cart_service, variant_validator=None, quantity_validator=None
    ):
        self.cart_service = cart_service
        self.variant_validator = variant_validator or VariantValidator()
        self.quantity_validator = quantity_validator or QuantityValidator()

    def validate_basic_inputs(self, variant_id, quantity):
        if not variant_id or not quantity:
            return (
                None,
                None,
                JsonResponse(
                    {"status": "error", "message": "اطلاعات محصول ناقص است"}
                ),
            )

        validated_quantity = self.quantity_validator.validate_positive_integer(
            quantity
        )
        if validated_quantity is None:
            return (
                None,
                None,
                JsonResponse(
                    {"status": "error", "message": "تعداد نامعتبر است"}
                ),
            )

        variant = self.variant_validator.validate(variant_id)
        if variant is None:
            return (
                None,
                None,
                JsonResponse(
                    {
                        "status": "error",
                        "message": "محصول یافت نشد یا منتشر نشده است",
                    }
                ),
            )

        return variant, validated_quantity, None

    def execute(self, **kwargs):
        raise NotImplementedError("Subclasses must implement execute method")
