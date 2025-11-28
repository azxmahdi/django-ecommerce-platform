import logging

from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver

from .services.cart import CartService
from .storage import SessionStorage

logger = logging.getLogger(__name__)


@receiver(user_logged_in)
def post_login(sender, user, request, **kwargs):
    cart_service = CartService(SessionStorage(request.session), user)
    cart_service.sync(user)
    logger.info(
        "Cart synced after login",
        extra={
            "user_id": user.id,
            "session_items_count": cart_service.total_quantity(),
        },
    )


@receiver(user_logged_out)
def pre_logout(sender, user, request, **kwargs):
    cart_service = CartService(SessionStorage(request.session), user)
    cart_service.merge(user)
    logger.info("Cart merged before logout", extra={"user_id": user.id})
