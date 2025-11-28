from abc import ABC, abstractmethod
import logging

from core.constants import TaskName, LoggerName

otp_logger = logging.getLogger(LoggerName.OTP)


class OTPProvider(ABC):
    @abstractmethod
    def send(self, phone: str, code: str) -> bool:
        pass


class SMSProvider(OTPProvider):
    def send(self, phone: str, code: str) -> bool:
        from .utils import send_otp_sms

        result = send_otp_sms(phone, code)
        if result["status"] == "success":
            otp_logger.info(
                "OTP sent successfully",
                extra={"task_name": TaskName.SEND_OTP, "phone": phone},
            )
        else:
            otp_logger.error(
                "OTP send failed",
                extra={
                    "task_name": TaskName.SEND_OTP,
                    "phone": phone,
                },
            )
        return result


class ConsoleSMSProvider(OTPProvider):
    def send(self, phone: str, code: str) -> bool:
        print(f"[DEBUG] OTP for {phone}: {code}")
        return True
