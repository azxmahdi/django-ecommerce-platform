import logging

from django.views.generic import (
    TemplateView,
    ListView,
    DetailView,
    View,
    FormView,
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Prefetch, Exists, OuterRef, Q
from django.http import JsonResponse
from django.shortcuts import redirect
from django.utils import timezone
from django.contrib.auth import (
    get_user_model,
    authenticate,
    update_session_auth_hash,
)
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator

from django_ratelimit.decorators import ratelimit

from .services.context_builders import (
    CounterContextBuilder,
    OrderListContextBuilder,
    WishlistProductContextBuilder,
    OrderDetailContextBuilder,
    MessageListContextBuilder,
)
from .services.filters import OrderFilter
from .forms import PasswordForm, FirstnameAndLastnameForm, PhoneForm
from recently_viewed.services.recently_viewed_products import (
    RecentlyViewedProductsService,
)
from order.models import (
    OrderModel,
    OrderItemModel,
    AddressModel,
    OrderStatusType,
)
from wishlist.models import WishlistProductModel
from shop.models import ProductVariantModel
from order.services.order import StockValidationService
from payment.services import PaymentService
from notifications.models import (
    MessageModel,
    MessageType,
    UserMessageStatusModel,
)
from account.views import BaseOTPView
from core.constants import TaskName, LoggerName

User = get_user_model()

apps_logger = logging.getLogger(LoggerName.APPS)
payment_logger = logging.getLogger(LoggerName.PAYMENT)
security_logger = logging.getLogger(LoggerName.SECURITY)


class CounterView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard/counter.html"

    context_builder_class = CounterContextBuilder

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)

        builder = self.context_builder_class(
            request=self.request,
            base_context=context_data,
        )

        return builder.build()


class OrderListView(LoginRequiredMixin, ListView):
    template_name = "dashboard/order-list.html"
    context_object_name = "orders"
    paginate_by = 10

    context_builder_class = OrderListContextBuilder
    filter_class = OrderFilter

    def get_queryset(self):
        base_queryset = (
            OrderModel.objects.filter(user=self.request.user)
            .select_related("shipping_method", "coupon")
            .prefetch_related(
                "payment",
                Prefetch(
                    "order_items",
                    queryset=OrderItemModel.objects.select_related(
                        "product_variant__product"
                    ),
                ),
            )
            .order_by("-created_date")
        )
        return self.filter_class(self.request.GET).apply(base_queryset)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        builder = self.context_builder_class(
            request=self.request, base_context=context, orders=self.object_list
        )

        return builder.build()


