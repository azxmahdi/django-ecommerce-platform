import logging
from django.views.generic import ListView, DetailView
from django.db.models import (
    F,
    Q,
    Exists,
    OuterRef,
    Prefetch,
    ExpressionWrapper,
    DecimalField,
)
from django.db.models.functions import Round
from django.http import JsonResponse
from django.views import View


from .models import (
    ProductModel,
    ProductStatusType,
    ProductCategoryModel,
    ProductVariantModel,
    CategoryFeatureModel,
    FeatureOptionModel,
    ProductFeatureModel,
    AttributeValueModel,
    ProductImageModel,
)
from .services.context_builders import (
    ProductListContextBuilder,
    ProductDetailContextBuilder,
)
from .services.filters import ProductFilter
from recently_viewed.services.recently_viewed_products import (
    RecentlyViewedProductsService,
)
from review.models import ProductCommentModel, CommentStatus
from .services.search_log.add import add_search_log
from core.constants import TaskName, LoggerName


apps_logger = logging.getLogger(LoggerName.APPS)


class ProductListView(ListView):
    template_name = "shop/product-list.html"
    context_object_name = "products"
    paginate_by = 12

    filter_class = ProductFilter
    context_builder_class = ProductListContextBuilder

    def get_queryset(self):
        if q := self.request.GET.get("q"):
            last_q = self.request.session.get("last_search")
            if last_q != q:
                add_search_log(q, self.request.user)
                self.request.session["last_search"] = q

        base_queryset = ProductModel.objects.all()
        return self.filter_class(self.request.GET).apply(base_queryset)

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        builder = self.context_builder_class(
            request=self.request, base_context=context_data
        )
        return builder.build()


class ProductDetailView(DetailView):
    queryset = (
        ProductModel.objects.filter(status=ProductStatusType.PUBLISH.value)
        .select_related("category")
        .prefetch_related(
            Prefetch(
                "variants",
                queryset=ProductVariantModel.objects.filter(
                    stock__gt=0
                ).select_related("attribute_value__attribute"),
            ),
            "product_images",
            Prefetch(
                "features",
                queryset=ProductFeatureModel.objects.select_related(
                    "feature", "option"
                ),
            ),
            Prefetch(
                "comments",
                queryset=ProductCommentModel.objects.filter(
                    status=CommentStatus.APPROVED.value
                ).select_related("user"),
                to_attr="prefetched_comments",
            ),
        )
    )
    template_name = "shop/product-detail.html"
    context_object_name = "product"

    context_builder_class = ProductDetailContextBuilder

    def get_object(self, queryset=None):
        if not hasattr(self, "_object"):
            self._object = super().get_object(queryset)
            if self.request.user.is_authenticated:
                service = RecentlyViewedProductsService(user=self.request.user)
                service.add_product(self._object.id)
        return self._object

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        builder = self.context_builder_class(
            request=self.request,
            base_context=context_data,
            product=self.object,
        )
        return builder.build()


class ProductVariantView(View):
    def get(self, request, *args, **kwargs):
        product_id = kwargs.get("pk")
        selected_attrs = request.GET.dict()
        apps_logger.info(
            "ProductVariantView: request received",
            extra={
                "task_name": TaskName.PRODUCT_VARIANT,
                "user_id": getattr(request.user, "id", None),
                "product_id": product_id,
                "selected_attrs": selected_attrs,
                "correlation_id": getattr(request, "correlation_id", None),
            },
        )

        try:
            product = ProductModel.objects.prefetch_related(
                Prefetch(
                    "variants",
                    queryset=ProductVariantModel.objects.filter(
                        stock__gt=0
                    ).select_related("attribute_value__attribute"),
                )
            ).get(id=product_id, status=ProductStatusType.PUBLISH.value)
            apps_logger.info(
                "ProductVariantView: product retrieved successfully",
                extra={
                    "task_name": TaskName.PRODUCT_VARIANT,
                    "product_id": product_id,
                    "user_id": getattr(request.user, "id", None),
                    "correlation_id": getattr(request, "correlation_id", None),
                },
            )
        except ProductModel.DoesNotExist:
            apps_logger.error(
                "ProductVariantView: product not found or not available",
                extra={
                    "task_name": TaskName.PRODUCT_VARIANT,
                    "product_id": product_id,
                    "user_id": getattr(request.user, "id", None),
                    "correlation_id": getattr(request, "correlation_id", None),
                },
            )
            return JsonResponse(
                {"error": "Product not found or not available"}, status=404
            )

        matched_variant = None
        for variant in product.variants.all():
            attr_name = variant.attribute_value.attribute.name
            attr_value = variant.attribute_value.value

            if (
                selected_attrs.get(attr_name) == attr_value
                and len(selected_attrs) == 1
            ):
                matched_variant = variant
                break

        if matched_variant:
            has_discount = matched_variant.discount_percent > 0
            base_price = float(matched_variant.price)
            final_price = matched_variant.final_price

            apps_logger.info(
                "ProductVariantView: variant matched successfully",
                extra={
                    "task_name": TaskName.PRODUCT_VARIANT,
                    "product_id": product_id,
                    "variant_id": matched_variant.id,
                    "stock": matched_variant.stock,
                    "base_price": base_price,
                    "final_price": final_price,
                    "has_discount": has_discount,
                    "discount_percent": matched_variant.discount_percent,
                    "user_id": getattr(request.user, "id", None),
                    "correlation_id": getattr(request, "correlation_id", None),
                },
            )

            return JsonResponse(
                {
                    "success": True,
                    "variant_id": matched_variant.id,
                    "stock": matched_variant.stock,
                    "base_price": base_price,
                    "final_price": final_price,
                    "has_discount": has_discount,
                    "discount_percent": matched_variant.discount_percent,
                }
            )
        apps_logger.warning(
            "ProductVariantView: no matching variant found",
            extra={
                "task_name": TaskName.PRODUCT_VARIANT,
                "product_id": product_id,
                "selected_attrs": selected_attrs,
                "user_id": getattr(request.user, "id", None),
                "correlation_id": getattr(request, "correlation_id", None),
            },
        )

        return JsonResponse(
            {
                "success": False,
                "message": "No matching variant found for the selected options.",
            }
        )
