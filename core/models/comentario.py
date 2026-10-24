from django.db import models

from core.models import Tarefa, User


class Comentario(models.Model):
    descricao = models.CharField(max_length=255)

    # Autor do comentário (definido pelo servidor, nunca pelo cliente).
    user = models.ForeignKey(User, related_name='comentarios', on_delete=models.CASCADE)
    tarefa = models.ForeignKey(Tarefa, related_name='comentarios', on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return f"{self.user} - {self.tarefa}"

    def papel_de(self, user):
        return self.tarefa.papel_de(user)
