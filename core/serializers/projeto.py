
from django.db import transaction
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from core.models import Projeto, Tarefa
from core.serializers.tarefa import (
    TarefaCreateUpdateSerializer,
    TarefaListSerializer,
)


class ProjetoCreateUpdateSerializer(ModelSerializer):
    tarefas = TarefaCreateUpdateSerializer(
        many=True,
        required=False,
    )

    class Meta:
        model = Projeto
        fields = ('id', 'nome', 'descricao', 'tarefas')

    @transaction.atomic
    def create(self, validated_data):
        tarefas_data = validated_data.pop('tarefas', [])
        projeto = Projeto.objects.create(**validated_data)

        for tarefa_data in tarefas_data:
            tarefa_data.pop('id', None)
            tarefa_data.pop('projeto', None)

            Tarefa.objects.create(
                projeto=projeto,
                **tarefa_data,
            )

        return projeto

    @transaction.atomic
    def update(self, instance, validated_data):
        tarefas_data = validated_data.pop('tarefas', None)

        instance = super().update(instance, validated_data)

        if tarefas_data is None:
            return instance

        for tarefa_data in tarefas_data:
            tarefa_id = tarefa_data.pop('id', None)
            tarefa_data.pop('projeto', None)

            if tarefa_id is None:
                Tarefa.objects.create(
                    projeto=instance,
                    **tarefa_data,
                )
                continue

            try:
                tarefa = Tarefa.objects.get(
                    pk=tarefa_id,
                    projeto=instance,
                )
            except Tarefa.DoesNotExist:
                raise serializers.ValidationError({
                    'tarefas': (
                        f'A tarefa {tarefa_id} não existe '
                        'ou não pertence a este projeto.'
                    )
                })

            serializer = TarefaCreateUpdateSerializer(
                tarefa,
                data=tarefa_data,
                partial=True,
                context=self.context,
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()

        return instance


class ProjetoListSerializer(ModelSerializer):
    tarefas = TarefaListSerializer(many=True, read_only=True)

    class Meta:
        model = Projeto
        fields = ('id', 'nome', 'descricao', 'tarefas')


class ProjetoRetrieveSerializer(ModelSerializer):
    tarefas = TarefaListSerializer(many=True, read_only=True)

    class Meta:
        model = Projeto
        fields = ('id', 'nome', 'descricao', 'tarefas')
