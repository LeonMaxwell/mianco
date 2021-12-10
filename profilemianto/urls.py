from django.contrib.auth.views import LogoutView
from django.urls import path
from django.contrib import admin
from .views import LoginProfileView, RegisterProfileView, SettingsProfileView, LoginAPIView, LogoutAPIView, RegisterProfileAPIVIew, ProfileAPIDetail, ProfileFeedAPIView,ProfileMessagesAPIView, profileConfirm, \
    branch_profile, profile_feed, profile_logout, chat_list, room

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
    # API
    path('api/login/', LoginAPIView.as_view(), name='apiprofilelogin'),
    path('api/logout/', LogoutAPIView.as_view(), name='apiprofilelogout'),
    path('api/register/', RegisterProfileAPIVIew.as_view(), name='apiprofileregister'),
    path('api/<int:pk>/', ProfileAPIDetail.as_view(), name='apiprofile'),
    path('api/<int:pk>/feed/', ProfileFeedAPIView.as_view(), name='apiprofilefeed'),
    path('api/<int:pk>/messages/', ProfileMessagesAPIView.as_view(), name='apiprofilefeed')
]
