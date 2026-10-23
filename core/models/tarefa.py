from django.db import models

from .projeto import Projeto
from .user import User


class Tarefa(models.Model):
    titulo = models.CharField(max_length=45)
    descricao = models.CharField(max_length=200, null=True, blank=True)

    class TipoSituacao(models.IntegerChoices):
        A_FAZER = 1, 'A fazer'
        EM_ANDAMENTO = 2, 'Em andamento'
        CONCLUIDO = 3, 'Concluído'

    situacao = models.IntegerField(
        choices=TipoSituacao.choices,
        default=TipoSituacao.A_FAZER
    )
    class TipoPrioridade(models.IntegerChoices):
        BAIXA = 1, 'Baixa',
        MEDIA = 2, 'Média',
        ALTA = 3, 'Alta',
        URGENTE = 4, 'Urgente'

    prioridade = models.IntegerField(
        choices=TipoPrioridade.choices,
        default=TipoPrioridade.BAIXA
    )

    prazoInicio = models.DateField()
    prazoFim = models.DateField()
    texto = models.CharField(max_length=500, null=True, blank=True)

    user = models.ForeignKey(User, related_name='tarefas', on_delete=models.PROTECT)

    projeto = models.ForeignKey(Projeto, related_name='tarefas', on_delete=models.PROTECT)

    def __str__(self):
        return self.titulo
