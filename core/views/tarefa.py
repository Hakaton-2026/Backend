from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from rest_framework.viewsets import ModelViewSet

from core.models import Tarefa
from core.serializers import (
    TarefaCreateUpdateSerializer,
    TarefaListSerializer,
    TarefaRetrieveSerializer,
)


class TarefaViewSet(ModelViewSet):
    queryset = Tarefa.objects.all().order_by('-id')

    def get_serializer_class(self):
        if self.action in {'create', 'update', 'partial_update'}:
            return TarefaCreateUpdateSerializer

        if self.action == 'list':
            return TarefaListSerializer

        return TarefaRetrieveSerializer

    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['situacao', 'prioridade', 'prazoInicio', 'prazoFim', 'user__email']
    search_fields = ['titulo']
