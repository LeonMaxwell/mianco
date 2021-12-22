from datetime import timedelta
from django.utils import timezone
from mianto.celery import app
from .models import Announcement


@app.task
def clearing_old_ad():
    # Задача при которой удаляются все объявления которые были созданы 30 дней назад.
    now = timezone.now()
    Announcement.objects.filter(created_at__lt=now - timedelta(days=30)).delete()
    print(now - timedelta(days=30))


@app.task
def expiration_time_premium():
    now = timezone.now()
    an = Announcement.objects.filter(finish_prime__lt=now + timedelta(hours=3)).update(is_prime=False, finish_prime=None)
    print("Это очистка")

"""

celery -A mianto worker -B

"""