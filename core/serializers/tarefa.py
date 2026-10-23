from rest_framework.serializers import ModelSerializer

from core.models import Tarefa

from .comentario import ComentarioSerializer


class TarefaCreateUpdateSerializer(ModelSerializer):
    comentarios = ComentarioSerializer(many=True)

    class Meta:
        model = Tarefa
        fields = (
            'titulo',
            'descricao',
            'situacao',
            'prioridade',
            'prazoInicio',
            'prazoFim',
            'texto',
            'user',
            'comentarios'
        )


class TarefaListSerializer(ModelSerializer):
    class Meta:
        model = Tarefa
        fields = (
            'titulo',
            'descricao',
            'situacao',
            'prioridade',
            'prazoInicio',
            'prazoFim',
            'texto',
            'user',
        )


class TarefaRetrieveSerializer(ModelSerializer):
    comentarios = ComentarioSerializer(many=True, read_only=True)

    class Meta:
        model = Tarefa
        fields = (
            'titulo',
            'descricao',
            'situacao',
            'prioridade',
            'prazoInicio',
            'prazoFim',
            'texto',
            'user',
            'comentarios',
        )
