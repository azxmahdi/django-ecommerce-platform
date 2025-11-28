from datetime import timedelta
from django.core.cache import cache


from shop.models import SearchLogModel


class PopularSearchCache:
    cache_key = "popular_searches"

    def get(self):
        popular_searches = cache.get(self.cache_key)

        if popular_searches is None:
            popular_searches = SearchLogModel.objects.get_popular_searches()
            cache.set(
                self.cache_key,
                popular_searches,
                timedelta(days=2).total_seconds(),
            )

        return popular_searches
