from django.contrib.auth.views import LogoutView
from django.urls import path
from django.contrib import admin
from .views import LoginProfileView, RegisterProfileView, SettingsProfileView, profileConfirm, branch_profile, \
    profile_feed, profile_logout, chat_list, room

urlpatterns = [
    path('', branch_profile, name='profile'),
    path('login/', LoginProfileView.as_view(), name='profilelogin'),
    path('register/', RegisterProfileView.as_view(), name='profileregister'),
    path('admin/', admin.site.urls),
    path('<int:pk>/feed/', profile_feed, name='profilefeed'),
    path('<int:pk>/logout/', profile_logout, name='profilelogout'),
    path('<int:pk>/feed/messages/', chat_list, name='profilemessages'),
    path('<int:pk>/feed/messages/chat/<uuid:id_messages>/', room, name='profileroom'),
    path('<int:pk>/feed/settings/', SettingsProfileView.as_view(), name='profilesettings'),
    path('<int:pk>/confirm/<uuid:profile_uuid>/', profileConfirm, name='profileconfirm'),
]
