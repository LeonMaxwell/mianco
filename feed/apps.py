from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class FeedConfig(AppConfig):
    """ Конфиг созданного приложения """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'feed'
    verbose_name = _("Стена объявлений")
