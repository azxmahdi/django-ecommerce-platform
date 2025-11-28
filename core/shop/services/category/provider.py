from django.db.models import Prefetch
from mptt.templatetags.mptt_tags import cache_tree_children
from shop.models import ProductCategoryModel


class CategoryProvider:
    def get_all(self):
        queryset = ProductCategoryModel.objects.prefetch_related(
            Prefetch(
                "children",
                queryset=ProductCategoryModel.objects.prefetch_related(
                    Prefetch(
                        "children", queryset=ProductCategoryModel.objects.all()
                    )
                ),
            )
        ).all()

        return cache_tree_children(queryset)
