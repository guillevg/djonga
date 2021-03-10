from rest_framework import viewsets, filters
from .models import Juego, Partida
from .serializers import JuegoSerializer, PartidaSerializer


class JuegoViewSet(viewsets.ModelViewSet):
    queryset = Juego.objects.all()
    serializer_class = JuegoSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('nombre', 'article_heading', 'article_body')


class PartidaViewSet(viewsets.ModelViewSet):
    queryset = Partida.objects.all()
    serializer_class = PartidaSerializer
