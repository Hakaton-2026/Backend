from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.viewsets import ModelViewSet

from core.models import Tarefa
from core.serializers import TarefaSerializer


class TarefaViewSet(ModelViewSet):
    queryset = Tarefa.objects.all()
    serializer_class = TarefaSerializer

    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['titulo', 'situacao', 'prioridade', 'prazoInicio', 'prazoFim', 'user__email']
