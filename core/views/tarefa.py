
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
