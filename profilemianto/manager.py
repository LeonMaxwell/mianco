from django.contrib.auth.models import BaseUserManager


class ProfileManager(BaseUserManager):
    """ Менеджер для модели профилей"""

    def create_user(self, login, email, password=None, is_admin=False, is_active=True, is_staff=False,
                    is_confirm=False):
        # Функция при создании профиля
        if not login:
            raise ValueError("Для регистрации профиля требуется указать логин")
        if not email:
            raise ValueError("Для регистрации профиля нужна почта для его подтверждения")
        if not password:
            raise ValueError("Для защиты профиля он должен иметь пароль")

        profile_obj = self.model(
            email=self.normalize_email(email),
            login=login,
        )
        profile_obj.set_password(password)
        profile_obj.is_confirm = is_confirm
        profile_obj.is_active = is_active
        profile_obj.is_admin = is_admin
        profile_obj.is_staff = is_staff
        profile_obj.save(using=self.db)
        return profile_obj

    def create_superuser(self, login, email, password=None):
        # Функция для создании суперпользователя
        super_profile = self.create_user(
            login,
            email,
            password=password,
            is_staff=True,
            is_admin=True,
            is_active=True,
            is_confirm=True
        )
        return super_profile

