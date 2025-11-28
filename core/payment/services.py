import logging
import json

from django.conf import settings

from .models import PaymentModel, PaymentGateway, PaymentStatusType
from .factories import PaymentFactoryCreator
from core.constants import TaskName, LoggerName

payment_logger = logging.getLogger(LoggerName.PAYMENT)


def _json_safe(data):
    return json.loads(json.dumps(data, default=str))


class PaymentService:

    @staticmethod
    def create_payment(gateway, amount, order, user=None, description=""):

        payment = PaymentModel.objects.create(
            gateway=gateway,
            amount=amount,
            user=user,
            order=order,
            description=description,
        )
        payment_logger.info(
            "Payment created successfully",
            extra={
                "task_name": TaskName.PAYMENT_CREATE,
                "payment_id": payment.id,
                "gateway": gateway.name,
                "amount": amount,
                "order_id": order.id,
                "user_id": getattr(user, "id", None),
            },
        )
        return payment, None

    @staticmethod
    def initiate_payment(payment, description=""):
        try:
            factory = PaymentFactoryCreator.get_factory(
                gateway_name=payment.gateway.name,
                sandbox=getattr(settings, "PAYMENT_SANDBOX_MODE", True),
            )
            processor = factory.create_payment_processor()
            result = processor.payment_request(payment.amount, description)
            if result.get("data") and result["data"].get("authority"):
                authority = result["data"]["authority"]
                payment_url = processor.generate_payment_url(authority)

                payment.authority_id = authority
                payment.response_json = result
                payment.save()
                payment_logger.info(
                    "Payment initiated successfully",
                    extra={
                        "task_name": TaskName.PAYMENT_INITIATE,
                        "payment_id": payment.id,
                        "gateway": payment.gateway.name,
                        "amount": payment.amount,
                        "authority": authority,
                        "payment_url": payment_url,
                    },
                )

                return payment_url, authority, None
            else:
                error_msg = result.get("errors", {}).get(
                    "message", "خطا در اتصال به درگاه"
                )
                payment_logger.error(
                    "Payment initiation failed",
                    extra={
                        "task_name": TaskName.PAYMENT_INITIATE,
                        "payment_id": payment.id,
                        "gateway": payment.gateway.name,
                        "amount": payment.amount,
                        "error": error_msg,
                        "response": result,
                    },
                )
                return None, None, error_msg

        except Exception as e:
            payment_logger.error(
                "Exception occurred during payment initiation",
                extra={
                    "task_name": TaskName.PAYMENT_INITIATE,
                    "payment_id": payment.id,
                    "gateway": payment.gateway.name,
                    "amount": payment.amount,
                    "error": str(e),
                },
            )
            return None, None, str(e)

    @staticmethod
    def verify_payment(payment):
        try:
            factory = PaymentFactoryCreator.get_factory(
                gateway_name=payment.gateway.name,
                sandbox=getattr(settings, "PAYMENT_SANDBOX_MODE", True),
            )
            verifier = factory.create_payment_verifier()

            result = verifier.payment_verify(
                int(payment.amount), payment.authority_id
            )

            if result.get("data") and result["data"].get("code") == 100:
                ref_id = result["data"].get("ref_id")

                payment.ref_id = ref_id
                payment.status = PaymentStatusType.SUCCESS.value
                payment.response_json = _json_safe(result)
                payment.response_code = result["data"].get("code")
                payment.save()

                payment_logger.info(
                    "Payment verified successfully",
                    extra={
                        "task_name": TaskName.PAYMENT_VERIFY,
                        "payment_id": payment.id,
                        "gateway": payment.gateway.name,
                        "amount": int(payment.amount),
                        "authority": payment.authority_id,
                        "ref_id": ref_id,
                        "response_code": result["data"].get("code"),
                    },
                )

                return True, ref_id, None
            else:
                error_code = result.get("data", {}).get("code", "نامشخص")
                payment.status = PaymentStatusType.FAILED.value
                payment.response_json = _json_safe(result)
                payment.response_code = error_code
                payment.save()

                payment_logger.warning(
                    "Payment verification failed",
                    extra={
                        "task_name": TaskName.PAYMENT_VERIFY,
                        "payment_id": payment.id,
                        "gateway": payment.gateway.name,
                        "amount": int(payment.amount),
                        "authority": payment.authority_id,
                        "error_code": error_code,
                        "response": _json_safe(result),
                    },
                )

                return False, None, f"کد خطا: {error_code}"

        except Exception as e:
            payment_logger.error(
                "Exception occurred during payment verification",
                extra={
                    "task_name": TaskName.PAYMENT_VERIFY,
                    "payment_id": payment.id,
                    "gateway": payment.gateway.name,
                    "amount": int(payment.amount),
                    "authority": payment.authority_id,
                    "error": str(e),
                },
            )
            return False, None, str

    @staticmethod
    def get_payment_by_authority(authority):
        try:
            payment = PaymentModel.objects.get(authority_id=authority)
            payment_logger.info(
                "Payment found by authority",
                extra={
                    "task_name": TaskName.PAYMENT_GET_BY_AUTHORITY,
                    "authority": authority,
                    "payment_id": payment.id,
                },
            )
            return payment
        except PaymentModel.DoesNotExist:
            payment_logger.warning(
                "Payment not found by authority",
                extra={
                    "task_name": TaskName.PAYMENT_GET_BY_AUTHORITY,
                    "authority": authority,
                },
            )
            return None

    @staticmethod
    def generate_payment_url(gateway, authority_id):
        factory = PaymentFactoryCreator.get_factory(
            gateway_name=gateway.name,
            sandbox=getattr(settings, "PAYMENT_SANDBOX_MODE", True),
        )
        processor = factory.create_payment_processor()
        payment_url = processor.generate_payment_url(authority_id)
        payment_logger.info(
            "Payment URL generated",
            extra={
                "task_name": TaskName.GENERATE_PAYMENT_URL,
                "gateway": gateway.name,
                "authority": authority_id,
                "payment_url": payment_url,
            },
        )
        return payment_url
