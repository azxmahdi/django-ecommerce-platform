from common.services.base_context_builders import BaseContextBuilder
from banner.models import BannerModel, BannerPosition


class IndexContextBuilder(BaseContextBuilder):
    def _get_default_processors(self):
        return [
            self._add_banners,
        ]

    def get_base_data(self):
        return {}

    def _add_banners(self):
        banners = (
            BannerModel.objects.filter(is_active=True)
            .select_related("product_category", "post_category")
            .order_by("position", "order")
        )

        self.context["main_banners"] = [
            b for b in banners if b.position == BannerPosition.MAIN.value
        ]
        self.context["small_banners"] = [
            b for b in banners if b.position == BannerPosition.SMALL.value
        ]
        self.context["sidebar_banners"] = [
            b for b in banners if b.position == BannerPosition.SIDEBAR.value
        ]
        self.context["category_banners"] = [
            b for b in banners if b.position == BannerPosition.CATEGORY.value
        ]
