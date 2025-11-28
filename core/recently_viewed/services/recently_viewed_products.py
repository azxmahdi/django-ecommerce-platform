from django.core.cache import cache
from django.contrib.auth import get_user_model
from shop.models import ProductModel


User = get_user_model()


class RecentlyViewedProductsService:
    def __init__(self, user: User, limit=30, timeout=60 * 60 * 24 * 7):

        self.key = f"recently_viewed_products:user:{user.id}"
        self.limit = limit
        self.timeout = timeout

    def add_product(self, product_id: int):
        viewed_products = cache.get(self.key, [])

        if product_id in viewed_products:
            viewed_products.remove(product_id)

        viewed_products.insert(0, product_id)

        cache.set(
            self.key, viewed_products[: self.limit], timeout=self.timeout
        )

    def remove_product(self, product_id: int):
        viewed_products = cache.get(self.key, [])
        if product_id in viewed_products:
            viewed_products.remove(product_id)
            cache.set(self.key, viewed_products, timeout=self.timeout)

    def get_products(self):
        product_ids = cache.get(self.key, [])
        if not product_ids:
            return ProductModel.objects.none()

        from django.db.models import Case, When

        preserved = Case(
            *[When(pk=pk, then=pos) for pos, pk in enumerate(product_ids)]
        )
        return ProductModel.objects.filter(pk__in=product_ids).order_by(
            preserved
        )

    def clear(self):
        cache.delete(self.key)
