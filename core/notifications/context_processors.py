from django.db.models import Q

from .models import MessageModel, UserMessageStatusModel, MessageType


def new_messages_count_processor(request):
    if not request.user.is_authenticated:
        return {"new_messages": None}

    user = request.user
    count = MessageModel.objects.filter(
        Q(type=MessageType.BROADCAST.value)
        & ~Q(user_statuses__user=user, user_statuses__is_read=True)
        | Q(
            user=user,
            type__in=[MessageType.ORDER.value, MessageType.PERSONAL.value],
            is_read=False,
        )
    ).count()

    return {"new_messages_count": count}
