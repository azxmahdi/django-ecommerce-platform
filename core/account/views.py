import logging
from abc import ABC, abstractmethod

from django.contrib import messages
from django.contrib.auth import get_user_model, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.hashers import make_password
from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic import FormView, View, TemplateView
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from django.core.cache import cache
from django.conf import settings

from django_ratelimit.decorators import ratelimit


from .forms import (
    PhoneAuthenticationForm,
    LoginPasswordForm,
    OTPForm,
    SetPasswordForm,
)
from .mixins import OTPContextMixin, LoginRedirectMixin, RedirectNextMixin
from .otp.services import OTPService, OTPVerificationService
from .utils import set_next_url, get_redirect_url, set_next_url_logout
from core.constants import TaskName, LoggerName


User = get_user_model()


auth_logger = logging.getLogger(LoggerName.AUTHENTICATION)
security_logger = logging.getLogger(LoggerName.SECURITY)
otp_logger = logging.getLogger(LoggerName.OTP)


class BaseOTPView(OTPContextMixin, FormView, ABC):
    form_class = OTPForm
    template_name = "account/otp.html"
    success_url = None
    success_message = ""
    otp_verification_service = OTPVerificationService()
    page_title = ""

    def get(self, request, *args, **kwargs):
        phone = request.session.get("phone")
        if phone:
            cache.delete(f"otp:{phone}")
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data["page_title"] = self.page_title
        return context_data

    def get_success_url(self):
        next_url = self.request.session.get("next_url")
        if next_url:
            self.request.session.pop("next_url", None)
            return next_url
        return super().get_success_url()

    def form_valid(self, form):
        phone = self.request.session.get("phone")
        code = form.cleaned_data["code"]

        auth_logger.info(
            "OTP verification attempt",
            extra={
                "task_name": TaskName.OTP_VERIFICATION,
                "phone": phone,
                "view": self.__class__.__name__,
                "code_length": len(code) if code else 0,
                "correlation_id": getattr(
                    self.request, "correlation_id", None
                ),
            },
        )

        result = self.otp_verification_service.verify(phone, code)

        if result["status"] == "error":
            auth_logger.warning(
                "OTP verification failed",
                extra={
                    "task_name": TaskName.OTP_VERIFICATION,
                    "phone": phone,
                    "view": self.__class__.__name__,
                    "error": result["message"],
                    "correlation_id": getattr(
                        self.request, "correlation_id", None
                    ),
                },
            )
            messages.error(self.request, result["message"])
            return self.form_invalid(form)

        auth_logger.info(
            "OTP verification successful",
            extra={
                "task_name": TaskName.OTP_VERIFICATION,
                "phone": phone,
                "view": self.__class__.__name__,
                "correlation_id": getattr(
                    self.request, "correlation_id", None
                ),
            },
        )

        self.post_verify()
        messages.success(self.request, self.success_message)
        return redirect(self.success_url or self.get_success_url())

    @abstractmethod
    def post_verify(self):
        pass


class BaseLoginView(LoginRedirectMixin, FormView, ABC):
    template_name = None
    form_class = None
    success_message = "شما با موفقیت وارد شدید"
    redirect_url = reverse_lazy("website:index")

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.phone = request.session.get("phone")

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(self.get_success_url())
        return super().dispatch(request, *args, **kwargs)

    def get_user(self):
        try:
            return User.objects.get(phone=self.phone)
        except User.DoesNotExist:
            auth_logger.error(
                "User not found",
                extra={
                    "task_name": TaskName.LOGIN,
                    "phone": self.phone,
                    "view": self.__class__.__name__,
                    "correlation_id": getattr(
                        self.request, "correlation_id", None
                    ),
                },
            )
            messages.error(self.request, "خطای سیستمی: کاربر یافت نشد.")
            return None

    def validate_user(self, user):
        if not user:
            auth_logger.warning(
                "Login attempt for inactive user",
                extra={
                    "task_name": TaskName.LOGIN,
                    "phone": self.phone,
                    "view": self.__class__.__name__,
                    "correlation_id": getattr(
                        self.request, "correlation_id", None
                    ),
                },
            )
            return False

        if not user.is_active:
            messages.error(
                self.request,
                "حساب شما غیرفعال است. لطفا با پشتیبانی تماس بگیرید.",
            )
            return False
        return True

    @abstractmethod
    def authenticate(self, form):
        pass

    def form_valid(self, form):
        user = self.get_user()
        if not self.validate_user(user):
            return self.form_invalid(form)

        if not self.authenticate(form):
            return self.form_invalid(form)

        login(self.request, user)

        auth_logger.info(
            "User logged in successfully",
            extra={
                "task_name": TaskName.LOGIN,
                "user_id": user.id,
                "phone": self.phone,
                "view": self.__class__.__name__,
                "correlation_id": getattr(
                    self.request, "correlation_id", None
                ),
            },
        )

        messages.success(self.request, self.success_message)

        return redirect(self.get_success_url())


