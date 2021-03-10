from django.db import models
from django.core.validators import MinValueValidator
from django.utils.text import slugify
from markdownx.models import MarkdownxField
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from .engines import *


class JuegoAbstract(models.Model):
    nombre = models.CharField('Nombre del juego', max_length=30)
    num_jugadores = models.SmallIntegerField('Número de jugadores', validators=[MinValueValidator(0, message='El número de jugadores no puede ser negativo')])
    slug = models.SlugField(unique=True, blank=True, max_length=200, help_text="Si se deja vacío, se autogenera un slug a partir del nombre del juego")
    reglas = MarkdownxField()

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nombre)
        super(JuegoAbstract, self).save(*args, **kwargs)

    def __str__(self):
        return self.nombre

    class Meta:
        abstract = True


class TresEnRaya(JuegoAbstract):
    tablero = models.CharField(max_length=9, default='')

    def is_valid_move(self, *args, **kwargs):
        tablero = kwargs['tablero']
        turno = kwargs['turno']
        move = kwargs['move']
        if len(tablero) == 9:
            return False  # Tablero lleno
        elif str(move) in tablero:
            return False  # La casilla está ocupada
        elif turno != 'OX'[len(tablero) % 2]:
            return False  # No es el turno de este jugador
        return True


class Juego(models.Model):
    nombre = models.CharField('Nombre del juego', max_length=30)
    num_jugadores = models.SmallIntegerField('Número de jugadores', validators=[MinValueValidator(0, message='El número de jugadores no puede ser negativo')])
    slug = models.SlugField(unique=True, blank=True, max_length=200, help_text="Si se deja vacío, se autogenera un slug a partir del nombre del juego")
    reglas = MarkdownxField()
    # engine_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    # engine_id = models.PositiveIntegerField()
    # engine = GenericForeignKey('engine_type', 'engine_id')

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nombre)
        super(Juego, self).save(*args, **kwargs)

    def __str__(self):
        return self.nombre

    @property
    def script(self):
        return f"juegos/{self.slug}.js"

    def is_valid_move(self, *args, **kwargs):
        print('is_valid_move', args, kwargs)
        return ENGINE_DICT[self.slug](*args, **kwargs)


class GameEngine(models.Model):
    nombre = models.CharField('Nombre del juego', max_length=50)

    def __str__(self):
        return f"Engine {self.nombre}"

    class Meta:
        abstract = True


class SillyEngine(GameEngine):
    def is_valid_move(self, *args, **kwargs):
        return True


class TresEnRayaEngine(GameEngine):
    juego = GenericRelation(Juego)
    def is_valid_move(self, *args, **kwargs):
        tablero = kwargs['tablero']
        turno = kwargs['turno']
        move = kwargs['move']
        turnos = 'OX'
        if len(tablero) == 9:
            return False
        else:
            # Comprueba que la jugada no se ha hecho y que es el turno del jugador correcto
            return str(move) not in tablero and turno == turnos[len(tablero) % 2]


class Jugador(models.Model):
    nombre = models.CharField('Nombre del jugador', max_length=20)


class Partida(models.Model):
    NEW = 'NW'
    WAITING = 'WT'
    IN_PROGRESS = 'PR'
    ABORTED = 'AB'
    FINISHED = 'FN'
    ESTADO_JUEGO_CHOICES = [
        (NEW, "Partida nueva"),                # Recién creada
        (WAITING, "Esperando jugadores"),      # Un usuario conectado
        (IN_PROGRESS, "Partida en progreso"),  # Dos usuarios conectados
        (ABORTED, "Partida abortada"),         # Se ha roto la conexión
        (FINISHED, "Partida terminada")        # La partida terminó satisfactoriamente
    ]
    # id = models.CharField('ID de la partida', primary_key=True, max_length=256)
    id = models.AutoField(primary_key=True)
    fecha = models.DateField(auto_now=True)
    juego = models.ForeignKey('Juego', related_name="partidas", on_delete=models.CASCADE)
    n_jugadas = models.SmallIntegerField('Número de jugadas', default=0)
    movimientos = models.CharField('Lista de movimientos', max_length=256)
    jugadores = models.ManyToManyField('Jugador', through='InfoPartida')
    estado = models.CharField('Estado de la partida', max_length=2, choices=ESTADO_JUEGO_CHOICES, default=NEW)

    def __str__(self):
        return f"{self.juego.nombre} [#{self.id}]"

    def is_valid_move(self, *args, **kwargs):
        return self.juego.is_valid_move(*args, **kwargs)


class InfoPartida(models.Model):
    jugador = models.ForeignKey(Jugador, on_delete=models.CASCADE)
    partida = models.ForeignKey(Partida, on_delete=models.CASCADE)
    orden = models.PositiveSmallIntegerField('Orden del jugador', help_text='El orden del jugador en la partida: 1º, 2º...')
