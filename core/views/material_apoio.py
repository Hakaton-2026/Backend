from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from core.models import MaterialApoio, Projeto, Tarefa
from core.serializers import MaterialApoioSerializer

from .projeto import PapelNoProjetoPermission


class MaterialApoioViewSet(ModelViewSet):
    serializer_class = MaterialApoioSerializer
    permission_classes = [IsAuthenticated, PapelNoProjetoPermission]
    pagination_class = None
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['projeto', 'tarefa']

    def get_queryset(self):
        usuario = self.request.user
        projetos = Projeto.objects.visiveis_para(usuario).values('pk')
        tarefas = Tarefa.objects.visiveis_para(usuario).values('pk')

        return MaterialApoio.objects.filter(
            Q(projeto__in=projetos) | Q(tarefa__in=tarefas)
        ).order_by('-id')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
