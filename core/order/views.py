import logging

from django.views.generic import (
    TemplateView,
    FormView,
    CreateView,
    DeleteView,
    UpdateView,
    View,
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.contrib.messages.views import SuccessMessageMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.core.exceptions import ValidationError
from django.db.models import ProtectedError

from cart.models import CartModel
from cart.services.cart import CartService
from cart.storage import SessionStorage
from .models import (
    AddressModel,
    ShippingMethodModel,
    OrderModel,
    OrderItemModel,
    OrderStatusType,
)
from .forms import CheckoutShippingForm, AddressForm
from .services.context_builders import CheckoutShippingContextBuilder
from .services.order import OrderService
from core.constants import TaskName, LoggerName


apps_logger = logging.getLogger(LoggerName.APPS)


class CheckoutShippingView(LoginRequiredMixin, FormView):
    template_name = "order/checkout-shipping.html"
    form_class = CheckoutShippingForm

    context_builder_class = CheckoutShippingContextBuilder

    def get_success_url(self):
        return reverse_lazy(
            "payment:checkout-payment", kwargs={"order_id": self.order.id}
        )

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)

        builder = self.context_builder_class(
            request=self.request,
            base_context=context_data,
        )
        return builder.build()

    def form_valid(self, form):
        user = self.request.user
        cart = get_object_or_404(CartModel, user=user)

        self.order = OrderModel.objects.create(
            user=user,
            address=form.cleaned_data["address"],
            shipping_method=form.cleaned_data["shipping_method"],
        )

        try:
            OrderService.validate_and_create_order(
                self.order, cart, self.request
            )

            cart.cart_items.all().delete()
            cart_service = CartService(SessionStorage(self.request.session))

            apps_logger.info(
                "Order created successfully in checkout shipping view",
                extra={
                    "task_name": TaskName.ORDER_CHECKOUT_SHIPPING,
                    "order_id": self.order.id,
                    "user_id": user.id,
                    "items_count": cart.cart_items.count(),
                    "correlation_id": getattr(
                        self.request, "correlation_id", None
                    ),
                },
            )

            cart_service.clear()

            return super().form_valid(form)

        except ValidationError as e:
            self.order.delete()
            apps_logger.error(
                "Checkout shipping failed due to stock validation error",
                extra={
                    "task_name": TaskName.ORDER_CHECKOUT_SHIPPING,
                    "user_id": user.id,
                    "errors": e.messages,
                    "correlation_id": getattr(
                        self.request, "correlation_id", None
                    ),
                },
            )

            for error in e.messages:
                messages.error(self.request, error)

            return redirect("cart:checkout")

    def form_invalid(self, form):
        apps_logger.warning(
            "Checkout shipping form invalid",
            extra={
                "task_name": TaskName.ORDER_CHECKOUT_SHIPPING,
                "user_id": self.request.user.id,
                "errors": form.errors,
                "correlation_id": getattr(
                    self.request, "correlation_id", None
                ),
            },
        )
        return super().form_invalid(form)


class CreateAddressView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    http_method_names = ["post"]
    model = AddressModel
    form_class = AddressForm
    success_message = "آدرس با موفقیت ایجاد شد"

    def get_success_url(self):
        return self.request.META.get("HTTP_REFERER")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["initial"] = {"user": self.request.user}
        return kwargs

    def form_valid(self, form):
        form.instance.user = self.request.user
        apps_logger.info(
            "Address created successfully",
            extra={
                "task_name": TaskName.ADDRESS_CREATE,
                "user_id": self.request.user.id,
                "address_id": form.instance.id,
                "correlation_id": getattr(
                    self.request, "correlation_id", None
                ),
            },
        )
        return super().form_valid(form)

    def form_invalid(self, form):
        apps_logger.error(
            "Address creation failed due to invalid form",
            extra={
                "task_name": TaskName.ADDRESS_CREATE,
                "user_id": self.request.user.id,
                "errors": form.errors,
                "correlation_id": getattr(
                    self.request, "correlation_id", None
                ),
            },
        )
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, error)

        return redirect(self.get_success_url())

    def get_queryset(self):
        return AddressModel.objects.filter(user=self.request.user)


