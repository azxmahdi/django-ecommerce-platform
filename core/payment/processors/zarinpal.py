import json
import requests
from django.urls import reverse
from django.conf import settings
from .base import BasePaymentProcessor, BasePaymentVerifier
import logging
from core.constants import TaskName, LoggerName

payment_logger = logging.getLogger(LoggerName.PAYMENT)


def get_domain():
    try:
        from django.contrib.sites.models import Site

        domain = Site.objects.get_current().domain
        payment_logger.info(
            "Domain retrieved successfully",
            extra={"task_name": TaskName.GET_DOMAIN, "domain": domain},
        )
        return domain
    except BaseException as e:
        payment_logger.warning(
            "Fallback to default domain due to error",
            extra={
                "task_name": TaskName.GET_DOMAIN,
                "domain": "example.com",
                "error": str(e),
            },
        )
        return "example.com"


def get_protocol():
    return (
        "https" if getattr(settings, "SECURE_SSL_REDIRECT", False) else "http"
    )


class ZarinPalSandboxProcessor(BasePaymentProcessor):

    _payment_request_url = (
        "https://sandbox.zarinpal.com/pg/v4/payment/request.json"
    )
    _payment_page_url = "https://sandbox.zarinpal.com/pg/StartPay/"

    def __init__(self, merchant_id=settings.MERCHANT_ID):
        self.merchant_id = merchant_id

    @property
    def _callback_url(self):
        return f"{get_protocol()}://{get_domain()}{reverse('payment:verify')}"

    def payment_request(self, amount, description="پرداختی کاربر"):

        payload = {
            "merchant_id": self.merchant_id,
            "amount": str(amount),
            "callback_url": self._callback_url,
            "description": "افزایش اعتبار کاربر شماره ۱۱۳۴۶۲۹",
            "metadata": {
                "mobile": "09195523234",
                "email": "info.davari@gmail.com",
            },
        }
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        response = requests.post(
            self._payment_request_url,
            headers=headers,
            data=json.dumps(payload),
        )
        result = response.json()
        payment_logger.info(
            "Payment request sent successfully to ZarinPal sandbox",
            extra={
                "task_name": TaskName.PAYMENT_REQUEST,
                "merchant_id": self.merchant_id,
                "amount": amount,
                "authority": result["data"]["authority"],
                "response_code": result["data"].get("code"),
            },
        )
        return result

    def generate_payment_url(self, authority):
        payment_url = f"{self._payment_page_url}{authority}"
        payment_logger.info(
            "Payment URL generated successfully for ZarinPal sandbox",
            extra={
                "task_name": TaskName.GENERATE_PAYMENT_URL,
                "merchant_id": self.merchant_id,
                "authority": authority,
                "payment_url": payment_url,
            },
        )
        return payment_url


class ZarinPalSandboxVerifier(BasePaymentVerifier):

    _payment_verify_url = (
        "https://sandbox.zarinpal.com/pg/v4/payment/verify.json"
    )

    def __init__(self, merchant_id=settings.MERCHANT_ID):
        self.merchant_id = merchant_id

    def payment_verify(self, amount, authority):
        payload = {
            "merchant_id": self.merchant_id,
            "amount": amount,
            "authority": authority,
        }
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        response = requests.post(
            self._payment_verify_url, headers=headers, data=json.dumps(payload)
        )
        result = response.json()
        payment_logger.info(
            "Payment verification succeeded in ZarinPal sandbox",
            extra={
                "task_name": TaskName.PAYMENT_VERIFY,
                "merchant_id": self.merchant_id,
                "amount": amount,
                "authority": authority,
                "ref_id": result["data"].get("ref_id"),
                "response_code": result["data"].get("code"),
            },
        )
        return result


class ZarinPalProductionProcessor(BasePaymentProcessor):
    _payment_request_url = (
        "https://api.zarinpal.com/pg/v4/payment/request.json"
    )
    _payment_page_url = "https://www.zarinpal.com/pg/StartPay/"
    _callback_url = f"{get_protocol()}://{get_domain()}/payment/verify"

    def __init__(self, merchant_id=settings.MERCHANT_ID):
        self.merchant_id = merchant_id

    def payment_request(self, amount, description="پرداختی کاربر"):
        payload = {
            "merchant_id": self.merchant_id,
            "amount": str(amount),
            "callback_url": self._callback_url,
            "description": description,
            "metadata": {
                "mobile": "09195523234",
                "email": "info.davari@gmail.com",
            },
        }
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        response = requests.post(
            self._payment_request_url,
            headers=headers,
            data=json.dumps(payload),
        )
        result = response.json()

        payment_logger.info(
            "Payment request sent successfully to ZarinPal production",
            extra={
                "task_name": TaskName.PAYMENT_REQUEST,
                "merchant_id": self.merchant_id,
                "amount": amount,
                "authority": result["data"]["authority"],
                "response_code": result["data"].get("code"),
            },
        )

        return result

    def generate_payment_url(self, authority):
        payment_url = f"{self._payment_page_url}{authority}"
        payment_logger.info(
            "Payment URL generated successfully for ZarinPal production",
            extra={
                "task_name": TaskName.GENERATE_PAYMENT_URL,
                "merchant_id": self.merchant_id,
                "authority": authority,
                "payment_url": payment_url,
            },
        )
        return payment_url


class ZarinPalProductionVerifier(BasePaymentVerifier):

    _payment_verify_url = "https://api.zarinpal.com/pg/v4/payment/verify.json"

    def __init__(self, merchant_id=settings.MERCHANT_ID):
        self.merchant_id = merchant_id

    def payment_verify(self, amount, authority):
        payload = {
            "merchant_id": self.merchant_id,
            "amount": amount,
            "authority": authority,
        }
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        response = requests.post(
            self._payment_verify_url, headers=headers, data=json.dumps(payload)
        )
        result = response.json()

        payment_logger.info(
            "Payment verification succeeded in ZarinPal production",
            extra={
                "task_name": TaskName.PAYMENT_VERIFY,
                "merchant_id": self.merchant_id,
                "amount": amount,
                "authority": authority,
                "ref_id": result["data"].get("ref_id"),
                "response_code": result["data"].get("code"),
            },
        )

        return result
