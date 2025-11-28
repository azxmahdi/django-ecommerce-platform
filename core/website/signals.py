import logging
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from .models import SiteInfoModel, SiteResourceModel
from .services.site_info.provider import SiteInfoProvider
from .services.site_info.cache import SiteInfoCache
from .services.site_resource.cache import (
    SiteResourceLicensesCache,
    SiteResourceSocialsCache,
)
from .services.site_resource.provider import (
    SiteResourceLicensesProvider,
    SiteResourceSocialsProvider,
)
from core.constants import TaskName, LoggerName


apps_logger = logging.getLogger(LoggerName.APPS)


@receiver([post_save, post_delete], sender=SiteInfoModel)
def clear_site_info_cache(sender, **kwargs):
    cache_manager = SiteInfoCache(SiteInfoProvider())
    instance = kwargs.get("instance", None)
    created = kwargs.get("created", None)

    cache_manager.invalidate()

    if created is True:
        apps_logger.info(
            "SiteInfo cache invalidated after creation",
            extra={
                "task_name": TaskName.SITE_INFO_CACHE_INVALIDATE,
                "site_info_id": getattr(instance, "id", None),
                "action": "created",
                "correlation_id": getattr(
                    getattr(instance, "_request", None), "correlation_id", None
                ),
            },
        )
    elif created is False:
        apps_logger.info(
            "SiteInfo cache invalidated after update",
            extra={
                "task_name": TaskName.SITE_INFO_CACHE_INVALIDATE,
                "site_info_id": getattr(instance, "id", None),
                "action": "updated",
                "correlation_id": getattr(
                    getattr(instance, "_request", None), "correlation_id", None
                ),
            },
        )
    else:
        apps_logger.warning(
            "SiteInfo cache invalidated after deletion",
            extra={
                "task_name": TaskName.SITE_INFO_CACHE_INVALIDATE,
                "site_info_id": getattr(instance, "id", None),
                "action": "deleted",
                "correlation_id": getattr(
                    getattr(instance, "_request", None), "correlation_id", None
                ),
            },
        )


@receiver([post_save, post_delete], sender=SiteResourceModel)
def clear_site_resource_cache(sender, **kwargs):
    instance = kwargs.get("instance", None)
    created = kwargs.get("created", None)

    socials_cache = SiteResourceSocialsCache(SiteResourceSocialsProvider())
    licenses_cache = SiteResourceLicensesCache(SiteResourceLicensesProvider())

    socials_cache.invalidate()
    licenses_cache.invalidate()

    if created is True:
        action = "created"
        msg = "SiteResource cache invalidated after creation"
    elif created is False:
        action = "updated"
        msg = "SiteResource cache invalidated after update"
    else:
        action = "deleted"
        msg = "SiteResource cache invalidated after deletion"

    apps_logger.info(
        msg,
        extra={
            "task_name": TaskName.SITE_RESOURCE_CACHE_INVALIDATE,
            "site_resource_id": getattr(instance, "id", None),
            "action": action,
            "correlation_id": getattr(
                getattr(instance, "_request", None), "correlation_id", None
            ),
        },
    )
