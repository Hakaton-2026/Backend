from django.db import models


class Projeto(models.Model):
    nome = models.CharField(max_length=45)
    descricao = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.nome
