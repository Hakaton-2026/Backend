from django.db import models
from django.db.models import Q

from .projeto import Projeto
from .user import User


class TarefaQuerySet(models.QuerySet):
    def visiveis_para(self, user):
        """Tarefas dos projetos do usuário e as pessoais (sem projeto)."""
        if not user or not user.is_authenticated:
            return self.none()

        projetos = Projeto.objects.visiveis_para(user).values('pk')

        return self.filter(
            Q(projeto__in=projetos) | Q(projeto__isnull=True, user=user)
        ).distinct()


class Tarefa(models.Model):
    titulo = models.CharField(max_length=45)
    descricao = models.CharField(
        max_length=200,
        null=True,
        blank=True,
    )

    class TipoSituacao(models.IntegerChoices):
        A_FAZER = 1, 'A fazer'
        EM_ANDAMENTO = 2, 'Em andamento'
        CONCLUIDO = 3, 'Concluído'

    situacao = models.IntegerField(
        choices=TipoSituacao.choices,
        default=TipoSituacao.A_FAZER,
    )

    class TipoPrioridade(models.IntegerChoices):
        BAIXA = 1, 'Baixa'
        MEDIA = 2, 'Média'
        ALTA = 3, 'Alta'
        URGENTE = 4, 'Urgente'

    prioridade = models.IntegerField(
        choices=TipoPrioridade.choices,
        default=TipoPrioridade.BAIXA,
    )

    prazoInicio = models.DateField()
    prazoFim = models.DateField()
    texto = models.CharField(
        max_length=500,
        null=True,
        blank=True,
    )

    # Responsável pela tarefa (precisa participar do projeto).
    user = models.ForeignKey(
        User,
        related_name='tarefas',
        on_delete=models.PROTECT,
    )

    projeto = models.ForeignKey(
        Projeto,
        related_name='tarefas',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )

    objects = TarefaQuerySet.as_manager()

    def __str__(self):
        return self.titulo

    def papel_de(self, user):
        """Papel do usuário na tarefa (herdado do projeto)."""
        if self.projeto_id:
            return self.projeto.papel_de(user)

        if user and user.is_authenticated and self.user_id == user.id:
            return Projeto.PAPEL_PROPRIETARIO

        return None

    def pode_ver(self, user):
        return self.papel_de(user) is not None

    def pode_editar(self, user):
        return self.papel_de(user) in {
            Projeto.PAPEL_PROPRIETARIO,
            Projeto.PAPEL_EDITOR,
        }
