import json
from channels.generic.websocket import WebsocketConsumer, AsyncWebsocketConsumer
from .models import Juego, Partida
# from channels.db import database_sync_to_async
from asgiref.sync import async_to_sync
import channels.layers
from django.core.cache import cache


class PartidaConsumerAsync(AsyncWebsocketConsumer):
    async def connect(self):
        print("CONECTANDO !!!")
        self.game_slug = self.scope['url_route']['kwargs']['game_slug']
        self.game_id = self.scope['url_route']['kwargs']['id_partida']
        juego = Juego.objects.get(slug=self.game_slug)
        self.partida = Partida.objects.get_or_create(id=self.game_id, juego=juego)
        print(self.partida)
        print(self.scope['user'].id)
        print(dir(self.scope['session']))
        print('session =', self.scope['session'])
        print(self.game_slug, self.game_id)
        self.room_group_name = f"{self.game_slug}_{self.game_id}"
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        print('receive')
        text_data_json = json.loads(text_data)
        i = text_data_json['i']
        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'i': i,
            }
        )

    async def move(self, event):
        print('move', event)

    # Receive message from room group
    async def chat_message(self, event):
        print('chat_message')
        print(event)
        #message = event['message']
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'i': event['i'],
        }))


class GameLobbyConsumer(WebsocketConsumer):
    def connect(self):
        self.game_slug = self.scope['url_route']['kwargs']['game_slug']
        self.usercount_name = f"usercount_lobby_{self.game_slug}"
        self.lobby_group_name = f"lobby_{self.game_slug}"
        self.waiting_games_list_name = f"waiting_{self.game_slug}"
        self.usercount = cache.get(self.usercount_name, 0) + 1
        cache.set(self.usercount_name, self.usercount)

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.lobby_group_name,
            self.channel_name
        )
        async_to_sync(self.channel_layer.group_send)(
            self.lobby_group_name,
            {
                'type': 'lobby.newuser',
                'message': 'new user'
            }
        )
        self.accept()

        # Enviar lista de partidas en espera
        self.waiting_games_list = cache.get(self.waiting_games_list_name, list())
        self.send(text_data=json.dumps({
                'type': 'lobby.listupdate',
                'waiting_games_list': self.waiting_games_list,
            }))

    def disconnect(self, close_code):
        self.usercount = cache.get(f"usercount_lobby_{self.game_slug}", 1) - 1
        cache.set(f"usercount_lobby_{self.game_slug}", self.usercount)
        async_to_sync(self.channel_layer.group_send)(
            self.lobby_group_name,
            {
                'type': 'lobby.userquit',
                'message': 'user quit'
            }
        )

    def lobby_newuser(self, event):
        print('lobby_newuser', event)
        self.usercount = cache.get(f"usercount_lobby_{self.game_slug}", 0)
        self.send(text_data=json.dumps({
                'type': 'lobby.newuser',
                'usercount': self.usercount,
            }))

    def lobby_newgame(self, event):
        print('lobby_newgame', event)
        game_id = event['game_id']
        waiting_games_list = cache.get(self.waiting_games_list_name, list())
        self.send(text_data=json.dumps({
                'type': 'lobby.newgame',
                'game_id': game_id,
                'waiting_games_list': waiting_games_list,
            }))

    def lobby_gamestart(self, event):
        print('lobby_gamestart', event)
        game_id = event['game_id']
        waiting_games_list = cache.get(self.waiting_games_list_name, list())
        self.send(text_data=json.dumps({
                'type': 'lobby.gamestart',
                'game_id': game_id,
                'waiting_games_list': waiting_games_list,
            }))

    def lobby_gameabort(self, event):
        print('lobby_gameabort', event)
        print(dir(self))
        game_id = event['game_id']
        waiting_games_list = cache.get(self.waiting_games_list_name, list())
        self.send(text_data=json.dumps({
                'type': 'lobby.gameabort',
                'game_id': game_id,
                'waiting_games_list': waiting_games_list,
            }))

    def lobby_userquit(self, event):
        print('lobby_userquit', event)
        self.usercount = cache.get(f"usercount_lobby_{self.game_slug}", 0)
        self.send(text_data=json.dumps({
                'type': 'lobby.userquit',
                'usercount': self.usercount,
            }))