@method_decorator(
    ratelimit(key="ip", rate="3/m", method="POST", block=False),
    name="dispatch",
)
@method_decorator(
    ratelimit(key="post:phone", rate="3/m", method="POST", block=False),
    name="dispatch",
)
class PhoneAuthenticationView(LoginRedirectMixin, FormView):
    template_name = "account/phone-authentication.html"
    form_class = PhoneAuthenticationForm
    redirect_url = reverse_lazy("website:index")

    def dispatch(self, request, *args, **kwargs):
        if getattr(request, "limited", False):
            security_logger.warning(
                "Rate limit exceeded for phone authentication",
                extra={
                    "task_name": TaskName.AUTHENTICATION,
                    "ip": request.META.get("REMOTE_ADDR"),
                    "view": self.__class__.__name__,
                    "user_agent": request.META.get("HTTP_USER_AGENT", ""),
                    "correlation_id": getattr(
                        self.request, "correlation_id", None
                    ),
                },
            )
            messages.error(
                request,
                "شما بیش از ۳ بار در دقیقه درخواست داده‌اید. لطفا یک دقیقه دیگر تلاش کنید.",
            )
            return redirect("account:phone-auth")

        if request.user.is_authenticated:
            return redirect(self.get_success_url())

        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        next_url = request.GET.get("next")
        set_next_url(request, next_url)
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        phone = form.cleaned_data["phone"]

        auth_logger.info(
            "Phone authentication initiated",
            extra={
                "task_name": TaskName.AUTHENTICATION,
                "phone": phone,
                "view": self.__class__.__name__,
                "correlation_id": getattr(
                    self.request, "correlation_id", None
                ),
            },
        )

        user, created = User.objects.get_or_create(phone=phone)
        if created:

            auth_logger.info(
                "New user created",
                extra={
                    "task_name": TaskName.AUTHENTICATION,
                    "user_id": user.id,
                    "phone": phone,
                    "view": self.__class__.__name__,
                    "correlation_id": getattr(
                        self.request, "correlation_id", None
                    ),
                },
            )

            user.set_unusable_password()
            user.save()

        request = self.request
        request.session["phone"] = phone

        auth_logger.info(
            "Phone authentication completed",
            extra={
                "task_name": TaskName.AUTHENTICATION,
                "user_id": user.id,
                "phone": phone,
                "has_password": user.has_usable_password(),
                "view": self.__class__.__name__,
                "correlation_id": getattr(
                    self.request, "correlation_id", None
                ),
            },
        )

        if user.has_usable_password():
            return redirect("account:login-password")

        return redirect("account:signup-otp")


@method_decorator(
    ratelimit(key="ip", rate="5/10m", method="POST", block=False),
    name="dispatch",
)
class SendOTPView(View):
    def dispatch(self, request, *args, **kwargs):
        if getattr(request, "limited", False):
            security_logger.warning(
                "Rate limit exceeded for OTP sending",
                extra={
                    "task_name": TaskName.SEND_OTP,
                    "ip": request.META.get("REMOTE_ADDR"),
                    "view": self.__class__.__name__,
                    "correlation_id": getattr(
                        self.request, "correlation_id", None
                    ),
                },
            )
            return JsonResponse(
                {
                    "status": "error",
                    "message": "شما بیش از ۵ بار در ده دقیقه درخواست ارسال پیامک داده‌اید. لطفا ده دقیقه دیگر تلاش کنید.",
                },
                status=429,
            )
        return super().dispatch(request, *args, **kwargs)

    def post(self, request):
        phone = request.session.get("phone")

        otp_logger.info(
            "OTP send request",
            extra={
                "task_name": TaskName.SEND_OTP,
                "phone": phone,
                "view": self.__class__.__name__,
                "correlation_id": getattr(
                    self.request, "correlation_id", None
                ),
            },
        )

        result = OTPService(phone).send()

        if result["status"] == "success":
            otp_logger.info(
                "OTP sent successfully",
                extra={
                    "task_name": TaskName.SEND_OTP,
                    "phone": phone,
                    "view": self.__class__.__name__,
                    "correlation_id": getattr(
                        self.request, "correlation_id", None
                    ),
                },
            )
        else:
            otp_logger.error(
                "OTP send failed",
                extra={
                    "task_name": TaskName.SEND_OTP,
                    "phone": phone,
                    "error": result.get("message", "Unknown error"),
                    "view": self.__class__.__name__,
                    "correlation_id": getattr(
                        self.request, "correlation_id", None
                    ),
                },
            )

        return JsonResponse(result)


