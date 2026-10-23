from rest_framework.serializers import ModelSerializer

from core.models import Tarefa


class TarefaSerializer(ModelSerializer):
    class Meta:
        model = Tarefa
        fields = '__all__'
