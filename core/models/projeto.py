
from django.conf import settings
from django.db import models


class Projeto(models.Model):
    nome = models.CharField(max_length=45)
    descricao = models.CharField(max_length=255, null=True, blank=True)

    proprietario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="projetos_proprios",
    )

    participantes = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through="ProjetoParticipante",
        related_name="projetos_compartilhados",
        blank=True,
    )

    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nome


class ProjetoParticipante(models.Model):
    class Papel(models.TextChoices):
        VISUALIZADOR = "visualizador", "Visualizador"
        EDITOR = "editor", "Editor"

    projeto = models.ForeignKey(
        Projeto,
        on_delete=models.CASCADE,
        related_name="membros",
    )

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="participacoes_projetos",
    )

    papel = models.CharField(
        max_length=20,
        choices=Papel.choices,
        default=Papel.VISUALIZADOR,
    )

    compartilhado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["projeto", "usuario"],
                name="unico_participante_por_projeto",
            )
        ]

    def __str__(self):
        return f"{self.usuario} - {self.projeto} ({self.papel})"