@method_decorator(
    ratelimit(key="ip", rate="5/5m", method="POST", block=False),
    name="dispatch",
)
class SignupOTPView(BaseOTPView):
    success_url = reverse_lazy("account:set-password")
    success_message = "حساب شما فعال شد"
    page_title = "ثبت نام"

    def dispatch(self, request, *args, **kwargs):
        if getattr(request, "limited", False):
            security_logger.warning(
                "Rate limit exceeded for signup OTP",
                extra={
                    "task_name": TaskName.SIGNUP_OTP,
                    "ip": request.META.get("REMOTE_ADDR"),
                    "view": self.__class__.__name__,
                    "correlation_id": getattr(
                        self.request, "correlation_id", None
                    ),
                },
            )
            messages.error(
                request,
                "شما بیش از ۵ بار در پنج دقیقه تلاش برای تأیید کد کرده‌اید. لطفا چند دقیقه دیگر تلاش کنید.",
            )
            return redirect("account:signup-otp")
        return super().dispatch(request, *args, **kwargs)

    def post_verify(self):
        phone = self.request.session.get("phone")
        user = User.objects.get(phone=phone)
        user.is_active = True
        user.save()
        auth_logger.info(
            "User activated via OTP",
            extra={
                "task_name": TaskName.SIGNUP_OTP,
                "user_id": user.id,
                "phone": phone,
                "view": self.__class__.__name__,
                "correlation_id": getattr(
                    self.request, "correlation_id", None
                ),
            },
        )


@method_decorator(
    ratelimit(key="ip", rate="5/5m", method="POST", block=False),
    name="dispatch",
)
class ForgotOTPView(BaseOTPView):
    success_url = reverse_lazy("account:forgot-reset")
    success_message = "کد بازیابی رمز عبور شما تایید شد"
    page_title = "بازنشانی رمز عبور"

    def dispatch(self, request, *args, **kwargs):
        if getattr(request, "limited", False):
            security_logger.warning(
                "Rate limit exceeded for forgot password OTP",
                extra={
                    "task_name": TaskName.FORGOT_OTP,
                    "ip": request.META.get("REMOTE_ADDR"),
                    "view": self.__class__.__name__,
                    "user_agent": request.META.get("HTTP_USER_AGENT", ""),
                    "correlation_id": getattr(
                        self.request, "correlation_id", None
                    ),
                },
            )
            messages.error(
                request,
                "شما بیش از ۵ بار در پنج دقیقه تلاش برای تایید کد بازیابی رمز عبور کرده‌اید. لطفا چند دقیقه دیگر تلاش کنید.",
            )
            return redirect("account:forgot-otp")
        return super().dispatch(request, *args, **kwargs)

    def post_verify(self):
        phone = self.request.session.get("phone")
        cache.set(f"forgot_reset_{phone}", True, 10 * 60)


@method_decorator(
    ratelimit(key="ip", rate="5/10m", method="POST", block=False),
    name="dispatch",
)
class LoginPasswordView(BaseLoginView):
    template_name = "account/login-password.html"
    form_class = LoginPasswordForm
    success_message = "ورود با رمز عبور موفقیت‌آمیز بود"
    success_url = reverse_lazy("website:index")

    def dispatch(self, request, *args, **kwargs):
        if getattr(request, "limited", False):
            security_logger.warning(
                "Rate limit exceeded for password login",
                extra={
                    "task_name": TaskName.LOGIN_PASSWORD,
                    "ip": request.META.get("REMOTE_ADDR"),
                    "view": self.__class__.__name__,
                    "correlation_id": getattr(
                        self.request, "correlation_id", None
                    ),
                },
            )
            messages.error(
                request,
                "شما بیش از ۵ بار در ده دقیقه تلاش برای ورود کرده‌اید. لطفا ده دقیقه دیگر امتحان کنید.",
            )
            return redirect("account:login-password")
        return super().dispatch(request, *args, **kwargs)

    def authenticate(self, form):
        password = form.cleaned_data["password"]
        user = self.get_user()

        if not user or not user.check_password(password):
            auth_logger.warning(
                "Password authentication failed",
                extra={
                    "task_name": TaskName.LOGIN_PASSWORD,
                    "user_id": user.id if user else None,
                    "phone": self.phone,
                    "view": self.__class__.__name__,
                    "correlation_id": getattr(
                        self.request, "correlation_id", None
                    ),
                },
            )
            messages.error(self.request, "رمز عبور صحیح نیست.")
            return False
        return True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user_phone"] = self.phone
        return context


