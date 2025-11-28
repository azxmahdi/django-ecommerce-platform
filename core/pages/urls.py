from django.urls import re_path

from .views import StaticPageView


app_name = "pages"

urlpatterns = [
    re_path(
        r"static-page/(?P<slug>[-\w]+)/",
        StaticPageView.as_view(),
        name="static-page",
    ),
]
