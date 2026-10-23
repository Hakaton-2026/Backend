from django.db import transaction
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from core.models import Projeto, ProjetoParticipante, Tarefa, User
from core.serializers import TarefaCreateUpdateSerializer, TarefaListSerializer


class ProjetoUsuarioSerializer(ModelSerializer):
    """Resumo de um usuário exibido dentro de um projeto."""

    class Meta:
        model = User
        fields = ('id', 'name', 'email')
        read_only_fields = fields


class ProjetoCreateUpdateSerializer(ModelSerializer):
    tarefas = TarefaCreateUpdateSerializer(many=True, required=False)
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
    tarefas = TarefaListSerializer(many=True, read_only=True)
    proprietario = ProjetoUsuarioSerializer(read_only=True)
    meu_papel = serializers.SerializerMethodField()
    total_participantes = serializers.SerializerMethodField()

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

    def get_meu_papel(self, projeto) -> str:
        """Papel de quem consulta: 'proprietario', 'editor' ou 'visualizador'."""
        usuario = self.context['request'].user

        if projeto.proprietario_id == usuario.id:
            return 'proprietario'

        for membro in projeto.membros.all():
            if membro.usuario_id == usuario.id:
                return membro.papel

        return ''

    def get_total_participantes(self, projeto) -> int:
        return len(projeto.membros.all())


class ProjetoRetrieveSerializer(ProjetoListSerializer):
    pass


class ProjetoMembroSerializer(ModelSerializer):
    """Participante de um projeto.

    Na escrita, `usuario` recebe o id da pessoa; na leitura, devolve
    um resumo dela (id, name e email).
    """

    usuario = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = ProjetoParticipante
        fields = ('id', 'usuario', 'papel', 'compartilhado_em')
        read_only_fields = ('id', 'compartilhado_em')

    def validate_usuario(self, usuario):
        # Na edição só o papel muda; a pessoa continua a mesma.
        if self.instance is not None:
            return usuario

        projeto = self.context['projeto']

        if usuario.pk == projeto.proprietario_id:
            raise serializers.ValidationError(
                'O proprietário já tem acesso total ao projeto.'
            )

        if projeto.membros.filter(usuario=usuario).exists():
            raise serializers.ValidationError(
                'Esta pessoa já participa do projeto.'
            )

        return usuario

    def update(self, instance, validated_data):
        validated_data.pop('usuario', None)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        dados = super().to_representation(instance)
        dados['usuario'] = ProjetoUsuarioSerializer(instance.usuario).data
        return dados