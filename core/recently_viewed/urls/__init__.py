from django.urls import include, path

app_name = "recently_viewed"


urlpatterns = [
    path("", include("recently_viewed.urls.products")),
]
