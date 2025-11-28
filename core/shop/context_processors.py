from shop.services.category.provider import CategoryProvider
from shop.services.category.cache import CategoryCache
from shop.models import SearchLogModel
from shop.services.search_log.cache import PopularSearchCache


def categories_processor(request):
    cache_manager = CategoryCache(CategoryProvider())
    return {"categories": cache_manager.get()}


def search_log_processor(request):
    popular_cache_manager = PopularSearchCache()
    recent_searches = None
    if request.user.is_authenticated:
        try:
            recent_searches = SearchLogModel.objects.filter(user=request.user)

        except SearchLogModel.DoesNotExist:
            pass

    return {
        "recent_searches": recent_searches,
        "popular_searches": popular_cache_manager.get(),
    }