class WishlistProductView(LoginRequiredMixin, ListView):
    template_name = "dashboard/wishlist-product.html"
    context_object_name = "wishlists"
    paginate_by = 4

    context_builder_class = WishlistProductContextBuilder

    def get_queryset(self):
        return (
            WishlistProductModel.objects.filter(user=self.request.user)
            .select_related("product")
            .annotate(
                is_available=Exists(
                    ProductVariantModel.objects.filter(
                        product=OuterRef("product"), stock__gt=0
                    )
                )
            )
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        builder = self.context_builder_class(
            request=self.request,
            base_context=context,
        )
        return builder.build()


class RecentlyViewedProductsView(LoginRequiredMixin, ListView):
    template_name = "dashboard/recently-viewed-products.html"
    context_object_name = "products"
    paginate_by = 4

    def get_queryset(self):
        return (
            RecentlyViewedProductsService(self.request.user)
            .get_products()
            .annotate(
                is_available=Exists(
                    ProductVariantModel.objects.filter(
                        product=OuterRef("pk"), stock__gt=0
                    )
                )
            )
        )


class OrderDetailView(LoginRequiredMixin, DetailView):
    template_name = "dashboard/order-detail.html"
    context_object_name = "order"
    context_builder_class = OrderDetailContextBuilder

    def get_queryset(self):
        return (
            OrderModel.objects.filter(user=self.request.user)
            .prefetch_related(
                "payment",
                Prefetch(
                    "order_items",
                    queryset=OrderItemModel.objects.select_related(
                        "product_variant__product",
                        "product_variant__attribute_value",
                    ),
                ),
            )
            .select_related("shipping_method", "address")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        builder = self.context_builder_class(
            request=self.request,
            base_context=context,
        )
        return builder.build()


class RepaymentView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        address_id = request.POST.get("address_id")
        order_id = request.POST.get("order_id")

        if order_id:
            try:
                order = (
                    OrderModel.objects.filter(
                        status=OrderStatusType.FAILED.value
                    )
                    .select_related("address")
                    .prefetch_related(
                        "order_items__product_variant__product", "payment"
                    )
                    .get(id=order_id, user=self.request.user)
                )
            except OrderModel.DoesNotExist:
                payment_logger.warning(
                    "Order not found for repayment",
                    extra={
                        "task_name": TaskName.REPAYMENT,
                        "user_id": request.user.id,
                        "order_id": order_id,
                        "correlation_id": getattr(
                            request, "correlation_id", None
                        ),
                    },
                )
                return JsonResponse(
                    {"status": "error", "message": "سفارش یافت نشد"}
                )

            if address_id and address_id != str(order.address.id):

                try:
                    address = AddressModel.objects.get(
                        id=address_id, user=request.user
                    )
                    order.address = address
                    order.save()
                    payment_logger.info(
                        "Order address updated for repayment",
                        extra={
                            "task_name": TaskName.REPAYMENT,
                            "user_id": request.user.id,
                            "order_id": order.id,
                            "address_id": address_id,
                            "correlation_id": getattr(
                                request, "correlation_id", None
                            ),
                        },
                    )
                except AddressModel.DoesNotExist:
                    payment_logger.warning(
                        "Address not found for repayment",
                        extra={
                            "task_name": TaskName.REPAYMENT,
                            "user_id": request.user.id,
                            "order_id": order.id,
                            "address_id": address_id,
                            "correlation_id": getattr(
                                request, "correlation_id", None
                            ),
                        },
                    )
                    return JsonResponse(
                        {"status": "error", "message": "آدرس یافت نشد"}
                    )

            errors, items_not_available = (
                StockValidationService.validate_stock(order.order_items.all())
            )
            if errors:
                product_names = ", ".join(
                    item.product_variant.product.name
                    for item in items_not_available
                )
                payment_logger.warning(
                    "Stock validation failed for repayment",
                    extra={
                        "task_name": TaskName.REPAYMENT,
                        "user_id": request.user.id,
                        "order_id": order.id,
                        "items_not_available": product_names,
                        "correlation_id": getattr(
                            request, "correlation_id", None
                        ),
                    },
                )
                prefix = (
                    "محصول" if len(items_not_available) == 1 else "محصولات"
                )
                return JsonResponse(
                    {
                        "status": "error",
                        "message": f"{prefix} {product_names} به تعداد کافی موجود نیست",
                    }
                )

            latest_payment = order.payment.latest("created_date")
            request.session["payment_data"] = {
                "gateway": latest_payment.gateway,
            }
            request.session["current_order_id"] = order.id

            order.status = OrderStatusType.PENDING.value
            order.save()

            payment_logger.info(
                "Repayment prepared successfully",
                extra={
                    "task_name": TaskName.REPAYMENT,
                    "user_id": request.user.id,
                    "order_id": order.id,
                    "gateway": latest_payment.gateway,
                    "correlation_id": getattr(request, "correlation_id", None),
                },
            )

            return redirect("payment:process")

        payment_logger.error(
            "Invalid repayment request: missing order_id",
            extra={
                "task_name": TaskName.REPAYMENT,
                "user_id": request.user.id,
                "order_id": order_id,
                "address_id": address_id,
                "correlation_id": getattr(request, "correlation_id", None),
            },
        )
        return JsonResponse(
            {"status": "error", "message": "شناسه سفارش ارسال نشده است"}
        )


class GeneratePaymentUrlView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        order_id = request.GET.get("order_id")
        if order_id:
            try:
                order = OrderModel.objects.get(
                    id=order_id,
                    user=self.request.user,
                    status=OrderStatusType.PENDING.value,
                )
            except OrderModel.DoesNotExist:
                payment_logger.warning(
                    "Order not found for payment URL generation",
                    extra={
                        "task_name": TaskName.GENERATE_PAYMENT_URL,
                        "user_id": request.user.id,
                        "order_id": order_id,
                        "correlation_id": getattr(
                            request, "correlation_id", None
                        ),
                    },
                )
                return JsonResponse(
                    {"status": "error", "message": "سفارش یافت نشد"}
                )

            now = timezone.now()

            payment = order.payment.latest("created_date")

            if payment.expired_date < now:
                payment_logger.warning(
                    "Payment gateway expired",
                    extra={
                        "task_name": TaskName.GENERATE_PAYMENT_URL,
                        "user_id": request.user.id,
                        "order_id": order.id,
                        "gateway": payment.gateway,
                        "correlation_id": getattr(
                            request, "correlation_id", None
                        ),
                    },
                )
                return JsonResponse(
                    {
                        "status": "error",
                        "message": "مدت زمان درگاه پرداخت به پایان رسیده است",
                    }
                )

            payment_url = PaymentService.generate_payment_url(
                payment.gateway, payment.authority_id
            )

            payment_logger.info(
                "Payment URL generated successfully",
                extra={
                    "task_name": TaskName.GENERATE_PAYMENT_URL,
                    "user_id": request.user.id,
                    "order_id": order.id,
                    "gateway": payment.gateway,
                    "payment_url": payment_url,
                    "correlation_id": getattr(request, "correlation_id", None),
                },
            )

            return JsonResponse(
                {"status": "success", "payment_url": payment_url}
            )
        payment_logger.error(
            "Invalid payment URL request: missing order_id",
            extra={
                "task_name": TaskName.GENERATE_PAYMENT_URL,
                "user_id": request.user.id,
                "order_id": order_id,
                "correlation_id": getattr(request, "correlation_id", None),
            },
        )
        return JsonResponse({"status": "error", "message": "داده ها ناقص است"})


class GetAddressDetailsView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        address_id = request.POST.get("address_id")

        if address_id:
            try:
                address = AddressModel.objects.get(
                    id=address_id, user=request.user
                )
                return JsonResponse(
                    {
                        "status": "success",
                        "data": {
                            "full_address": address.get_full_address(),
                            "full_name": address.get_full_name(),
                        },
                    }
                )
            except AddressModel.DoesNotExist:
                return JsonResponse(
                    {"status": "error", "message": "آدرس یافت نشد."}
                )
            except Exception as e:
                return JsonResponse(
                    {"status": "error", "message": "خطای سرور."}
                )

        return JsonResponse({"status": "error", "message": "آدرس یافت نشد."})


class AddressView(LoginRequiredMixin, ListView):
    template_name = "dashboard/address.html"
    context_object_name = "addresses"

    def get_queryset(self):
        return AddressModel.objects.filter(user=self.request.user)


class MessageListView(LoginRequiredMixin, ListView):
    template_name = "dashboard/message-list.html"
    context_object_name = "user_messages"
    context_builder_class = MessageListContextBuilder

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        builder = self.context_builder_class(
            request=self.request,
            base_context=context,
        )
        return builder.build()

    def get_queryset(self):
        user = self.request.user

        personal_and_order_messages = (
            MessageModel.objects.filter(
                Q(
                    user=user,
                    type__in=[
                        MessageType.ORDER.value,
                        MessageType.PERSONAL.value,
                    ],
                )
            )
            .select_related("order")
            .prefetch_related(
                Prefetch(
                    "order__order_items",
                    queryset=OrderItemModel.objects.select_related(
                        "product_variant__product"
                    ),
                )
            )
        )
        broadcast_messages = MessageModel.objects.filter(
            Q(type=MessageType.BROADCAST.value)
            & ~Q(user_statuses__user=user, user_statuses__is_hidden=True)
        )

        personal_and_order_messages.update(is_read=True)

        new_broadcasts = broadcast_messages.exclude(user_statuses__user=user)
        if new_broadcasts.exists():
            UserMessageStatusModel.objects.bulk_create(
                [
                    UserMessageStatusModel(
                        user=user, message=message, is_read=True
                    )
                    for message in new_broadcasts
                ]
            )

        return personal_and_order_messages | broadcast_messages


class ProfileDetailView(LoginRequiredMixin, DetailView):
    template_name = "dashboard/profile-detail.html"
    context_object_name = "user"

    def get_queryset(self):
        return User.objects.filter(
            id=self.request.user.id, is_active=True
        ).prefetch_related("user_profile")


class FirstnameAndLastnameEditView(LoginRequiredMixin, FormView):
    http_method_names = ["post"]
    form_class = FirstnameAndLastnameForm
    template_name = "dashboard/profile-detail.html"

    def form_valid(self, form):
        first_name = form.cleaned_data["first_name"]
        last_name = form.cleaned_data["last_name"]
        try:
            user = User.objects.get(id=self.request.user.id)
            profile = user.user_profile
            profile.first_name = first_name
            profile.last_name = last_name
            profile.save()
            apps_logger.info(
                "User name updated successfully",
                extra={
                    "task_name": TaskName.PROFILE_EDIT_NAME,
                    "user_id": self.request.user.id,
                    "first_name": first_name,
                    "last_name": last_name,
                    "correlation_id": getattr(
                        self.request, "correlation_id", None
                    ),
                },
            )
            messages.success(
                self.request, _("نام و نام خانوادگی با موفقیت تغییر یافت")
            )
        except User.DoesNotExist:
            apps_logger.warning(
                "User not found while updating name",
                extra={
                    "task_name": TaskName.PROFILE_EDIT_NAME,
                    "user_id": self.request.user.id,
                    "correlation_id": getattr(
                        self.request, "correlation_id", None
                    ),
                },
            )
            messages.error(self.request, _("کاربر یافت نشد"))
            return self.form_invalid(form)
        except AttributeError:
            apps_logger.warning(
                "User profile not found while updating name",
                extra={
                    "task_name": TaskName.PROFILE_EDIT_NAME,
                    "user_id": self.request.user.id,
                    "correlation_id": getattr(
                        self.request, "correlation_id", None
                    ),
                },
            )
            messages.error(self.request, _("پروفایل کاربری یافت نشد"))
            return self.form_invalid(form)
        return super().form_valid(form)

    def form_invalid(self, form):
        apps_logger.error(
            "Invalid data submitted for name update",
            extra={
                "task_name": TaskName.PROFILE_EDIT_NAME,
                "user_id": self.request.user.id,
                "errors": form.errors,
                "correlation_id": getattr(
                    self.request, "correlation_id", None
                ),
            },
        )

        messages.error(self.request, _("اطلاعات وارد شده نامعتبر است."))
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse_lazy(
            "dashboard:profile-detail", kwargs={"pk": self.request.user.id}
        )


class PasswordEditView(LoginRequiredMixin, FormView):
    http_method_names = ["post"]
    form_class = PasswordForm
    template_name = "dashboard/profile-detail.html"

    def form_valid(self, form):
        old_password = form.cleaned_data["old_password"]
        new_password = form.cleaned_data["new_password"]

        user = authenticate(
            self.request, phone=self.request.user.phone, password=old_password
        )
        if user is not None:
            user.set_password(new_password)
            user.save()
            update_session_auth_hash(self.request, user)
            apps_logger.info(
                "Password changed successfully",
                extra={
                    "task_name": TaskName.PROFILE_EDIT_PASSWORD,
                    "user_id": self.request.user.id,
                    "correlation_id": getattr(
                        self.request, "correlation_id", None
                    ),
                },
            )
            messages.success(self.request, _("رمز عبور با موفقیت تغییر یافت"))
            return super().form_valid(form)
        else:
            apps_logger.warning(
                "Old password incorrect",
                extra={
                    "task_name": TaskName.PROFILE_EDIT_PASSWORD,
                    "user_id": self.request.user.id,
                    "correlation_id": getattr(
                        self.request, "correlation_id", None
                    ),
                },
            )
            messages.error(
                self.request,
                _("پسورد قبلی شما اشتباه وارد شده است، لطفا تصحیح نمایید."),
            )
            return self.form_invalid(form)

    def form_invalid(self, form):
        apps_logger.error(
            "Invalid data submitted for password change",
            extra={
                "task_name": TaskName.PROFILE_EDIT_PASSWORD,
                "user_id": self.request.user.id,
                "errors": form.errors,
                "correlation_id": getattr(
                    self.request, "correlation_id", None
                ),
            },
        )
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse_lazy(
            "dashboard:profile-detail", kwargs={"pk": self.request.user.id}
        )


class PhoneEditView(LoginRequiredMixin, FormView):
    http_method_names = ["post"]
    template_name = "dashboard/profile-detail.html"
    form_class = PhoneForm

    def form_valid(self, form):
        phone = form.cleaned_data["phone"]
        self.request.session["phone"] = phone

        apps_logger.info(
            "Phone change initiated",
            extra={
                "task_name": TaskName.PROFILE_EDIT_PHONE,
                "user_id": self.request.user.id,
                "new_phone": phone,
                "correlation_id": getattr(
                    self.request, "correlation_id", None
                ),
            },
        )
        return super().form_valid(form)

    def form_invalid(self, form):
        apps_logger.error(
            "Invalid data submitted for phone change",
            extra={
                "task_name": TaskName.PROFILE_EDIT_PHONE,
                "user_id": self.request.user.id,
                "errors": form.errors,
                "correlation_id": getattr(
                    self.request, "correlation_id", None
                ),
            },
        )
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse_lazy("dashboard:verify-new-phone")


@method_decorator(
    ratelimit(key="ip", rate="5/5m", method="POST", block=False),
    name="dispatch",
)
class VerifyNewPhoneView(LoginRequiredMixin, BaseOTPView):
    success_message = "شماره با موفقیت تغییر یافت"
    page_title = "تغییر شماره"

    def dispatch(self, request, *args, **kwargs):
        if getattr(request, "limited", False):
            security_logger.warning(
                "Rate limit exceeded for phone verification",
                extra={
                    "task_name": TaskName.PROFILE_VERIFY_PHONE,
                    "user_id": request.user.id,
                    "correlation_id": getattr(request, "correlation_id", None),
                },
            )
            messages.error(
                request,
                "شما بیش از ۵ بار در پنج دقیقه تلاش برای تأیید کد کرده‌اید. لطفا چند دقیقه دیگر تلاش کنید.",
            )
            return redirect("account:signup-otp")
        return super().dispatch(request, *args, **kwargs)

    def post_verify(self):
        new_phone = self.request.session.get("phone")
        if User.objects.filter(phone=new_phone).exists():
            apps_logger.warning(
                "Phone already exists during verification",
                extra={
                    "task_name": TaskName.PROFILE_VERIFY_PHONE,
                    "user_id": self.request.user.id,
                    "new_phone": new_phone,
                    "correlation_id": getattr(
                        self.request, "correlation_id", None
                    ),
                },
            )
            messages.error(self.request, "این شماره قبلاً ثبت شده است.")
            return redirect(self.get_success_url())

        user = self.request.user
        user.phone = new_phone
        user.save()
        self.request.session.pop("phone", None)

        apps_logger.info(
            "Phone verified and updated successfully",
            extra={
                "task_name": TaskName.PROFILE_VERIFY_PHONE,
                "user_id": self.request.user.id,
                "new_phone": new_phone,
                "correlation_id": getattr(
                    self.request, "correlation_id", None
                ),
            },
        )

    def get_success_url(self):
        return reverse_lazy(
            "dashboard:profile-detail", kwargs={"pk": self.request.user.id}
        )
