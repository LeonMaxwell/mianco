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


"""

celery -A mianto worker -B

"""