from django.db import models

from core.models import Tarefa, User


class Comentario(models.Model):
    descricao = models.CharField(max_length=255)

    user = models.ForeignKey(User, related_name='comentarios', on_delete=models.CASCADE)
    tarefa = models.ForeignKey(Tarefa, related_name='comentarios', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user} - {self.tarefa}"
