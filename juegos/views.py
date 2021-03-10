from django.shortcuts import render, redirect
from django.views import generic
from .models import Juego, Partida
from django.core.cache import cache
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

channel_layer = get_channel_layer()

def index(request):
    juegos = Juego.objects.all()
    return render(request, 'juegos/index.html', {'juegos': juegos})


def game_lobby(request, *args, **kwargs):
    game_slug = kwargs.get('game_slug', "NO_SLUG")
    try:
        juego = Juego.objects.get(slug=game_slug)
        return render(request, 'juegos/game_lobby.html', context={'juego': juego})
    except Exception as e:
        print(e, f"NO EXISTE EL JUEGO CON SLUG {game_slug}")
        return redirect('juegos:index')


def game_new(self, *args, **kwargs):
    game_slug = kwargs.get('game_slug', "NO_SLUG")
    try:
        juego = Juego.objects.get(slug=game_slug)
        partida = Partida.objects.create(juego=juego)
        async_to_sync(channel_layer.group_send)(
            f"lobby_{game_slug}",
            {
                "type": "lobby.newgame",
                "game_id": partida.id,
            })
        print(f"Nueva partida de {juego.nombre} #{partida.id}")
        return redirect('juegos:partida', game_slug=game_slug, id_partida=partida.id)
    except Exception as e:
        print("Exception en game_new()", e)
        return redirect('juegos:index')


def game_room(request, *args, **kwargs):
    print('GAME_ROOM')
    print(request, args, kwargs)
    game_slug = kwargs.get('game_slug', "WEIRD")
    id_partida = kwargs.get('id_partida', "calentamiento")
    partida = cache.get(id_partida, None)
    if partida:
        print(f"La partida '{id_partida}' está en cache")
        if partida.estado != partida.FINISHED:
            print(f"La partida '{id_partida}' está en estado {partida.estado}")
        else:
            print("Esto no debería ocurrir: si está en cache es porque la partida no ha terminado")
    else:
        juego = Juego.objects.get(slug=game_slug)
        partida, created = Partida.objects.get_or_create(id=id_partida, juego=juego)
        if partida.estado in {partida.NEW, partida.WAITING, partida.IN_PROGRESS}:
            print('Partida guardada en cache')
            cache.set(partida.id, partida)
        print("Partida nueva" if created else "Partida recuperada de DB")
    context = {
        'slug': game_slug,
        'id_partida': id_partida,
    }
    print(context)
    return render(request, 'juegos/game_room.html', context=context)
