import logging
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from .models import ProductCategoryModel
from .services.category.provider import CategoryProvider
from .services.category.cache import CategoryCache
from core.constants import TaskName, LoggerName

cache_manager = CategoryCache(CategoryProvider())
apps_logger = logging.getLogger(LoggerName.APPS)


@receiver([post_save, post_delete], sender=ProductCategoryModel)
def clear_category_cache(sender, **kwargs):
    instance = kwargs.get("instance", None)
    created = kwargs.get("created", None)

    cache_manager.invalidate()

    if created is True:
        apps_logger.info(
            "Category cache invalidated after category creation",
            extra={
                "task_name": TaskName.CATEGORY_CACHE_INVALIDATE,
                "category_id": getattr(instance, "id", None),
                "category_name": getattr(instance, "name", None),
                "action": "created",
            },
        )
    elif created is False:
        apps_logger.info(
            "Category cache invalidated after category update",
            extra={
                "task_name": TaskName.CATEGORY_CACHE_INVALIDATE,
                "category_id": getattr(instance, "id", None),
                "category_name": getattr(instance, "name", None),
                "action": "updated",
            },
        )
    else:
        apps_logger.warning(
            "Category cache invalidated after category deletion",
            extra={
                "task_name": TaskName.CATEGORY_CACHE_INVALIDATE,
                "category_id": getattr(instance, "id", None),
                "category_name": getattr(instance, "name", None),
                "action": "deleted",
            },
        )
