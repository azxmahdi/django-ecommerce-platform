from abc import ABC, abstractmethod


class PaymentGatewayFactory(ABC):
    @abstractmethod
    def create_payment_processor(self):
        pass

    @abstractmethod
    def create_payment_verifier(self):
        pass
