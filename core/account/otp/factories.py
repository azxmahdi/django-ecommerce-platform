from django.conf import settings
from .providers import SMSProvider, ConsoleSMSProvider


class SMSProviderFactory:
    @staticmethod
    def create_provider():
        if settings.DEBUG:
            return ConsoleSMSProvider()
        return SMSProvider()
