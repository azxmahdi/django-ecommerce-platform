import json
from django.views import View
from django.http import JsonResponse


class CartServiceMixin:
    cart_service_class = None
    storage_class = None

    def get_cart_service(self, request):
        if not self.cart_service_class or not self.storage_class:
            raise ValueError(
                "cart_service_class and storage_class must be set"
            )

        storage = self.storage_class(request.session)
        user = getattr(request, "user", None)
        return self.cart_service_class(storage, user)


class MergeCartMixin(CartServiceMixin):
    def merge_if_authenticated(self, request, result):
        data = json.loads(result.content.decode("utf-8"))

        if request.user.is_authenticated and data.get("status") == "success":

            cart_service = self.get_cart_service(request)
            cart_service.merge(request.user)
