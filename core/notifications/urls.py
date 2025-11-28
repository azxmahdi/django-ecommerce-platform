from django.urls import path

from .views import RemoveAllMessagesView

app_name = "notifications"

urlpatterns = [
    path(
        "remove/all/messages/",
        RemoveAllMessagesView.as_view(),
        name="remove-all-messages",
    )
]
