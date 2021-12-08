import os

from celery import Celery

# Установите модуль настроек Django по умолчанию для программы 'celery'.
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mianto.settings')

# Настройка Celery. Передача названия и брокера для организации выполнения задач.
app = Celery('feed', broker="amqp://leom:Lion2011@localhost:5672/MyVirtualHost")
# Использование строки здесь означает, что не нужно сериализовать объект
# конфигурации для дочерних процессов. namespace = 'CELERY' означает, что все ключи
# конфигурации, связанные с сельдереем, должны иметь префикс
app.config_from_object('django.conf:settings', namespace='CELERY')

# Настройка выполнения задач
app.conf.beat_schedule = {
    'myFirstTask':{
        'task': 'feed.tasks.clearing_old_ad',
        'schedule': crontab(hour=21, minute=00),
    }
}

# Загрузка модулей задач из всех зарагестрированных приложений
app.autodiscover_tasks()

