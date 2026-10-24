from django.db import models

from core.models import Projeto, User


class Nota(models.Model):
    titulo = models.CharField(max_length=45)
    texto = models.CharField(max_length=10000)

    user = models.ForeignKey(User, related_name='nota', on_delete=models.PROTECT)

    def __str__(self):
        return self.titulo
