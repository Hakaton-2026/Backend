from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from core.models import ChecklistItem, Tarefa
from core.serializers import ChecklistItemSerializer

from .projeto import PapelNoProjetoPermission


class ChecklistItemViewSet(ModelViewSet):
    serializer_class = ChecklistItemSerializer
    permission_classes = [IsAuthenticated, PapelNoProjetoPermission]
    pagination_class = None
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['tarefa', 'concluido']

    def get_queryset(self):
        tarefas = Tarefa.objects.visiveis_para(self.request.user).values('pk')

        return ChecklistItem.objects.filter(tarefa__in=tarefas).order_by('id')
