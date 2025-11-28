from django.urls import path

from .views import NewsLetterCreateView

app_name = "newsletter"

urlpatterns = [path("create/", NewsLetterCreateView.as_view(), name="create")]
