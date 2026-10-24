from django.db import models

from core.models import Projeto, Tarefa, User


class MaterialApoio(models.Model):
    """Link para documento, pasta ou recurso ligado a um projeto ou tarefa."""

    titulo = models.CharField(max_length=100)
    url = models.URLField(max_length=500)
    descricao = models.CharField(max_length=255, null=True, blank=True)

    projeto = models.ForeignKey(
        Projeto,
        related_name='materiais',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    tarefa = models.ForeignKey(
        Tarefa,
        related_name='materiais',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    user = models.ForeignKey(
        User,
        related_name='materiais',
        on_delete=models.CASCADE,
    )
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        ordering = ['-id']
        constraints = [
            # Exatamente um destino: projeto OU tarefa.
            models.CheckConstraint(
                condition=(
                    models.Q(projeto__isnull=False, tarefa__isnull=True)
                    | models.Q(projeto__isnull=True, tarefa__isnull=False)
                ),
                name='material_projeto_xor_tarefa',
            ),
        ]

    def __str__(self):
        return self.titulo

    def papel_de(self, user):
        if self.tarefa_id:
            return self.tarefa.papel_de(user)

        return self.projeto.papel_de(user)
