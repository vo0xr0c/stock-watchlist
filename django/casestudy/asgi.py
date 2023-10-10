"""
Defines the ASGI application for the project.
"""
from casestudy import routing
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter

from django.core.asgi import get_asgi_application

application = ProtocolTypeRouter({
    # Pointing the HTTP requests to the default ASGI app function.
    "http": get_asgi_application(),
    # Handling WebSockets with Django Channels.
    "websocket": AuthMiddlewareStack(
        URLRouter(
            routing.ws_urlpatterns
        )
    ),
})
