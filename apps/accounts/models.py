from django.db import models
from django.contrib.auth.models import AbstractBaseUser

from apps.accounts.managers import CustomUserManager
from apps.common.models import IsDeletedModel


ACCOUNT_TYPE_CHOICES = (
    ("SELLER", "SELLER"),
    ("BUYER", "BUYER"),
)


class User(AbstractBaseUser, IsDeletedModel):
    """
    Custom user model extending AbstractBaseUser.

    Attributes:
        first_name (str): Имя пользователя.
        last_name (str): Фамилиия пользователя.
        email (str): Адрес электронной почты пользователя,
        используемый в качестве поля имени пользователя.
        avatar (ImageField): Аватар пользователя.
        is_staff (bool): пределяет, может ли пользователь
        войти на этот сайт администратора.

        is_active (bool): Указывает, следует ли считать
        данного пользователя активным.

        account_type (str): Тип аккаунта (SELLER or BUYER).

    Methods:
        full_name(): Возвращает полное имя пользователя.
        __str__(): Возвращает строковое представление пользователя..

    """

    first_name = models.CharField(
        verbose_name="First name", max_length=25, null=True)
    last_name = models.CharField(
        verbose_name="Last name", max_length=25, null=True)
    email = models.EmailField(verbose_name="Email address", unique=True)
    avatar = models.ImageField(
        upload_to="avatars/", null=True, default='avatars/default.jpg')

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    account_type = models.CharField(
        max_length=6, choices=ACCOUNT_TYPE_CHOICES, default="BUYER")

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    objects = CustomUserManager()

    @property
    def full_name(self):
        """
        Возвращает полное имя пользователя путем объединения имени и фамилии.

        Returns:
            str: Полное имя пользователя.
        """
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        """
        Возвращает строковое представление пользователя,
        представляющее собой его полное имя.

        Returns:
            str: Полное имя пользователя.
        """
        return self.full_name

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_superuser(self):
        return self.is_staff
