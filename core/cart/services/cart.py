from collections import OrderedDict
from cart.cart import CartSession
from cart.storage import BaseStorage
from order.models import ShippingMethodModel


class CartService:
    def __init__(self, storage: BaseStorage, user=None):
        self.cart = CartSession(storage)
        self.user = user

    def add(self, variant_id, product_id: int, quantity: int):
        self.cart.add_product(variant_id, product_id, quantity)
        return self.cart

    def remove(self, variant_id):
        self.cart.remove_product(variant_id)
        return self.cart

    def update_quantity(self, variant_id, quantity: int):
        self.cart.update_quantity_product(variant_id, quantity)
        return self.cart

    def cart_dict(self):
        return self.cart.get_cart_dict()

    def cart_items(self):
        return self.cart.get_cart_items()

    def total_payment_amount(
        self, shipping_method: ShippingMethodModel = None
    ):
        return self.cart.get_total_payment_amount(shipping_method)

    def total_amount_without_discount(self):
        return self.cart.get_total_amount_without_discount()

    def total_amount_discounts(self):
        return self.cart.get_total_discounts()

    def total_quantity(self):
        return self.cart.get_total_quantity()

    def get_serializable_cart_data(
        self, shipping_method: ShippingMethodModel = None
    ):
        raw = self.cart_items()
        serializable = OrderedDict()

        for key, item in raw.items():
            v = item["variant_obj"]
            serializable[key] = {
                "product_id": item["product_id"],
                "quantity": item["quantity"],
                "total_price_without_discount": float(
                    item["total_price_without_discount"]
                ),
                "total_price_with_discount": float(
                    item["total_price_with_discount"]
                ),
                "total_discounts": float(item["total_discounts"]),
                "variant_info": {
                    "id": v.id,
                    "stock": v.stock,
                    "price": float(v.price),
                    "final_price": float(v.final_price),
                    "attribute_value": v.attribute_value.value,
                    "product_name": v.product.name,
                    "product_image_url": (
                        v.product.image.url if v.product.image else None
                    ),
                },
            }

        result = {
            "cart_items": serializable,
            "total_payment_amount": float(
                self.total_payment_amount(shipping_method)
            ),
            "total_amount_without_discount": float(
                self.total_amount_without_discount()
            ),
            "total_amount_discounts": float(self.total_amount_discounts()),
            "total_quantity": self.total_quantity(),
        }

        if shipping_method is not None:
            result["price_shipping_method"] = shipping_method.price

        return result

    def cart_item(self, variant_id):
        return self.cart.get_cart_item(variant_id)

    def clear(self):
        return self.cart.clear()

    def merge(self, user):
        return self.cart.merge_session_cart_in_db(user)

    def sync(self, user):
        return self.cart.sync_cart_items_from_db(user)
