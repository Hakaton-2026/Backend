from django.db import models
from django.db.models import Q


class ProjetoQuerySet(models.QuerySet):
    def visiveis_para(self, user):
        """Projetos em que o usuário é proprietário ou participante."""
        if not user or not user.is_authenticated:
            return self.none()

        return self.filter(
            Q(proprietario=user) | Q(membros__usuario=user)
        ).distinct()


class Projeto(models.Model):
    PAPEL_PROPRIETARIO = 'proprietario'
    PAPEL_EDITOR = 'editor'
    PAPEL_VISUALIZADOR = 'visualizador'

    nome = models.CharField(max_length=45)
    descricao = models.CharField(max_length=255, null=True, blank=True)

    # Null apenas para projetos antigos, criados antes do controle de acesso.
    proprietario = models.ForeignKey(
        'core.User',
        related_name='projetos_proprios',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )

    objects = ProjetoQuerySet.as_manager()

    def __str__(self):
        return self.nome

    def papel_de(self, user):
        """Retorna o papel do usuário no projeto ou None se não participa."""
        if not user or not user.is_authenticated:
            return None

        if self.proprietario_id == user.id:
            return self.PAPEL_PROPRIETARIO

        membro = self.membros.filter(usuario=user).first()
        return membro.papel if membro else None

    def pode_ver(self, user):
        return self.papel_de(user) is not None

    def pode_editar(self, user):
        return self.papel_de(user) in {
            self.PAPEL_PROPRIETARIO,
            self.PAPEL_EDITOR,
        }

    def eh_participante(self, user):
        return self.pode_ver(user)
