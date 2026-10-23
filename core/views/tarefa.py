from rest_framework.viewsets import ModelViewSet

from core.models import Tarefa
from core.serializers import TarefaSerializer


class TarefaViewSet(ModelViewSet):
    queryset = Tarefa.objects.all()
    serializer_class = TarefaSerializer
