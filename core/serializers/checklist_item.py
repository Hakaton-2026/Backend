from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from core.models import ChecklistItem


class ChecklistItemSerializer(ModelSerializer):
    class Meta:
        model = ChecklistItem
        fields = ('id', 'texto', 'concluido', 'tarefa')

    def validate_tarefa(self, tarefa):
        request = self.context['request']

        if self.instance and tarefa != self.instance.tarefa:
            raise serializers.ValidationError(
                'Não é possível mover o item para outra tarefa.'
            )

        if not tarefa.pode_editar(request.user):
            raise serializers.ValidationError(
                'Você não tem permissão para editar esta tarefa.'
            )

        return tarefa
