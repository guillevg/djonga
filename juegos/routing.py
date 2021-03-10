from django.urls import path
from . import consumers
# from django.core.asgi import get_asgi_application

websocket_urlpatterns = [
    path('ws/juegos/<str:game_slug>/', consumers.GameLobbyConsumer.as_asgi()),
    path('ws/juegos/<str:game_slug>/<str:id_partida>/', consumers.PartidaConsumer.as_asgi()),
]
