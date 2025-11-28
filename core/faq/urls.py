from django.urls import path

from .views import FAQListView


app_name = "faq"

urlpatterns = [
    path("list/", FAQListView.as_view(), name="list"),
]
