from django.core.cache import cache


class SiteInfoCache:
    site_info_key = "site_info"
    version_key = "site_info_version"

    def __init__(self, provider):
        self.provider = provider
        self._initialize_version()

    def _initialize_version(self):
        if not cache.has_key(self.version_key):
            cache.set(self.version_key, 1)

    def get(self):
        version = cache.get(self.version_key, 1)
        key = f"{self.site_info_key}_v{version}"
        site_info = cache.get(key)

        if site_info is None:
            site_info = self.provider.get_latest()
            cache.set(key, site_info, None)

        return site_info

    def invalidate(self):
        try:
            cache.incr(self.version_key)
        except ValueError:
            cache.set(self.version_key, 2)
