from django.db import transaction
from rest_framework.serializers import ModelSerializer

from core.models import Projeto, Tarefa
from core.serializers import TarefaSerializer


class ProjetoCreateUpdateSerializer(ModelSerializer):
    tarefas = TarefaSerializer(many=True, required=False)
    class Meta:
        model = Projeto
        fields = ('id', 'nome', 'descricao', 'tarefas',)

    @transaction.atomic
    def create(self, validated_data):
        tarefas = validated_data.pop('tarefas', [])
        projeto = Projeto.objects.create(**validated_data)
        for tarefa in tarefas:
            Tarefa.objects.create(projeto=projeto, **tarefa)
        projeto.save()
        return projeto


class ProjetoListSerializer(ModelSerializer):
    tarefas = TarefaSerializer(many=True, read_only=True)
    class Meta:
        model = Projeto
        fields = ('id', 'nome', 'descricao', 'tarefas',)


class ProjetoRetrieveSerializer(ModelSerializer):
    tarefas = TarefaSerializer(many=True, read_only=True)
    class Meta:
        model = Projeto
        fields = ('id', 'nome', 'descricao', 'tarefas',)
