from django.db import transaction
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from core.models import Projeto, ProjetoMembro, Tarefa, User

from .material_apoio import MaterialApoioSerializer
from .tarefa import TarefaAninhadaSerializer, TarefaListSerializer
from .user import UserResumoSerializer


class ProjetoMembroSerializer(ModelSerializer):
    """Participante do projeto.

    Na escrita, `usuario` é o id; na leitura, devolve o resumo do usuário.
    """

    usuario = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(is_active=True),
    )

    class Meta:
        model = ProjetoMembro
        fields = ('id', 'usuario', 'papel')

    def to_representation(self, instance):
        dados = super().to_representation(instance)
        dados['usuario'] = UserResumoSerializer(instance.usuario).data
        return dados

    def validate_usuario(self, usuario):
        projeto = self.context['projeto']

        if self.instance:
            if usuario != self.instance.usuario:
                raise serializers.ValidationError(
                    'Não é possível trocar a pessoa; remova e adicione de novo.'
                )
            return usuario

        if projeto.proprietario_id == usuario.id:
            raise serializers.ValidationError(
                'O proprietário já tem acesso total ao projeto.'
            )

        if projeto.membros.filter(usuario=usuario).exists():
            raise serializers.ValidationError(
                'Esta pessoa já participa do projeto.'
            )

        return usuario


class _ProjetoBaseSerializer(ModelSerializer):
    proprietario = UserResumoSerializer(read_only=True)
    meu_papel = serializers.SerializerMethodField()
    total_participantes = serializers.SerializerMethodField()

    def get_meu_papel(self, projeto):
        request = self.context.get('request')

        if not request:
            return None

        return projeto.papel_de(request.user)

    def get_total_participantes(self, projeto):
        return projeto.membros.count()


class ProjetoCreateUpdateSerializer(_ProjetoBaseSerializer):
    tarefas = TarefaAninhadaSerializer(
        many=True,
        required=False,
    )

    class Meta:
        model = Projeto
        fields = (
            'id',
            'nome',
            'descricao',
            'proprietario',
            'meu_papel',
            'total_participantes',
            'tarefas',
        )

    @staticmethod
    def _validar_responsavel(projeto, tarefa_data, tarefa_existente=None):
        responsavel = tarefa_data.get(
            'user',
            tarefa_existente.user if tarefa_existente is not None else None,
        )

        if responsavel is None:
            responsavel = projeto.proprietario

        if responsavel is None or not projeto.eh_participante(responsavel):
            raise serializers.ValidationError({
                'tarefas': (
                    f'{responsavel or "O responsável"} precisa participar do projeto '
                    'para ser responsável por uma tarefa.'
                )
            })

    @transaction.atomic
    def create(self, validated_data):
        tarefas_data = validated_data.pop('tarefas', [])

        # `proprietario` vem de serializer.save(proprietario=request.user).
        projeto = Projeto.objects.create(**validated_data)

        for tarefa_data in tarefas_data:
            tarefa_data.pop('id', None)
            tarefa_data.pop('projeto', None)
            tarefa_data.setdefault('user', projeto.proprietario)

            self._validar_responsavel(projeto, tarefa_data)

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
                tarefa_data.setdefault('user', instance.proprietario)
                self._validar_responsavel(instance, tarefa_data)

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

            self._validar_responsavel(
                instance,
                tarefa_data,
                tarefa_existente=tarefa,
            )

            for campo, valor in tarefa_data.items():
                setattr(tarefa, campo, valor)

            tarefa.save()

        return instance


class ProjetoListSerializer(_ProjetoBaseSerializer):
    tarefas = TarefaListSerializer(many=True, read_only=True)

    class Meta:
        model = Projeto
        fields = (
            'id',
            'nome',
            'descricao',
            'proprietario',
            'meu_papel',
            'total_participantes',
            'tarefas',
        )


class ProjetoRetrieveSerializer(_ProjetoBaseSerializer):
    tarefas = TarefaListSerializer(many=True, read_only=True)
    materiais = MaterialApoioSerializer(many=True, read_only=True)

    class Meta:
        model = Projeto
        fields = (
            'id',
            'nome',
            'descricao',
            'proprietario',
            'meu_papel',
            'total_participantes',
            'tarefas',
            'materiais',
        )
