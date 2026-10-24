from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import SAFE_METHODS, BasePermission, IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from core.models import Comentario, Tarefa
from core.serializers import ComentarioSerializer


class AutorDoComentarioPermission(BasePermission):
    """Todo participante lê; só o autor edita ou apaga o próprio comentário."""

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return obj.tarefa.pode_ver(request.user)

        return obj.user_id == request.user.id


class ComentarioViewSet(ModelViewSet):
    serializer_class = ComentarioSerializer
    permission_classes = [IsAuthenticated, AutorDoComentarioPermission]
    pagination_class = None
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['tarefa']

    def get_queryset(self):
        tarefas = Tarefa.objects.visiveis_para(self.request.user).values('pk')

        return (
            Comentario.objects.filter(tarefa__in=tarefas)
            .select_related('user')
            .order_by('id')
        )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