@method_decorator(
    ratelimit(key="ip", rate="5/10m", method="POST", block=False),
    name="dispatch",
)
class LoginOTPView(OTPContextMixin, BaseLoginView):
    form_class = OTPForm
    success_message = "ورود با کد یکبار مصرف موفقیت‌آمیز بود"
    success_url = reverse_lazy("website:index")
    otp_verification_service = OTPVerificationService()
    page_title = "ورود"

    def dispatch(self, request, *args, **kwargs):
        if getattr(request, "limited", False):
            security_logger.warning(
                "Rate limit exceeded for OTP login",
                extra={
                    "task_name": TaskName.LOGIN_OTP,
                    "ip": request.META.get("REMOTE_ADDR"),
                    "view": self.__class__.__name__,
                    "correlation_id": getattr(
                        self.request, "correlation_id", None
                    ),
                },
            )
            messages.error(
                request,
                "شما بیش از ۵ بار در ده دقیقه تلاش برای ورود با کد یکبار مصرف کرده‌اید. لطفا ده دقیقه دیگر امتحان کنید.",
            )
            return redirect("account:login-otp")
        return super().dispatch(request, *args, **kwargs)

    def authenticate(self, form):
        code = form.cleaned_data["code"]

        auth_logger.info(
            "OTP login attempt",
            extra={
                "task_name": TaskName.LOGIN_OTP,
                "phone": self.phone,
                "view": self.__class__.__name__,
                "code_length": len(code) if code else 0,
                "correlation_id": getattr(
                    self.request, "correlation_id", None
                ),
            },
        )

        result = self.otp_verification_service.verify(self.phone, code)

        if result["status"] == "error":
            auth_logger.warning(
                "OTP login failed",
                extra={
                    "task_name": TaskName.LOGIN_OTP,
                    "phone": self.phone,
                    "view": self.__class__.__name__,
                    "error": result["message"],
                    "correlation_id": getattr(
                        self.request, "correlation_id", None
                    ),
                },
            )
            messages.error(self.request, result["message"])
            return False
        auth_logger.info(
            "OTP login successful",
            extra={
                "task_name": TaskName.LOGIN_OTP,
                "phone": self.phone,
                "view": self.__class__.__name__,
                "correlation_id": getattr(
                    self.request, "correlation_id", None
                ),
            },
        )
        return True

    def get(self, request, *args, **kwargs):
        phone = request.session.get("phone")
        if phone:
            cache.delete(f"otp:{phone}")
        storage = messages.get_messages(request)
        context = self.get_context_data()
        context["system_messages"] = [
            {"text": msg.message, "tags": msg.tags} for msg in storage
        ]
        return self.render_to_response(context)

    def get_success_url(self):
        next_url = self.request.session.get("next_url")
        if next_url:
            self.request.session.pop("next_url", None)
            return next_url

        return self.redirect_url


