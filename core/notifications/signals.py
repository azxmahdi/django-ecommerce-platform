from django.db.models.signals import post_save
from django.dispatch import receiver

from order.models import OrderModel, OrderStatusType, FulfillmentStatus
from .models import MessageModel, MessageType


def build_order_message(order, created, old_status=None, old_fulfillment=None):

    if created:
        return {
            "title": "ثبت سفارش جدید",
            "body": f"سفارش شماره {order.id} با مبلغ {order.get_amount()} ثبت شد.",
        }

    if old_status and old_status != order.status:
        return {
            "title": f"تغییر وضعیت سفارش {order.id}",
            "body": f"وضعیت سفارش شما به '{OrderStatusType(order.status).label}' تغییر کرد.",
        }

    if old_fulfillment and old_fulfillment != order.fulfillment_status:
        return {
            "title": f"بروزرسانی ارسال سفارش {order.id}",
            "body": f"وضعیت ارسال سفارش شما به '{FulfillmentStatus(order.fulfillment_status).label}' تغییر کرد.",
        }

    return None


@receiver(post_save, sender=OrderModel)
def order_message_handler(sender, instance, created, **kwargs):
    if created:
        message_data = build_order_message(instance, created)
    else:
        old_status = instance.tracker.previous("status")
        old_fulfillment = instance.tracker.previous("fulfillment_status")

        message_data = build_order_message(
            instance, created, old_status, old_fulfillment
        )

    if message_data:
        MessageModel.objects.create(
            type=MessageType.ORDER,
            title=message_data["title"],
            body=message_data["body"],
            user=instance.user,
            order=instance,
        )
