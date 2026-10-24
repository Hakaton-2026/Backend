from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from core.models import Projeto, Tarefa, User

from .checklist_item import ChecklistItemSerializer
from .comentario import ComentarioSerializer
from .material_apoio import MaterialApoioSerializer


class TarefaCreateUpdateSerializer(ModelSerializer):
    id = serializers.IntegerField(
        required=False,
        read_only=True,
    )

    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        required=False,
    )

    projeto = serializers.PrimaryKeyRelatedField(
        queryset=Projeto.objects.all(),
        required=False,
        allow_null=True,
    )

    comentarios = ComentarioSerializer(
        many=True,
        read_only=True,
    )

    checklist = ChecklistItemSerializer(
        many=True,
        read_only=True,
    )

    materiais = MaterialApoioSerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = Tarefa
        fields = (
            'id',
            'titulo',
            'descricao',
            'situacao',
            'prioridade',
            'prazoInicio',
            'prazoFim',
            'texto',
            'user',
            'projeto',
            'comentarios',
            'checklist',
            'materiais',
        )

    def validate(self, attrs):
        request = self.context['request']

        prazo_inicio = attrs.get(
            'prazoInicio',
            getattr(self.instance, 'prazoInicio', None),
        )

        prazo_fim = attrs.get(
            'prazoFim',
            getattr(self.instance, 'prazoFim', None),
        )

        if prazo_inicio and prazo_fim and prazo_fim < prazo_inicio:
            raise serializers.ValidationError({
                'prazoFim': (
                    'O prazo final não pode ser anterior ao início.'
                )
            })

        projeto = attrs.get(
            'projeto',
            getattr(self.instance, 'projeto', None),
        )

        mudou_projeto = (
            self.instance is None
            or (
                'projeto' in attrs
                and attrs['projeto'] != self.instance.projeto
            )
        )

        if self.instance is None:
            responsavel = attrs.get('user') or request.user
            attrs['user'] = responsavel
        else:
            responsavel = attrs.get(
                'user',
                self.instance.user,
            )

        mudou_responsavel = (
            self.instance is None
            or (
                'user' in attrs
                and attrs['user'] != self.instance.user
            )
        )

        if projeto is None:
            if responsavel != request.user:
                raise serializers.ValidationError({
                    'user': (
                        'Uma tarefa sem projeto só pode ser sua.'
                    )
                })

            return attrs

        if mudou_projeto and not projeto.pode_editar(request.user):
            raise serializers.ValidationError({
                'projeto': (
                    'Você não tem permissão para criar tarefas '
                    'neste projeto.'
                )
            })

        if (
            mudou_projeto or mudou_responsavel
        ) and not projeto.eh_participante(responsavel):
            raise serializers.ValidationError({
                'user': (
                    'O responsável precisa participar do projeto.'
                )
            })

        return attrs


class TarefaAninhadaSerializer(TarefaCreateUpdateSerializer):
    """Tarefa enviada dentro do payload de um projeto."""

    def validate(self, attrs):
        prazo_inicio = attrs.get('prazoInicio')
        prazo_fim = attrs.get('prazoFim')

        if prazo_inicio and prazo_fim and prazo_fim < prazo_inicio:
            raise serializers.ValidationError({
                'prazoFim': (
                    'O prazo final não pode ser anterior ao início.'
                )
            })

        return attrs


class TarefaListSerializer(ModelSerializer):
    projeto = serializers.PrimaryKeyRelatedField(
        read_only=True,
    )

    checklist_total = serializers.IntegerField(
        read_only=True,
        default=0,
    )

    checklist_concluidos = serializers.IntegerField(
        read_only=True,
        default=0,
    )

    class Meta:
        model = Tarefa
        fields = (
            'id',
            'titulo',
            'descricao',
            'situacao',
            'prioridade',
            'prazoInicio',
            'prazoFim',
            'texto',
            'user',
            'projeto',
            'checklist_total',
            'checklist_concluidos',
        )


class TarefaRetrieveSerializer(ModelSerializer):
    comentarios = ComentarioSerializer(
        many=True,
        read_only=True,
    )

    checklist = ChecklistItemSerializer(
        many=True,
        read_only=True,
    )

    materiais = MaterialApoioSerializer(
        many=True,
        read_only=True,
    )

    projeto = serializers.PrimaryKeyRelatedField(
        read_only=True,
    )

    class Meta:
        model = Tarefa
        fields = (
            'id',
            'titulo',
            'descricao',
            'situacao',
            'prioridade',
            'prazoInicio',
            'prazoFim',
            'texto',
            'user',
            'projeto',
            'comentarios',
            'checklist',
            'materiais',
        )
