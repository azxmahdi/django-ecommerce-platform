from django.conf import settings
from .base import PaymentGatewayFactory
from payment.processors.zarinpal import (
    ZarinPalSandboxProcessor,
    ZarinPalSandboxVerifier,
    ZarinPalProductionProcessor,
    ZarinPalProductionVerifier,
)


class ZarinPalSandboxFactory(PaymentGatewayFactory):

    def __init__(self, merchant_id=None):
        self.merchant_id = merchant_id or getattr(settings, "MERCHANT_ID", "")

    def create_payment_processor(self):
        return ZarinPalSandboxProcessor(merchant_id=self.merchant_id)

    def create_payment_verifier(self):
        return ZarinPalSandboxVerifier(merchant_id=self.merchant_id)


class ZarinPalProductionFactory(PaymentGatewayFactory):

    def __init__(self, merchant_id=None):
        self.merchant_id = merchant_id or getattr(settings, "MERCHANT_ID", "")

    def create_payment_processor(self):
        return ZarinPalProductionProcessor(merchant_id=self.merchant_id)

    def create_payment_verifier(self):
        return ZarinPalProductionVerifier(merchant_id=self.merchant_id)
