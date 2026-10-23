
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from core.models import Projeto, Tarefa

from .comentario import ComentarioSerializer


class TarefaCreateUpdateSerializer(ModelSerializer):
    id = serializers.IntegerField(required=False, read_only=True)

    projeto = serializers.PrimaryKeyRelatedField(
        queryset=Projeto.objects.all(),
        required=False,
        allow_null=True,
    )

    comentarios = ComentarioSerializer(
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
        )


class TarefaListSerializer(ModelSerializer):
    projeto = serializers.PrimaryKeyRelatedField(read_only=True)

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
        )


class TarefaRetrieveSerializer(ModelSerializer):
    comentarios = ComentarioSerializer(many=True, read_only=True)
    projeto = serializers.PrimaryKeyRelatedField(read_only=True)

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
        )
