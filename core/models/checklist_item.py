from django.db import models

from core.models import Tarefa


class ChecklistItem(models.Model):
    texto = models.CharField(max_length=255)
    concluido = models.BooleanField(default=False)

    tarefa = models.ForeignKey(
        Tarefa,
        related_name='checklist',
        on_delete=models.CASCADE,
    )

    class Meta:
        ordering = ['id']

    def __str__(self):
        return self.texto

    def papel_de(self, user):
        return self.tarefa.papel_de(user)
