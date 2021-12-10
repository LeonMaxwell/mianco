from django.contrib import admin
from django.contrib.auth.models import Group

# Register your models here.
from profilemianto.models import ProfileMianto, ProfileFeed, ProfileMessages

admin.site.register(ProfileMianto)
admin.site.register(ProfileFeed)
admin.site.register(ProfileMessages)
admin.site.unregister(Group)