@method_decorator(
    ratelimit(key="ip", rate="3/h", method="POST", block=False),
    name="dispatch",
)
class SetPasswordView(FormView):
    template_name = "account/set-password.html"
    form_class = SetPasswordForm
    success_url = reverse_lazy("website:index")
    success_message = "ساخت حساب شما با موفقیت تکمیل شد"

    def dispatch(self, request, *args, **kwargs):
        if getattr(request, "limited", False):
            security_logger.warning(
                "Rate limit exceeded for set password",
                extra={
                    "task_name": TaskName.SET_PASSWORD,
                    "ip": request.META.get("REMOTE_ADDR"),
                    "view": self.__class__.__name__,
                    "correlation_id": getattr(
                        self.request, "correlation_id", None
                    ),
                },
            )
            messages.error(
                request,
                "شما بیش از ۳ بار در هر ساعت تلاش برای تنظیم رمز عبور کرده‌اید. لطفا یک ساعت دیگر تلاش کنید.",
            )
            return redirect("account:set-password")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        phone = self.request.session.get("phone")
        user = User.objects.get(phone=phone)
        user.set_password(form.cleaned_data["password"])
        user.save()

        auth_logger.info(
            "Password set successfully",
            extra={
                "task_name": TaskName.SET_PASSWORD,
                "user_id": user.id,
                "phone": phone,
                "view": self.__class__.__name__,
                "correlation_id": getattr(
                    self.request, "correlation_id", None
                ),
            },
        )

        security_logger.info(
            "Password set successfully (security event)",
            extra={
                "task_name": TaskName.SET_PASSWORD,
                "user_id": user.id,
                "phone": phone,
                "ip": self.request.META.get("REMOTE_ADDR"),
                "view": self.__class__.__name__,
                "correlation_id": getattr(
                    self.request, "correlation_id", None
                ),
            },
        )

        login(self.request, user)
        messages.success(self.request, self.success_message)
        return super().form_valid(form)

    def get_success_url(self):
        next_url = self.request.session.get("next_url")
        if next_url:
            self.request.session.pop("next_url", None)
            return next_url
        return super().get_success_url()


@method_decorator(
    ratelimit(key="ip", rate="3/h", method="POST", block=False),
    name="dispatch",
)
class ForgotResetView(FormView):
    template_name = "account/forgot-reset.html"
    form_class = SetPasswordForm
    success_url = reverse_lazy("account:phone-auth")
    success_message = "رمز عبور شما با موفقیت تغییر یافت"

    def dispatch(self, request, *args, **kwargs):
        if getattr(request, "limited", False):
            security_logger.warning(
                "Rate limit exceeded for password reset",
                extra={
                    "task_name": TaskName.PASSWORD_RESET,
                    "ip": request.META.get("REMOTE_ADDR"),
                    "view": self.__class__.__name__,
                    "user_agent": request.META.get("HTTP_USER_AGENT", ""),
                    "correlation_id": getattr(
                        self.request, "correlation_id", None
                    ),
                },
            )
            messages.error(
                request,
                "شما بیش از ۳ بار در هر ساعت تلاش برای بازیابی رمز عبور کرده‌اید. لطفا یک ساعت دیگر تلاش کنید.",
            )
            return redirect("account:forgot-reset")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        phone = self.request.session.get("phone")
        if not cache.get(f"forgot_reset_{phone}"):
            security_logger.warning(
                "Unauthorized password reset attempt",
                extra={
                    "task_name": TaskName.PASSWORD_RESET,
                    "phone": phone,
                    "view": self.__class__.__name__,
                    "ip": self.request.META.get("REMOTE_ADDR"),
                    "correlation_id": getattr(
                        self.request, "correlation_id", None
                    ),
                },
            )
            messages.error(self.request, "شما مجوز تغییر رمز عبور را ندارید.")
            return redirect("account:forgot-otp")

        user = User.objects.get(phone=phone)
        user.set_password(form.cleaned_data["password"])
        user.save()
        messages.success(self.request, self.success_message)
        return super().form_valid(form)


@method_decorator(
    ratelimit(key="user", rate="5/m", method="GET", block=False),
    name="dispatch",
)
class LogoutView(RedirectNextMixin, View, LoginRequiredMixin):
    default_redirect_url = reverse_lazy("website:index")

    def dispatch(self, request, *args, **kwargs):
        if getattr(request, "limited", False):
            security_logger.warning(
                "Rate limit exceeded for logout",
                extra={
                    "task_name": TaskName.LOGOUT,
                    "user_id": request.user.id,
                    "ip": request.META.get("REMOTE_ADDR"),
                    "view": self.__class__.__name__,
                    "correlation_id": getattr(
                        self.request, "correlation_id", None
                    ),
                },
            )
            messages.error(
                request,
                "شما بیش از حد مجاز در یک دقیقه درخواست خروج داده‌اید. لطفاً کمی بعد دوباره تلاش کنید.",
            )
            return redirect("website:index")
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        user_id = request.user.id
        set_next_url_logout(request)

        logout(request)

        auth_logger.info(
            "User logged out successfully",
            extra={
                "task_name": TaskName.LOGOUT,
                "user_id": user_id,
                "view": self.__class__.__name__,
                "correlation_id": getattr(
                    self.request, "correlation_id", None
                ),
            },
        )

        messages.success(request, "با موفقیت از حساب کاربری خارج شدید.")

        return redirect(self.get_success_url())

    def post(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)
