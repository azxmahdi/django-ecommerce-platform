from django.core.cache import cache


class SiteResourceSocialsCache:
    site_resource_socials_key = "site_resource_socials"
    version_key = "site_resource_social_version"

    def __init__(self, provider):
        self.provider = provider
        self._initialize_version()

    def _initialize_version(self):
        if not cache.has_key(self.version_key):
            cache.set(self.version_key, 1)

    def get(self):
        version = cache.get(self.version_key, 1)
        key = f"{self.site_resource_socials_key}_v{version}"
        site_resource_socials = cache.get(key)

        if site_resource_socials is None:
            site_resource_socials = self.provider.get_all()
            cache.set(key, site_resource_socials, None)

        return site_resource_socials

    def invalidate(self):
        try:
            cache.incr(self.version_key)
        except ValueError:
            cache.set(self.version_key, 2)


class SiteResourceLicensesCache:
    site_resource_licenses_key = "site_resource_licenses"
    version_key = "site_resource_licenses_version"

    def __init__(self, provider):
        self.provider = provider
        self._initialize_version()

    def _initialize_version(self):
        if not cache.has_key(self.version_key):
            cache.set(self.version_key, 1)

    def get(self):
        version = cache.get(self.version_key, 1)
        key = f"{self.site_resource_licenses_key}_v{version}"
        site_resource_licenses = cache.get(key)

        if site_resource_licenses is None:
            site_resource_licenses = self.provider.get_all()
            cache.set(key, site_resource_licenses, None)

        return site_resource_licenses

    def invalidate(self):
        try:
            cache.incr(self.version_key)
        except ValueError:
            cache.set(self.version_key, 2)
