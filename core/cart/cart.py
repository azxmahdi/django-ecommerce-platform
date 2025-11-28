import logging

from collections import OrderedDict

from shop.models import ProductVariantModel, ProductStatusType, ProductModel
from order.models import ShippingMethodModel
from .storage import BaseStorage
from .models import CartItemModel, CartModel
from core.constants import TaskName, LoggerName

apps_logger = logging.getLogger(LoggerName.APPS)


class CartSession:
    def __init__(self, storage: BaseStorage):
        self.storage = storage
        self._cart = self.storage.get_container()

        if "items" not in self._cart:
            self._cart["items"] = OrderedDict()
        else:
            self._cart["items"] = OrderedDict(self._cart["items"])

    def _set_item(self, variant_id, product_id: int, quantity: int):
        key = f"v{variant_id}"
        if key in self._cart["items"]:
            self._cart["items"][key]["quantity"] = quantity
        else:
            self._cart["items"][key] = {
                "product_id": product_id,
                "quantity": quantity,
            }

    def add_product(self, variant_id, product_id: int, quantity: int):
        key = f"v{variant_id}"
        items = self._cart["items"]

        if key in items:
            new_quantity = items[key]["quantity"] + quantity
            apps_logger.info(
                "Product quantity increased in cart",
                extra={
                    "task_name": TaskName.CART_ITEM_UPDATE,
                    "variant_id": variant_id,
                    "old_quantity": items[key]["quantity"],
                    "added_quantity": quantity,
                    "new_quantity": new_quantity,
                },
            )

        else:
            apps_logger.info(
                "New product added to cart",
                extra={
                    "task_name": TaskName.CART_ITEM_ADD,
                    "variant_id": variant_id,
                    "product_id": product_id,
                    "quantity": quantity,
                },
            )
            new_quantity = quantity

        self._set_item(variant_id, product_id, new_quantity)
        self.storage.mark_modified()

    def remove_product(self, variant_id):
        key = f"v{variant_id}"
        if key in self._cart["items"]:
            removed_quantity = self._cart["items"][key]["quantity"]
            apps_logger.info(
                "Product removed from cart",
                extra={
                    "task_name": TaskName.CART_ITEM_REMOVE,
                    "variant_id": variant_id,
                    "removed_quantity": removed_quantity,
                },
            )
            del self._cart["items"][key]
            self.storage.mark_modified()

    def update_quantity_product(self, variant_id, quantity: int):
        key = f"v{variant_id}"
        if key in self._cart["items"]:
            self._cart["items"][key]["quantity"] = quantity
            old_quantity = self._cart["items"][key]["quantity"]

            apps_logger.info(
                "Product quantity updated in cart",
                extra={
                    "task_name": TaskName.CART_ITEM_UPDATE,
                    "variant_id": variant_id,
                    "old_quantity": old_quantity,
                    "new_quantity": quantity,
                    "quantity_change": quantity - old_quantity,
                    "quantity_change": quantity - old_quantity,
                },
            )
            self.storage.mark_modified()

    def get_cart_dict(self):
        return self._cart

    def get_cart_items(self):
        cart_items = OrderedDict()
        items = self._cart.get("items", OrderedDict())

        for key in items:
            item = items[key]
            variant_id = int(key.replace("v", ""))
            variant_obj = ProductVariantModel.objects.select_related(
                "product", "attribute_value"
            ).get(
                id=variant_id,
                product__status=ProductStatusType.PUBLISH.value,
            )

            cart_items[key] = {
                **item,
                "variant_obj": variant_obj,
                "total_price_without_discount": item["quantity"]
                * variant_obj.price,
                "total_price_with_discount": item["quantity"]
                * variant_obj.final_price,
                "total_discounts": item["quantity"] * variant_obj.price
                - item["quantity"] * variant_obj.final_price,
            }
        return cart_items

    def get_cart_item(self, variant_id):
        return self._cart["items"].get(f"v{variant_id}", {})

    def get_total_payment_amount(
        self, shipping_method: ShippingMethodModel = None
    ):
        result = sum(
            item["total_price_with_discount"]
            for item in self.get_cart_items().values()
        )

        return (
            result
            if shipping_method is None
            else result + shipping_method.price
        )

    def get_total_amount_without_discount(self):
        return sum(
            item["total_price_without_discount"]
            for item in self.get_cart_items().values()
        )

    def get_total_discounts(self):
        return sum(
            item["total_discounts"] for item in self.get_cart_items().values()
        )

    def get_total_quantity(self):
        return sum(
            int(item.get("quantity", 0) or 0)
            for item in self._cart.get("items", {}).values()
        )

    def clear(self):
        items_count = len(self._cart["items"])
        del self._cart["items"]
        self.storage.mark_modified()
        apps_logger.info(
            "Cart cleared", extra={"cleared_items_count": items_count}
        )

    def sync_cart_items_from_db(self, user):
        cart, created = CartModel.objects.get_or_create(user=user)
        cart_items = CartItemModel.objects.filter(cart=cart)
        db_items_count = cart_items.count()
        session_items_before = len(self._cart["items"])

        for cart_item in cart_items:
            self._set_item(
                cart_item.product_variant.id,
                cart_item.product_variant.product.id,
                cart_item.quantity,
            )
        apps_logger.info(
            "Cart synced from database",
            extra={
                "task_name": TaskName.CART_SYNC,
                "user_id": user.id,
                "db_items_count": db_items_count,
                "session_items_before": session_items_before,
                "session_items_after": len(self._cart["items"]),
                "cart_created": created,
            },
        )
        self.merge_session_cart_in_db(user)
        self.storage.mark_modified()

    def merge_session_cart_in_db(self, user):
        session_items_count = len(self._cart["items"])

        apps_logger.info(
            "Session cart merged to database",
            extra={
                "task_name": TaskName.CART_MERGE,
                "user_id": user.id,
                "session_items_count": session_items_count,
                "merged_items_count": len(self._cart["items"]),
            },
        )
        cart, created = CartModel.objects.get_or_create(user=user)

        for item_id, item in self._cart["items"].items():
            product_variant_obj = ProductVariantModel.objects.get(
                id=item_id[1:], product__status=ProductStatusType.PUBLISH.value
            )
            cart_item, created = CartItemModel.objects.get_or_create(
                cart=cart, product_variant=product_variant_obj
            )
            cart_item.quantity = item["quantity"]
            cart_item.save()

        session_variant_ids = [key[1:] for key in self._cart["items"].keys()]
        CartItemModel.objects.filter(cart=cart).exclude(
            product_variant__id__in=session_variant_ids
        ).delete()
