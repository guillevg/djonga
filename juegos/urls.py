from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('<slug:game_slug>/', views.game_lobby, name='lobby'),
    path('<slug:game_slug>/new/', views.game_new, name='nueva_partida'),
    path('<slug:game_slug>/<str:id_partida>/', views.game_room, name='partida'),
]
