from django.db.models import Q
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import SAFE_METHODS, BasePermission, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from core.models import Projeto, ProjetoParticipante
from core.serializers import (
    ProjetoCreateUpdateSerializer,
    ProjetoListSerializer,
    ProjetoMembroSerializer,
    ProjetoRetrieveSerializer,
)


class PermissaoProjeto(BasePermission):
    """Regras por papel (o queryset já limita aos projetos acessíveis).

    - proprietário: tudo, inclusive gerenciar participantes;
    - editor: ver e editar o projeto (PUT/PATCH);
    - visualizador: somente leitura.
    """

    message = 'Você não tem permissão para realizar esta ação neste projeto.'

    def has_object_permission(self, request, view, projeto):
        if projeto.proprietario_id == request.user.id:
            return True

        if request.method in SAFE_METHODS:
            return True

        if view.action in {'update', 'partial_update'}:
            return projeto.membros.filter(
                usuario=request.user,
                papel=ProjetoParticipante.Papel.EDITOR,
            ).exists()

        return False


class ProjetoViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated, PermissaoProjeto]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Projeto.objects.none()

        usuario = self.request.user

        return (
            Projeto.objects
            .filter(Q(proprietario=usuario) | Q(membros__usuario=usuario))
            .distinct()
            .select_related('proprietario')
            .prefetch_related('membros', 'tarefas')
            .order_by('-id')
        )

    def get_serializer_class(self):
        if self.action in {'create', 'update', 'partial_update'}:
            return ProjetoCreateUpdateSerializer
        if self.action == 'list':
            return ProjetoListSerializer
        return ProjetoRetrieveSerializer

    def perform_create(self, serializer):
        serializer.save(proprietario=self.request.user)

    @extend_schema(
        request=ProjetoMembroSerializer,
        responses={
            200: ProjetoMembroSerializer(many=True),
            201: ProjetoMembroSerializer,
        },
    )
    @action(detail=True, methods=['get', 'post'], url_path='membros')
    def membros(self, request, pk=None):
        """GET lista os participantes; POST (só o proprietário) adiciona um."""
        projeto = self.get_object()

        if request.method == 'GET':
            participantes = (
                projeto.membros
                .select_related('usuario')
                .order_by('compartilhado_em')
            )
            return Response(
                ProjetoMembroSerializer(participantes, many=True).data
            )

        serializer = ProjetoMembroSerializer(
            data=request.data,
            context={'projeto': projeto},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(projeto=projeto)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @extend_schema(
        request=ProjetoMembroSerializer,
        responses={200: ProjetoMembroSerializer, 204: None},
    )
    @action(
        detail=True,
        methods=['patch', 'delete'],
        url_path=r'membros/(?P<membro_id>\d+)',
    )
    def membro(self, request, pk=None, membro_id=None):
        """PATCH altera o papel; DELETE remove o participante (só o proprietário)."""
        projeto = self.get_object()
        participante = get_object_or_404(
            projeto.membros.select_related('usuario'),
            pk=membro_id,
        )

        if request.method == 'DELETE':
            participante.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        serializer = ProjetoMembroSerializer(
            participante,
            data=request.data,
            partial=True,
            context={'projeto': projeto},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)
