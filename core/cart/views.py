from django.http import JsonResponse
from django.views import View
from django.views.generic import TemplateView

from cart.mixins import CartServiceMixin, MergeCartMixin
from cart.storage import SessionStorage
from cart.services.cart import CartService
from cart.commands.add_item import AddItemCommand
from cart.commands.update_quantity import UpdateQuantityCommand


class BaseCartView(MergeCartMixin, CartServiceMixin, View):
    command_class = None
    cart_service_class = CartService
    storage_class = SessionStorage

    def post(self, request):
        if not self.command_class:
            return JsonResponse(
                {"status": "error", "message": "دستور مشخص نشده است"}
            )

        cart_service = self.get_cart_service(request)
        command = self.command_class(cart_service)

        result = self.execute_command(command, request)

        self.merge_if_authenticated(request, result)

        return result

    def execute_command(self, command, request):
        raise NotImplementedError("Subclasses must implement execute_command")


class AddProductView(BaseCartView):
    command_class = AddItemCommand

    def execute_command(self, command, request):
        return command.execute(
            product_id=request.POST.get("product_id"),
            variant_id=request.POST.get("variant_id"),
            quantity=request.POST.get("quantity"),
        )


class UpdateQuantityProductView(BaseCartView):
    command_class = UpdateQuantityCommand

    def execute_command(self, command, request):
        return command.execute(
            variant_id=request.POST.get("variant_id"),
            quantity=request.POST.get("quantity"),
        )


class RemoveProductView(MergeCartMixin, CartServiceMixin, View):
    cart_service_class = CartService
    storage_class = SessionStorage

    def post(self, request):
        variant_id = request.POST.get("variant_id")
        if not variant_id:
            return JsonResponse(
                {"status": "error", "message": "اطلاعات محصول ناقص است"}
            )

        cart_service = self.get_cart_service(request)
        cart_service.remove(variant_id)

        result = JsonResponse(
            {
                "status": "success",
                "message": "محصول از سبد خرید حذف شد",
                **cart_service.get_serializable_cart_data(),
            }
        )

        self.merge_if_authenticated(request, result)

        return result


class ClearView(MergeCartMixin, CartServiceMixin, View):
    cart_service_class = CartService
    storage_class = SessionStorage

    def post(self, request):

        cart_service = self.get_cart_service(request)
        cart_service.clear()

        result = JsonResponse(
            {
                "status": "success",
                "message": "همه محصولات سبد خرید حذف شد",
                **cart_service.get_serializable_cart_data(),
            }
        )

        self.merge_if_authenticated(request, result)

        return result


class CheckoutView(TemplateView):
    template_name = "cart/checkout.html"
