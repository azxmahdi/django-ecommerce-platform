from website.services.site_info.cache import SiteInfoCache
from website.services.site_info.provider import SiteInfoProvider
from website.services.site_resource.cache import (
    SiteResourceLicensesCache,
    SiteResourceSocialsCache,
)
from website.services.site_resource.provider import (
    SiteResourceLicensesProvider,
    SiteResourceSocialsProvider,
)


def site_info_processor(request):
    cache_manager = SiteInfoCache(SiteInfoProvider())
    return {"site_info": cache_manager.get()}


def site_resource_socials_processor(request):
    cache_manager = SiteResourceSocialsCache(SiteResourceSocialsProvider())
    return {"site_resource_socials": cache_manager.get()}


def site_resource_licenses_processor(request):
    cache_manager = SiteResourceLicensesCache(SiteResourceLicensesProvider())
    return {"site_resource_licenses": cache_manager.get()}
