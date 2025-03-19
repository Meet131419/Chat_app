from django.urls import path
from channels.auth import AuthMiddlewareStack  # Import the auth middleware
from user import consumers

websocket_urlpatterns = [
    path('ws/chat/<str:group_name>/', AuthMiddlewareStack(  # Wrap your consumers with AuthMiddlewareStack
        consumers.ChatConsumer.as_asgi()
    )),
]
