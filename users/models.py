from datetime import datetime, timedelta

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager

from django_jalali.db import models as jmodels


class CustomUserManager(BaseUserManager):

    def create_user(self, phone, password, **extra_fields):
        if not phone:
            raise ValueError('User must have a phone number!')
        if "email" in extra_fields.keys():
            extra_fields["email"] = self.normalize_email(extra_fields["email"])
        user = self.model(phone=phone, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, phone, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        return self.create_user(phone, password, **extra_fields)


class Users(AbstractBaseUser, PermissionsMixin):
    phone = models.CharField(unique=True, null=False, max_length=11)
    email = models.EmailField(unique=True, null=False)
    name = models.CharField(max_length=100, null=True, blank=True)
    family = models.CharField(max_length=100, null=True, blank=True)
    store = models.CharField(max_length=255, null=True)
    created_date = jmodels.jDateTimeField(auto_now_add=True)
    update_date = jmodels.jDateTimeField(auto_now=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = "Users"
        verbose_name_plural = "Users"

    def __str__(self) -> str:
        return self.phone


# model for sms numbers
class Sms(models.Model):
    phone = models.CharField(max_length=11, null=False)
    code = models.CharField(max_length=4, null=False)
    created_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Sms"
        verbose_name_plural = "Sms"


# model for email verify:
class EmailVerify(models.Model):
    email = models.EmailField(null=False)
    code = models.CharField(max_length=4, null=False)
    created_date = models.DateTimeField(auto_now_add=True)

# valid numbers model


class ValidNumbers(models.Model):
    phone = models.CharField(max_length=11, unique=True, null=False)
    name = models.CharField(max_length=255, null=False)
    created_date = jmodels.jDateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "ValidNumbers"
        verbose_name_plural = "ValidNumbers"
