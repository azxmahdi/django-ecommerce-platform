from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from common.validators import phone_validator
from common.models import TimeStampedModel


class UserType(models.IntegerChoices):
    customer = 1, _("کاربر")
    superuser = 3, _("سوپر وایزر")


class CustomUserManager(BaseUserManager):

    def create_user(self, phone, password, **extra_fields):

        if not phone:
            raise ValueError(_("The Phone must be set"))
        user = self.model(phone=phone, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, phone, password, **extra_fields):

        extra_fields.setdefault("type", UserType.superuser.value)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("type") != UserType.superuser.value:
            raise ValueError(_("Superuser must have type=superuser."))
        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))
        if extra_fields.get("is_active") is not True:
            raise ValueError(_("Superuser must have is_active=True."))

        return self.create_user(phone, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):

    phone = models.CharField(
        max_length=12,
        validators=[phone_validator],
        unique=True,
        verbose_name=_("شماره موبایل"),
    )
    type = models.IntegerField(
        choices=UserType.choices,
        default=UserType.customer.value,
        verbose_name=_("نوع کاربر"),
    )
    is_superuser = models.BooleanField(
        default=False, verbose_name=_("مدیر کل")
    )
    is_staff = models.BooleanField(default=False, verbose_name=_("کارمند"))
    is_active = models.BooleanField(default=False, verbose_name=_("فعال"))
    created_date = models.DateTimeField(
        auto_now_add=True, verbose_name=_("تاریخ ایجاد")
    )
    updated_date = models.DateTimeField(
        auto_now=True, verbose_name=_("تاریخ به‌روزرسانی")
    )

    USERNAME_FIELD = "phone"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    class Meta:
        verbose_name = _("کاربر")
        verbose_name_plural = _("کاربران")

    def __str__(self):
        return self.phone

    def get_status(self):
        return {
            "id": self.type,
            "title": UserType(self.type).name,
            "label": UserType(self.type).label,
        }


class ProfileModel(TimeStampedModel):

    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="user_profile",
        verbose_name=_("کاربر"),
    )
    first_name = models.CharField(
        max_length=250, default="کاربر جدید", verbose_name=_("نام")
    )
    last_name = models.CharField(
        max_length=250, blank=True, verbose_name=_("نام خانوادگی")
    )
    image = models.ImageField(
        upload_to="profile/",
        default="profile/default.png",
        verbose_name=_("تصویر پروفایل"),
    )

    def __str__(self):
        return self.user.phone

    class Meta:
        verbose_name = _("پروفایل")
        verbose_name_plural = _("پروفایل‌ها")

    def save(self, *args, **kwargs):
        if not self.pk:
            if ProfileModel.objects.filter(user=self.user).exists():
                raise ValidationError(
                    "Each user can only create one instance."
                )

        super().save(*args, **kwargs)

    @property
    def full_name(self):
        return self.first_name + " " + self.last_name


@receiver(post_save, sender=CustomUser)
def create_profile(sender, instance, created, **kwargs):
    if created:
        ProfileModel.objects.create(user=instance, pk=instance.pk)
