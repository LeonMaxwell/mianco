"""
ASGI config for feed project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/asgi/
"""

import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

import profilemianto.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mianto.settings')

application = ProtocolTypeRouter({
    # Настройка ас синхронного сервера.
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            profilemianto.routing.websocket_urlpatterns
        )
    ),
})
