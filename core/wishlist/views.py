import logging

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.http import JsonResponse

from .models import WishlistProductModel
from core.constants import TaskName, LoggerName

apps_logger = logging.getLogger(LoggerName.APPS)


class AddOrRemoveWishlistProductView(LoginRequiredMixin, View):

    def post(self, request, *args, **kwargs):
        if product_id := request.POST.get("product_id"):
            try:
                wishlist_item = WishlistProductModel.objects.get(
                    user=request.user, product__id=product_id
                )
                wishlist_item.delete()
                apps_logger.info(
                    "Wishlist product removed",
                    extra={
                        "task_name": TaskName.WISHLIST_REMOVE,
                        "user_id": request.user.id,
                        "product_id": product_id,
                        "correlation_id": getattr(
                            self.request, "correlation_id", None
                        ),
                    },
                )
                return JsonResponse(
                    {
                        "status": "success",
                        "message": "محصول از لیست علایق حذف شد",
                    }
                )
            except WishlistProductModel.DoesNotExist:
                WishlistProductModel.objects.create(
                    user=request.user, product_id=product_id
                )
                apps_logger.info(
                    "Wishlist product added",
                    extra={
                        "task_name": TaskName.WISHLIST_ADD,
                        "user_id": request.user.id,
                        "product_id": product_id,
                        "correlation_id": getattr(
                            self.request, "correlation_id", None
                        ),
                    },
                )
                return JsonResponse(
                    {
                        "status": "success",
                        "message": "محصول به لیست علایق اضافه شد",
                    }
                )
        apps_logger.error(
            "Wishlist product add/remove failed: missing product_id",
            extra={
                "task_name": TaskName.WISHLIST_ERROR,
                "user_id": request.user.id,
                "correlation_id": getattr(
                    self.request, "correlation_id", None
                ),
            },
        )
        return JsonResponse(
            {"status": "error", "message": "داده ها ناقص است."}
        )


class RemoveWishlistProductView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        if product_id := request.POST.get("product_id"):
            try:
                wishlist_item = WishlistProductModel.objects.get(
                    user=request.user, product__id=product_id
                )
                wishlist_item.delete()

                apps_logger.info(
                    "Wishlist product removed",
                    extra={
                        "task_name": TaskName.WISHLIST_REMOVE,
                        "user_id": request.user.id,
                        "product_id": product_id,
                        "correlation_id": getattr(
                            self.request, "correlation_id", None
                        ),
                    },
                )
                return JsonResponse(
                    {
                        "status": "success",
                        "message": "محصول از لیست علایق حذف شد",
                    }
                )
            except WishlistProductModel.DoesNotExist:
                apps_logger.warning(
                    "Wishlist product not found for removal",
                    extra={
                        "task_name": TaskName.WISHLIST_REMOVE,
                        "user_id": request.user.id,
                        "product_id": product_id,
                        "correlation_id": getattr(
                            self.request, "correlation_id", None
                        ),
                    },
                )
                return JsonResponse(
                    {"status": "error", "message": "محصول یافت نشد"}
                )

        apps_logger.error(
            "Wishlist product removal failed: missing product_id",
            extra={
                "task_name": TaskName.WISHLIST_ERROR,
                "user_id": request.user.id,
            },
        )
        return JsonResponse(
            {"status": "error", "message": "داده ها ناقص است."}
        )


class RemoveAllWishlistProductsView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        wishlist_items = WishlistProductModel.objects.filter(user=request.user)
        count = wishlist_items.count()
        wishlist_items.delete()
        apps_logger.info(
            "All wishlist products removed",
            extra={
                "task_name": TaskName.WISHLIST_REMOVE_ALL,
                "user_id": request.user.id,
                "removed_count": count,
                "correlation_id": getattr(
                    self.request, "correlation_id", None
                ),
            },
        )
        return JsonResponse(
            {
                "status": "success",
                "message": "همه محصولات از لیست علایق حذف شدند",
            }
        )
