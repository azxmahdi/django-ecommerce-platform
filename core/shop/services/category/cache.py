from django.core.cache import cache

from .provider import CategoryProvider


class CategoryCache:
    category_key = "categories_tree"
    version_key = "categories_version"

    def __init__(self, provider):
        self.provider = provider
        self._initialize_version()

    def _initialize_version(self):
        if not cache.has_key(self.version_key):
            cache.set(self.version_key, 1)

    def get(self):
        version = cache.get(self.version_key, 1)
        key = f"{self.category_key}_v{version}"
        categories = cache.get(key)

        if categories is None:
            categories = self.provider.get_all()
            cache.set(key, categories, None)

        return categories

    def invalidate(self):
        try:
            cache.incr(self.version_key)
        except ValueError:
            cache.set(self.version_key, 2)
