from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0016_preencher_proprietario_projetos'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunSQL(
                    sql='''
                        ALTER TABLE core_nota
                        DROP COLUMN IF EXISTS projeto_id;
                    ''',
                    reverse_sql=migrations.RunSQL.noop,
                ),
            ],
            state_operations=[
                migrations.RemoveField(
                    model_name='nota',
                    name='projeto',
                ),
            ],
        ),
    ]