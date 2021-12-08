import uuid

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.deconstruct import deconstructible
from django.core.validators import BaseValidator
from datetime import date
from django.core.mail import send_mail
from django.utils import timezone


def calculate_age(born):
    # Функция которая вычисляет кол-во лет
    today = date.today()
    return today.year - born.year - ((today.month, today.day) < (born.month, born.day))


@deconstructible
class MinAgeValidator(BaseValidator):
    """
    Класс валидации для проверки возраста при
    создании объявления оно должно быть менее 18 лет.
    """

    code = 'min_age'
    message = _("Возраст должен быть не менее %(limit_value)d лет.")

    def compare(self, a, b):
        return calculate_age(a) < b


class Announcement(models.Model):
    """
    Модель который хранит созданные объявления. Объявление так же может быть платным.
    Которое будет находится выше всех объявлений на 24 часа. Само объявление может
    хранится в базе данных 30 дней.
    """

    class PurposeOfAcquaintance(models.TextChoices):
        """ Класс выборки цели знакомств """
        UNCERTAINTY = "UNT", _("Не важно")
        ROMANCE = "ROM", _("Серьезные отношения")
        TRAVEL = "TRV", _("Совместное путешествие")
        VIRTUAL = "VTL", _("Виртуальное общение")
        SEX = "SEX", _("Секс")

    class Gender(models.TextChoices):
        """ Класс выборки пола создавшего объявление """
        MALE = "M", _("Парень")
        FEMALE = "F", _("Девушка")

    class Interlocutor(models.TextChoices):
        """ Класс выборки предпочитающего пола """
        MALE = "M", _("Парень")
        FEMALE = "F", _("Девушка")
        PAIR = "P", _("Пара")

    email = models.EmailField(verbose_name=_("Электронная почта"))
    dob = models.DateField(validators=[MinAgeValidator(18)], verbose_name=_("Дата рождения"))
    text = models.TextField(verbose_name=_('Текст объявления'))
    gender = models.CharField(max_length=1, choices=Gender.choices, default=Gender.MALE, verbose_name=_("Кто вы?"))
    interlocutor = models.CharField(max_length=1, choices=Interlocutor.choices, default=Interlocutor.FEMALE,
                                    verbose_name=_("Кого ищете?"))
    purpose_of_acquaintance = models.CharField(max_length=3, choices=PurposeOfAcquaintance.choices,
                                               default=PurposeOfAcquaintance.UNCERTAINTY,
                                               verbose_name=_("Цель знакомств"))
    city = models.CharField(max_length=255, verbose_name=_("Город"))
    created_at = models.DateField(auto_now_add=True, verbose_name=_("Дата создания объявления"))
    is_prime = models.BooleanField(verbose_name=_("Премиум объявление"), default=False)
    is_checked = models.BooleanField(verbose_name=_("Статус проверки"), default=False)
    is_confirm = models.BooleanField(verbose_name=_("Статус подтверждения"), default=False)
    is_active = models.BooleanField(verbose_name=_("Статус активности"), default=True)
    uuid_ad = models.UUIDField(default=uuid.uuid4, editable=False)

    class Meta:
        verbose_name = "Объявление"
        verbose_name_plural = "Объявления"
        db_table = 'announcement'

    def __str__(self):
        return f"Объявление №{self.pk} созданное {self.created_at}"

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        # Функция при которой оповещает пользователя как и при создании объявлении так и при успешном прохождении
        # модерации.
        super(Announcement, self).save()
        if self.is_confirm:
            if self.is_checked:
                send_mail("Mianto Love",
                          "Ваше объявление успешно прошло модерацию и оно размещено на сайте",
                          'leo.urabaros@gmail.com', [f'{self.email}'], fail_silently=False)
            else:
                send_mail("Mianto Love",
                          "Успешно отправили на модерацию объявление. Как только оно пройдет модерацию вы получите "
                          "оповещение на почту.",
                          'leo.urabaros@gmail.com', [f'{self.email}'], fail_silently=False)
        else:
            send_mail("Mianto Love",
                      f"Здравствуйте, для создания объявления вам требуется подтвердить ваше объявление. Перейдите"
                      f"по следующей ссылке: http://127.0.0.1:8000/announce/id{self.pk}/active/{self.uuid_ad}/",
                      f"leo.urabaros@gmail.com", [f'{self.email}'], fail_silently=False)

    def correct_data(self):
        now = timezone.now()
        cur_date = self.created_at
        if str(cur_date) == f"{now.year}-{now.month}-{now.fold}{now.day}":
            return "Сегодня"
        else:
            return cur_date

    def short_description_for_ad(self):
        # Функция для вывода части описания объявления
        gender_clear = "Парень" if self.gender == "M" else "Девушка"
        interlocutor_clear = "парня" if self.interlocutor == "M" else "девушку" if self.interlocutor == "F" else "пару"
        return f"{gender_clear} {calculate_age(self.dob)} года ищет {interlocutor_clear}"

    def ad_description(self):
        # Функция для вывода короткого описания объявления
        gender_clear = "Парень" if self.gender == "M" else "Девушка"
        interlocutor_clear = "парня" if self.interlocutor == "M" else "девушку" if self.interlocutor == "F" else "пару"
        purpose_of_acquaintance_clear = "для секса" if self.purpose_of_acquaintance == "SEX" else "для виртуального " \
                                                                                                  "общения" \
            if self.purpose_of_acquaintance == "VIRTUAL" else "для совместного путешествия" \
            if self.purpose_of_acquaintance == "TRV" else "для серьезных отношений" \
            if self.purpose_of_acquaintance == "ROM" else ""

        return f"{gender_clear} {calculate_age(self.dob)} года ищет {interlocutor_clear}" \
               f" {purpose_of_acquaintance_clear} из города {self.city}"