class PartidaConsumer(WebsocketConsumer):
    def connect(self):
        self.game_slug = self.scope['url_route']['kwargs']['game_slug']
        self.id_partida = self.scope['url_route']['kwargs']['id_partida']
        print(f"CONECTANDO A PARTIDA {self.game_slug} #{self.id_partida}")
        partida = cache.get(self.id_partida, None)
        usercount = cache.get(f"usercount_{self.id_partida}", 0)
        print('USERCOUNT', usercount)
        # juego = cache.get(self.game_slug, None)
        if partida is None:
            print("¿QUÉ PASA? ¡NO DEBERÍAMOS ESTAR EN EL CONSUMER SI LA PARTIDA NO ESTÁ EN CACHE!")
            self.close()
        self.partida = partida
        self.partida_name = f"game_{self.id_partida}"
        self.waiting_games_list_name = f"waiting_{self.game_slug}"
        self.room_group_name = f"{self.game_slug}_{self.id_partida}"
        self.lobby_group_name = f"lobby_{self.game_slug}"

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        # self.send_type_message('chat.message', '¡Bienvenid@!')
        self.accept()
        if partida.estado == partida.NEW:
            print("Eres el primer jugador, vamos a esperar...")
            self.is_player = 1
            partida.estado = partida.WAITING
            cache.set(self.partida_name, partida)
            # Send message to game lobby
            waiting_games_list = cache.get(self.waiting_games_list_name, list())
            waiting_games_list.append(self.id_partida)
            cache.set(self.waiting_games_list_name, waiting_games_list)
            async_to_sync(self.channel_layer.group_send)(
                self.lobby_group_name,
                {
                    'type': 'lobby.newgame',
                    'game_id': self.partida.id,
                }
            )
            cache.set(self.id_partida, partida)
            cache.set(f"usercount_{self.id_partida}", 1)
            self.send(text_data=json.dumps({
                'type': 'game.me',
                'me': 'O',
            }))
        elif partida.estado == partida.WAITING:
            print("Había un jugador esperando, ya estamos todos. ¡Empezamos!")
            self.is_player = 2
            cache.set(f"usercount_{self.id_partida}", 2)

            # Send message to game lobby
            waiting_games_list = cache.get(self.waiting_games_list_name, list())
            waiting_games_list.remove(self.id_partida)
            cache.set(self.waiting_games_list_name, waiting_games_list)
            async_to_sync(self.channel_layer.group_send)(
                self.lobby_group_name,
                {
                    'type': 'lobby.gamestart',
                    'game_id': self.partida.id,
                }
            )
            # Send message to player
            self.send(text_data=json.dumps({
                'type': 'game.me',
                'me': 'X',
            }))
            self.send_type_message('game.start', 'probando')
        elif partida.estado == partida.IN_PROGRESS:
            print("Partida en marcha")
            usercount = cache.get(f"usercount_{self.id_partida}") + 1
            cache.set(f"usercount_{self.id_partida}", usercount)
            self.is_player = 0
        else:
            print(f"No puede ser, el estado es {partida.estado}")
        # game_state = self.partida.game_state
        game_moves = partida.movimientos

        self.send(text_data=json.dumps({
            'type': 'game.movelist',
            'game_moves': game_moves,
            'i': 666,
        }))

    def disconnect(self, close_code):
        # Leave room group
        usercount = cache.get(f"usercount_{self.id_partida}", 1) - 1
        cache.set(f"usercount_{self.id_partida}", usercount)
        if self.is_player:
            # If a player disconnects, the game is aborted
            print(f"PLAYER {self.is_player} LEFT THE ROOM")
            try:
                partida = cache.get(self.partida_name)
                partida.estado = partida.ABORTED
                partida.save()
            except Exception as e:
                print(e)
            # Warn other player and spectators
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    'type': 'game.abort',
                    'message': f"Game aborted (Player {self.is_player} left the room)"
                }
            )
            # Remove game from waiting list in lobby
            waiting_games_list = cache.get(self.waiting_games_list_name, list())
            try:
                waiting_games_list.remove(self.id_partida)
            except Exception as e:
                print(e)  # game_id is not in list
            cache.set(self.waiting_games_list_name, waiting_games_list)
            async_to_sync(self.channel_layer.group_send)(
                self.lobby_group_name,
                {
                    'type': 'lobby.gameabort',
                    'game_id': self.partida.id,
                }
            )
        else:
            print("SPECTATOR LEFT THE ROOM")
        print("USER DISCONNECTED: USERCOUNT", usercount)
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    def receive(self, text_data):
        print('receive')
        text_data_json = json.loads(text_data)
        type = text_data_json.get('type', None)
        move = text_data_json.get('move', None)
        tablero = text_data_json.get('tablero', None)
        player = text_data_json.get('player', None)
        print(text_data_json)
        if type == 'game.move':
            partida = cache.get(self.id_partida, None)
            is_valid_move = partida.is_valid_move(move=move, player=player, tablero=tablero)
            if is_valid_move == player:
                # valid and game won by player
                partida.movimientos += str(move)
                partida.estado = partida.FINISHED
                partida.save()
                cache.set(self.id_partida, partida)
                async_to_sync(self.channel_layer.group_send)(
                    self.room_group_name,
                    {
                        'type': 'game.end',
                        'move': move,
                        'tablero': partida.movimientos,
                        'player': player,
                    }
                )
            elif is_valid_move:
                # valid but game not finished
                partida.movimientos += str(move)
                cache.set(self.id_partida, partida)
                async_to_sync(self.channel_layer.group_send)(
                    self.room_group_name,
                    {
                        'type': 'game.move',
                        'move': move,
                        'player': player,
                    }
                )

        elif type == 'game.end':
            partida = cache.get(self.id_partida, None)


    def send_type_message(self, type, message):
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': type,
                'message': message
            }
        )

    def game_move(self, event):
        print('game_move', event)
        partida = cache.get(self.id_partida)
        move = event['move']
        player = event['player']
        self.send(text_data=json.dumps({
            'type': 'game.move',
            'move': move,
            'tablero': partida.movimientos,
            'player': player,
        }))

    def game_start(self, event):
        print('game_start', event)
        partida = cache.get(self.id_partida)
        partida.estado = partida.IN_PROGRESS
        cache.set(self.id_partida, partida)
        self.send(text_data=json.dumps({
            'type': 'game.start',
            'message': 'VAMONOS',
        }))

    def game_end(self, event):
        print('game_end', event)
        move = event['move']
        player = event['player']
        tablero = event['tablero']
        self.send(text_data=json.dumps({
            'type': 'game.end',
            'move': move,
            'tablero': tablero,
            'player': player,
        }))


    def game_abort(self, event):
        print('game_abort', event)
        self.send(text_data=json.dumps({
            'type': 'game.abort',
            'message': event['message'],
        }))

    def chat_message(self, event):
        print('chat_message', event)
        self.send(text_data=json.dumps({
            'type': 'chat.message',
            'message': event['message'],
        }))


class JuegoConsumer(WebsocketConsumer):
    def connect(self):
        print(self.scope)
        self.accept()

    def disconnect(self, close_code):
        pass

    def receive(self, text_data):
        print('receive')
        print(self)
        text_data_json = json.loads(text_data)
        jugada = text_data_json['jugada']

        self.send(text_data=json.dumps({ 'message': jugada, 'jugador': 1, }))
