from django.db import models

from .projeto import Projeto
from .user import User


class ProjetoMembro(models.Model):
    """Participante de um projeto (o proprietário fica em Projeto)."""

    class TipoPapel(models.TextChoices):
        VISUALIZADOR = 'visualizador', 'Visualizador'
        EDITOR = 'editor', 'Editor'

    projeto = models.ForeignKey(
        Projeto,
        related_name='membros',
        on_delete=models.CASCADE,
    )
    usuario = models.ForeignKey(
        User,
        related_name='participacoes',
        on_delete=models.CASCADE,
    )
    papel = models.CharField(
        max_length=20,
        choices=TipoPapel.choices,
        default=TipoPapel.VISUALIZADOR,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['projeto', 'usuario'],
                name='membro_unico_por_projeto',
            ),
        ]

    def __str__(self):
        return f'{self.usuario} em {self.projeto} ({self.papel})'