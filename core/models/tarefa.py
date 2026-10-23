from django.db import models

from core.models.user import User


class Tarefa(models.Model):
    titulo = models.CharField(max_length=45)
    descricao = models.CharField(max_length=200, null=True, blank=True)

    class TipoPrioridade(models.IntegerChoices):
        A_FAZER = 1, 'A fazer'
        EM_ANDAMENTO = 2, 'Em andamento'
        CONCLUIDO = 3, 'Concluído'

    prioridade = models.IntegerField(
        choices=TipoPrioridade.choices,
        default=TipoPrioridade.A_FAZER
    )
    prazoInicio = models.DateField()
    prazoFim = models.DateField()
    texto = models.CharField(max_length=500, null=True, blank=True)

    user = models.ForeignKey(User, related_name='user', on_delete=models.PROTECT)
