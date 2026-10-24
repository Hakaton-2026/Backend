from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from core.models import MaterialApoio


class MaterialApoioSerializer(ModelSerializer):
    class Meta:
        model = MaterialApoio
        fields = (
            'id',
            'titulo',
            'url',
            'descricao',
            'projeto',
            'tarefa',
            'user',
            'created_at',
        )
        read_only_fields = ('id', 'user', 'created_at')

    def validate(self, attrs):
        request = self.context['request']

        projeto = attrs.get('projeto', getattr(self.instance, 'projeto', None))
        tarefa = attrs.get('tarefa', getattr(self.instance, 'tarefa', None))

        if bool(projeto) == bool(tarefa):
            raise serializers.ValidationError(
                'Informe o projeto ou a tarefa (apenas um dos dois).'
            )

        if self.instance and (
            projeto != self.instance.projeto or tarefa != self.instance.tarefa
        ):
            raise serializers.ValidationError(
                'Não é possível mudar o destino de um material.'
            )

        alvo = tarefa or projeto

        if not alvo.pode_editar(request.user):
            raise serializers.ValidationError(
                'Você não tem permissão para adicionar materiais aqui.'
            )

        return attrs
