from django.contrib.auth.base_user import BaseUserManager
from django.core.validators import validate_email
from django.core.exceptions import ValidationError


class CustomUserManager(BaseUserManager):

    def email_validator(self, email):
        try:
            validate_email(email)
        except ValidationError:
            raise ValueError('Вы должны предоставить действительный адрес электронной почты.')

    def validate_user(self, first_name, last_name, email):
        if not first_name:
            raise ValueError('ользователи должны указать свое имя.')

        if not last_name:
            raise ValueError('Пользователи должны указать фамилию')

        if email:
            email = self.normalize_email(email)
            self.email_validator(email)
        else:
            raise ValueError('Базовая учетная запись пользователя: требуется адрес электронной почты.')

    def create_user(self, first_name, last_name, email, password, **extra_fields):
        self.validate_user(first_name, last_name, email)

        user = self.model(
            first_name=first_name, last_name=last_name, email=email, **extra_fields
        )

        user.set_password(password)
        extra_fields.setdefault("is_staff", False)
        user.save()
        return user

    def validate_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superusers must have is_staff=True")

        if not password:
            raise ValueError('Суперпользователи должны иметь пароль')

        if email:
            email = self.normalize_email(email)
            self.email_validator(email)
        else:
            raise ValueError('Учетная запись администратора: требуется адрес электронной почты')
        return extra_fields

    def create_superuser(self, first_name, last_name, email, password, **extra_fields):
        extra_fields = self.validate_superuser(email, password, **extra_fields)
        user = self.create_user(first_name, last_name, email, password, **extra_fields)
        return user