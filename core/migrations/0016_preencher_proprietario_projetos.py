from django.db import migrations


def preencher_proprietario(apps, schema_editor):
    """Preenche o proprietário de projetos antigos que ainda não têm dono."""

    Projeto = apps.get_model('core', 'Projeto')
    Tarefa = apps.get_model('core', 'Tarefa')
    User = apps.get_model('core', 'User')

    padrao = (
        User.objects.filter(is_superuser=True).order_by('id').first()
        or User.objects.order_by('id').first()
    )

    for projeto in Projeto.objects.filter(proprietario__isnull=True):
        tarefa = Tarefa.objects.filter(projeto=projeto).order_by('id').first()
        dono_id = tarefa.user_id if tarefa else (padrao.id if padrao else None)

        if dono_id:
            projeto.proprietario_id = dono_id
            projeto.save(update_fields=['proprietario'])


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0015_projetos_membros_checklist_materiai'),
    ]

    operations = [
        migrations.RunPython(
            preencher_proprietario,
            migrations.RunPython.noop,
        ),
    ]