class DeleteAddressView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = AddressModel
    http_method_names = ["post"]
    success_message = "آدرس با موفقیت حذف شد"

    def get_success_url(self):
        return self.request.META.get("HTTP_REFERER")

    def get_queryset(self):
        return AddressModel.objects.filter(user=self.request.user)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        related_orders = OrderModel.objects.filter(address=self.object)

        if related_orders.exists():
            apps_logger.warning(
                "Address deletion blocked because it is used in orders",
                extra={
                    "task_name": TaskName.ADDRESS_DELETE,
                    "user_id": request.user.id,
                    "address_id": self.object.id,
                    "related_orders_count": related_orders.count(),
                    "correlation_id": getattr(request, "correlation_id", None),
                },
            )
            messages.error(
                request,
                f"این آدرس در {related_orders.count()} سفارش استفاده شده و قابل حذف نیست.",
            )
            return redirect(self.get_success_url())

        try:
            self.object.delete()
            apps_logger.info(
                "Address deleted successfully",
                extra={
                    "task_name": TaskName.ADDRESS_DELETE,
                    "user_id": request.user.id,
                    "address_id": self.object.id,
                    "correlation_id": getattr(request, "correlation_id", None),
                },
            )
            messages.success(request, "آدرس با موفقیت حذف شد")
        except ProtectedError as e:
            apps_logger.error(
                "ProtectedError occurred while deleting address",
                extra={
                    "task_name": TaskName.ADDRESS_DELETE,
                    "user_id": request.user.id,
                    "address_id": self.object.id,
                    "error": str(e),
                    "correlation_id": getattr(request, "correlation_id", None),
                },
            )
            messages.error(
                request,
                "این آدرس در سفارش‌های سیستم استفاده شده و قابل حذف نیست.",
            )

        return redirect(self.get_success_url())


class EditAddressView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    http_method_names = ["post"]
    form_class = AddressForm
    success_message = "آدرس با موفقیت ویرایش شد"

    def form_valid(self, form):
        apps_logger.info(
            "Address edited successfully",
            extra={
                "task_name": TaskName.ADDRESS_EDIT,
                "user_id": self.request.user.id,
                "address_id": form.instance.id,
                "correlation_id": getattr(
                    self.request, "correlation_id", None
                ),
            },
        )
        return super().form_valid(form)

    def get_queryset(self):
        return AddressModel.objects.filter(user=self.request.user)

    def form_invalid(self, form):
        apps_logger.error(
            "Address edit failed due to invalid form",
            extra={
                "task_name": TaskName.ADDRESS_EDIT,
                "user_id": self.request.user.id,
                "errors": form.errors,
                "correlation_id": getattr(
                    self.request, "correlation_id", None
                ),
            },
        )

        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, error)

        return redirect(self.get_success_url())

    def get_success_url(self):
        return self.request.META.get("HTTP_REFERER")


class ApplyShippingMethodView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        cart_service = CartService(storage=SessionStorage(request.session))
        shipping_method_id = request.POST.get("shipping_method_id")

        try:
            shipping_method = ShippingMethodModel.objects.get(
                id=int(shipping_method_id)
            )
            apps_logger.info(
                "Shipping method applied successfully",
                extra={
                    "task_name": TaskName.APPLY_SHIPPING_METHOD,
                    "user_id": request.user.id,
                    "shipping_method_id": shipping_method.id,
                    "correlation_id": getattr(request, "correlation_id", None),
                },
            )
        except (ShippingMethodModel.DoesNotExist, ValueError) as e:
            apps_logger.error(
                "Invalid shipping method id",
                extra={
                    "task_name": TaskName.APPLY_SHIPPING_METHOD,
                    "user_id": request.user.id,
                    "shipping_method_id": shipping_method_id,
                    "error": str(e),
                    "correlation_id": getattr(request, "correlation_id", None),
                },
            )
            return JsonResponse(
                {
                    "status": "error",
                    "message": "لطفا مجدد امتحان کنید"
                    ** cart_service.get_serializable_cart_data(),
                }
            )
        return JsonResponse(
            {
                "status": "success",
                **cart_service.get_serializable_cart_data(shipping_method),
            }
        )
