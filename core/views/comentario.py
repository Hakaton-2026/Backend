from rest_framework.viewsets import ModelViewSet

from core.models import Comentario
from core.serializers import ComentarioSerializer


class ComentarioViewSet(ModelViewSet):
    queryset = Comentario.objects.all().order_by('-id')
    serializer_class = ComentarioSerializer
