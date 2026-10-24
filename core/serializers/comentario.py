from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from core.models import Comentario

from .user import UserResumoSerializer


class ComentarioSerializer(ModelSerializer):
    # O autor é sempre o usuário autenticado (definido na view).
    autor = UserResumoSerializer(source='user', read_only=True)

    class Meta:
        model = Comentario
        fields = ('id', 'descricao', 'tarefa', 'user', 'autor', 'created_at')
        read_only_fields = ('id', 'user', 'autor', 'created_at')

    def validate_tarefa(self, tarefa):
        request = self.context['request']

        if self.instance and tarefa != self.instance.tarefa:
            raise serializers.ValidationError(
                'Não é possível mover o comentário para outra tarefa.'
            )

        # Qualquer participante do projeto pode comentar.
        if not tarefa.pode_ver(request.user):
            raise serializers.ValidationError(
                'Você não participa do projeto desta tarefa.'
            )

        return tarefa
