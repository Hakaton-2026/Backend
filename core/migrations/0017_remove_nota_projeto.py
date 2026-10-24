from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0016_preencher_proprietario_projetos'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='nota',
            name='projeto',
        ),
    ]