from django.db.models import Count, Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from core.models import Tarefa
from core.serializers import (
    TarefaCreateUpdateSerializer,
    TarefaListSerializer,
    TarefaRetrieveSerializer,
)

from .projeto import PapelNoProjetoPermission


class TarefaViewSet(ModelViewSet):
    permission_classes = [
        IsAuthenticated,
        PapelNoProjetoPermission,
    ]

    def get_queryset(self):
        return (
            Tarefa.objects.visiveis_para(self.request.user)
            .select_related('projeto')
            .annotate(
                checklist_total=Count(
                    'checklist',
                    distinct=True,
                ),
                checklist_concluidos=Count(
                    'checklist',
                    filter=Q(checklist__concluido=True),
                    distinct=True,
                ),
            )
            .order_by('-id')
        )

    def get_serializer_class(self):
        if self.action in {
            'create',
            'update',
            'partial_update',
        }:
            return TarefaCreateUpdateSerializer

        if self.action == 'list':
            return TarefaListSerializer

        return TarefaRetrieveSerializer

    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
    ]

    filterset_fields = [
        'situacao',
        'prioridade',
        'prazoInicio',
        'prazoFim',
        'user',
        'user__email',
        'projeto',
    ]

    search_fields = [
        'titulo',
    ]
