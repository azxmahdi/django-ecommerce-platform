from django.urls import path

from .views import ContactCreateView

app_name = "contact"

urlpatterns = [
    path("create/", ContactCreateView.as_view(), name="create"),
]
