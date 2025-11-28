from django.urls import path, re_path

from .views import PostListView, PostDetailView

app_name = "blog"


urlpatterns = [
    path("post/list/", PostListView.as_view(), name="post-list"),
    re_path(
        r"post/(?P<slug>[-\w]+)/detail/",
        PostDetailView.as_view(),
        name="post-detail",
    ),
]
