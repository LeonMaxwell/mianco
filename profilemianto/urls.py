from django.urls import path
from .views import LoginProfileView, RegisterProfileView, profileConfirm
urlpatterns = [
    path('login/', LoginProfileView.as_view(), name='profilelogin'),
    path('register/', RegisterProfileView.as_view(), name='profileregister'),
    # path('<int:pk>/feed/', name='profilefeed'),
    # path('<int:pk>/messages/', name='profilemessages'),
    # path('<int:pk>/messages/<int:id_messages>/', name='profilemessages'),
    # path('<int:pk>/settings/', name='profilesettings'),
    path('<int:pk>/confirm/<uuid:profile_uuid>/', profileConfirm, name='profileconfirm'),
]