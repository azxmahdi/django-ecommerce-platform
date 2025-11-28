from django.http import JsonResponse
from cart.commands.base import BaseCartCommand


class UpdateQuantityCommand(BaseCartCommand):

    def execute(self, variant_id, quantity):
        variant, validated_quantity, error = self.validate_basic_inputs(
            variant_id, quantity
        )
        if error:
            return error

        if not self.quantity_validator.validate_stock_availability(
            validated_quantity, variant
        ):
            self.cart_service.update_quantity(variant_id, variant.stock)
            return JsonResponse(
                {
                    "status": "error",
                    "message": "تعداد انتخابی بیشتر از موجودی است. تعداد این محصول داخل سبد خرید شما به حداکثر موجودی تغییر یافت",
                    **self.cart_service.get_serializable_cart_data(),
                }
            )

        self.cart_service.update_quantity(variant_id, validated_quantity)

        return JsonResponse(
            {
                "status": "success",
                **self.cart_service.get_serializable_cart_data(),
            }
        )
