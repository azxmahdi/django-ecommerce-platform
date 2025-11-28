from abc import ABC, abstractmethod


class BasePaymentProcessor(ABC):
    @abstractmethod
    def payment_request(self, amount, description):
        pass

    @abstractmethod
    def generate_payment_url(self, authority):
        pass


class BasePaymentVerifier(ABC):
    @abstractmethod
    def payment_verify(self, amount, authority):
        pass
