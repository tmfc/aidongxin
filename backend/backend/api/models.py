from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    """Custom manager for the project's user model."""

    use_in_migrations = True

    def _create_user(self, phone_number, password, **extra_fields):
        if not phone_number:
            raise ValueError("A phone number must be provided for every user.")

        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(phone_number, password, **extra_fields)

    def create_superuser(self, phone_number, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(phone_number, password, **extra_fields)


class GenderChoices(models.TextChoices):
    FEMALE = 'female', _('Female')
    MALE = 'male', _('Male')
    UNKNOWN = 'unknown', _('Unknown')


class User(AbstractUser):
    """Project specific user model with mobile first identification."""

    username = None
    first_name = None
    last_name = None

    phone_number = models.CharField(_('phone number'), max_length=32, unique=True)
    email = models.EmailField(_('email address'), unique=True, blank=True, null=True)
    name = models.CharField(_('name'), max_length=255, blank=True)
    gender = models.CharField(_('gender'), max_length=10, choices=GenderChoices.choices, default=GenderChoices.UNKNOWN)
    birth_date = models.DateField(_('birth date'), blank=True, null=True)
    wechat_openid = models.CharField(_('wechat openid'), max_length=128, unique=True, blank=True, null=True)
    wechat_unionid = models.CharField(_('wechat unionid'), max_length=128, unique=True, blank=True, null=True)

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self) -> str:
        return self.phone_number
