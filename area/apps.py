from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class AreaConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'area'
    verbose_name = _("Хранилище городов")
