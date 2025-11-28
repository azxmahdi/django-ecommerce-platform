import logging
import random

from django.conf import settings
from django.core.cache import cache

from .providers import OTPProvider
from .factories import SMSProviderFactory
from core.constants import TaskName, LoggerName

otp_logger = logging.getLogger(LoggerName.OTP)


class OTPService:
    def __init__(self, phone: str, provider: OTPProvider = None):
        self.phone = phone
        self.cache_key = f"otp:{phone}"
        self.provider = provider or SMSProviderFactory.create_provider()

    def _generate_code(self) -> str:
        return "".join(
            random.choices("0123456789", k=settings.OTP_CODE_LENGTH)
        )

    def exists(self) -> bool:
        return cache.get(self.cache_key) is not None

    def time_remaining(self) -> int:
        return cache.ttl(self.cache_key) or 0

    def send_new(self) -> dict:
        code = self._generate_code()
        cache.set(self.cache_key, code, settings.OTP_EXPIRY_SECONDS)

        if not self.provider.send(self.phone, code):
            otp_logger.error(
                "OTP send failed",
                extra={
                    "task_name": TaskName.SEND_OTP,
                    "phone": self.phone,
                },
            )
            cache.delete(self.cache_key)
            return {"status": "error", "message": "خطا در ارسال پیامک."}
        otp_logger.info(
            "OTP sent successfully",
            extra={
                "task_name": TaskName.SEND_OTP,
                "phone": self.phone,
            },
        )
        return {
            "status": "success",
            "message": f"کد تأیید به شماره {self.phone} ارسال شد.",
            "expiry": settings.OTP_EXPIRY_SECONDS,
        }

    def send(self) -> dict:
        if self.exists():
            return {
                "status": "error",
                "message": f"کد قبلا ارسال شده. لطفا {self.time_remaining()} ثانیه منتظر بمانید.",
                "remaining_time": self.time_remaining(),
            }
        return self.send_new()


class OTPVerificationService:
    def __init__(self, cache_backend=cache, prefix: str = "otp:"):
        self.cache = cache_backend
        self.prefix = prefix

    def verify(self, phone: str, code: str) -> dict:
        key = f"{self.prefix}{phone}"
        stored = self.cache.get(key)

        if stored is None:
            return {"status": "error", "message": "کد منقضی شده یا وجود ندارد"}

        if code != stored:
            return {"status": "error", "message": "کد واردشده نادرست است"}

        self.cache.delete(key)
        return {"status": "success", "message": "کد با موفقیت تأیید شد"}
