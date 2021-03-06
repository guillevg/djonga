# Generated by Django 3.1.7 on 2021-03-10 12:27

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import markdownx.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='InfoPartida',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('orden', models.PositiveSmallIntegerField(help_text='El orden del jugador en la partida: 1º, 2º...', verbose_name='Orden del jugador')),
            ],
        ),
        migrations.CreateModel(
            name='Juego',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=30, verbose_name='Nombre del juego')),
                ('num_jugadores', models.SmallIntegerField(validators=[django.core.validators.MinValueValidator(0, message='El número de jugadores no puede ser negativo')], verbose_name='Número de jugadores')),
                ('slug', models.SlugField(blank=True, help_text='Si se deja vacío, se autogenera un slug a partir del nombre del juego', max_length=200, unique=True)),
                ('reglas', markdownx.models.MarkdownxField()),
            ],
        ),
        migrations.CreateModel(
            name='Jugador',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=20, verbose_name='Nombre del jugador')),
            ],
        ),
        migrations.CreateModel(
            name='SillyEngine',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=50, verbose_name='Nombre del juego')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TresEnRaya',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=30, verbose_name='Nombre del juego')),
                ('num_jugadores', models.SmallIntegerField(validators=[django.core.validators.MinValueValidator(0, message='El número de jugadores no puede ser negativo')], verbose_name='Número de jugadores')),
                ('slug', models.SlugField(blank=True, help_text='Si se deja vacío, se autogenera un slug a partir del nombre del juego', max_length=200, unique=True)),
                ('reglas', markdownx.models.MarkdownxField()),
                ('tablero', models.CharField(default='', max_length=9)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TresEnRayaEngine',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=50, verbose_name='Nombre del juego')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Partida',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('fecha', models.DateField(auto_now=True)),
                ('n_jugadas', models.SmallIntegerField(default=0, verbose_name='Número de jugadas')),
                ('movimientos', models.CharField(max_length=256, verbose_name='Lista de movimientos')),
                ('estado', models.CharField(choices=[('NW', 'Partida nueva'), ('WT', 'Esperando jugadores'), ('PR', 'Partida en progreso'), ('AB', 'Partida abortada'), ('FN', 'Partida terminada')], default='NW', max_length=2, verbose_name='Estado de la partida')),
                ('juego', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='partidas', to='juegos.juego')),
                ('jugadores', models.ManyToManyField(through='juegos.InfoPartida', to='juegos.Jugador')),
            ],
        ),
        migrations.AddField(
            model_name='infopartida',
            name='jugador',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='juegos.jugador'),
        ),
        migrations.AddField(
            model_name='infopartida',
            name='partida',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='juegos.partida'),
        ),
    ]
