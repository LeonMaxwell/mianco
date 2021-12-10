from django.urls import re_path

from . import consumer

websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<id_messages>[0-9A-Fa-f]{8}(?:-[0-9A-Fa-f]{4}){3}-[0-9A-Fa-f]{12})/$', consumer.ProfileConsumer.as_asgi()),
]