from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.http import JsonResponse

from .models import MessageModel, MessageType, UserMessageStatusModel


class RemoveAllMessagesView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        MessageModel.objects.filter(
            user=request.user,
            type__in=[MessageType.ORDER, MessageType.PERSONAL],
        ).delete()

        broadcast_messages = MessageModel.objects.filter(
            type=MessageType.BROADCAST
        )
        for msg in broadcast_messages:
            UserMessageStatusModel.objects.update_or_create(
                user=request.user, message=msg, defaults={"is_hidden": True}
            )

        return JsonResponse(
            {
                "status": "success",
                "message": "همه پیام‌ها حذف شدند و پیام‌های عمومی برای شما مخفی شدند",
            }
        )
