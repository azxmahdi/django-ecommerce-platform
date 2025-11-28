from .models import StaticPageModel


def static_pages_processor(request):
    static_pages = StaticPageModel.objects.filter(is_active=True)
    return {"static_pages": static_pages}
