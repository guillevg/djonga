from rest_framework import routers
from juegos.viewsets import JuegoViewSet

router = routers.DefaultRouter()

router.register(r'juegos', JuegoViewSet)
