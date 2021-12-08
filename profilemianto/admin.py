from django.contrib import admin
from django.contrib.auth.models import Group

# Register your models here.
from profilemianto.models import ProfileMianto

admin.site.register(ProfileMianto)
admin.site.unregister(Group)