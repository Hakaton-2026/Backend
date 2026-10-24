from django.shortcuts import get_object_or_404
from django.db import transaction
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import SAFE_METHODS, BasePermission, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from core.models import Projeto, Tarefa
from core.serializers import (
    ProjetoCreateUpdateSerializer,
    ProjetoListSerializer,
    ProjetoMembroSerializer,
    ProjetoRetrieveSerializer,
)


class PapelNoProjetoPermission(BasePermission):
    """Leitura para qualquer participante; escrita para dono e editores."""

    def has_object_permission(self, request, view, obj):
        papel = obj.papel_de(request.user)

        if request.method in SAFE_METHODS:
            return papel is not None

        return papel in {
            Projeto.PAPEL_PROPRIETARIO,
            Projeto.PAPEL_EDITOR,
        }


class ProjetoViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated, PapelNoProjetoPermission]

    def get_queryset(self):
        return (
            Projeto.objects.visiveis_para(self.request.user)
            .select_related('proprietario')
            .prefetch_related('tarefas', 'membros', 'materiais')
            .order_by('-id')
        )

    def get_serializer_class(self):
        if self.action in {'create', 'update', 'partial_update'}:
            return ProjetoCreateUpdateSerializer

        if self.action == 'list':
            return ProjetoListSerializer

        if self.action in {'membros', 'membro'}:
            return ProjetoMembroSerializer

        return ProjetoRetrieveSerializer

    def perform_create(self, serializer):
        serializer.save(proprietario=self.request.user)

    def perform_destroy(self, instance):
        if instance.proprietario_id != self.request.user.id:
            raise PermissionDenied(
                'Somente o proprietário pode excluir o projeto.'
            )

        instance.delete()

    # Participantes: /projetos/{id}/membros/
    # e /projetos/{id}/membros/{membro_id}/

    def _exigir_proprietario(self, projeto):
        if projeto.proprietario_id != self.request.user.id:
            raise PermissionDenied(
                'Somente o proprietário gerencia os participantes.'
            )

    @action(detail=True, methods=['get', 'post'], url_path='membros')
    def membros(self, request, pk=None):
        projeto = self.get_object()

        if request.method == 'GET':
            lista = projeto.membros.select_related('usuario').order_by('id')
            serializer = ProjetoMembroSerializer(lista, many=True)
            return Response(serializer.data)

        self._exigir_proprietario(projeto)

        serializer = ProjetoMembroSerializer(
            data=request.data,
            context={'request': request, 'projeto': projeto},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(projeto=projeto)

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
        )

    @action(
        detail=True,
        methods=['patch', 'delete'],
        url_path=r'membros/(?P<membro_id>\d+)',
    )
    def membro(self, request, pk=None, membro_id=None):
        projeto = self.get_object()
        self._exigir_proprietario(projeto)

        membro = get_object_or_404(projeto.membros, pk=membro_id)

        if request.method == 'DELETE':
            # Não deixe tarefas atribuídas a alguém que saiu do projeto.
            tarefas_atribuidas = Tarefa.objects.filter(
                projeto=projeto,
                user=membro.usuario,
            )

            substituto_id = projeto.proprietario_id

            if substituto_id is None:
                substituto_id = (
                    projeto.membros.exclude(pk=membro.pk)
                    .order_by('id')
                    .values_list('usuario_id', flat=True)
                    .first()
                )

            if tarefas_atribuidas.exists() and substituto_id is None:
                raise ValidationError({
                    'detail': (
                        'Não é possível remover este participante porque ele '
                        'é responsável por tarefas e não há outro participante '
                        'para receber essas tarefas.'
                    )
                })

            with transaction.atomic():
                if tarefas_atribuidas.exists():
                    tarefas_atribuidas.update(user_id=substituto_id)

                membro.delete()

            return Response(status=status.HTTP_204_NO_CONTENT)

        serializer = ProjetoMembroSerializer(
            membro,
            data=request.data,
            partial=True,
            context={'request': request, 'projeto': projeto},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)
