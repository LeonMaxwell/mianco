import os
import uuid
from django.contrib.auth.base_user import AbstractBaseUser
from django.core.mail import send_mail
from django.db import models
from django.utils.translation import ugettext_lazy as _
from feed.models import MinAgeValidator, Announcement
from .manager import ProfileManager


def get_file_path(instance, filename):
    # функция для изменения назания файла на UUID4
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    return os.path.join("profileMianto/log/", filename)


def get_image_path(instance, filename):
    # функция изменяет фото на UUID4
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    return os.path.join("profileMianto/avatar/", filename)


class ProfileMianto(AbstractBaseUser):
    """ Модель участников которая создана на основе пользовательской модели """

    class GenderChoice(models.TextChoices):
        MALE = "M", _("Парень")
        FEMALE = "F", _("Девушка")

    login = models.CharField(max_length=255, verbose_name=_("Логин"), unique=True)
    email = models.EmailField(unique=True, verbose_name=_("Электронная почта"))
    avatar = models.ImageField(upload_to=get_image_path, blank=True, null=True,
                               verbose_name=_("Аватар"))
    dob = models.DateField(validators=[MinAgeValidator(18)], null=True, blank=True, verbose_name=_("Дата рождения"))
    gender = models.CharField(max_length=20, null=True, blank=True,
                              choices=GenderChoice.choices, verbose_name=_("Пол"))
    profile_uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата регистрации")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    is_confirm = models.BooleanField(verbose_name=_("Статус подтверждения"), default=False)
    is_active = models.BooleanField(verbose_name=_("Статус активности"), default=True)
    is_admin = models.BooleanField(default=False, verbose_name="Права администратора")
    is_staff = models.BooleanField(default=False, verbose_name="Права доступа")

    USERNAME_FIELD = 'login'
    REQUIRED_FIELDS = ['email', ]

    objects = ProfileManager()

    def __str__(self):
        return self.login

    class Meta:
        verbose_name = "Профиль"
        verbose_name_plural = "Профили"
        db_table = 'profile'
        ordering = ('-created_at', '-updated_at',)

    def has_perm(self, perm, obj=None):
        # получение прав для входа в админ панель
        return True

    def has_module_perms(self, app_label):
        # получение прав для входа в админ панель
        return True

    def save(self, *args, **kwargs):
        # при сохранения пользователя происходит отправка сообщения на почту для подтверждения профиля
        super().save(*args, **kwargs)
        if not self.is_confirm:
            send_mail("Mianto Love",
                      "Ваши данные успешно отправлены для регистрации. Для того что бы завершить регистрацию"
                      "и иметь доступ к своему профилю на сайте требуется подтвердить свой профиль. Для этого"
                      f"перейдите по ссылке: http://127.0.0.1:8000/profile/{self.pk}/confirm/{self.profile_uuid}/",
                      'leo.urabaros@gmail.com', [f'{self.email}'], fail_silently=False)


class ProfileFeed(models.Model):
    """ Модель для создания хранилища объявлений к пользователю """
    profile = models.ForeignKey(ProfileMianto, related_name="profiles", on_delete=models.CASCADE, verbose_name=_("Профиль"))
    ad = models.ForeignKey(Announcement, related_name='ads', on_delete=models.CASCADE, verbose_name=_("Объявление"))

    class Meta:
        verbose_name = "Стена профиля"
        verbose_name_plural = "Стены профиля"

    def __str__(self):
        return f"{self.profile} - (№ {self.ad.pk})"


class ProfileMessages(models.Model):
    """ Класс который хранит каналы чатов пользователей. """
    first_interlocutor = models.ForeignKey(ProfileMianto, related_name="first", on_delete=models.PROTECT,
                                           verbose_name=_("Первый собеседник"))
    second_interlocutor = models.ForeignKey(ProfileMianto, related_name="second", on_delete=models.PROTECT,
                                            verbose_name=_("Второй собеседник"))
    uuid_channel = models.UUIDField(default=uuid.uuid4, editable=False, verbose_name=_("ID канала"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Дата создания канала"))
    log_file = models.FileField(upload_to=get_file_path, blank=True, null=True,
                                verbose_name=_("Лог канал"))

    class Meta:
        verbose_name = "Канал"
        verbose_name_plural = "Каналы"

    def __str__(self):
        return f"{self.pk}:Канал ID {self.uuid_channel}: " \
               f"({self.first_interlocutor.login}-{self.second_interlocutor.login})"
