from django.contrib.auth import get_user_model


User = get_user_model()


def user_processor(request):
    if not request.user.is_authenticated:
        return {"user": None}
    try:
        user = User.objects.prefetch_related("user_profile").get(
            id=request.user.id
        )
    except User.DoesNotExist:
        user = None
    return {"user": user}
