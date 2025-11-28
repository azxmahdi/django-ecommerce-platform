from django.db.models import Prefetch
from mptt.templatetags.mptt_tags import cache_tree_children

from website.models import SiteInfoModel


class SiteInfoProvider:
    def get_latest(self):
        try:
            return SiteInfoModel.objects.latest("created_date")
        except SiteInfoModel.DoesNotExist:
            return None
