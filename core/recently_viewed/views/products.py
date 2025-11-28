from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse

from ..services.recently_viewed_products import RecentlyViewedProductsService


class RemoveProductView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        if product_id := request.POST.get("product_id"):
            service = RecentlyViewedProductsService(self.request.user)
            service.remove_product(int(product_id))
            return JsonResponse(
                {"status": "success", "message": "محصول از با موفقیت حذف شد"}
            )
        return JsonResponse(
            {"status": "error", "message": "داده ها ناقص است."}
        )


class RemoveAllProductsView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        service = RecentlyViewedProductsService(self.request.user)
        service.clear()
        return JsonResponse(
            {"status": "success", "message": "همه محصولات با موفقیت حذف شدند"}
        )
