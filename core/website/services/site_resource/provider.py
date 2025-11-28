from website.models import SiteResourceModel, SiteResourceType


class SiteResourceSocialsProvider:
    def get_all(self):
        return SiteResourceModel.objects.filter(
            type=SiteResourceType.SOCIAL.value
        )


class SiteResourceLicensesProvider:
    def get_all(self):
        return SiteResourceModel.objects.filter(
            type=SiteResourceType.LICENSE.value
        )
