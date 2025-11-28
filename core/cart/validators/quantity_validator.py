from typing import Optional


class QuantityValidator:
    @staticmethod
    def validate_positive_integer(quantity) -> Optional[int]:
        try:
            quantity = int(quantity)
            return quantity if quantity > 0 else None
        except (ValueError, TypeError):
            return None

    @staticmethod
    def validate_stock_availability(quantity: int, variant) -> bool:
        return quantity <= getattr(variant, "stock", 0)

    @staticmethod
    def validate_cart_stock_availability(
        variant, quantity: int, cart_service
    ) -> bool:
        cart_item = cart_service.cart_item(variant.id) or {}
        current_qty = cart_item.get("quantity", 0)
        return (current_qty + quantity) <= getattr(variant, "stock", 0)
