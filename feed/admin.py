from django.contrib import admin
from .models import Announcement

# Регистрация модели в админке
admin.site.register(Announcement)
