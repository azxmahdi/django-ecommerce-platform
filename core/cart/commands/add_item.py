from django.http import JsonResponse
from cart.commands.base import BaseCartCommand


class AddItemCommand(BaseCartCommand):

    def execute(self, product_id, variant_id, quantity):
        if not all([product_id, variant_id, quantity]):
            return JsonResponse(
                {"status": "error", "message": "اطلاعات محصول ناقص است"}
            )

        variant, validated_quantity, error = self.validate_basic_inputs(
            variant_id, quantity
        )
        if error:
            return error

        if not self.quantity_validator.validate_stock_availability(
            validated_quantity, variant
        ):
            return JsonResponse(
                {
                    "status": "error",
                    "message": "تعداد انتخابی بیشتر از موجودی است",
                }
            )

        if not self.quantity_validator.validate_cart_stock_availability(
            variant, validated_quantity, self.cart_service
        ):
            return JsonResponse(
                {
                    "status": "error",
                    "message": "تعداد این محصول داخل سبد خرید شما بیشتر از موجودی است",
                }
            )

        self.cart_service.add(variant_id, product_id, validated_quantity)

        return JsonResponse(
            {
                "status": "success",
                "message": "محصول به سبد خرید اضافه شد",
                **self.cart_service.get_serializable_cart_data(),
            }
        )
